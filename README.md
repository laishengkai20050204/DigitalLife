# DigitalLife

DigitalLife is an experiment in **bottom-up digital evolution**.

The project does not start from an AI model, neural network, genome, organism, reward function, or hand-written notion of life. It starts from a minimal digital universe and asks whether increasingly complex structures can emerge from local interactions alone.

## V1 research question

> Can a fixed universe made only of binary local state, fixed four-neighbor interactions, and time produce persistent structures, moving structures, bound structures, replication, variation, and eventually Darwinian evolution without those concepts being encoded explicitly?

## V1 axioms

1. **Binary state** — every lattice site is either `0` or `1`.
2. **Fixed two-dimensional space** — coordinates never move and adjacency is always the four orthogonal neighbors.
3. **Von Neumann neighborhood** — every center has exactly `UP`, `RIGHT`, `DOWN`, and `LEFT` neighbors.
4. **Snapshot time** — every tick begins by freezing the complete current state. Every interaction in that tick reads only that snapshot.
5. **Local exchange** — a microscopic event may only exchange an adjacent `1,0` pair into `0,1`.
6. **Simultaneous commit** — accepted changes are written only after all candidate interactions have been evaluated.
7. **Conflict cancellation** — if two active interaction instances want to write any common site during the same tick, all overlapping instances are cancelled for that tick. No scan order or arbitrary winner decides physics.
8. **Conservation** — every accepted event is a `1,0 -> 0,1` exchange, so the total number of `1` bits is preserved exactly.
9. **Rotational symmetry** — one rule is shared by all four directions using a target-relative coordinate frame; there is no separate north/east/south/west physics table.
10. **No predefined high-level objects** — there is no particle ID, velocity field, mass, force, energy variable, bond, molecule, genome, organism, reproduction operation, fitness function, neural network, or intelligence score.
11. **Toroidal boundary** — the top joins the bottom and the left joins the right. There are no special edge cells.

The simulator may measure emergent behavior from outside, but measurements never affect the universe.

## Fixed local neighborhood

For a center site `C`, adjacency is permanently:

```text
    U
    |
L - C - R
    |
    D
```

There is no `2 x 2` computational block and no repartitioning.

At the start of every tick, the complete grid is copied into an immutable snapshot `S_t`. Every center reads `C,U,R,D,L` only from that snapshot.

## Candidate interaction

A candidate event starts from a center with state `1` and selects one of its four neighboring sites whose state is `0`.

For the selected direction, call that target `T`. The other three neighbors are rotated into a target-relative frame:

```text
LEFT, BACK, RIGHT
```

Thus the same microscopic rule works identically for all four absolute directions.

Because an active candidate already fixes `C=1` and `T=0`, only the other three neighbor bits vary. They give eight possible local contexts:

```text
000 ... 111
```

For each context, the rule has one binary decision:

```text
0 = do nothing
1 = propose exchange C,T : 1,0 -> 0,1
```

Therefore the complete conservative V1 rule-search space contains:

```text
2^8 = 256 rules
```

The current `V1_RULE` is only a non-biological baseline. It proposes an exchange when `LEFT` and `RIGHT` differ. It is not intended as the final physics; all 256 legal rule tables can be searched.

## Why this is genuinely four-neighbor physics

For every occupied center, all four target directions are evaluated from the same frozen snapshot:

```text
C -> U
C -> R
C -> D
C -> L
```

No direction is processed first. No direction receives a privileged rule. If a perfectly symmetric isolated `1` proposes the same move in several directions, those proposals overlap at their common source and are all cancelled. Directional motion therefore cannot be created by an arbitrary update order; it must arise from asymmetric multi-bit surroundings.

## Tick transaction

```text
S_t
  |
  +--> freeze immutable snapshot
  |
  +--> for every center, inspect U/R/D/L
  |
  +--> generate all enabled adjacent exchange proposals
  |
  +--> count every site touched by proposals
  |
  +--> cancel every proposal sharing a source or target with another
  |
  +--> commit all remaining disjoint exchanges simultaneously
  v
S_(t+1)
```

A conflict is an event in one tick, not a permanent defect in the rule table. The conflicting **instances** are cancelled; the rule itself remains available elsewhere. Permanently deleting any rule that ever conflicts would bias the search toward trivial no-op physics.

## Observer-side local states

The physical rule is not allowed to see observer metrics. For analysis only, the observer can classify each fixed five-bit neighborhood:

```text
C,U,R,D,L
```

There are:

```text
2^5 = 32
```

possible observer-side local microstates. Their frequency and Shannon entropy can be measured without affecting the universe.

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

V1 is deliberately only a **digital physics sandbox**. It does not claim that the current baseline rule will generate life. Its purpose is to provide a clean experimental base for exhaustive rule search, pattern detection, collision analysis, long-run experiments, and eventually open-ended digital evolution without contaminating the universe with high-level biological assumptions.
