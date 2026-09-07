"""Exhaustive rule search for the DigitalLife V1 universe.

This module does not score "life" or "intelligence".  It only measures
low-level dynamical properties so that trivial/frozen rule tables can be
separated from rules that sustain activity and local structural diversity.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .observe import observe
from .rule import rule_from_mask
from .world import BinaryWorld


@dataclass(frozen=True, slots=True)
class RuleResult:
    mask: int
    mean_activity: float
    tail_activity: float
    mean_proposals: float
    conflict_fraction: float
    final_local_entropy: float
    final_active_microstates: float
    frozen_runs: int
    runs: int


def evaluate_rule(
    mask: int,
    *,
    width: int,
    height: int,
    density: float,
    steps: int,
    seeds: tuple[int, ...],
    tail_window: int,
) -> RuleResult:
    """Evaluate one legal rule over several independent random worlds."""
    if tail_window <= 0 or tail_window > steps:
        raise ValueError("tail_window must be in [1, steps]")

    rule = rule_from_mask(mask)
    cell_count = width * height

    mean_activity: list[float] = []
    tail_activity: list[float] = []
    mean_proposals: list[float] = []
    conflicts: list[float] = []
    entropies: list[float] = []
    microstates: list[float] = []
    frozen_runs = 0

    for seed in seeds:
        world = BinaryWorld.random(
            height=height,
            width=width,
            density=density,
            seed=seed,
        )
        initial_ones = world.ones
        accepted_history: list[int] = []
        proposed_history: list[int] = []

        for _ in range(steps):
            stats = world.step(rule)
            accepted_history.append(stats.accepted)
            proposed_history.append(stats.proposed)

        if world.ones != initial_ones:
            raise RuntimeError(f"rule {mask} violated 1-bit conservation")

        total_proposed = sum(proposed_history)
        total_accepted = sum(accepted_history)
        tail_accepted = sum(accepted_history[-tail_window:])
        obs = observe(world)

        mean_activity.append(total_accepted / (steps * cell_count))
        tail_activity.append(tail_accepted / (tail_window * cell_count))
        mean_proposals.append(total_proposed / (steps * cell_count))
        conflicts.append(
            0.0 if total_proposed == 0 else 1.0 - total_accepted / total_proposed
        )
        entropies.append(obs.local_entropy_bits)
        microstates.append(float(obs.active_microstates))
        if tail_accepted == 0:
            frozen_runs += 1

    return RuleResult(
        mask=mask,
        mean_activity=float(np.mean(mean_activity)),
        tail_activity=float(np.mean(tail_activity)),
        mean_proposals=float(np.mean(mean_proposals)),
        conflict_fraction=float(np.mean(conflicts)),
        final_local_entropy=float(np.mean(entropies)),
        final_active_microstates=float(np.mean(microstates)),
        frozen_runs=frozen_runs,
        runs=len(seeds),
    )


def search_all(
    *,
    width: int,
    height: int,
    density: float,
    steps: int,
    seeds: tuple[int, ...],
    tail_window: int,
) -> list[RuleResult]:
    """Evaluate all 256 conservative V1 rules."""
    results = [
        evaluate_rule(
            mask,
            width=width,
            height=height,
            density=density,
            steps=steps,
            seeds=seeds,
            tail_window=tail_window,
        )
        for mask in range(256)
    ]

    # Do not pretend that one scalar means "best universe".  First prefer
    # sustained activity, then average activity, then local diversity.
    results.sort(
        key=lambda r: (
            r.tail_activity,
            r.mean_activity,
            r.final_active_microstates,
            r.final_local_entropy,
        ),
        reverse=True,
    )
    return results


def write_csv(results: list[RuleResult], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(RuleResult.__dataclass_fields__))
        writer.writeheader()
        for result in results:
            writer.writerow({name: getattr(result, name) for name in writer.fieldnames})


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Search all 256 DigitalLife V1 rules")
    parser.add_argument("--width", type=int, default=32)
    parser.add_argument("--height", type=int, default=32)
    parser.add_argument("--density", type=float, default=0.20)
    parser.add_argument("--steps", type=int, default=100)
    parser.add_argument("--tail-window", type=int, default=25)
    parser.add_argument("--seeds", type=int, nargs="+", default=[1, 7, 19])
    parser.add_argument("--top", type=int, default=20)
    parser.add_argument("--csv", type=Path, default=Path("results/rule_scan.csv"))
    return parser


def main() -> None:
    args = build_parser().parse_args()
    results = search_all(
        width=args.width,
        height=args.height,
        density=args.density,
        steps=args.steps,
        seeds=tuple(args.seeds),
        tail_window=args.tail_window,
    )
    write_csv(results, args.csv)

    print(
        "rank mask tail_activity mean_activity proposal conflict "
        "entropy states frozen"
    )
    for rank, result in enumerate(results[: args.top], start=1):
        print(
            f"{rank:4d} {result.mask:4d} "
            f"{result.tail_activity:.8f} {result.mean_activity:.8f} "
            f"{result.mean_proposals:.8f} {result.conflict_fraction:.6f} "
            f"{result.final_local_entropy:.6f} "
            f"{result.final_active_microstates:.2f} "
            f"{result.frozen_runs}/{result.runs}"
        )

    frozen_all = sum(result.frozen_runs == result.runs for result in results)
    print(f"fully_frozen_rules={frozen_all}/256")
    print(f"csv={args.csv}")


if __name__ == "__main__":
    main()
