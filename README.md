# SelectCarryBindWriteAskSelect

**The slow fluid field is now the operator.**

This repo is the assembled line from `SighImageSuper`, `InformationFlow`, `-mp-ri`, the active-observer work, and the old phase-space experiments:

```text
SELECT -> CARRY -> BIND -> WRITE -> ASK -> SELECT -> ...
```

The previous revision had one conspicuous remaining handoff:

```text
Navier-Stokes collision field DeltaOmega(x,y)
                  -> fixed calibrated projection
                  -> finite modal coupling Theta_AB
```

That handoff is no longer used by the **default machine**.

The current path is literally

```text
carrier A + carrier B
        |
        v
2-D incompressible Navier-Stokes
        |
        v
collision-specific slow vorticity field
        |
        |   stored as the medium itself
        v
later cue A is injected into that field
        |
        v
its physical trajectory changes
        |
        v
bounded local detector B
```

There is no `DeltaOmega -> Theta` projection in this path and no amplification of the learned field (`memory_gain = 1.0`).

It is **not a quantum computer**, and it does not show that bare Navier-Stokes discovers semantics or learning goals. It is a numerical proof-of-mechanism that a carrier-addressed nonlinear fluid interaction can leave a slow distributed field which later participates directly in routing another carrier.

## WRITE: the physical memory

Four equal-time worlds are advanced:

```text
W0   no carrier forcing
WA   A only
WB   B only
WAB  A + B
```

with

```math
\partial_t\omega + u\cdot\nabla\omega = \nu\Delta\omega + f,
\qquad \nabla\cdot u=0.
```

After forcing stops, all worlds undergo a long forcing-free washout. The stored field is

```math
\boxed{
\Delta\Omega_{AB}
=P_{\rm slow}[\omega_{AB}-\omega_A-\omega_B+\omega_0].
}
```

That removes the unilateral A and B effects and retains the collision-specific low-frequency part.

For the default 24x24 construction, the matched field has slow norm about `1.757e-2`; after 700 washout steps its high-frequency remainder is only about `8.95%` of the slow collision field.

Carrier addressing survives physically:

```text
matched phase 0      slow norm  1.757e-2
phase pi/2                      2.427e-3
phase pi                        1.777e-2
frequency mismatch              1.559e-4
spatial separation              5.407e-4
```

The old calibrated-port experiment remains in `scbwas-modal-reference`, but it is now a reference rather than the default organism.

## RECALL: no transducer

To ask whether the stored field actually changes a later cue, three new fluid worlds are evolved:

```text
memory + cue A
memory only
cue A in blank fluid
```

At every time step we form

```math
\boxed{
\chi_A(t)
=\omega_{\Delta\Omega+A}(t)
-\omega_{\Delta\Omega}(t)
-\omega_A(t).
}
```

So the recall signal cannot be explained by static memory amplitude or direct cue leakage. It is the nonlinear physical interaction between the stored field and the later cue.

A bounded Gaussian detector at B reads only a local signed projection of `chi_A`.

With the raw stored fields (`memory_gain = 1`) the deterministic direct recall gives approximately:

| stored field | signed peak at B |
| --- | ---: |
| matched phase 0 | **`-6.315e-4`** |
| phase pi/2 | `-2.595e-5` |
| phase pi | **`+5.901e-4`** |
| frequency mismatch | `+6.34e-7` |
| spatial separation | `-1.24e-5` |
| blank | `0` |

Thus the matched memory changes the later B response about **24x** more than quadrature, **~1000x** more than frequency mismatch, and **~51x** more than spatial separation. Antiphase reverses the sign of the later physical response.

The matched B response is also about **46x** its response at a distant distractor detector.

Nothing in those ratios comes from projecting the learned field onto a matched template: there is no such template in direct recall.

## SELECT

The physical WRITE already contains one Sigh-like selection step. The fast carrier content is deliberately allowed to decay and only the low-frequency field is retained as memory. What persists is therefore selected by the medium's dissipation and spectral timescales rather than by saving the training waveform.

The earlier modal implementation remains useful because it shows the complementary statement explicitly in eigenspace: changing an operator changes its hierarchy of forgetting times. But the direct fluid machine no longer needs that modal matrix to recall.

## CARRY / BIND

Each event still has wave-native coordinates:

```text
q          WHERE
k          WHICH spatial carrier / direction-scale
omega      WHICH temporal carrier
Delta phi  signed phase relation
```

Localized oscillatory vorticity packets carry those coordinates. Navier-Stokes supplies the quadratic binding term rather than an explicit `z_j z_i* -> write` rule.

## ASK

ASK remains deliberately bounded. The machine first queries the local B detector. If the signed response magnitude clears a fixed threshold (`1e-4` in the default receipt), it stops after one question. Otherwise it spends its second question on a distractor location.

In the default direct run:

```text
matched field          B decisive, cost 1
frequency mismatch     no B decision, cost 2
spatial separation     no B decision, cost 2
blank                  no B decision, cost 2
```

## Run

```bash
python -m pip install -e .[dev]

# default: the distributed fluid memory itself routes the later cue
scbwas-machine --out results/direct_fluid.json

# previous hybrid: Navier-Stokes write projected into modal Theta
scbwas-modal-reference --writer fluid --out results/transduced_reference.json

# earliest explicit coherence write
scbwas-modal-reference --writer coherence --out results/coherence_reference.json

pytest -q
```

Only NumPy is required.

## Code map

- `src/scbwas/fluid_backreaction.py` — pseudo-spectral incompressible solver and four-world collision isolation.
- `src/scbwas/direct_fluid.py` — **current machine**: stores `DeltaOmega(x,y)` and lets a later cue travel through it directly.
- `src/scbwas/direct_cli.py` — default CLI.
- `src/scbwas/core.py` — earlier modal/Sigh assembly, retained as a controlled reference and for phase-space visualization.
- `src/scbwas/experiment.py` — older coherence and transduced-fluid experiments.
- `index.html` — interactive low-dimensional Slider2 descendant; still a surrogate rather than CFD in the browser.

## What changed conceptually

The sequence is now more literal:

```text
SELECT
  spent high-k carrier state is dissipated

CARRY
  coherent q/k/omega/phase packets move through the medium

BIND
  u.grad(omega) creates a collision-specific interaction

WRITE
  the surviving slow vorticity pattern *is* the memory/operator

ASK
  a bounded local detector asks what a later cue became

SELECT
  the changed medium and dissipation determine what survives next
```

The key identity is now

```text
WRITE changes the medium
and the changed medium changes the next CARRY
```

without an intervening learned matrix.

## Claim boundary

This repository now establishes for one deterministic numerical construction that:

1. matched carrier interactions leave a slow collision-specific Navier-Stokes field after washout;
2. frequency mismatch, spatial separation and quadrature strongly suppress that field/effect;
3. antiphase reverses the sign of the later local physical response;
4. after training carriers are gone, the raw stored field itself changes the trajectory of a newly injected cue;
5. a bounded local detector can distinguish the matched memory from the controls.

Still engineered are the carrier geometry, the low/fast split, detector locations, thresholds, and task meaning of A and B. We have not shown spontaneous semantic organization, a general learning rule, hardware advantage, or superior AI performance.

But the last finite-dimensional WRITE transducer is no longer required for the demonstrated recall effect.
