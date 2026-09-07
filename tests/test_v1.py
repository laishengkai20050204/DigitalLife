import unittest

import numpy as np

from digitallife.rule import V1_RULE, conservative_rules, rule_from_mask, validate_rule
from digitallife.world import BinaryWorld


class V1RuleTests(unittest.TestCase):
    def test_baseline_rule_is_valid(self) -> None:
        validate_rule(V1_RULE)

    def test_complete_conservative_rule_space_has_256_unique_rules(self) -> None:
        rules = list(conservative_rules())
        self.assertEqual(len(rules), 256)
        self.assertEqual(len({tuple(int(x) for x in rule) for rule in rules}), 256)
        for rule in rules:
            validate_rule(rule)

    def test_mask_zero_never_proposes(self) -> None:
        np.testing.assert_array_equal(rule_from_mask(0), np.zeros(8, dtype=np.uint8))

    def test_mask_255_proposes_in_every_relative_context(self) -> None:
        np.testing.assert_array_equal(rule_from_mask(255), np.ones(8, dtype=np.uint8))


class WorldTests(unittest.TestCase):
    def test_random_world_conserves_ones(self) -> None:
        world = BinaryWorld.random(height=31, width=33, density=0.31, seed=7)
        initial = world.ones
        world.run(1000)
        self.assertEqual(world.ones, initial)

    def test_deterministic_with_same_seed(self) -> None:
        a = BinaryWorld.random(height=17, width=19, density=0.2, seed=42)
        b = BinaryWorld.random(height=17, width=19, density=0.2, seed=42)
        a.run(100)
        b.run(100)
        np.testing.assert_array_equal(a.grid, b.grid)

    def test_world_has_fixed_four_neighbors(self) -> None:
        world = BinaryWorld.random(height=15, width=17, density=0.2, seed=1)
        self.assertEqual(world.grid.shape, (15, 17))
        self.assertEqual(set(world.DIRECTIONS), {(-1, 0), (0, 1), (1, 0), (0, -1)})

    def test_overlapping_snapshot_proposals_are_cancelled(self) -> None:
        grid = np.zeros((5, 5), dtype=np.uint8)
        grid[2, 2] = 1
        world = BinaryWorld(grid)

        # With every relative context enabled, the isolated center proposes to
        # all four empty neighbors.  All four proposals share the same source,
        # so all are cancelled instead of choosing an arbitrary direction.
        stats = world.step(rule_from_mask(255))

        np.testing.assert_array_equal(world.grid, grid)
        self.assertEqual(stats.proposed, 4)
        self.assertEqual(stats.accepted, 0)
        self.assertEqual(stats.cancelled_conflicts, 4)

    def test_step_reads_only_snapshot(self) -> None:
        grid = np.array(
            [
                [0, 0, 0, 0, 0],
                [0, 1, 0, 1, 0],
                [0, 0, 1, 0, 0],
                [0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0],
            ],
            dtype=np.uint8,
        )
        a = BinaryWorld(grid)
        b = BinaryWorld(grid.copy())
        a.step(V1_RULE)
        b.step(V1_RULE)
        np.testing.assert_array_equal(a.grid, b.grid)

    def test_physics_is_rotation_equivariant(self) -> None:
        grid = np.array(
            [
                [0, 0, 1, 0, 0, 0, 0],
                [0, 1, 1, 0, 1, 0, 0],
                [0, 0, 0, 1, 0, 0, 0],
                [1, 0, 1, 0, 0, 1, 0],
                [0, 0, 0, 0, 1, 0, 0],
                [0, 1, 0, 0, 0, 0, 1],
                [0, 0, 0, 1, 0, 0, 0],
            ],
            dtype=np.uint8,
        )
        rule = rule_from_mask(173)

        original = BinaryWorld(grid)
        rotated = BinaryWorld(np.rot90(grid))
        original.step(rule)
        rotated.step(rule)

        np.testing.assert_array_equal(rotated.grid, np.rot90(original.grid))


if __name__ == "__main__":
    unittest.main()
