from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np

from .core import Mode, default_modes
from .fluid_backreaction import CollisionField, FluidBackreactionWriter, FluidConfig, NavierStokes2D

Array = np.ndarray


@dataclass(frozen=True)
class DirectRecallReceipt:
    condition: str
    target_signed_peak: float
    target_peak_step: int
    distractor_signed_peak: float
    distractor_peak_step: int
    target_over_distractor_abs: float
    decision: str | None
    polarity: int
    ask_cost: int


class DirectFluidOperator:
    """Use the learned slow vorticity field itself as the future operator.

    There is deliberately no ``DeltaOmega -> theta`` projection here.

    WRITE:
        carrier A + carrier B
            -> Navier--Stokes quadratic interaction
            -> P_slow[omega_AB - omega_A - omega_B + omega_0]

    RECALL:
        initialize a new fluid world with that *distributed slow field itself*,
        inject cue A, and ask whether the cue's later physical trajectory changes
        at the local B detector.

    The recall observable subtracts both the memory-only evolution and the same
    cue in a blank fluid:

        cross(t) = omega_(memory+A)(t) - omega_memory(t) - omega_A(t).

    Thus the reported route is the physical interaction between the stored field
    and the later cue, not leftover memory amplitude and not direct cue leakage.
    """

    def __init__(
        self,
        config: FluidConfig | None = None,
        *,
        recall_steps: int = 250,
        cue_amplitude: float = 3.0,
        probe_sigma: float = 0.45,
        ask_threshold: float = 1.0e-4,
        distractor_q: float = 4.55,
    ) -> None:
        self.writer = FluidBackreactionWriter(config)
        self.config = self.writer.config
        self.recall_steps = int(recall_steps)
        self.cue_amplitude = float(cue_amplitude)
        self.probe_sigma = float(probe_sigma)
        self.ask_threshold = float(ask_threshold)
        self.distractor_q = float(distractor_q)

    def _periodic_delta(self, x: Array, center: float) -> Array:
        d = x - center
        return (d + 0.5 * self.config.length) % self.config.length - 0.5 * self.config.length

    def _local_probe(self, sim: NavierStokes2D, q: float) -> Array:
        dx = self._periodic_delta(sim.x, 0.5 * self.config.length)
        dy = self._periodic_delta(sim.y, float(q))
        mask = np.exp(-(dx * dx + dy * dy) / (2.0 * self.probe_sigma * self.probe_sigma))
        norm = float(np.linalg.norm(mask))
        return mask / max(norm, 1e-15)

    def _cue_field(self, sim: NavierStokes2D, source: Mode) -> Array:
        raw = self.writer._packet(sim, replace(source, phase=0.0), 0.0)
        return raw * (self.cue_amplitude / max(self.config.packet_amplitude, 1e-15))

    @staticmethod
    def _signed_peak(values: list[float]) -> tuple[float, int]:
        arr = np.asarray(values, dtype=float)
        idx = int(np.argmax(np.abs(arr)))
        return float(arr[idx]), idx

    def recall(
        self,
        memory: CollisionField | Array,
        source: Mode,
        target: Mode,
        *,
        condition: str = "memory",
    ) -> DirectRecallReceipt:
        slow = memory.slow if isinstance(memory, CollisionField) else np.asarray(memory, dtype=float)

        cue_memory = NavierStokes2D(self.config)
        memory_only = NavierStokes2D(self.config)
        cue_blank = NavierStokes2D(self.config)

        cue_memory.omega = np.array(slow, copy=True)
        memory_only.omega = np.array(slow, copy=True)
        cue = self._cue_field(cue_memory, source)
        cue_memory.omega += cue
        cue_blank.omega += cue

        target_probe = self._local_probe(cue_memory, target.q)
        distractor_probe = self._local_probe(cue_memory, self.distractor_q)
        target_values: list[float] = []
        distractor_values: list[float] = []

        for _ in range(self.recall_steps):
            cue_memory.step()
            memory_only.step()
            cue_blank.step()
            cross = cue_memory.omega - memory_only.omega - cue_blank.omega
            target_values.append(float(np.sum(target_probe * cross)))
            distractor_values.append(float(np.sum(distractor_probe * cross)))

        target_peak, target_step = self._signed_peak(target_values)
        distractor_peak, distractor_step = self._signed_peak(distractor_values)
        target_abs = abs(target_peak)
        distractor_abs = abs(distractor_peak)
        decisive = target_abs >= self.ask_threshold
        decision = target.name if decisive else None
        polarity = 0 if not decisive else (1 if target_peak > 0.0 else -1)
        ask_cost = 1 if decisive else 2
        return DirectRecallReceipt(
            condition=condition,
            target_signed_peak=target_peak,
            target_peak_step=target_step,
            distractor_signed_peak=distractor_peak,
            distractor_peak_step=distractor_step,
            target_over_distractor_abs=float(target_abs / (distractor_abs + 1e-15)),
            decision=decision,
            polarity=polarity,
            ask_cost=ask_cost,
        )

    def build_memories(self, source: Mode, target: Mode) -> dict[str, CollisionField]:
        variants = {
            "matched_phase_0": replace(target, phase=0.0),
            "phase_pi_over_2": replace(target, phase=np.pi / 2.0),
            "phase_pi": replace(target, phase=np.pi),
            "frequency_mismatch": replace(target, omega=float(target.omega) + 8.0, phase=0.0),
            "spatial_separation": replace(target, q=3.55, phase=0.0),
        }
        return {name: self.writer.collision_field(source, mode) for name, mode in variants.items()}

    def run(self) -> dict:
        modes = default_modes()
        source = next(m for m in modes if m.name == "A")
        target = next(m for m in modes if m.name == "B")
        memories = self.build_memories(source, target)

        blank = np.zeros((self.config.n, self.config.n), dtype=float)
        recalls: dict[str, DirectRecallReceipt] = {
            "blank": self.recall(blank, source, target, condition="blank")
        }
        recalls.update(
            {name: self.recall(memory, source, target, condition=name) for name, memory in memories.items()}
        )

        matched = memories["matched_phase_0"]
        rm = recalls["matched_phase_0"]
        quarter = recalls["phase_pi_over_2"]
        anti = recalls["phase_pi"]
        freq = recalls["frequency_mismatch"]
        sep = recalls["spatial_separation"]

        return {
            "status": "direct_fluid_operator",
            "claim_boundary": (
                "The collision-specific low-frequency Navier-Stokes field is used directly "
                "as the routing medium for the later cue. There is no projection onto, or "
                "installation into, a finite Theta operator. The local detector, carrier "
                "geometry and low/fast spectral split remain engineered."
            ),
            "config": {
                "grid": self.config.n,
                "dt": self.config.dt,
                "viscosity": self.config.viscosity,
                "k_split": self.config.k_split,
                "carrier_k": self.config.carrier_k,
                "packet_sigma": self.config.packet_sigma,
                "packet_amplitude": self.config.packet_amplitude,
                "train_steps": self.config.train_steps,
                "washout_steps": self.config.washout_steps,
                "recall_steps": self.recall_steps,
                "cue_amplitude": self.cue_amplitude,
                "probe_sigma": self.probe_sigma,
                "ask_threshold": self.ask_threshold,
                "memory_gain": 1.0,
            },
            "memory": {
                name: {
                    "slow_norm": float(field.slow_norm),
                    "fast_over_slow_after_washout": float(field.fast_over_slow),
                }
                for name, field in memories.items()
            },
            "recall": {
                name: {
                    "target_signed_peak": float(r.target_signed_peak),
                    "target_peak_step": int(r.target_peak_step),
                    "distractor_signed_peak": float(r.distractor_signed_peak),
                    "distractor_peak_step": int(r.distractor_peak_step),
                    "target_over_distractor_abs": float(r.target_over_distractor_abs),
                    "decision": r.decision,
                    "polarity": int(r.polarity),
                    "ask_cost": int(r.ask_cost),
                }
                for name, r in recalls.items()
            },
            "metrics": {
                "matched_target_abs": abs(float(rm.target_signed_peak)),
                "matched_target_signed": float(rm.target_signed_peak),
                "quadrature_target_abs": abs(float(quarter.target_signed_peak)),
                "antiphase_target_signed": float(anti.target_signed_peak),
                "frequency_target_abs": abs(float(freq.target_signed_peak)),
                "spatial_target_abs": abs(float(sep.target_signed_peak)),
                "matched_over_quadrature_abs": float(abs(rm.target_signed_peak) / (abs(quarter.target_signed_peak) + 1e-15)),
                "matched_over_frequency_abs": float(abs(rm.target_signed_peak) / (abs(freq.target_signed_peak) + 1e-15)),
                "matched_over_spatial_abs": float(abs(rm.target_signed_peak) / (abs(sep.target_signed_peak) + 1e-15)),
                "matched_target_over_distractor_abs": float(rm.target_over_distractor_abs),
                "matched_fast_over_slow_after_washout": float(matched.fast_over_slow),
                "antiphase_reverses_target_sign": bool(rm.target_signed_peak * anti.target_signed_peak < 0.0),
            },
        }


def run_direct_fluid_machine(*, fluid_config: FluidConfig | None = None, recall_steps: int = 250) -> dict:
    return DirectFluidOperator(fluid_config, recall_steps=recall_steps).run()
