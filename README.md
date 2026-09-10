# SelectCarryBindWriteAskSelect

**Almost there. Now it is one machine — and WRITE is physical.**

This repo composes the mechanisms that kept reappearing across `SighImageSuper`, `InformationFlow`, `-mp-ri`, the Geometric Neuron / active-observer line, and the older phase-space experiments into one executable classical wave system:

```text
SELECT -> CARRY -> BIND -> WRITE -> ASK -> SELECT -> ...
```

It is **not a quantum computer**. It is also no longer true that the default machine simply stipulates the slow write with `Re(z_j z_i*) -> Theta`.

The current default asks the stronger question:

> Can carrier-addressed activity generate a collision-specific low-frequency write through an actual nonlinear incompressible Navier–Stokes evolution, and can that physical write be inserted into the same organism without redesigning SELECT, CARRY, ASK, recall, or mode selection?

For the present numerical construction, the answer is **yes**.

## The machine

A fast state is a small set of localized complex modes

```math
a(t) = (a_1, ..., a_N) \in \mathbb{C}^N
```

with physical basis functions

```math
\phi_i(x)=G(x-q_i)e^{ik_i x}.
```

Each mode therefore carries an address:

```text
q      WHERE in space
k      WHICH spatial carrier / direction-scale
omega  WHICH temporal carrier
phi    SIGN / phase relation when binding
```

The modal state evolves under a slow operator

```math
\dot a = [\operatorname{diag}(-d_i+i\omega_i)+g\Theta]a+u(t).
```

`Theta` is the finite operator coordinate used by the assembled organism. Erasing `a` does not erase the physical write that was read into `Theta`.

## SELECT — Sigh-style mode survival

Different modes have different decay rates. Repeated dynamics therefore select the longest-lived directions:

```math
a(t)=\sum_j c_j e^{\lambda_j t}v_j.
```

The seeded broadband receipt contracts modal effective dimension from **3.011 -> 1.898** before learning.

This is the Sigh piece: **the operator assigns forgetting times**.

## CARRY — coherent carrier state

Modes rotate at their carrier frequency while retaining complex amplitude and phase. Information is not reduced immediately to a Boolean symbol. The coherent carrier is transient state and address at once.

## BIND — let the nonlinear medium decide what survives

The previous implementation explicitly low-passed

```math
z_jz_i^*
```

and then wrote its real part into `Theta`. That version still exists as `--writer coherence` because it is a useful architectural control.

The **default** backend now removes that write arrow.

For each candidate A/B event, the program advances four exact-parity 2-D incompressible Navier–Stokes worlds:

```text
W0   no carrier forcing
WA   A only
WB   B only
WAB  A + B
```

The carriers enter as localized oscillatory vorticity forcing. The equation itself supplies the quadratic interaction:

```math
\partial_t\omega + u\cdot\nabla\omega = \nu\Delta\omega + f,
\qquad \nabla\cdot u=0.
```

After training, all forcing is removed and the fluid is allowed to relax. Only then do we form the collision-specific slow residual

```math
\boxed{
\Delta\Omega_{AB}
=P_{\rm slow}[\omega_{AB}-\omega_A-\omega_B+\omega_0]
}
```

This subtraction removes individual A and B writes and equal-time background evolution. It is the fluid version of asking for the interaction term rather than merely noticing that the final state changed.

## WRITE — Navier–Stokes backreaction becomes operator

The distributed slow fluid field has many degrees of freedom while the assembled modal organism expects a finite A->B route coordinate. A one-time matched phase-0 run therefore defines the **orientation and units of that port**.

Every other condition is projected onto the exact same physical template:

```math
c=\frac{\langle\Delta\Omega_{\rm ref},\Delta\Omega\rangle}
        {\langle\Delta\Omega_{\rm ref},\Delta\Omega_{\rm ref}\rangle}.
```

Then `c` is converted into the existing modal coupling units. This projection is an engineered transducer, but it does **not** supply carrier selectivity or sign: those have to exist in the Navier–Stokes residual before projection.

The deterministic 24×24 physical receipt gives:

| training condition | projection on matched physical port | installed A->B route |
| --- | ---: | ---: |
| matched, phase 0 | `+1.000000` | **`+0.180000`** |
| phase pi/2 | `+0.038213` | `+0.006878` |
| phase pi | **`-1.004178`** | **`-0.180000`** |
| frequency mismatch | `-0.003462` | `-0.000623` |
| spatial separation | `+0.014735` | `+0.002652` |

The raw low-frequency collision field is also selective: matched slow-field norm is **112.7×** the frequency-mismatch control and **32.5×** the spatial-separation control.

After 700 forcing-free washout steps, the matched collision residual has

