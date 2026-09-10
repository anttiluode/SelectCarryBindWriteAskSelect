# Theory note: a self-modifying modal flow

The useful object in this repo is not a quantum analogy. It is a two-timescale operator system with wave-native addressing.

## Fast state

For localized modes `phi_i(x)`,

```math
\psi(x,t)=\sum_i a_i(t)\phi_i(x).
```

The modal coefficients obey

```math
\dot a = G(\Theta)a+u(t),
```

with

```math
G(\Theta)=\operatorname{diag}(-d_i+i\omega_i)+g\Theta.
```

The real parts of the eigenvalues of `G` define forgetting / growth times. This is the Sigh side of the construction.

## Carrier address

A driven channel is

```math
z_i(t)=A_i e^{i(\omega_i t+\phi_i)}.
```

The pair product is

```math
z_jz_i^*=A_jA_i e^{i[(\omega_j-\omega_i)t+(\phi_j-\phi_i)]}.
```

A slow detector integrates this product. Carrier mismatch is rejected by time averaging; matched carriers survive.

## Spatial address

The basis functions use localized Gaussian envelopes. Their envelope overlap is

```math
O_{ji}=\int |\phi_j(x)|\,|\phi_i(x)|\,dx.
```

A temporally coherent pair that never occupies overlapping spatial support therefore produces only a weak write.

This gives an address with multiple coordinates:

```text
q          spatial location
k          spatial carrier / wavevector
omega      temporal carrier
Delta phi  signed phase relation
```

## Bind and write

The low-pass coherence state is

```math
\tau_r \dot r_{ji}=-r_{ji}+z_jz_i^*.
```

The slow route is

```math
\tau_\Theta \dot\Theta_{ji}
=-\Theta_{ji}
+\eta O_{ji}\Re(r_{ji}).
```

For matched carriers:

```math
\Re(r_{ji})\propto\cos(\Delta\phi).
```

So relative phase supplies a signed plasticity coordinate in the real write channel.

This is intentionally an engineered constitutive law. A stronger physical substrate would derive the slow write from an actual nonlinear medium rather than stipulate this coupling.

## Why symmetric writing changes selection

A single directed triangular route can change transfer without changing eigenvalues. For the main demonstration we therefore write both `Theta_ji` and `Theta_ij` from the same pair event.

The A/B block is approximately

```math
\begin{pmatrix}
-d_A+i\omega & g\theta\\
g\theta & -d_B+i\omega
\end{pmatrix}.
```

Its real eigenvalues split around the original decay rates. One coupled combination becomes more persistent while the orthogonal combination becomes less persistent.

This closes the Sigh / InformationFlow loop:

```text
coherent co-occurrence
      -> structural coupling
      -> new eigensystem
      -> new persistence hierarchy
      -> different future state
```

## Bounded observation

A full modal-state readout would make ASK meaningless. The machine instead exposes local projections of the reconstructed field and stops when a local response clears a confidence threshold or the question budget is exhausted.

## Relation to wavebits

Wavebits use coherent classical carrier signals and time-averaged products to recover quantum-state structure. This repo borrows the signal-processing lesson, not the quantum claim:

```text
orthogonal / mismatched carriers -> unwanted products average away
matched carriers                 -> selected product survives
```

Here the surviving product is not used to reconstruct a quantum state. It is allowed to alter the slow operator.

## Relation to Navier--Stokes

The analogy to fluid mechanics remains a design guide:

```text
carry       ~ advection / coherent transport
bind        ~ quadratic interaction
write       ~ slow backreaction / changed routing field
ask         ~ bounded local projection
```

But the present model is not a Navier--Stokes discretization. `InformationFlow` and `-mp-ri` contain the more explicitly fluid substrates. This repo is the assembly layer where the causal roles are separated cleanly enough to swap substrates without losing the machine.
