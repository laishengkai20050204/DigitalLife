# First V1 rule scan — 2026-09-07

## Purpose

The first experiment asks only whether the current microscopic physics can sustain non-trivial motion. It does **not** score life, intelligence, replication, or fitness.

V1 physics under test:

- fixed 2D binary lattice;
- fixed Von Neumann (`U/R/D/L`) adjacency;
- immutable snapshot at the start of each tick;
- only conservative adjacent exchange `1,0 -> 0,1`;
- all proposals are generated from the same snapshot;
- every proposal that overlaps another write is cancelled;
- one rotationally shared rule table;
- 8 binary relative contexts, hence `2^8 = 256` legal rules.

## Preliminary short scan

A lightweight exploratory sweep was run over all 256 rules on a `20 x 20` world, density `0.20`, seed `7`, for `40` ticks. A rule was called short-run frozen when it had zero accepted exchanges during the final 10 ticks.

Result:

- `238 / 256` rules were already frozen by that criterion.
- Only 18 rules still had any accepted exchange in the final 10 ticks.
- The strongest short-run tail activity was seen around masks `164`, `152`, and `132`.

This result is diagnostic, not a claim that those masks are intrinsically "better".

## Preliminary long recheck

Masks `164`, `152`, `132`, `226`, `204`, and `236` were then rechecked on `40 x 40` worlds at density `0.20`, for `300` ticks, using seeds `1`, `7`, and `19`.

All six candidates had zero accepted exchanges during the final 50 ticks for all three seeds.

## Interpretation

The first result suggests that the current combination

```text
exchange-only dynamics
+
strict cancellation of every overlapping proposal
```

creates many absorbing states and may suppress sustained dynamics too strongly.

That is useful evidence. The next change should not be to add biological concepts. Instead, the microscopic interaction/conflict semantics should be examined while preserving the project principles: fixed space, locality, snapshot updates, no scan-order privilege, and no predefined life.

## Reproducible repository search

The repository now provides an exhaustive search command:

```bash
digitallife-search --width 32 --height 32 --density 0.20 --steps 100 --tail-window 25 --seeds 1 7 19
```

It writes a CSV containing separate low-level measurements rather than one opaque "life score":

- mean accepted activity;
- tail accepted activity;
- proposal rate;
- conflict fraction;
- final five-bit neighborhood entropy;
- number of active five-bit microstates;
- frozen-run count.

Longer second-stage runs should be applied only after the cheap exhaustive pass.
