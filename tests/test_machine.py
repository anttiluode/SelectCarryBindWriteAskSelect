import numpy as np

from scbwas.core import effective_dimension
from scbwas.experiment import make_machine, recall_a, train_association


def test_effective_dimension_contracts_under_sigh_selection():
    m = make_machine("matched", 128)
    r = m.select_from_broadband(steps=800, seed=3)
    assert r["after_effective_dimension"] < r["before_effective_dimension"]


def test_phase_controls_signed_write():
    pos = make_machine("matched", 128)
    zero = make_machine("matched", 128)
    neg = make_machine("matched", 128)
    p = train_association(pos, phase=0.0, cycles=8)
    q = train_association(zero, phase=np.pi / 2, cycles=8)
    n = train_association(neg, phase=np.pi, cycles=8)
    assert p["final_route_A_to_B"] > 0.04
    assert abs(q["final_route_A_to_B"]) < 0.01
    assert n["final_route_A_to_B"] < -0.04


def test_frequency_and_space_address_binding():
    matched = make_machine("matched", 128)
    freq = make_machine("frequency_mismatch", 128)
    sep = make_machine("spatial_separation", 128)
    wm = abs(train_association(matched, cycles=8)["final_route_A_to_B"])
    wf = abs(train_association(freq, cycles=8)["final_route_A_to_B"])
    ws = abs(train_association(sep, cycles=8)["final_route_A_to_B"])
    assert wm > 8.0 * wf
    assert wm > 4.0 * ws


def test_write_changes_the_persistence_spectrum():
    m = make_machine("matched", 128)
    before = m.spectrum()["spectral_abscissa"]
    train_association(m, cycles=12)
    after = m.spectrum()["spectral_abscissa"]
    assert after > before
    assert after < 0.0


def test_fast_wipe_leaves_slow_structure_and_recall_route():
    m = make_machine("matched", 128)
    train_association(m, cycles=12)
    theta = m.theta.copy()
    m.reset_fast()
    assert np.allclose(m.a, 0.0)
    assert np.allclose(m.theta, theta)
    r = recall_a(m, steps=120)
    assert r["peak_B_mode_power"] > 1e-4


def test_bounded_ask_uses_fewer_questions_after_matching_write():
    blank = make_machine("matched", 128)
    learned = make_machine("matched", 128)
    train_association(learned, cycles=28)
    rb = recall_a(blank, steps=190)
    rl = recall_a(learned, steps=190)
    assert rb["ask"]["decision"] is None
    assert rb["ask"]["cost"] == 2
    assert rl["ask"]["decision"] == "B"
    assert rl["ask"]["cost"] == 1
