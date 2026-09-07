"""Local binary physics for DigitalLife V0.

A 2x2 block is encoded as:

    8 4
    2 1

The rule is deliberately low level. It knows nothing about particles, forces,
bonds, life, replication, or fitness. It only maps one 4-bit microstate to
another 4-bit microstate.
"""

from __future__ import annotations

import numpy as np

# Conservative, reversible (involutive) 2x2 Margolus block rule.
# Index = input 4-bit block, value = output 4-bit block.
V0_RULE = np.array(
    [0, 8, 4, 12, 2, 10, 9, 14, 1, 6, 5, 13, 3, 11, 7, 15],
    dtype=np.uint8,
)


def bit_count(state: int) -> int:
    """Return the number of 1 bits in a 4-bit block state."""
    return int(state).bit_count()


def validate_rule(rule: np.ndarray = V0_RULE) -> None:
    """Validate the low-level invariants required by the V0 universe.

    V0 requires:
    - exactly 16 outputs in the range [0, 15];
    - bijectivity;
    - local reversibility by involution: T(T(x)) == x;
    - exact conservation of the number of 1 bits.
    """
    if rule.shape != (16,):
        raise ValueError("A 2x2 binary rule must contain exactly 16 outputs")

    values = [int(x) for x in rule]
    if any(x < 0 or x > 15 for x in values):
        raise ValueError("Rule outputs must be 4-bit states in [0, 15]")

    if len(set(values)) != 16:
        raise ValueError("V0 rule must be bijective")

    for state in range(16):
        out = int(rule[state])
        if int(rule[out]) != state:
            raise ValueError(f"Rule is not involutive at state {state}")
        if bit_count(state) != bit_count(out):
            raise ValueError(f"Rule does not conserve 1 bits at state {state}")


validate_rule()
