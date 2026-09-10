# Results

Deterministic default run from `results/machine.json`.

## SELECT before learning

A seeded broadband state begins with modal participation ratio

```text
3.010822
```

and contracts under autonomous dynamics to

```text
1.897843
```

after 800 steps. This is ordinary dissipative mode selection, not a learned effect.

## BIND / WRITE controls

After equal-duration continuous two-channel driving:

| condition | theta A->B |
| --- | ---: |
| matched frequency, phase 0 | `+0.180000` |
| matched frequency, phase pi/2 | `+2.92e-17` |
| matched frequency, phase pi | `-0.180000` |
| temporal frequency mismatch | `-0.0006256` |
| spatial separation | `+0.0168447` |
| blank | `0` |

The matched absolute write is about `287.7x` the frequency-mismatch control and `10.69x` the spatial-separation control.

The phase result is intentionally interpreted narrowly. The write channel is the real part of a complex coherence product, so the `cos(Delta phi)` pattern is expected from the implementation.

## WRITE changes SELECT

Before learning, the spectral abscissa is

```text
-0.140000
```

with dominant lifetime `~7.14` model-time units.

After the matched A/B write, a coupled A/B mode becomes dominant:

```text
spectral abscissa  -0.0675171
lifetime           14.8111
```

The orthogonal A/B combination becomes shorter-lived (`~2.31`). Thus the structural write does not merely store an association; it changes the hierarchy of persistence.

## Fast wipe then recall

All fast modal amplitudes and coherence traces are erased before recall. `Theta` is retained.

Cue A alone then gives peak B-mode power:

| condition | peak B power |
| --- | ---: |
| matched write | `4.63397e-2` |
| spatial separation | `3.90713e-4` |
| frequency mismatch | `2.01240e-8` |
| quadrature phase | `~1.17e-33` |
| blank | `0` |

So the matched association survives in the slow operator rather than residual fast state.

## ASK

With a two-question budget and fixed threshold:

```text
blank world    asks B, then C, no decision        cost 2
matched world  asks B, decides B immediately      cost 1
```

The antiphase world has the same B modal *power* as the positive write but a different local reconstructed-field response, which is a useful reminder that state energy and bounded query geometry are not the same observable.

## Status

All six unit tests pass locally. CI runs the tests and a smaller end-to-end smoke receipt on Python 3.10 and 3.12.

The result is an architectural proof-of-mechanism. The slow write law remains explicit and engineered.
