# SelectCarryBindWriteAskSelect

**Almost there. Now it is one machine.**

This repo composes the mechanisms that kept reappearing across `SighImageSuper`, `InformationFlow`, `-mp-ri`, the Geometric Neuron / active-observer line, and the older phase-space experiments into one executable classical wave system:

```text
SELECT -> CARRY -> BIND -> WRITE -> ASK -> SELECT -> ...
```

It is **not a quantum computer** and it is **not a claim that Navier–Stokes spontaneously learns**. The useful question is narrower:

> Can a bounded machine keep information in coherent modal state, make only addressed pairs interact, let those interactions rewrite the operator, and then have the changed operator select and route future state differently?

The current answer in this engineered model is **yes**.

## The machine

A fast state is a small set of localized complex modes

```math
a(t) = (a_1, ..., a_N) \in \mathbb{C}^N
```

with physical basis functions

```math
\phi_i(x)=G(x-q_i) e^{i k_i x}.
```

Each mode therefore carries an address

```text
q      WHERE in space
k      WHICH spatial carrier / direction-scale
omega  WHICH temporal carrier
phi    SIGN / phase relation when binding
```

The fast state evolves under a slow self-written operator

```math
\dot a = \left[\operatorname{diag}(-d_i+i\omega_i)+g\Theta\right]a + u(t).
```

`Theta` is the persistent body. Erasing `a` does not erase `Theta`.

### SELECT — Sigh-style mode survival

Different modes have different decay rates. Repeated dynamics therefore select the longest-lived directions:

```math
a(t)=\sum_j c_j e^{\lambda_j t} v_j.
```

The default broadband receipt contracts modal effective dimension from **3.011 -> 1.898** before learning.

This is the piece inherited from `SighImageSuper`: **the operator assigns forgetting times**.

### CARRY — coherent classical wave state

Modes rotate at their carrier frequency while retaining complex amplitude and phase. The machine does not reduce an event immediately to a Boolean bit. The carrier state itself is the transient memory and transport variable.

### BIND — addressed quadratic interaction

For two simultaneously driven channels, the slow coincidence detector receives

```math
z_j z_i^*.
```

Its low-pass accumulator is

```math
r_{ji} \leftarrow \beta r_{ji}+(1-\beta)z_j z_i^*.
```

Three selectors fall out:

```text
spatial envelope overlap  -> WHERE can bind
Delta omega               -> WHICH pair survives time averaging
Delta phase               -> SIGN of the real write channel
```

Thus equal-frequency phase relations give the expected pattern:

```text
Delta phi = 0       positive write
Delta phi = pi/2    ~zero real write
Delta phi = pi      negative write
```

### WRITE — experience becomes operator

The retained coherent product writes the persistent route:

```math
\Theta_{ji}\leftarrow\Theta_{ji}+\eta\,O_{ji}\,\Re(r_{ji}),
```

where `O_ji` is the measured spatial overlap between the two localized carrier envelopes.

For the main demonstration the route is written symmetrically, so learning does something stronger than add a lookup-table edge: it changes the **eigensystem and persistence hierarchy** of the fast dynamics.

Before learning the dominant real eigenvalue is

```text
-0.1400   lifetime ~7.14
```

After matched A+B binding it becomes

```text
-0.06752  lifetime ~14.81
```

A new coupled A/B mode has become the longest-lived direction. This is the direct Sigh -> InformationFlow bridge:

> **binding changes structure; structure changes which modes survive.**

### ASK — bounded active readout

The observer is not handed the full state vector. It can query only local probes and has a finite question budget.

After a complete fast-state wipe, an untrained world needs both available questions and still makes no decision. The matched learned world answers `B` with the **first** local question.

The observer is deliberately tiny. Its purpose is to keep the interface honest so a stronger active-sensing policy can later replace it without changing the substrate.

### SELECT again

The loop closes because the write changed the generator itself. New broadband state is filtered by a different persistence spectrum than the one that existed before experience.

That is the machine:

```text
                  +---------------------------+
                  |        slow Theta         |
                  |  persistent operator/body |
                  +-------------^-------------+
                                |
                             WRITE
                                |
world -> SELECT -> CARRY -> BIND+-----> ASK -> action/question
          ^                     |                |
          |                     +----------------+
          +------ changed operator / history ----+
```

## Browser phase-space machine

`index.html` is a dependency-free interactive version intended for GitHub Pages. It keeps the old Slider2 visual intuition but makes the plotted slow coordinate causal:

```text
X = Re(a_A)
Y = Im(a_A)
Z = Theta_BA
```

Use the buttons to inject broadband state, write with phase `0`, `pi/2`, or `pi`, attack the write with a frequency mismatch, wipe all fast activity, and recall cue A. The browser model is deliberately lower-dimensional than the Python receipt, but the same loop is visible rather than hidden behind the plot.

## Main receipt

The deterministic default experiment runs six matched-time worlds.

| world | learned A->B route |
| --- | ---: |
| matched, phase 0 | **+0.180000** |
| phase pi/2 | `2.9e-17` |
| phase pi | **-0.180000** |
| frequency mismatch | `-0.000626` |
| spatial separation | `+0.016845` |
| blank | `0` |

Absolute route selectivity is about **288x** over the frequency-mismatch control and **10.7x** over the spatial-separation control.

After all transient state is erased, cue A alone produces peak B-mode power

```text
matched write       4.63e-2
frequency mismatch  2.01e-8
spatial separation  3.91e-4
blank                0
```

The matched world therefore retains a functional A->B route in the slow operator, not in leftover fast activity.

See [`RESULTS.md`](RESULTS.md) and [`results/machine.json`](results/machine.json).

## Run

```bash
python -m pip install -e .[dev]
scbwas-machine --out results/latest.json
pytest -q
```

Only NumPy is required by the machine itself.

## What this is assembled from

The implementation is new code, but the mechanisms are deliberately the smallest surviving pieces of the earlier repo line:

- **SighImageSuper** — operator iteration selects modes by persistence; memory is not restricted to lingering activity; changed material can alter later query geometry.
- **InformationFlow** — carrier/phase/frequency addressed quadratic products can write a persistent routing field by construction.
- **-mp-ri** — fast flow / slow body separation; later routing depends on persistent field objects.
- **GeometricNeuron / active observer** — a distinction can exist while remaining invisible to the wrong bounded query.
- **Child / Jello / delayed-credit line** — present state, stored structure, and the act of asking should not be collapsed into one variable.
- **Slider2 / old phase-space UI** — phase space is useful once the plotted coordinates are causal state variables rather than decoration.

## Why this is not just another gate

There are controls, because without them every wave toy lies to us. But the repo is organized around **one reusable machine class**, not a ladder of unrelated gates.

`ModalFieldComputer` exposes the full loop:

```python
machine.inject(...)
machine.step(...)
machine.write_from_pair(...)
machine.ask(...)
machine.select_from_broadband(...)
machine.reset_fast(...)
```

The next work should happen *inside this object*: replace the explicit structural write with progressively more physical substrates, feed it real Splat/Gabor sensory packets, or attach the old Slider2 audio loop as a hardware carrier source.

## Claim boundary

The positive result is real for this implementation but partly **by construction**.

We explicitly chose:

- the carrier basis;
- the low-pass coherence detector;
- the structural coupling rule;
- the bounded probe policy.

So this repo does **not** establish a new fundamental law, quantum advantage, a solution to general continual learning, or spontaneous learning in bare Navier–Stokes.

What it establishes is an executable architectural identity:

> **selective coherent interaction can write a slow operator, and the written operator can change both later routing and the modal hierarchy that selects what persists.**

That is enough to build on.
