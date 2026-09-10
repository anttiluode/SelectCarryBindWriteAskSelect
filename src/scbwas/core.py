from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Iterable, Sequence

import numpy as np

Array = np.ndarray


def periodic_delta(x: Array, center: float, length: float) -> Array:
    d = x - center
    return (d + 0.5 * length) % length - 0.5 * length


def effective_dimension(power: Array) -> float:
    """Participation ratio of non-negative modal powers."""
    p = np.asarray(power, dtype=float)
    s = float(p.sum())
    if s <= 0.0:
        return 0.0
    p = p / s
    return float(1.0 / np.sum(p * p))


@dataclass(frozen=True)
class Mode:
    """One addressed classical wave mode.

    q      spatial center / WHERE
    k      spatial carrier / WHICH direction-scale
    omega  temporal carrier / WHICH temporal channel
    phase  injection phase / signed binding coordinate
    decay  autonomous forgetting rate
    sigma  spatial envelope width
    """

    name: str
    q: float
    k: int
    omega: float
    decay: float
    sigma: float = 0.42
    phase: float = 0.0


@dataclass(frozen=True)
class Probe:
    name: str
    q: float
    sigma: float = 0.36


@dataclass(frozen=True)
class AskResult:
    chosen: tuple[str, ...]
    values: tuple[float, ...]
    decision: str | None
    cost: int