```text
||fast residual|| / ||slow residual|| = 0.0895
```

so the measured write is no longer dominated by the high-frequency carrier residue.

The phase result is particularly useful. With the same locations, amplitudes and carrier frequency, `pi` reverses the physical low-frequency write while `pi/2` nearly suppresses the matched port. The sign is no longer inserted by `cos(Delta phi)` in the plasticity rule; it emerges in the nonlinear fluid residual.

## WRITE changes SELECT

The rest of the organism is unchanged.

Before installing the matched physical write:

```text
spectral abscissa  -0.140000
longest lifetime    7.142857
```

After the Navier–Stokes-derived A/B route:

```text
spectral abscissa  -0.0675171
longest lifetime   14.8111
```

The selected effective dimension after the same broadband challenge changes from `1.89784` to `1.39667`.

So the physical collision does more than produce a stored scalar:

> **the fluid changes the operator, and the changed operator changes which future modes persist.**

## ASK — bounded active readout

The observer is not handed the full state vector. It can query only local probes and has a finite question budget.

In the CI smoke receipt, after a complete modal fast-state wipe and 100 recall steps:

```text
matched physical write       peak B power  1.9726e-2
frequency mismatch                         2.3393e-7
spatial separation                         4.2371e-6
blank                                      0
```

The blank machine asks `B`, then `C`, and still makes no decision. The matched machine asks `B` once and decides `B`.

The association is therefore being reused by the same bounded observer after the transient modal state has been erased.

## SELECT again

The loop is now:

```text
coherent addressed carriers
        |
        v
actual nonlinear fluid collision
        |
        v
collision-specific slow field
        |
        v
fixed operator-port transducer
        |
        v
changed Theta / changed eigensystem
        |
        v
bounded ASK and new SELECT
```

Or compactly:

```text
SELECT -> CARRY -> BIND(NS) -> WRITE(NS slow residual) -> ASK -> SELECT
```

## Browser phase-space machine

`index.html` is the dependency-free Pages visualizer. Its causal axes remain

```text
X = Re(a_A)
Y = Im(a_A)
Z = Theta_BA
```

so the plotted slow coordinate changes later trajectories rather than merely decorating them.

Important distinction: the browser intentionally uses the reduced modal surrogate for interactive speed. The **Python default** is the Navier–Stokes physical WRITE backend. The browser is a view of the assembled causal loop, not a CFD implementation.

## Run

```bash
python -m pip install -e .[dev]

# default: physical Navier-Stokes WRITE
scbwas-machine --out results/latest.json

# old explicit coherence writer, retained as a control
scbwas-machine --writer coherence --out results/coherence_reference.json

pytest -q
```

Only NumPy is required by the machine itself.

See [`RESULTS.md`](RESULTS.md), [`THEORY.md`](THEORY.md), and [`results/physical_write.json`](results/physical_write.json).

## What this is assembled from

- **SighImageSuper** — structure assigns mode lifetimes; changed material changes later recoverability.
- **InformationFlow** — space/frequency/phase can address a quadratic write rather than letting every interaction count.
- **-mp-ri / Gemini Gate 6** — use equal-time counterfactual worlds and isolate `AB-A-B+0`; its failed unaddressed synapse motivated carrier addressing.
- **GeometricNeuron / active observer** — a distinction can physically exist while remaining invisible to the wrong bounded query.
- **Child / Jello / delayed-credit line** — state, structure, question and consequence should not be collapsed into one variable.
- **Slider2** — phase space becomes computational once plotted slow coordinates feed back into the next dynamics.

## What changed in this revision

The old full loop was already executable, but WRITE was the conspicuous hand-supplied step:

```text
low-pass coherence -> explicit plasticity rule -> Theta
```

The default path is now:

```text
carrier forcing
    -> Navier-Stokes u.grad(omega)
    -> four-world collision residual
    -> forcing-free washout
    -> slow physical field
    -> fixed port readout
    -> Theta
```

So the organism did not need redesigning. We replaced the substrate under one interface.

## Claim boundary

This is stronger than the previous version, but the boundary still matters.

The code now establishes, for this numerical construction, that:

1. a carrier-matched collision creates a reproducible low-frequency Navier–Stokes residual;
2. frequency mismatch and spatial separation strongly suppress that physical residual;
3. relative phase reverses its projection on a fixed learned/calibrated port;
4. that physical write can alter the same modal operator, persistence hierarchy, recall path and bounded ASK behavior used by the assembled machine.

It does **not** establish that bare Navier–Stokes discovers useful semantic ports, chooses rewards, provides a general learning algorithm, or beats digital neural networks. The reference-port projection and finite modal interface remain engineered.

But the explicit plasticity arrow is no longer doing the interesting selection.
