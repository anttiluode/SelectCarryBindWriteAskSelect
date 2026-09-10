# Results

Default result: **the learned slow Navier–Stokes field itself routes the later cue**.

The previous revision still projected the distributed fluid write onto a finite modal `Theta_AB` port. The default path no longer does that.

## Physical WRITE

The stored field is

```math
\Delta\Omega_{AB}
=P_{\rm slow}[\omega_{AB}-\omega_A-\omega_B+\omega_0]
```

after 210 driven steps and 700 forcing-free washout steps.

Default 24x24 collision fields:

| condition | slow collision norm |
| --- | ---: |
| matched phase 0 | `1.75699e-2` |
| phase pi/2 | `2.42715e-3` |
| phase pi | `1.77728e-2` |
| frequency mismatch | `1.55921e-4` |
| spatial separation | `5.40720e-4` |

The matched field is about `112.7x` the frequency-mismatch field and `32.5x` the spatial-separation field by slow-field norm.

After washout:

```text
matched ||fast|| / ||slow|| = 0.089514
```

so the retained write is predominantly low-frequency rather than leftover carrier state.

## Direct physical RECALL

The memory is not converted into a matrix. It is copied directly into the initial vorticity field of the recall world with

```text
memory_gain = 1.0
```

A later cue A is injected once. The physical memory-specific cue response is isolated with

```math
\chi_A(t)
=\omega_{\Delta\Omega+A}(t)
-\omega_{\Delta\Omega}(t)
-\omega_A(t).
```

A local Gaussian detector at B measures the signed projection of this field. With 250 recall steps:

| stored field | signed peak at B |
| --- | ---: |
| matched phase 0 | **`-6.31486e-4`** |
| phase pi/2 | `-2.59460e-5` |
| phase pi | **`+5.90061e-4`** |
| frequency mismatch | `+6.33743e-7` |
| spatial separation | `-1.24081e-5` |
| blank | `0` |

Absolute selectivity:

```text
matched / quadrature         ~24.34x
matched / frequency mismatch ~996.4x
matched / spatial separation ~50.9x
```

Antiphase reverses the sign of the later B response while preserving a comparable magnitude.

The matched response at B is also about `45.5x` larger than the matched response at a distant distractor detector.

## Bounded ASK

With a fixed local threshold of `1e-4`:

```text
matched phase 0      B decisive, cost 1
phase pi             B decisive with opposite polarity, cost 1
frequency mismatch   no B decision, cost 2
spatial separation   no B decision, cost 2
blank                no B decision, cost 2
```

ASK therefore operates directly on the changed fluid trajectory; it no longer reads a consequence mediated by `Theta`.

## What this establishes

For this deterministic numerical construction:

1. addressed carrier co-occurrence leaves a collision-specific slow fluid field;
2. the stored field survives after the training carriers have substantially washed out;
3. the raw field itself changes the nonlinear evolution of a later cue;
4. the change is locally detectable at B and is strongly suppressed by frequency mismatch, spatial separation and quadrature;
5. antiphase reverses the sign of the later local response.

## What remains engineered

The carrier geometry, spectral split, detector locations, cue amplitude, and task meaning of A/B remain chosen by us. The four-world inclusion/exclusion construction is also an experimental isolation device rather than an autonomous biological learning controller.

The current result therefore does **not** establish spontaneous semantics, general continual learning, hardware advantage, or a superior AI architecture.

What changed is narrower but important:

> **the demonstrated recall effect no longer requires a finite-dimensional transducer between the learned fluid field and the next computation.**

The medium writes itself, and the next wave propagates in that changed medium.