class ModalFieldComputer:
    r"""SELECT -> CARRY -> BIND -> WRITE -> ASK -> SELECT.

    This is an engineered classical wave machine, not a quantum computer and
    not a claim that these dynamics arise automatically from Navier--Stokes.

    Fast state is a vector of complex modal amplitudes ``a``. Each mode has a
    localized spatial carrier ``phi_i(x)``. A slowly varying structural matrix
    ``theta`` changes the fast generator, so experience changes later routing.

        da/dt = [diag(-d_i + i omega_i) + coupling * theta] a + input

    The write is generated from a low-pass coherence accumulator. For a pair
    i,j, the instantaneous product a_j conj(a_i) rotates at Delta omega; the
    exponentially slow accumulator therefore keeps matched carriers and
    averages mismatched carriers toward zero. Spatial envelope overlap is a
    second gate. The real part of the accumulated product gives signed write.

        r_ji <- beta r_ji + (1-beta) a_j conj(a_i)
        theta_ji <- leak theta_ji + eta overlap_ji Re(r_ji)

    Relative phase therefore controls the sign: 0 -> positive, pi/2 -> near
    zero, pi -> negative when carriers are otherwise matched.
    """

    def __init__(
        self,
        modes: Sequence[Mode],
        *,
        n_space: int = 256,
        length: float = 2.0 * np.pi,
        dt: float = 0.01,
        coupling: float = 1.8,
        coherence_tau: float = 0.8,
        structure_tau: float = 80.0,
        write_rate: float = 0.55,
        theta_clip: float = 0.42,
    ) -> None:
        if len(modes) < 2:
            raise ValueError("need at least two modes")
        if n_space < 64:
            raise ValueError("n_space must be >= 64")
        self.modes = list(modes)
        self.length = float(length)
        self.dt = float(dt)
        self.coupling = float(coupling)
        self.coherence_tau = float(coherence_tau)
        self.structure_tau = float(structure_tau)
        self.write_rate = float(write_rate)
        self.theta_clip = float(theta_clip)

        self.x = np.linspace(0.0, self.length, int(n_space), endpoint=False)
        self.dx = self.length / int(n_space)
        self.phi = self._build_modes()
        self.overlap = self._build_overlap()
        m = len(self.modes)
        self.a = np.zeros(m, dtype=np.complex128)
        self.coherence = np.zeros((m, m), dtype=np.complex128)
        self.theta = np.zeros((m, m), dtype=np.float64)
        self.time = 0.0

    @property
    def size(self) -> int:
        return len(self.modes)

    def copy(self, *, keep_structure: bool = True) -> "ModalFieldComputer":
        out = ModalFieldComputer(
            self.modes,
            n_space=len(self.x),
            length=self.length,
            dt=self.dt,
            coupling=self.coupling,
            coherence_tau=self.coherence_tau,
            structure_tau=self.structure_tau,
            write_rate=self.write_rate,
            theta_clip=self.theta_clip,
        )
        if keep_structure:
            out.theta = self.theta.copy()
        return out

    def _build_modes(self) -> Array:
        rows = []
        for mode in self.modes:
            dq = periodic_delta(self.x, mode.q, self.length)
            envelope = np.exp(-0.5 * (dq / mode.sigma) ** 2)
            carrier = np.exp(1j * mode.k * self.x)
            phi = envelope * carrier
            norm = np.sqrt(np.sum(np.abs(phi) ** 2) * self.dx)
            rows.append(phi / max(norm, 1e-15))
        return np.stack(rows, axis=0)

    def _build_overlap(self) -> Array:
        env = np.abs(self.phi)
        ov = np.empty((self.size, self.size), dtype=float)
        for j in range(self.size):
            for i in range(self.size):
                ov[j, i] = float(np.sum(env[j] * env[i]) * self.dx)
        np.fill_diagonal(ov, 0.0)
        return ov

    def generator(self) -> Array:
        diagonal = np.diag(
            np.array([-m.decay + 1j * m.omega for m in self.modes], dtype=complex)
        )
        return diagonal + self.coupling * self.theta.astype(complex)

    def modal_field(self) -> Array:
        return np.einsum("i,ix->x", self.a, self.phi)

    def modal_power(self) -> Array:
        return np.abs(self.a) ** 2

    def inject(self, index: int, amplitude: complex = 1.0) -> None:
        self.a[int(index)] += complex(amplitude)

    def inject_named(self, name: str, amplitude: complex = 1.0) -> None:
        self.inject(self.index(name), amplitude)

    def index(self, name: str) -> int:
        for i, mode in enumerate(self.modes):
            if mode.name == name:
                return i
        raise KeyError(name)

    def reset_fast(self, *, reset_coherence: bool = True) -> None:
        self.a.fill(0.0)
        if reset_coherence:
            self.coherence.fill(0.0)

    def _update_coherence(self, signal: Array | None = None) -> None:
        beta = float(np.exp(-self.dt / max(self.coherence_tau, 1e-12)))
        z = self.a if signal is None else np.asarray(signal, dtype=complex)
        inst = np.outer(z, np.conj(z))
        self.coherence = beta * self.coherence + (1.0 - beta) * inst
        np.fill_diagonal(self.coherence, 0.0)

    def write_from_pair(
        self,
        source: int,
        target: int,
        *,
        sign: float = 1.0,
        bidirectional: bool = False,
    ) -> float:
        """Apply one addressed structural write from accumulated coherence."""
        i = int(source)
        j = int(target)
        drive = (
            float(sign)
            * self.overlap[j, i]
            * float(np.real(self.coherence[j, i]))
        )
        self.theta[j, i] += self.dt * self.write_rate * drive
        if bidirectional:
            self.theta[i, j] += self.dt * self.write_rate * drive
        np.clip(self.theta, -self.theta_clip, self.theta_clip, out=self.theta)
        np.fill_diagonal(self.theta, 0.0)
        return drive

    def step(
        self,
        *,
        write_pairs: Iterable[tuple[int, int, float]] = (),
        drive: Array | None = None,
        input_gain: float = 0.35,
    ) -> None:
        """Advance fast state once, update coherence, then optional slow writes.

        ``drive`` contains complex carrier amplitudes in each mode's rotating
        channel. A lab-frame phasor ``drive_i exp(i omega_i t)`` is used both
        as a physical input forcing and, when present, as the signal seen by
        the slow coincidence detector. This makes frequency mismatch average
        naturally instead of depending on episode boundaries.
        """
        leak = float(np.exp(-self.dt / max(self.structure_tau, 1e-12)))
        self.theta *= leak
        g = self.generator()
        forcing = np.zeros(self.size, dtype=complex)
        bind_signal = None
        if drive is not None:
            d = np.asarray(drive, dtype=complex)
            if d.shape != (self.size,):
                raise ValueError("drive must have one complex amplitude per mode")
            phases = np.exp(1j * np.array([m.omega for m in self.modes]) * self.time)
            bind_signal = d * phases
            forcing = float(input_gain) * bind_signal
        k1 = g @ self.a + forcing
        mid = self.a + 0.5 * self.dt * k1
        k2 = g @ mid + forcing
        self.a = self.a + self.dt * k2
        self.time += self.dt
        self._update_coherence(bind_signal)
        for source, target, sign in write_pairs:
            self.write_from_pair(source, target, sign=sign)

    def run(
        self,
        steps: int,
        *,
        write_pairs: Iterable[tuple[int, int, float]] = (),
        drive: Array | None = None,
        input_gain: float = 0.35,
    ) -> None:
        pairs = tuple(write_pairs)
        for _ in range(int(steps)):
            self.step(write_pairs=pairs, drive=drive, input_gain=input_gain)

    def probe(self, probe: Probe) -> float:
        dq = periodic_delta(self.x, probe.q, self.length)
        mask = np.exp(-0.5 * (dq / probe.sigma) ** 2)
        mask /= max(float(mask.sum()), 1e-15)
        field = self.modal_field()
        return float(np.sum(mask * np.abs(field) ** 2))

    def ask(
        self,
        probes: Sequence[Probe],
        *,
        threshold: float = 0.025,
        max_questions: int = 2,
    ) -> AskResult:
        """Bounded active readout: query local probes until one is decisive."""
        if not probes:
            return AskResult((), (), None, 0)
        priorities = []
        pwr = self.modal_power()
        for probe in probes:
            score = 0.0
            for idx, mode in enumerate(self.modes):
                dq = float(periodic_delta(np.array([mode.q]), probe.q, self.length)[0])
                score += pwr[idx] * np.exp(-0.5 * (dq / probe.sigma) ** 2)
            priorities.append(float(score))
        order = np.argsort(priorities)[::-1]
        chosen: list[str] = []
        values: list[float] = []
        decision: str | None = None
        for idx in order[: max(1, int(max_questions))]:
            probe = probes[int(idx)]
            value = self.probe(probe)
            chosen.append(probe.name)
            values.append(value)
            if value >= threshold:
                decision = probe.name
                break
        return AskResult(tuple(chosen), tuple(values), decision, len(chosen))

    def spectrum(self) -> dict[str, Array | float]:
        eigvals = np.linalg.eigvals(self.generator())
        order = np.argsort(eigvals.real)[::-1]
        eigvals = eigvals[order]
        lifetimes = np.array(
            [np.inf if z.real >= 0 else -1.0 / z.real for z in eigvals], dtype=float
        )
        return {
            "eigenvalues": eigvals,
            "lifetimes": lifetimes,
            "spectral_abscissa": float(np.max(eigvals.real)),
        }

    def select_from_broadband(self, *, steps: int = 250, seed: int = 0) -> dict:
        """Sigh-style selection receipt: broadband state pruned by the operator."""
        rng = np.random.default_rng(seed)
        old_a = self.a.copy()
        old_coh = self.coherence.copy()
        old_time = self.time
        old_theta = self.theta.copy()
        self.a = rng.normal(size=self.size) + 1j * rng.normal(size=self.size)
        before = self.modal_power()
        before_dim = effective_dimension(before)
        self.run(steps)
        after = self.modal_power()
        after_dim = effective_dimension(after)
        out = {
            "before_power": before.copy(),
            "after_power": after.copy(),
            "before_effective_dimension": before_dim,
            "after_effective_dimension": after_dim,
        }
        self.a = old_a
        self.coherence = old_coh
        self.time = old_time
        self.theta = old_theta
        return out


def default_modes() -> list[Mode]:
    return [
        Mode("A", q=1.45, k=5, omega=4.0, decay=0.22, sigma=0.52),
        Mode("B", q=2.15, k=5, omega=4.0, decay=0.28, sigma=0.52),
        Mode("C", q=4.55, k=8, omega=7.0, decay=0.14, sigma=0.52),
        Mode("D", q=5.15, k=11, omega=9.5, decay=0.42, sigma=0.46),
    ]


def with_mode(modes: Sequence[Mode], name: str, **changes) -> list[Mode]:
    return [replace(m, **changes) if m.name == name else m for m in modes]
