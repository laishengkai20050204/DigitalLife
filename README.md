# DigitalLife

DigitalLife is an experiment in **bottom-up digital evolution**.

The project does not start from an AI model, neural network, genome, organism, reward function, or hand-written notion of life. It starts from a minimal digital universe and asks whether increasingly complex structures can emerge from local interactions alone.

## V1 research question

> Can a fixed universe made only of binary local state, local adjacent interactions, and time produce persistent structures, moving structures, bound structures, replication, variation, and eventually Darwinian evolution without those concepts being encoded explicitly?

## V1 axioms

1. **Binary state** — every lattice site is either `0` or `1`.
2. **Fixed two-dimensional space** — coordinates and adjacency never get repartitioned.
3. **Locality** — physical changes can only rewrite two adjacent sites.
4. **Snapshot time** — every tick begins by freezing the complete current state. Every interaction in that tick reads only that snapshot.
5. **Simultaneous commit** — accepted changes are written only after all candidate interactions have been evaluated.
6. **Conflict cancellation** — if two active interaction instances want to write any common site during the same tick, all overlapping instances are cancelled for that tick. No scan order or arbitrary winner decides physics.
7. **Conservation** — every accepted adjacent interaction preserves the number of `1` bits, so the world preserves it globally.
8. **No predefined high-level objects** — there is no particle ID, velocity field, mass, force, energy variable, bond, molecule, genome, organism, reproduction operation, fitness function, neural network, or intelligence score.
9. **Toroidal boundary** — the top joins the bottom and the left joins the right. There are no special edge cells.

The simulator may measure emergent behavior from outside, but measurements never affect the universe.

## Adjacent interaction rule

There are no `2 x 2` computational blocks and no Margolus repartitioning.

Instead, every horizontal and vertical adjacent pair `A-B` is a possible local interaction. The interaction is allowed to inspect one site immediately behind and ahead of the pair:

```text
L A B R
```

This is still local: only `A` and `B` may change. `L` and `R` are read-only context from the tick snapshot.

The four context bits give 16 possible local input states:

```text
0000 ... 1111
```

A rule entry outputs only the next two-bit state `A'B'`.

V1 currently enforces microscopic conservation. Therefore:

- `00 -> 00`
- `11 -> 11`
- a mixed pair `01` may either stay `01` or swap to `10`
- a mixed pair `10` may either stay `10` or swap to `01`

Across the 16 contexts, exactly eight contain a mixed selected pair. Each has two conservative choices, so the complete V1 conservative rule-search space is:

```text
2^8 = 256 rules
```

The current `V1_RULE` is only a non-biological baseline. It swaps a mixed pair when the two outer context bits differ. It is not intended as the final physics. The research path is to evaluate all legal rules and later enlarge the interaction context if the 256-rule space is too weak.

## Tick transaction

For each tick:

```text
S_t
  |
  +--> freeze immutable snapshot
  |
  +--> evaluate every adjacent horizontal/vertical interaction
  |
  +--> collect active write proposals
  |
  +--> cancel every proposal that overlaps another proposal
  |
  +--> commit all remaining disjoint proposals simultaneously
  v
S_(t+1)
```

This design prevents update-order artifacts without dynamically changing who is adjacent to whom.

A conflict is an event in one tick, not a permanent defect in the rule table. The conflicting *instances* are cancelled; the rule itself remains available in other local contexts. Permanently deleting any rule that ever conflicts would strongly bias the search toward trivial no-op physics.

## Important consequence of binary symmetry

An isolated `1` in a perfectly symmetric environment has no internal direction state. A deterministic symmetric law therefore has no physical reason to choose left instead of right, or up instead of down.

DigitalLife intentionally does not solve that by adding a hidden velocity or direction field. If directed motion emerges, it should preferably arise from an asymmetric multi-bit pattern rather than from a prewritten particle velocity.

## What counts as an observation, not a rule

These words are observer-side descriptions only:

```text
particle
motion
persistent pattern
bound state
collision
catalysis
self-maintenance
replication
heritable variation
competition
Darwinian evolution
```

None of them are concepts available to the simulated universe itself.

## Install

Requires Python 3.11+.

```bash
python -m pip install -e .
```

## Run

```bash
digitallife --width 128 --height 128 --density 0.20 --steps 10000 --report-every 100
```

For a small ASCII run:

```bash
digitallife --width 32 --height 16 --density 0.20 --steps 100 --report-every 10 --ascii
```

A fixed seed makes a run reproducible:

```bash
digitallife --seed 42
```

## Current scope

V1 is deliberately only a **digital physics sandbox**. It does not claim that the current rule will generate life. Its purpose is to provide a clean experimental base for exhaustive rule search, pattern detection, collision analysis, long-run experiments, and eventually open-ended digital evolution without contaminating the universe with high-level biological assumptions.
