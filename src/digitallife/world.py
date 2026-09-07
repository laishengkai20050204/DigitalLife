"""Binary 2D universe with alternating Margolus block updates."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .rule import V0_RULE, validate_rule


@dataclass(slots=True)
class BinaryWorld:
    """A toroidal 2D binary lattice.

    The world contains no object model for particles or organisms. Its complete
    physical state is the binary grid plus the current partition phase.
    """

    grid: np.ndarray
    tick: int = 0

    def __post_init__(self) -> None:
        grid = np.asarray(self.grid, dtype=np.uint8)
        if grid.ndim != 2:
            raise ValueError("grid must be a 2D array")
        if grid.shape[0] % 2 or grid.shape[1] % 2:
            raise ValueError("world width and height must both be even")
        if not np.all((grid == 0) | (grid == 1)):
            raise ValueError("grid must contain only 0 and 1")
        self.grid = grid.copy()

    @classmethod
    def random(
        cls,
        height: int,
        width: int,
        density: float = 0.2,
        seed: int | None = None,
    ) -> "BinaryWorld":
        if height <= 0 or width <= 0 or height % 2 or width % 2:
            raise ValueError("height and width must be positive even integers")
        if not 0.0 <= density <= 1.0:
            raise ValueError("density must be between 0 and 1")

        rng = np.random.default_rng(seed)
        grid = (rng.random((height, width)) < density).astype(np.uint8)
        return cls(grid=grid)

    @property
    def ones(self) -> int:
        return int(self.grid.sum())

    @property
    def density(self) -> float:
        return float(self.grid.mean())

    def step(self, rule: np.ndarray = V0_RULE) -> None:
        """Advance the universe by one tick using only local 2x2 updates."""
        validate_rule(rule)
        phase = self.tick & 1

        # Move the active Margolus partition to the origin. np.roll makes the
        # world toroidal, so no cell receives special boundary behavior.
        shifted = np.roll(self.grid, shift=(-phase, -phase), axis=(0, 1))

        tl = shifted[0::2, 0::2]
        tr = shifted[0::2, 1::2]
        bl = shifted[1::2, 0::2]
        br = shifted[1::2, 1::2]

        states = (tl << 3) | (tr << 2) | (bl << 1) | br
        outputs = rule[states]

        next_shifted = np.empty_like(shifted)
        next_shifted[0::2, 0::2] = (outputs >> 3) & 1
        next_shifted[0::2, 1::2] = (outputs >> 2) & 1
        next_shifted[1::2, 0::2] = (outputs >> 1) & 1
        next_shifted[1::2, 1::2] = outputs & 1

        self.grid = np.roll(next_shifted, shift=(phase, phase), axis=(0, 1))
        self.tick += 1

    def run(self, steps: int, rule: np.ndarray = V0_RULE) -> None:
        if steps < 0:
            raise ValueError("steps must be non-negative")
        for _ in range(steps):
            self.step(rule)

    def ascii(self) -> str:
        """Return a simple observer-side textual rendering."""
        return "\n".join("".join("█" if cell else "·" for cell in row) for row in self.grid)
