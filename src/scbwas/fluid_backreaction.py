from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np

from .core import Mode, ModalFieldComputer

Array = np.ndarray


@dataclass(frozen=True)
class FluidConfig:
    """Numerical and adapter parameters for the physical write backend.

    The writer uses an actual 2-D incompressible vorticity equation. Four
    counterfactual worlds are advanced with exact step parity so the stored
    field is the collision-specific inclusion/exclusion term

        P_slow[omega_AB - omega_A - omega_B + omega_0].

    ``theta_scale`` is only a unit conversion from the distributed physical
    write to the finite modal operator used by the rest of the organism.
    """

    n: int = 24
    length: float = 2.0 * np.pi
    dt: float = 0.015
    viscosity: float = 0.04
    k_split: float = 3.0
    carrier_k: float = 6.0
    packet_sigma: float = 0.55
    packet_amplitude: float = 8.0
    train_steps: int = 210
    washout_steps: int = 700
    theta_scale: float = 0.18


@dataclass
class CollisionField:
    slow: Array
    fast: Array
    slow_norm: float
    fast_norm: float
    fast_over_slow: float


@dataclass(frozen=True)
class PhysicalWriteReceipt:
    condition: str
    projection: float
    route_value: float
    slow_norm: float
    fast_over_slow: float
    target_phase: float
    target_omega: float
    target_q: float


class NavierStokes2D:
    r"""Small pseudo-spectral 2-D incompressible Navier--Stokes solver.

    Vorticity form:

        partial_t omega + u dot grad omega = nu Laplacian omega + f
        u = (partial_y psi, -partial_x psi),  -Laplacian psi = omega

    The nonlinear term is evaluated pseudo-spectrally with 2/3 de-aliasing.
    Diffusion is integrated exactly over one step and the nonlinear/forcing
    term uses a two-stage ETD-RK update.
    """

    def __init__(self, config: FluidConfig) -> None:
        self.config = config
        self.n = int(config.n)
        self.length = float(config.length)
        self.dt = float(config.dt)
        self.nu = float(config.viscosity)

        k = np.fft.fftfreq(self.n, d=self.length / self.n) * 2.0 * np.pi
        self.kx, self.ky = np.meshgrid(k, k, indexing="ij")
        self.k2 = self.kx * self.kx + self.ky * self.ky
        self.k2_inv = np.zeros_like(self.k2)
        self.k2_inv[self.k2 > 0.0] = 1.0 / self.k2[self.k2 > 0.0]

        kmax = float(np.max(np.abs(k))) * (2.0 / 3.0)
        self.dealias = (np.abs(self.kx) <= kmax) & (np.abs(self.ky) <= kmax)
        self.slow_mask = np.sqrt(self.k2) <= float(config.k_split)

        axis = np.linspace(0.0, self.length, self.n, endpoint=False)
        self.x, self.y = np.meshgrid(axis, axis, indexing="ij")
        self.omega = np.zeros((self.n, self.n), dtype=np.float64)

        lop = -self.nu * self.k2
        self._E = np.exp(lop * self.dt)
        self._phi1 = np.ones_like(lop)
        mask = np.abs(lop * self.dt) > 1e-10
        self._phi1[mask] = np.expm1(lop[mask] * self.dt) / (lop[mask] * self.dt)

    def _nonlinear_hat(self, omega_hat: Array) -> Array:
        psi_hat = omega_hat * self.k2_inv
        u = np.fft.ifft2(1j * self.ky * psi_hat).real
        v = np.fft.ifft2(-1j * self.kx * psi_hat).real
        omega_x = np.fft.ifft2(1j * self.kx * omega_hat).real
        omega_y = np.fft.ifft2(1j * self.ky * omega_hat).real
        return -np.fft.fft2(u * omega_x + v * omega_y) * self.dealias

    def step(self, forcing: Array | None = None) -> None:
        w_hat = np.fft.fft2(self.omega)
        f_hat = 0.0 if forcing is None else np.fft.fft2(forcing) * self.dealias

        n1 = self._nonlinear_hat(w_hat) + f_hat
        a_hat = self._E * w_hat + self.dt * self._phi1 * n1
        n2 = self._nonlinear_hat(a_hat) + f_hat
        w_hat = a_hat + self.dt * self._phi1 * (n2 - n1)
        self.omega = np.fft.ifft2(w_hat).real

    def low_pass(self, field: Array | None = None) -> Array:
        x = self.omega if field is None else np.asarray(field, dtype=float)
        return np.fft.ifft2(np.fft.fft2(x) * self.slow_mask).real


