"""Fixed binary 2D universe with snapshot-based four-neighbor interactions."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .rule import V1_RULE, validate_rule


@dataclass(frozen=True, slots=True)
class StepStats:
    proposed: int
    accepted: int
    cancelled_conflicts: int


@dataclass(slots=True)
class BinaryWorld:
    """A toroidal fixed 2D binary lattice.

    Every tick is transactional:
    1. freeze the complete current grid as an immutable snapshot;
    2. every occupied center inspects its fixed up/right/down/left neighbors;
    3. each possible 1->0 adjacent exchange may become a proposal;
    4. cancel every proposal whose source or target is touched by another;
    5. commit all remaining disjoint exchanges simultaneously.

    Coordinates and adjacency never change.  No update can observe another
    update from the same tick.
    """

    grid: np.ndarray
    tick: int = 0

    # Clockwise order.  The rule itself is expressed in a target-relative frame,
    # so these absolute directions do not create four different physics laws.
    DIRECTIONS = ((-1, 0), (0, 1), (1, 0), (0, -1))

    def __post_init__(self) -> None:
        grid = np.asarray(self.grid, dtype=np.uint8)
        if grid.ndim != 2:
            raise ValueError("grid must be a 2D array")
        if grid.shape[0] < 3 or grid.shape[1] < 3:
            raise ValueError("world width and height must both be at least 3")
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
        if height < 3 or width < 3:
            raise ValueError("height and width must both be at least 3")
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

    @staticmethod
    def _neighbor(array: np.ndarray, dy: int, dx: int) -> np.ndarray:
        """Return the value at offset (dy, dx) aligned to each source site."""
        return np.roll(array, shift=(-dy, -dx), axis=(0, 1))

    @classmethod
    def _direction_proposals(
        cls,
        snapshot: np.ndarray,
        rule: np.ndarray,
        dy: int,
        dx: int,
    ) -> np.ndarray:
        """Return source-aligned proposals toward one orthogonal neighbor.

        The selected target is one of U/R/D/L.  The remaining three neighbors
        are rotated into a target-relative LEFT/BACK/RIGHT frame before the
        shared rule table is consulted.  This makes the microscopic mechanism
        rotationally consistent.
        """
        center = snapshot
        target = cls._neighbor(snapshot, dy, dx)

        # Rotate the other three offsets relative to the chosen forward target.
        left_dy, left_dx = -dx, dy
        back_dy, back_dx = -dy, -dx
        right_dy, right_dx = dx, -dy

        left = cls._neighbor(snapshot, left_dy, left_dx)
        back = cls._neighbor(snapshot, back_dy, back_dx)
        right = cls._neighbor(snapshot, right_dy, right_dx)

        context = (left << 2) | (back << 1) | right
        enabled = rule[context].astype(bool)

        # An elementary event is only a conservative exchange 1,0 -> 0,1.
        return (center == 1) & (target == 0) & enabled

    def step(self, rule: np.ndarray = V1_RULE) -> StepStats:
        """Advance one tick from a frozen snapshot and return interaction stats."""
        validate_rule(rule)
        snapshot = self.grid.copy()

        proposals: list[tuple[int, int, np.ndarray]] = []
        touch_count = np.zeros_like(snapshot, dtype=np.uint8)

        for dy, dx in self.DIRECTIONS:
            active = self._direction_proposals(snapshot, rule, dy, dx)
            proposals.append((dy, dx, active))

            # Each active proposal writes its source and its selected target.
            touch_count += active.astype(np.uint8)
            touch_count += np.roll(active, shift=(dy, dx), axis=(0, 1)).astype(np.uint8)

        next_grid = snapshot.copy()
        proposed = 0
        accepted = 0

        for dy, dx, active in proposals:
            proposed += int(active.sum())
            target_touch_count = self._neighbor(touch_count, dy, dx)
            accept = active & (touch_count == 1) & (target_touch_count == 1)
            accepted += int(accept.sum())

            # Accepted proposals are disjoint, so their writes cannot interfere.
            next_grid[accept] = 0
            target_accept = np.roll(accept, shift=(dy, dx), axis=(0, 1))
            next_grid[target_accept] = 1

        self.grid = next_grid
        self.tick += 1

        return StepStats(
            proposed=proposed,
            accepted=accepted,
            cancelled_conflicts=proposed - accepted,
        )

    def run(self, steps: int, rule: np.ndarray = V1_RULE) -> None:
        if steps < 0:
            raise ValueError("steps must be non-negative")
        for _ in range(steps):
            self.step(rule)

    def ascii(self) -> str:
        """Return a simple observer-side textual rendering."""
        return "\n".join("".join("█" if cell else "·" for cell in row) for row in self.grid)
