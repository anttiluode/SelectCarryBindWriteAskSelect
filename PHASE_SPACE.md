# Making the old Slider2 phase space causal

The old `slider2` display plotted three consecutive waveform buffers against one another. That can be a useful delay embedding, but it did not control the future system.

This machine gives those axes a causal interpretation.

For an A carrier and its learned A->B structural route, a simple three-coordinate display is

```math
X=\Re a_A,\qquad
Y=\Im a_A,\qquad
Z=\Theta_{BA}.
```

Then:

- rotation in the `X-Y` plane is coherent carrier phase;
- radial decay/growth is modal selection;
- displacement along `Z` is persistent structural learning;
- a later cue follows different dynamics because `Z` enters the generator itself.

An even richer display can use

```text
q       where a packet is
k       which spatial carrier it occupies
omega   temporal carrier
phase   angular coordinate / signed binding relation
```

plus the slowly changing structural coordinates `Theta`.

The point is not to make a prettier plot. The test is whether moving in the displayed state changes the subsequent trajectory. In this repo it does: `Theta` is both observable as a slow phase-space coordinate and causal in the next fast-state update.
