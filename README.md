# DigitalLife

DigitalLife is an experiment in **bottom-up digital evolution**.

The project does not start from an AI model, neural network, genome, organism, reward function, or hand-written notion of life. It starts from a minimal digital universe and asks whether increasingly complex structures can emerge from local interactions alone.

## V0 research question

> Can a universe made only of binary local state, local update rules, and time produce persistent structures, moving structures, bound structures, replication, variation, and eventually Darwinian evolution without those concepts being encoded explicitly?

## V0 axioms

The initial universe intentionally contains as little semantics as possible:

1. **Binary state** — every lattice site is either `0` or `1`.
2. **Two-dimensional space** — the universe is an even-sized 2D lattice.
3. **Locality** — updates only inspect one local `2 x 2` block.
4. **Discrete time** — the universe advances in ticks.
5. **Margolus partitioning** — the `2 x 2` block partition shifts by one cell every tick so information can propagate between blocks.
6. **Conservation** — the number of `1` bits is preserved exactly.
7. **Reversibility** — the V0 local transition is an involution: applying the same local transition twice returns the original local state.
8. **No predefined high-level objects** — there is no particle class, mass, force, energy variable, bond, molecule, genome, organism, reproduction operation, fitness function, neural network, or intelligence score.
9. **Toroidal boundary** — the top joins the bottom and the left joins the right. There are no special edge cells.

The simulator may measure emergent behavior from outside, but measurements never affect the universe.

## Local physics

A `2 x 2` block contains four bits and therefore has only 16 possible microstates.

Bits are encoded as:

```text
8 4
2 1
```

The current V0 rule is a conservative reversible collision rule:

- empty and full blocks remain unchanged;
- one-bit states move to the opposite corner;
- adjacent two-bit states move to the opposite edge;
- diagonal two-bit states transform into the other diagonal;
- three-bit states rotate by 180 degrees.

The complete lookup table is:

```text
0  -> 0
1  -> 8
2  -> 4
3  -> 12
4  -> 2
5  -> 10
6  -> 9
7  -> 14
8  -> 1
9  -> 6
10 -> 5
11 -> 13
12 -> 3
13 -> 11
14 -> 7
15 -> 15
```

This table is not intended to encode life. It only supplies a tiny local dynamics with transport and collisions. Future research should search over other rule tables subject to low-level constraints rather than hand-coding biological behavior.

## What counts as an observation, not a rule

Terms such as these are descriptions an external observer may use if corresponding patterns appear:

```text
persistent pattern
moving pattern
bound state
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

V0 is deliberately only a **digital physics sandbox**. It does not claim that the current rule will generate life. Its purpose is to provide a clean experimental base from which rule search, pattern detection, long-run experiments, and open-ended evolution research can be added without contaminating the universe with high-level biological assumptions.