class FluidBackreactionWriter:
    """Adapter from carrier collisions to the organism's slow operator.

    No ``Re(z_j z_i*) -> theta`` write is applied here. Instead, the carriers
    are injected as oscillatory vorticity forcing into four exact-parity
    Navier--Stokes worlds. Their collision-specific residual is measured only
    after a forcing-free washout.

    A one-time matched phase-0 run defines the positive orientation and units
    of the A->B operator port. Every control is projected onto that *same*
    physical field template. This calibration cannot manufacture frequency,
    space or phase selectivity; those must be present in the fluid residual.
    """

    def __init__(self, config: FluidConfig | None = None) -> None:
        self.config = config or FluidConfig()

    def _periodic_delta(self, x: Array, center: float) -> Array:
        d = x - center
        return (d + 0.5 * self.config.length) % self.config.length - 0.5 * self.config.length

    def _packet(self, sim: NavierStokes2D, mode: Mode, time: float) -> Array:
        # q remains the spatial address. It controls both packet center and the
        # orientation of its carrier, so different addressed channels generate
        # genuinely different velocity/vorticity cross terms.
        x0 = 0.5 * self.config.length
        y0 = float(mode.q) % self.config.length
        dx = self._periodic_delta(sim.x, x0)
        dy = self._periodic_delta(sim.y, y0)
        sigma = float(self.config.packet_sigma)
        env = np.exp(-(dx * dx + dy * dy) / (2.0 * sigma * sigma))

        angle = float(mode.q) % (2.0 * np.pi)
        k = float(self.config.carrier_k)
        spatial_phase = k * (np.cos(angle) * dx + np.sin(angle) * dy)
        temporal = np.cos(float(mode.omega) * time + float(mode.phase))
        return float(self.config.packet_amplitude) * temporal * env * np.cos(spatial_phase)

    def collision_field(self, source: Mode, target: Mode) -> CollisionField:
        worlds = {name: NavierStokes2D(self.config) for name in ("W0", "WA", "WB", "WAB")}

        for step in range(int(self.config.train_steps)):
            t = step * self.config.dt
            a = self._packet(worlds["W0"], source, t)
            b = self._packet(worlds["W0"], target, t)
            worlds["W0"].step()
            worlds["WA"].step(a)
            worlds["WB"].step(b)
            worlds["WAB"].step(a + b)

        # Do not call a low-k projection "memory" while the high-k collision
        # residue is still large. Let the physical field relax with no forcing.
        for _ in range(int(self.config.washout_steps)):
            for world in worlds.values():
                world.step()

        total = (
            worlds["WAB"].omega
            - worlds["WA"].omega
            - worlds["WB"].omega
            + worlds["W0"].omega
        )
        slow = worlds["W0"].low_pass(total)
        fast = total - slow
        slow_norm = float(np.linalg.norm(slow))
        fast_norm = float(np.linalg.norm(fast))
        return CollisionField(
            slow=slow,
            fast=fast,
            slow_norm=slow_norm,
            fast_norm=fast_norm,
            fast_over_slow=float(fast_norm / (slow_norm + 1e-15)),
        )

    @staticmethod
    def projection(reference: Array, field: Array) -> float:
        denom = float(np.vdot(reference, reference).real)
        if denom <= 1e-20:
            raise ValueError("matched physical reference is too small to calibrate")
        return float(np.vdot(reference, field).real / denom)

    def sweep(self, source: Mode, target: Mode) -> dict[str, PhysicalWriteReceipt]:
        matched = self.collision_field(source, replace(target, phase=0.0))
        reference = matched.slow

        variants = {
            "matched_phase_0": replace(target, phase=0.0),
            "phase_pi_over_2": replace(target, phase=np.pi / 2.0),
            "phase_pi": replace(target, phase=np.pi),
            "frequency_mismatch": replace(target, omega=float(target.omega) + 8.0, phase=0.0),
            "spatial_separation": replace(target, q=3.55, phase=0.0),
        }

        fields: dict[str, CollisionField] = {"matched_phase_0": matched}
        for name, mode in variants.items():
            if name != "matched_phase_0":
                fields[name] = self.collision_field(source, mode)

        out: dict[str, PhysicalWriteReceipt] = {}
        for name, mode in variants.items():
            field = fields[name]
            coeff = self.projection(reference, field.slow)
            route = float(np.clip(self.config.theta_scale * coeff, -self.config.theta_scale, self.config.theta_scale))
            out[name] = PhysicalWriteReceipt(
                condition=name,
                projection=coeff,
                route_value=route,
                slow_norm=field.slow_norm,
                fast_over_slow=field.fast_over_slow,
                target_phase=float(mode.phase),
                target_omega=float(mode.omega),
                target_q=float(mode.q),
            )
        return out

    def install_route(
        self,
        machine: ModalFieldComputer,
        source_name: str,
        target_name: str,
        route_value: float,
        *,
        bidirectional: bool = True,
    ) -> None:
        """Read the distributed fluid write into the existing modal operator port.

        This does not perform another learning rule. ``route_value`` has already
        been determined by the physical collision residual. This method is the
        finite-dimensional transducer between the fluid field and the existing
        organism, analogous to choosing sensor units and orientation.
        """
        i = machine.index(source_name)
        j = machine.index(target_name)
        machine.theta[j, i] = float(route_value)
        if bidirectional:
            machine.theta[i, j] = float(route_value)
        np.clip(machine.theta, -machine.theta_clip, machine.theta_clip, out=machine.theta)
        np.fill_diagonal(machine.theta, 0.0)
