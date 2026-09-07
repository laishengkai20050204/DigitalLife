"""Rotationally symmetric four-neighbor interaction rules for DigitalLife V1.

The universe is a fixed binary lattice.  A potential microscopic event starts
from a center site C=1 and one selected orthogonal neighbor T=0.  The complete
Von Neumann neighborhood is read from the frozen tick snapshot:

        U
        |
    L - C - R
        |
        D

For each candidate target direction, the other three neighbors are expressed
in the target-relative frame as LEFT, BACK, RIGHT.  The same rule is therefore
used for up, right, down, and left without a built-in compass preference.

Because C=1 and T=0 are fixed for an active candidate, only the other three
neighbor bits vary.  They form an index in [0, 7]:

    context = 4*LEFT + 2*BACK + RIGHT

A rule contains eight binary decisions.  0 means no event; 1 means propose the
local exchange 1,0 -> 0,1 between C and T.  Every accepted event therefore
conserves the total number of 1 bits exactly.

No rule knows about particles, velocity, force, bonds, life, replication, or
fitness.
"""

from __future__ import annotations

from collections.abc import Iterator

import numpy as np


def validate_rule(rule: np.ndarray) -> None:
    """Validate one rotationally shared 3-bit-context rule table."""
    rule = np.asarray(rule)
    if rule.shape != (8,):
        raise ValueError("a four-neighbor rule must contain exactly 8 decisions")
    if not np.all((rule == 0) | (rule == 1)):
        raise ValueError("rule decisions must be binary: 0=no proposal, 1=swap")


def rule_from_mask(mask: int) -> np.ndarray:
    """Build one of all 256 conservative four-neighbor rules.

    There are eight possible LEFT/BACK/RIGHT contexts and each independently
    chooses NO-OP or SWAP, so the complete V1 rule space is 2**8 == 256.
    """
    if mask < 0 or mask >= 256:
        raise ValueError("mask must be in [0, 255]")
    table = np.array([(mask >> i) & 1 for i in range(8)], dtype=np.uint8)
    validate_rule(table)
    return table


def conservative_rules() -> Iterator[np.ndarray]:
    """Yield the complete 256-rule conservative V1 search space."""
    for mask in range(256):
        yield rule_from_mask(mask)


def _baseline_rule() -> np.ndarray:
    """Low-level baseline: propose when LEFT and RIGHT differ.

    This has no absolute directional preference.  An isolated 1 sees the same
    symmetric context in all four directions and therefore does not move.
    Asymmetric multi-bit neighborhoods can generate directional proposals.
    """
    table = np.zeros(8, dtype=np.uint8)
    for context in range(8):
        left = (context >> 2) & 1
        right = context & 1
        table[context] = int(left != right)
    validate_rule(table)
    return table


V1_RULE = _baseline_rule()
