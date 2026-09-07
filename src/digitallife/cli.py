"""Command-line runner for DigitalLife V1."""

from __future__ import annotations

import argparse

from .observe import observe
from .world import BinaryWorld, StepStats


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the DigitalLife V1 universe")
    parser.add_argument("--width", type=int, default=128)
    parser.add_argument("--height", type=int, default=128)
    parser.add_argument("--density", type=float, default=0.20)
    parser.add_argument("--steps", type=int, default=10_000)
    parser.add_argument("--report-every", type=int, default=100)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--ascii", action="store_true", dest="show_ascii")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.report_every <= 0:
        raise SystemExit("--report-every must be positive")

    world = BinaryWorld.random(
        height=args.height,
        width=args.width,
        density=args.density,
        seed=args.seed,
    )

    initial_ones = world.ones
    last_stats = StepStats(proposed=0, accepted=0, cancelled_conflicts=0)

    def report() -> None:
        obs = observe(world)
        print(
            f"tick={obs.tick} "
            f"ones={obs.ones} "
            f"density={obs.density:.6f} "
            f"local_entropy={obs.local_entropy_bits:.6f} "
            f"active_microstates={obs.active_microstates}/32 "
            f"proposed={last_stats.proposed} "
            f"accepted={last_stats.accepted} "
            f"conflicts={last_stats.cancelled_conflicts}"
        )
        if args.show_ascii:
            print(world.ascii())
            print()

    report()
    for _ in range(args.steps):
        last_stats = world.step()
        if world.ones != initial_ones:
            raise RuntimeError("V1 conservation invariant violated: number of 1 bits changed")
        if world.tick % args.report_every == 0:
            report()

    if world.tick % args.report_every != 0:
        report()


if __name__ == "__main__":
    main()
