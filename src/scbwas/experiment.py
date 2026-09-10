from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from .core import ModalFieldComputer, Probe, default_modes, with_mode


def make_machine(kind: str, n_space: int = 256) -> ModalFieldComputer:
    modes = default_modes()
    if kind == "frequency_mismatch":
        modes = with_mode(modes, "B", omega=12.0)
    elif kind == "spatial_separation":
        modes = with_mode(modes, "B", q=3.55)
    return ModalFieldComputer(
        modes,
        n_space=n_space,
        dt=0.01,
        coupling=1.0,
        coherence_tau=0.65,
        structure_tau=120.0,
        write_rate=0.18,
        theta_clip=0.18,
    )


def train_association(
    machine: ModalFieldComputer,
    *,
    phase: float = 0.0,
    cycles: int = 28,
    active_steps: int = 55,
    gap_steps: int = 18,
) -> dict:
    """Drive A and B continuously; pair coherence performs the selection.

    ``cycles`` is retained as a convenient duration knob, but there are no
    episode resets. The same physical drive remains on for the equivalent
    number of steps, which prevents a frequency-mismatched channel from being
    spuriously re-phased at artificial boundaries.
    """
    ia = machine.index("A")
    ib = machine.index("B")
    drive = np.zeros(machine.size, dtype=complex)
    drive[ia] = 0.55
    drive[ib] = 0.55 * np.exp(1j * phase)
    total_steps = int(cycles) * (int(active_steps) + int(gap_steps))
    drives = []
    for _ in range(total_steps):
        machine.step(
            write_pairs=((ia, ib, 1.0), (ib, ia, 1.0)),
            drive=drive,
            input_gain=0.22,
        )
        drives.append(
            machine.overlap[ib, ia] * float(np.real(machine.coherence[ib, ia]))
        )
    return {
        "mean_write_drive": float(np.mean(drives)),
        "final_route_A_to_B": float(machine.theta[ib, ia]),
        "final_route_B_to_A": float(machine.theta[ia, ib]),
        "structure_l2": float(np.linalg.norm(machine.theta)),
    }


def recall_a(machine: ModalFieldComputer, *, steps: int = 190) -> dict:
    machine.reset_fast(reset_coherence=True)
    ia = machine.index("A")
    ib = machine.index("B")
    ic = machine.index("C")
    machine.inject(ia, 1.0)
    peak_b = 0.0
    peak_c = 0.0
    trajectory = []
    for t in range(int(steps)):
        machine.step()
        pb = float(machine.modal_power()[ib])
        pc = float(machine.modal_power()[ic])
        peak_b = max(peak_b, pb)
        peak_c = max(peak_c, pc)
        if t % 10 == 0:
            trajectory.append(
                {
                    "step": t,
                    "A": float(machine.modal_power()[ia]),
                    "B": pb,
                    "C": pc,
                }
            )
    probes = [
        Probe("B", machine.modes[ib].q, 0.46),
        Probe("C", machine.modes[ic].q, 0.46),
    ]
    asked = machine.ask(probes, threshold=0.22, max_questions=2)
    return {
        "peak_B_mode_power": peak_b,
        "peak_C_mode_power": peak_c,
        "B_over_C": float(peak_b / (peak_c + 1e-12)),
        "ask": {
            "chosen": list(asked.chosen),
            "values": list(asked.values),
            "decision": asked.decision,
            "cost": asked.cost,
        },
        "trajectory": trajectory,
    }


def eigen_receipt(machine: ModalFieldComputer) -> dict:
    spec = machine.spectrum()
    eig = np.asarray(spec["eigenvalues"])
    life = np.asarray(spec["lifetimes"])
    return {
        "spectral_abscissa": float(spec["spectral_abscissa"]),
        "eigenvalues": [
            {"real": float(z.real), "imag": float(z.imag)} for z in eig
        ],
        "lifetimes": [None if not np.isfinite(v) else float(v) for v in life],
    }


