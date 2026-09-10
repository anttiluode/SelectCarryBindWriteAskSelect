# Theory note: when the written field is the operator

The current default machine is not a quantum analogy and no longer needs a finite learned matrix between physical WRITE and later computation.

Its two relevant field states are

```text
fast carrier activity     w(x,t)
slow written vorticity    DeltaOmega(x,y)
```

and the key loop is

```text
fast carriers interact
      -> slow field remains
      -> later fast carrier evolves in that changed field
```

## Carrier address

A training channel carries several coordinates:

```text
q          spatial center / WHERE
k          spatial carrier / wavevector family
omega      temporal carrier / WHICH
Delta phi  relative phase / signed interaction coordinate
```

A packet is schematically

```math
f_i(x,t)=E_i(x;q_i)\cos(K_i\cdot x)\cos(\omega_i t+\phi_i).
```

This is the Wavebits/InformationFlow clue: coherent carrier relations can make selected products add while mismatched products oscillate or fail to overlap.

## BIND

The medium is periodic 2-D incompressible Navier-Stokes in vorticity form:

```math
\partial_t\omega+u\cdot\nabla\omega
=\nu\Delta\omega+f,
```

```math
u=(\partial_y\psi,-\partial_x\psi),
\qquad -\Delta\psi=\omega.
```

No explicit `z_j z_i*` product is given to the solver. The quadratic mixer is the convective term itself.

Frequency mismatch changes temporal cancellation, spatial separation suppresses local cross-terms, and relative phase changes the sign of the coherent collision pattern.

## WRITE: isolate the collision in state space

A changed final fluid by itself proves little. A and B can each alter the field independently. Therefore four exact-parity worlds are advanced:

```text
W0   no carriers
WA   A only
WB   B only
WAB  A+B
```

The pair-specific residual is

```math
\Delta\omega_{AB}
=\omega_{AB}-\omega_A-\omega_B+\omega_0.
```

After forcing is removed, every world receives the same long washout. Memory is defined as the slow part

```math
\boxed{
\Delta\Omega_{AB}=P_{\rm slow}\Delta\omega_{AB}.
}
```

This is a state-space inclusion/exclusion measurement, not a nonlinear detector applied after the fact.

The default matched collision leaves

```text
||fast residual|| / ||slow residual|| ~= 0.0895
```

after washout, so the retained field is dominated by the slow band.

## No Theta transducer

The previous version performed

```text
DeltaOmega(x,y) -> fixed projection -> Theta_AB.
```

The default machine now stops at `DeltaOmega`.

At recall, a new fluid world is initialized with that distributed field itself:

```math
\omega(x,0)=\Delta\Omega_{AB}(x)+\omega_{cue}(x).
```

Two controls are evolved in parallel:

```text
memory only
cue only in blank fluid
```

and the later memory-specific cue trajectory is

```math
\boxed{
\chi_A(t)
=\omega_{\Delta\Omega+A}(t)
-\omega_{\Delta\Omega}(t)
-\omega_A(t).
}
```

This subtraction removes static memory amplitude and direct cue propagation. `chi_A` therefore measures how the stored physical field changes the future evolution of the cue.

There is no matched-template projection of `DeltaOmega`, and the stored field is used with gain exactly `1`.

## ASK

A bounded local detector reads

```math
y_B(t)=\langle h_B,\chi_A(t)\rangle
```

with `h_B` a localized Gaussian patch.

This is intentionally a small observation rather than full field tomography. The direct machine asks B first and only spends another question if B is not decisive.

The detector is engineered, but it is not a WRITE transducer: it only observes what the new cue physically became after evolving in the stored field.

## The measured address structure survives direct recall

With the raw stored fields:

```text
matched phase 0       B signed peak  -6.315e-4
phase pi/2                            -2.595e-5
phase pi                              +5.901e-4
frequency mismatch                    +6.34e-7
spatial separation                    -1.24e-5
blank                                  0
```

So direct later routing retains the same qualitative address structure:

```text
space       matters
frequency   matters strongly
phase       controls sign
```

Antiphase is especially informative: it does not merely change the amount of stored energy. It reverses the sign of the later local cue response.

## SELECT

The Sigh connection now appears physically as a hierarchy of survival times.

Training injects high-frequency carrier structure, but the machine does not save that waveform. Dissipation removes the fast content and the low-frequency collision field remains. What survives the dynamics becomes the operator seen by the next cue.

The older modal model in `core.py` still gives a clean eigensystem view of the same design principle:

> structure determines which modes persist.

The direct fluid path simply realizes the next step without first compressing the written structure into a finite matrix.

## Relation to the failed fluid-synapse Gate 6

The earlier Gate 6 in `-mp-ri` found nonlinear low-frequency change but failed functional isolation: the separated control could route recall more strongly than the alleged collision synapse.

The important correction was not “more nonlinearity.” It was **address the interaction**.

The current machine keeps the four-world attacker but gives packets coherent spatial/frequency/phase addresses. The resulting matched memory is strongly larger than frequency and spatial controls, and—more importantly—the raw field itself selectively changes a later cue.

## What remains open

The removed gap was

```text
physical write -> finite Theta -> later route.
```

That gap is gone for the demonstrated effect.

The remaining gaps are higher-level:

- who chooses useful carrier addresses;
- how consequence decides which physical writes should be retained;
- how many memories can coexist before cross-talk dominates;
- whether the slow field can support continual adaptation and reversal;
- whether a hardware implementation offers any efficiency or robustness advantage;
- whether the same substrate can be driven by real sensory packets rather than named A/B channels.

Those are now questions about the machine's learning ecology, not about whether a written field can participate directly in the next computation.
