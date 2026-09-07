import unittest

import numpy as np

from digitallife.rule import V0_RULE, bit_count, validate_rule
from digitallife.world import BinaryWorld


class V0RuleTests(unittest.TestCase):
    def test_rule_is_valid(self) -> None:
        validate_rule(V0_RULE)

    def test_rule_is_involutive(self) -> None:
        for state in range(16):
            self.assertEqual(int(V0_RULE[int(V0_RULE[state])]), state)

    def test_rule_conserves_ones(self) -> None:
        for state in range(16):
            self.assertEqual(bit_count(state), bit_count(int(V0_RULE[state])))


class WorldTests(unittest.TestCase):
    def test_random_world_conserves_ones(self) -> None:
        world = BinaryWorld.random(height=32, width=32, density=0.31, seed=7)
        initial = world.ones
        world.run(1000)
        self.assertEqual(world.ones, initial)

    def test_deterministic_with_same_seed(self) -> None:
        a = BinaryWorld.random(height=16, width=16, density=0.2, seed=42)
        b = BinaryWorld.random(height=16, width=16, density=0.2, seed=42)
        a.run(100)
        b.run(100)
        np.testing.assert_array_equal(a.grid, b.grid)

    def test_even_dimensions_required(self) -> None:
        with self.assertRaises(ValueError):
            BinaryWorld.random(height=15, width=16)


if __name__ == "__main__":
    unittest.main()
