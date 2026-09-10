from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from .core import ModalFieldComputer, Probe, default_modes, with_mode
from .fluid_backreaction import FluidBackreactionWriter, FluidConfig, PhysicalWriteReceipt


def make_machine(kind: str, n_space: int = 256) -> ModalFieldComputer:
    """Construct the modal organism.

    ``kind`` remains for the legacy coherence writer. The physical writer keeps
    the post-training organism identical across controls and changes only the
    carrier conditions presented to the fluid during WRITE.
    """
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
    """Legacy engineered coherence writer retained as an explicit control.

    The current default machine no longer uses this rule for WRITE. It remains
    executable so the old result can be compared directly against the physical
    backreaction backend.
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
        "backend": "engineered_coherence",
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


def _receipt_dict(receipt: PhysicalWriteReceipt) -> dict:
    return {
        "backend": "navier_stokes_collision_backreaction",
        "projection_on_matched_port": float(receipt.projection),
        "final_route_A_to_B": float(receipt.route_value),
        "final_route_B_to_A": float(receipt.route_value),
        "collision_slow_norm": float(receipt.slow_norm),
        "collision_fast_over_slow_after_washout": float(receipt.fast_over_slow),
        "target_phase": float(receipt.target_phase),
        "target_omega": float(receipt.target_omega),
        "target_q": float(receipt.target_q),
    }


def run_physical_machine(
    *,
    n_space: int = 256,
    recall_steps: int = 190,
    fluid_config: FluidConfig | None = None,
) -> dict:
    """Run the assembled organism with WRITE supplied by Navier--Stokes.

    SELECT, CARRY, ASK and post-write modal dynamics are unchanged. Only the
    old explicit coherence->theta arrow is replaced. The writer advances four
    exact-parity fluid worlds, waits for forcing-free washout, extracts

        P_slow[omega_AB - omega_A - omega_B + omega_0],

    and projects that distributed physical residual onto one fixed A->B port.
    """
    modes = default_modes()
    source = next(m for m in modes if m.name == "A")
    target = next(m for m in modes if m.name == "B")
    writer = FluidBackreactionWriter(fluid_config)
    physical = writer.sweep(source, target)

    worlds = {
        "blank": make_machine("matched", n_space),
        "matched_phase_0": make_machine("matched", n_space),
        "phase_pi_over_2": make_machine("matched", n_space),
        "phase_pi": make_machine("matched", n_space),
        "frequency_mismatch": make_machine("matched", n_space),
        "spatial_separation": make_machine("matched", n_space),
    }

    before_select = worlds["matched_phase_0"].select_from_broadband(steps=800, seed=3)
    before_spectrum = eigen_receipt(worlds["matched_phase_0"])

    for name, receipt in physical.items():
        writer.install_route(worlds[name], "A", "B", receipt.route_value, bidirectional=True)

    training = {
        "blank": {
            "backend": "navier_stokes_collision_backreaction",
            "projection_on_matched_port": 0.0,
            "final_route_A_to_B": 0.0,
            "final_route_B_to_A": 0.0,
            "collision_slow_norm": 0.0,
            "collision_fast_over_slow_after_washout": 0.0,
        }
    }
    training.update({name: _receipt_dict(receipt) for name, receipt in physical.items()})

    learned = worlds["matched_phase_0"]
    after_spectrum = eigen_receipt(learned)
    after_select = learned.select_from_broadband(steps=800, seed=3)
    recall = {name: recall_a(world, steps=recall_steps) for name, world in worlds.items()}

    matched = physical["matched_phase_0"]
    quarter = physical["phase_pi_over_2"]
    anti = physical["phase_pi"]
    freq = physical["frequency_mismatch"]
    sep = physical["spatial_separation"]

    cfg = writer.config
    return {
        "status": "assembled_machine_physical_write",
        "claim_boundary": (
            "The old explicit Re(z_j z_i*) -> theta plasticity arrow has been replaced "
            "by a collision-specific low-frequency residual generated by a numerical "
            "2-D incompressible Navier-Stokes equation. One matched phase-0 fluid run "
            "calibrates the orientation and units of the A->B operator port; all controls "
            "use that identical fixed projection. This is still a hybrid engineered "
            "machine, not evidence of quantum advantage or a claim that Navier-Stokes "
            "alone supplies semantics, reward or useful ports."
        ),
        "config": {
            "n_space": n_space,
            "recall_steps": recall_steps,
            "write_backend": "navier_stokes_collision_backreaction",
            "fluid": {
                "grid": cfg.n,
                "dt": cfg.dt,
                "viscosity": cfg.viscosity,
                "k_split": cfg.k_split,
                "carrier_k": cfg.carrier_k,
                "packet_sigma": cfg.packet_sigma,
                "packet_amplitude": cfg.packet_amplitude,
                "train_steps": cfg.train_steps,
                "washout_steps": cfg.washout_steps,
                "theta_scale": cfg.theta_scale,
            },
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
            "matched_route": float(matched.route_value),
            "phase_quadrature_route": float(quarter.route_value),
            "antiphase_route": float(anti.route_value),
            "frequency_mismatch_route": float(freq.route_value),
            "spatial_separation_route": float(sep.route_value),
            "phase_quadrature_projection": float(quarter.projection),
            "antiphase_projection": float(anti.projection),
            "frequency_mismatch_projection": float(freq.projection),
            "spatial_separation_projection": float(sep.projection),
            "matched_slow_norm": float(matched.slow_norm),
            "matched_fast_over_slow_after_washout": float(matched.fast_over_slow),
            "matched_over_frequency_slow_norm": float(matched.slow_norm / (freq.slow_norm + 1e-15)),
            "matched_over_spatial_slow_norm": float(matched.slow_norm / (sep.slow_norm + 1e-15)),
            "matched_recall_B_peak": float(recall["matched_phase_0"]["peak_B_mode_power"]),
            "frequency_recall_B_peak": float(recall["frequency_mismatch"]["peak_B_mode_power"]),
            "spatial_recall_B_peak": float(recall["spatial_separation"]["peak_B_mode_power"]),
        },
    }


def run_coherence_machine(
    *,
    n_space: int = 256,
    cycles: int = 28,
    recall_steps: int = 190,
) -> dict:
    """Previous engineered-write receipt, retained for direct comparison."""
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
            "backend": "engineered_coherence",
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
        "status": "assembled_machine_engineered_write_reference",
        "claim_boundary": (
            "Legacy reference using the explicit low-pass coherence plasticity rule. "
            "The default CLI now uses the Navier-Stokes backreaction backend."
        ),
        "config": {
            "n_space": n_space,
            "training_cycles": cycles,
            "recall_steps": recall_steps,
            "write_backend": "engineered_coherence",
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


def run_machine(
    *,
    n_space: int = 256,
    cycles: int = 28,
    recall_steps: int = 190,
    writer_backend: str = "fluid",
    fluid_config: FluidConfig | None = None,
) -> dict:
    if writer_backend == "fluid":
        return run_physical_machine(
            n_space=n_space,
            recall_steps=recall_steps,
            fluid_config=fluid_config,
        )
    if writer_backend == "coherence":
        return run_coherence_machine(
            n_space=n_space,
            cycles=cycles,
            recall_steps=recall_steps,
        )
    raise ValueError(f"unknown writer backend: {writer_backend}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run SELECT-CARRY-BIND-WRITE-ASK-SELECT")
    parser.add_argument("--space", type=int, default=256)
    parser.add_argument("--cycles", type=int, default=28, help="legacy coherence backend only")
    parser.add_argument("--recall-steps", type=int, default=190)
    parser.add_argument("--writer", choices=("fluid", "coherence"), default="fluid")
    parser.add_argument("--fluid-grid", type=int, default=24)
    parser.add_argument("--fluid-train", type=int, default=210)
    parser.add_argument("--fluid-washout", type=int, default=700)
    parser.add_argument("--out", type=Path, default=Path("results/machine.json"))
    args = parser.parse_args()
    fluid = FluidConfig(
        n=args.fluid_grid,
        train_steps=args.fluid_train,
        washout_steps=args.fluid_washout,
    )
    receipt = run_machine(
        n_space=args.space,
        cycles=args.cycles,
        recall_steps=args.recall_steps,
        writer_backend=args.writer,
        fluid_config=fluid,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
