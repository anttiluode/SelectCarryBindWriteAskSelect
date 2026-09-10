# Theory note: modal flow with a physical write substrate

The useful object in this repo is not a quantum analogy. It is a two-timescale operator system with wave-native addressing. The current default now separates the **modal organism** from the **physical write substrate**.

## Fast modal state

For localized modes `phi_i(x)`,

```math
\psi(x,t)=\sum_i a_i(t)\phi_i(x),
```

with

```math
\dot a=G(\Theta)a+u(t),
\qquad
G(\Theta)=\operatorname{diag}(-d_i+i\omega_i)+g\Theta.
```

The real parts of the eigenvalues of `G` define forgetting/growth times. This is the Sigh side: structure assigns persistence.

## Carrier address

A physical training channel is specified by several coordinates:

```text
q          spatial center / WHERE
k          spatial carrier / wavevector family
omega      temporal carrier / WHICH
Delta phi  relative phase / signed interaction coordinate
```

The old reduced writer made this transparent with

```math
z_jz_i^*=A_jA_i e^{i[(\omega_j-\omega_i)t+(\phi_j-\phi_i)]},
```

then explicitly low-passed the product. That model is retained as `--writer coherence`.

The default path now asks whether a nonlinear field can implement the same selection physically.

## Navier–Stokes BIND

The write substrate is a periodic 2-D incompressible vorticity field:

```math
\partial_t\omega+u\cdot\nabla\omega
=\nu\Delta\omega+f,
```

```math
u=(\partial_y\psi,-\partial_x\psi),
\qquad
-\Delta\psi=\omega.
```

Carrier A and carrier B enter as localized, oscillatory, high-spatial-frequency forcing packets. The solver does not receive a coherence product. The only nonlinear mixer is the convective term `u.grad(omega)`.

The forcing has the schematic form

```math
f_i(x,t)=E_i(x;q_i)\cos(K_i\cdot x)\cos(\omega_i t+\phi_i).
```

Because the dynamics are quadratic, pair cross-terms can generate difference-frequency / difference-wavevector content. Frequency mismatch makes those contributions alternate in sign through time; spatial separation suppresses local cross-terms; relative phase can reverse the collision contribution.

## Four-world isolation

A changed final fluid is not sufficient evidence for binding. A alone and B alone can each alter the field, and every world diffuses with time.

Therefore all worlds start identically and advance for exactly the same number of steps:

```text
W0   background / no carriers
WA   A only
WB   B only
WAB  A + B
```

The pair-specific physical write is

```math
\Delta\Omega_{AB}
=P_{\rm slow}
[\omega_{AB}-\omega_A-\omega_B+\omega_0].
```

This is an inclusion/exclusion interaction residual in the **state itself**, before a nonlinear detector is applied.

After the carriers are switched off, every world receives a forcing-free washout. The current deterministic setting leaves the matched collision with

```text
||fast residual|| / ||slow residual|| = 0.0895
```

after washout, so the stored quantity used by the adapter is genuinely dominated by the low-frequency band.

## From distributed slow field to modal operator

There is still an interface problem. `DeltaOmega_AB(x,y)` is a distributed physical state, while the assembled organism currently expects a finite route `Theta_BA`.

The present solution is a fixed transducer.

One matched phase-0 run defines a reference physical port `R_AB(x,y)`. Every subsequent collision field is measured by

```math
c_{AB}
=\frac{\langle R_{AB},\Delta\Omega\rangle}
       {\langle R_{AB},R_{AB}\rangle}.
```

The modal route is then expressed in chosen coupling units:

```math
\Theta_{BA}=s\,c_{AB}.
```

For the main symmetric demonstration the same value is installed in `Theta_AB` so the structural event changes the eigenspectrum rather than only creating a triangular feed-forward edge.

This projection is **calibration**, not a second learning rule: the same fixed reference is used for phase, frequency and spatial controls. It chooses what finite physical deformation counts as the A<->B operator port, but it does not choose the sign or selectivity of each new collision.

## The measured address structure

With the current deterministic numerical substrate:

```text
matched phase 0       projection  +1.0000
phase pi/2                        +0.0382
phase pi                          -1.0042
frequency mismatch               -0.00346
spatial separation               +0.01473
```

and the raw matched slow-field norm is about `112.7x` the frequency-mismatch control and `32.5x` the spatial-separation control.

This is the main new fact relative to the previous version: **the nonlinear fluid itself now supplies most of the selection that the explicit coherence rule used to impose.**

## Why WRITE changes SELECT

The A/B modal block is approximately

```math
\begin{pmatrix}
-d_A+i\omega & g\theta\\
g\theta & -d_B+i\omega
\end{pmatrix}.
```

A nonzero physical write splits the decay rates of the coupled combinations. In the default receipt the longest lifetime changes from about `7.14` to `14.81`.

So the loop is now

```text
carrier event
    -> nonlinear physical collision
    -> slow distributed backreaction
    -> fixed operator port
    -> changed eigensystem
    -> changed persistence hierarchy
    -> changed future bounded observation
```

## Bounded observation

A full state tomography would make ASK trivial. The organism instead exposes local probes and stops when one clears a threshold or the question budget is exhausted.

The important architectural point is that ASK did not change when WRITE became physical. This is the benefit of treating the system as composable causal roles rather than one monolithic field metaphor.

## Relation to Wavebits

Wavebits supply the signal-processing clue that coherent carrier relations can make selected products survive temporal averaging while mismatched products cancel.

This repo uses that clue differently. It does not reconstruct an exponentially large quantum state. It injects carrier-coded activity into a nonlinear classical medium and asks whether the resulting slow physical state can alter future information flow.

## Relation to the failed fluid-synapse Gate 6

The earlier `-mp-ri/Claude/gate6_fluid_synapse.py` found substantial nonlinear low-frequency change but failed the functional isolation test: its separated control routed recall more strongly than the collision-specific term.

That failure suggested the missing variable was **addressing**, not more nonlinearity.

The current substrate therefore keeps the four-world attacker but gives the packets coherent spatial/frequency/phase addresses before they enter the same kind of nonlinear fluid dynamics.

## Remaining physical gap

The strongest next replacement is now very specific.

Currently:

```text
distributed Navier-Stokes slow field
          -> fixed calibrated modal port
          -> Theta
```

A more fully field-native machine would remove that transducer and let the slow physical field itself be the routing operator for the next fast carriers.

That is a narrower and better problem than inventing another external learning rule.
