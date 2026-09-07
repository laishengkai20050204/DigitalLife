"""Low-level adjacent interaction rules for DigitalLife V1.

The universe is a fixed binary lattice.  A rule application is centered on one
ordered adjacent pair A-B and may only rewrite that pair.  It may inspect one
cell immediately behind and ahead of the pair:

    L A B R

The four-bit context is encoded as 8*L + 4*A + 2*B + R.  A rule table contains
16 entries.  Each entry is a two-bit output A'B' in [0, 3].

No rule knows about particles, velocity, force, bonds, life, replication, or
fitness.  Conservation is enforced at the microscopic interaction boundary:
the number of 1 bits in A-B must equal the number in A'-B'.
"""

from __future__ import annotations

from collections.abc import Iterator

import numpy as np


def _pair_from_context(state: int) -> int:
    """Extract A-B from the L-A-B-R context as a two-bit integer."""
    a = (state >> 2) & 1
    b = (state >> 1) & 1
    return (a << 1) | b


def validate_rule(rule: np.ndarray) -> None:
    """Validate a 16-context adjacent-pair rule.

    V1 requires only microscopic number conservation.  Equal pairs (00, 11)
    therefore cannot change; mixed pairs (01, 10) may either stay or swap.
    """
    rule = np.asarray(rule)
    if rule.shape != (16,):
        raise ValueError("an adjacent interaction rule must contain 16 outputs")

    values = [int(x) for x in rule]
    if any(x < 0 or x > 3 for x in values):
        raise ValueError("rule outputs must be two-bit pair states in [0, 3]")

    for state, out in enumerate(values):
        pair = _pair_from_context(state)
        if pair.bit_count() != out.bit_count():
            raise ValueError(f"rule does not conserve 1 bits at context {state:04b}")


def rule_from_mask(mask: int) -> np.ndarray:
    """Build one of all 256 conservative V1 rules.

    There are eight contexts whose selected pair is mixed (01 or 10).  Each
    such context independently chooses either STAY or SWAP, so the complete
    conservative rule space has 2**8 == 256 members.  ``mask`` encodes those
    eight binary choices in context-number order.
    """
    if mask < 0 or mask >= 256:
        raise ValueError("mask must be in [0, 255]")

    table = np.empty(16, dtype=np.uint8)
    choice_index = 0
    for state in range(16):
        pair = _pair_from_context(state)
        if pair in (1, 2):
            swap = (mask >> choice_index) & 1
            table[state] = 3 - pair if swap else pair
            choice_index += 1
        else:
            table[state] = pair

    validate_rule(table)
    return table


def conservative_rules() -> Iterator[np.ndarray]:
    """Yield the complete 256-rule conservative V1 search space."""
    for mask in range(256):
        yield rule_from_mask(mask)


def _baseline_rule() -> np.ndarray:
    """A non-biological baseline: swap a mixed pair when L and R differ."""
    table = np.empty(16, dtype=np.uint8)
    for state in range(16):
        left = (state >> 3) & 1
        right = state & 1
        pair = _pair_from_context(state)
        table[state] = 3 - pair if pair in (1, 2) and left != right else pair
    validate_rule(table)
    return table


V1_RULE = _baseline_rule()
