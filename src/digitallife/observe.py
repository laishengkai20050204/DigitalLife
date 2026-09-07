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
    local_entropy_bits: float
    active_microstates: int


def local_2x2_histogram(grid: np.ndarray) -> np.ndarray:
    """Count all 16 sliding 2x2 patterns on the toroidal fixed lattice."""
    tl = grid
    tr = np.roll(grid, shift=-1, axis=1)
    bl = np.roll(grid, shift=-1, axis=0)
    br = np.roll(tr, shift=-1, axis=0)
    states = ((tl << 3) | (tr << 2) | (bl << 1) | br).ravel()
    return np.bincount(states, minlength=16)


def local_entropy_bits(grid: np.ndarray) -> float:
    """Shannon entropy of sliding local 2x2 pattern frequencies, in bits."""
    counts = local_2x2_histogram(grid)
    total = counts.sum()
    if total == 0:
        return 0.0
    p = counts[counts > 0] / total
    return float(-(p * np.log2(p)).sum())


def observe(world: BinaryWorld) -> Observation:
    hist = local_2x2_histogram(world.grid)
    return Observation(
        tick=world.tick,
        ones=world.ones,
        density=world.density,
        local_entropy_bits=local_entropy_bits(world.grid),
        active_microstates=int(np.count_nonzero(hist)),
    )