def run_machine(
    *,
    n_space: int = 256,
    cycles: int = 28,
    recall_steps: int = 190,
) -> dict:
    worlds = {
        "blank": make_machine("matched", n_space),
        "matched_phase_0": make_machine("matched", n_space),
        "phase_pi_over_2": make_machine("matched", n_space),
        "phase_pi": make_machine("matched", n_space),
        "frequency_mismatch": make_machine("frequency_mismatch", n_space),
        "spatial_separation": make_machine("spatial_separation", n_space),
    }

    before_select = worlds["matched_phase_0"].select_from_broadband(steps=800, seed=3)
    before_spectrum = eigen_receipt(worlds["matched_phase_0"])

    training = {
        "blank": {
            "mean_write_drive": 0.0,
            "final_route_A_to_B": 0.0,
            "structure_l2": 0.0,
        },
        "matched_phase_0": train_association(worlds["matched_phase_0"], phase=0.0, cycles=cycles),
        "phase_pi_over_2": train_association(worlds["phase_pi_over_2"], phase=np.pi / 2, cycles=cycles),
        "phase_pi": train_association(worlds["phase_pi"], phase=np.pi, cycles=cycles),
        "frequency_mismatch": train_association(worlds["frequency_mismatch"], phase=0.0, cycles=cycles),
        "spatial_separation": train_association(worlds["spatial_separation"], phase=0.0, cycles=cycles),
    }

    learned = worlds["matched_phase_0"]
    after_spectrum = eigen_receipt(learned)
    after_select = learned.select_from_broadband(steps=800, seed=3)

    recall = {name: recall_a(world, steps=recall_steps) for name, world in worlds.items()}

    matched_route = training["matched_phase_0"]["final_route_A_to_B"]
    freq_route = training["frequency_mismatch"]["final_route_A_to_B"]
    sep_route = training["spatial_separation"]["final_route_A_to_B"]
    quarter_route = training["phase_pi_over_2"]["final_route_A_to_B"]
    anti_route = training["phase_pi"]["final_route_A_to_B"]

    return {
        "status": "assembled_machine",
        "claim_boundary": (
            "This is an engineered classical modal-flow computer. It composes modal "
            "selection, coherent carrier transport, quadratic binding, slow structural "
            "writing, bounded active readout, and re-selection. The write law is explicit; "
            "this does not establish quantum advantage or spontaneous Navier-Stokes learning."
        ),
        "config": {
            "n_space": n_space,
            "training_cycles": cycles,
            "recall_steps": recall_steps,
        },
        "select_before": {
            "before_effective_dimension": float(before_select["before_effective_dimension"]),
            "after_effective_dimension": float(before_select["after_effective_dimension"]),
            "after_power": np.asarray(before_select["after_power"]).tolist(),
        },
        "spectrum_before": before_spectrum,
        "training": training,
        "spectrum_after": after_spectrum,
        "select_after": {
            "before_effective_dimension": float(after_select["before_effective_dimension"]),
            "after_effective_dimension": float(after_select["after_effective_dimension"]),
            "after_power": np.asarray(after_select["after_power"]).tolist(),
        },
        "recall_after_fast_wipe": recall,
        "metrics": {
            "matched_route": matched_route,
            "phase_quadrature_route": quarter_route,
            "antiphase_route": anti_route,
            "frequency_mismatch_route": freq_route,
            "spatial_separation_route": sep_route,
            "matched_over_frequency_abs": float(abs(matched_route) / (abs(freq_route) + 1e-12)),
            "matched_over_spatial_abs": float(abs(matched_route) / (abs(sep_route) + 1e-12)),
            "matched_recall_B_peak": float(recall["matched_phase_0"]["peak_B_mode_power"]),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run SELECT-CARRY-BIND-WRITE-ASK-SELECT")
    parser.add_argument("--space", type=int, default=256)
    parser.add_argument("--cycles", type=int, default=28)
    parser.add_argument("--recall-steps", type=int, default=190)
    parser.add_argument("--out", type=Path, default=Path("results/machine.json"))
    args = parser.parse_args()
    receipt = run_machine(
        n_space=args.space, cycles=args.cycles, recall_steps=args.recall_steps
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
