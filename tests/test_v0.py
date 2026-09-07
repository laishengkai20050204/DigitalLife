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

    def test_mask_zero_is_identity_on_selected_pair(self) -> None:
        rule = rule_from_mask(0)
        for state in range(16):
            pair = (((state >> 2) & 1) << 1) | ((state >> 1) & 1)
            self.assertEqual(int(rule[state]), pair)


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

    def test_no_even_dimension_requirement(self) -> None:
        world = BinaryWorld.random(height=15, width=17, density=0.2, seed=1)
        self.assertEqual(world.grid.shape, (15, 17))

    def test_overlapping_snapshot_proposals_are_cancelled(self) -> None:
        # Rule 255 swaps every mixed adjacent pair.  A single isolated 1 would
        # simultaneously propose swaps with all four empty neighbours.  Those
        # writes overlap at the center, so all four proposals must be cancelled.
        grid = np.zeros((5, 5), dtype=np.uint8)
        grid[2, 2] = 1
        world = BinaryWorld(grid)
        stats = world.step(rule_from_mask(255))
        np.testing.assert_array_equal(world.grid, grid)
        self.assertEqual(stats.proposed, 4)
        self.assertEqual(stats.accepted, 0)
        self.assertEqual(stats.cancelled_conflicts, 4)

    def test_step_reads_only_snapshot(self) -> None:
        # Determinism here also guards against in-place scan-order updates.
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


if __name__ == "__main__":
    unittest.main()
