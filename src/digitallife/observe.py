"""Observer-side measurements that never affect universe dynamics."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .world import BinaryWorld


@dataclass(frozen=True, slots=True)
class Observation:
    tick: int
    ones: int
    density: float
    block_entropy_bits: float
    active_microstates: int


def block_histogram(grid: np.ndarray, phase: int = 0) -> np.ndarray:
    """Count the 16 possible 2x2 microstates in one Margolus partition."""
    shifted = np.roll(grid, shift=(-phase, -phase), axis=(0, 1))
    tl = shifted[0::2, 0::2]
    tr = shifted[0::2, 1::2]
    bl = shifted[1::2, 0::2]
    br = shifted[1::2, 1::2]
    states = ((tl << 3) | (tr << 2) | (bl << 1) | br).ravel()
    return np.bincount(states, minlength=16)


def block_entropy_bits(grid: np.ndarray, phase: int = 0) -> float:
    """Shannon entropy of local 2x2 microstate frequencies, in bits."""
    counts = block_histogram(grid, phase)
    total = counts.sum()
    if total == 0:
        return 0.0
    p = counts[counts > 0] / total
    return float(-(p * np.log2(p)).sum())


def observe(world: BinaryWorld) -> Observation:
    hist = block_histogram(world.grid, world.tick & 1)
    return Observation(
        tick=world.tick,
        ones=world.ones,
        density=world.density,
        block_entropy_bits=block_entropy_bits(world.grid, world.tick & 1),
        active_microstates=int(np.count_nonzero(hist)),
    )
