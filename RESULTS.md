# Results

Default result: **Navier–Stokes collision backreaction supplies WRITE**.

The values below are from the deterministic 24×24 fluid backend used by CI. The modal smoke receipt uses `n_space=128` and 100 recall steps; the same physical writer is the CLI default.

See [`results/physical_write.json`](results/physical_write.json).

## 1. SELECT before learning

A seeded broadband modal state begins with participation ratio

```text
3.010822
```

and contracts under autonomous dynamics to

```text
1.897843
```

after 800 steps. This is ordinary dissipative mode selection.

## 2. Physical BIND / WRITE

The default WRITE backend advances four exact-parity 2-D incompressible Navier–Stokes worlds and measures

```math
DeltaOmega_AB = P_slow[omega_AB - omega_A - omega_B + omega_0].
```

A matched phase-0 collision is used once to define the positive orientation and units of the A->B operator port. Every control is projected onto that same fixed physical field.

| condition | physical-port projection | installed route | slow collision norm |
| --- | ---: | ---: | ---: |
| matched phase 0 | `+1.000000` | `+0.180000` | `1.75699e-2` |
| phase pi/2 | `+0.038213` | `+0.006878` | `2.42715e-3` |
| phase pi | `-1.004178` | `-0.180000` | `1.77728e-2` |
| frequency mismatch | `-0.003462` | `-0.000623` | `1.55921e-4` |
| spatial separation | `+0.014735` | `+0.002652` | `5.40720e-4` |

Raw slow-field selectivity:

```text
matched / frequency mismatch   112.68x
matched / spatial separation    32.49x
```

After 700 forcing-free steps, the matched collision residue has

```text
||fast|| / ||slow|| = 0.089514
```

so the retained signal used for WRITE is not dominated by the original high-frequency carrier activity.

The phase result is now a property of the fluid residual rather than an explicit `cos(Delta phi)` plasticity term: antiphase reverses the matched physical field projection, while quadrature leaves only a small residual on that port.

## 3. WRITE changes SELECT

Before installing the physical route:

```text
spectral abscissa  -0.140000
lifetime            7.142857
```

After the matched fluid write:

```text
spectral abscissa  -0.0675171
lifetime           14.811057
```

The same seeded broadband challenge contracts to effective dimension

```text
before physical write   1.897843
after physical write    1.396666
```

Thus the physically generated write changes the hierarchy of persistence used by later SELECT.

## 4. Fast wipe then recall

All fast **modal** amplitudes and coherence traces are erased before recall. The fluid-derived slow route remains in the operator interface.

At 100 recall steps:

| condition | peak B-mode power |
| --- | ---: |
| matched physical write | `1.97262e-2` |
| spatial-separation write | `4.23707e-6` |
| frequency-mismatch write | `2.33934e-7` |
| blank | `0` |

So the functional consequence survives the transient modal-state wipe.

## 5. ASK

With the same two-question budget:

```text
blank     asks B, then C, no decision      cost 2
matched   asks B, decides B                cost 1
```

The surrounding observer was not redesigned when WRITE changed substrate.

## 6. What is calibrated vs what is measured

The matched phase-0 field defines the finite-dimensional port basis. Consequently its own projection is `1` by definition and its route scale is a chosen unit conversion (`0.18`).

What is **not** defined by that calibration is the behavior of the controls. Frequency mismatch, spatial separation, quadrature and antiphase are run through the same fluid solver and the same fixed projection. Their suppression/sign is therefore an empirical property of this numerical physical substrate.

The stronger future version would eliminate even the fixed port projection by letting the distributed slow fluid field directly route the fast wave state.

## 7. CI status

The PR introducing the physical backend runs **7 tests successfully** on Python 3.10 and 3.12, then runs the full physical-write smoke receipt. The Python 3.12 job reports `7 passed in 9.61s`; the end-to-end physical machine also completed successfully.

## Claim boundary

This is now more than the previous engineered coherence rule, but it remains a hybrid machine.

Navier–Stokes supplies the collision-specific distributed slow write. The mapping from that distributed field into the finite modal A->B port is still an engineered, once-calibrated transducer. The system does not yet discover useful ports or semantic goals autonomously.
