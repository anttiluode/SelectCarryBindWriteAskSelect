import numpy as np

from scbwas.core import default_modes
from scbwas.experiment import make_machine, recall_a
from scbwas.fluid_backreaction import FluidBackreactionWriter, FluidConfig


def test_nav_stokes_collision_replaces_explicit_write_arrow():
    modes = default_modes()
    a = next(m for m in modes if m.name == "A")
    b = next(m for m in modes if m.name == "B")
    writer = FluidBackreactionWriter(
        FluidConfig(n=24, train_steps=210, washout_steps=700)
    )
    r = writer.sweep(a, b)

    matched = r["matched_phase_0"]
    quarter = r["phase_pi_over_2"]
    anti = r["phase_pi"]
    freq = r["frequency_mismatch"]
    sep = r["spatial_separation"]

    # The matched reference defines only orientation/units. Selectivity must
    # survive when every other condition is projected onto that same port.
    assert np.isclose(matched.projection, 1.0)
    assert abs(quarter.projection) < 0.10
    assert anti.projection < -0.80
    assert abs(freq.projection) < 0.05
    assert abs(sep.projection) < 0.05

    assert matched.slow_norm > 5.0 * freq.slow_norm
    assert matched.slow_norm > 5.0 * sep.slow_norm
    assert matched.fast_over_slow < 0.15

    # Install only the physical readout of the residual. The rest of the
    # organism is unchanged, and recall follows after a complete fast wipe.
    machine = make_machine("matched", 128)
    writer.install_route(machine, "A", "B", matched.route_value, bidirectional=True)
    theta = machine.theta.copy()
    machine.reset_fast()
    assert np.allclose(machine.theta, theta)
    recall = recall_a(machine, steps=190)
    assert recall["peak_B_mode_power"] > 0.02
    assert recall["ask"]["decision"] == "B"
