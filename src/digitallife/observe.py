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


def von_neumann_histogram(grid: np.ndarray) -> np.ndarray:
    """Count all 32 center+U/R/D/L local states on the toroidal lattice."""
    center = grid
    up = np.roll(grid, shift=1, axis=0)
    right = np.roll(grid, shift=-1, axis=1)
    down = np.roll(grid, shift=-1, axis=0)
    left = np.roll(grid, shift=1, axis=1)

    states = (
        (center << 4)
        | (up << 3)
        | (right << 2)
        | (down << 1)
        | left
    ).ravel()
    return np.bincount(states, minlength=32)


def local_entropy_bits(grid: np.ndarray) -> float:
    """Shannon entropy of fixed four-neighbor microstate frequencies, in bits."""
    counts = von_neumann_histogram(grid)
    total = counts.sum()
    if total == 0:
        return 0.0
    p = counts[counts > 0] / total
    return float(-(p * np.log2(p)).sum())


def observe(world: BinaryWorld) -> Observation:
    hist = von_neumann_histogram(world.grid)
    return Observation(
        tick=world.tick,
        ones=world.ones,
        density=world.density,
        local_entropy_bits=local_entropy_bits(world.grid),
        active_microstates=int(np.count_nonzero(hist)),
    )
