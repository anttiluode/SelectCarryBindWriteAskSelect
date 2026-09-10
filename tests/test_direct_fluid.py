from scbwas.direct_fluid import DirectFluidOperator


def test_direct_fluid_memory_routes_later_cue_without_theta():
    receipt = DirectFluidOperator(recall_steps=250).run()
    m = receipt["metrics"]
    r = receipt["recall"]

    assert receipt["status"] == "direct_fluid_operator"
    assert receipt["config"]["memory_gain"] == 1.0

    # The matched write is a direct physical effect at the target detector.
    assert m["matched_target_abs"] > 4.0e-4
    assert m["matched_target_over_distractor_abs"] > 10.0

    # Addressing survives when the distributed field itself is the operator.
    assert m["matched_over_quadrature_abs"] > 10.0
    assert m["matched_over_frequency_abs"] > 100.0
    assert m["matched_over_spatial_abs"] > 20.0

    # Relative phase reverses the later physical cue response.
    assert m["antiphase_reverses_target_sign"]
    assert abs(m["antiphase_target_signed"]) > 0.7 * m["matched_target_abs"]

    # The stored field is predominantly slow after forcing-free washout.
    assert m["matched_fast_over_slow_after_washout"] < 0.12

    # A bounded local question can distinguish the learned field from controls.
    assert r["matched_phase_0"]["decision"] == "B"
    assert r["matched_phase_0"]["ask_cost"] == 1
    assert r["frequency_mismatch"]["decision"] is None
    assert r["spatial_separation"]["decision"] is None
    assert r["blank"]["decision"] is None
