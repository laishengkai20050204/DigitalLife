"""Fixed binary 2D universe with snapshot-based adjacent interactions."""

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
    1. freeze the current grid as an immutable snapshot;
    2. evaluate every horizontal and vertical adjacent interaction from it;
    3. cancel every active proposal that shares a written cell with another;
    4. commit the remaining disjoint proposals simultaneously.

    No repartitioning occurs and no update can observe another update from the
    same tick.
    """

    grid: np.ndarray
    tick: int = 0

    def __post_init__(self) -> None:
        grid = np.asarray(self.grid, dtype=np.uint8)
        if grid.ndim != 2:
            raise ValueError("grid must be a 2D array")
        if grid.shape[0] <= 0 or grid.shape[1] <= 0:
            raise ValueError("world width and height must be positive")
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
        if height <= 0 or width <= 0:
            raise ValueError("height and width must be positive integers")
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
    def _edge_proposals(
        snapshot: np.ndarray,
        rule: np.ndarray,
        axis: int,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Evaluate every directed +axis adjacent edge from one snapshot.

        For each anchor A, B is the next cell in the positive axis direction.
        L and R are one cell behind A and one cell beyond B.  The same 16-entry
        rule is used for horizontal and vertical edges, so the mechanism itself
        does not require separate x/y physics tables.
        """
        left = np.roll(snapshot, shift=1, axis=axis)
        a = snapshot
        b = np.roll(snapshot, shift=-1, axis=axis)
        right = np.roll(snapshot, shift=-2, axis=axis)

        context = (left << 3) | (a << 2) | (b << 1) | right
        out = rule[context]
        out_a = (out >> 1) & 1
        out_b = out & 1
        active = (out_a != a) | (out_b != b)
        return active, out_a, out_b

    def step(self, rule: np.ndarray = V1_RULE) -> StepStats:
        """Advance one tick from a frozen snapshot and return interaction stats."""
        validate_rule(rule)
        snapshot = self.grid.copy()

        h_active, h_out_a, h_out_b = self._edge_proposals(snapshot, rule, axis=1)
        v_active, v_out_a, v_out_b = self._edge_proposals(snapshot, rule, axis=0)

        # Every active edge wants to write both of its endpoints.  Count how
        # many active proposals touch each site.  Snapshot reads never conflict;
        # only overlapping writes do.
        touch_count = (
            h_active.astype(np.uint8)
            + np.roll(h_active, shift=1, axis=1).astype(np.uint8)
            + v_active.astype(np.uint8)
            + np.roll(v_active, shift=1, axis=0).astype(np.uint8)
        )

        h_accept = (
            h_active
            & (touch_count == 1)
            & (np.roll(touch_count, shift=-1, axis=1) == 1)
        )
        v_accept = (
            v_active
            & (touch_count == 1)
            & (np.roll(touch_count, shift=-1, axis=0) == 1)
        )

        next_grid = snapshot.copy()

        # Horizontal A endpoints.
        next_grid[h_accept] = h_out_a[h_accept]
        # Horizontal B endpoints: shift anchor-aligned outputs onto B sites.
        h_b_accept = np.roll(h_accept, shift=1, axis=1)
        h_b_values = np.roll(h_out_b, shift=1, axis=1)
        next_grid[h_b_accept] = h_b_values[h_b_accept]

        # Vertical A endpoints.
        next_grid[v_accept] = v_out_a[v_accept]
        # Vertical B endpoints.
        v_b_accept = np.roll(v_accept, shift=1, axis=0)
        v_b_values = np.roll(v_out_b, shift=1, axis=0)
        next_grid[v_b_accept] = v_b_values[v_b_accept]

        proposed = int(h_active.sum() + v_active.sum())
        accepted = int(h_accept.sum() + v_accept.sum())

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
