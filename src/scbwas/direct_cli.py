from __future__ import annotations

import argparse
import json
from pathlib import Path

from .direct_fluid import run_direct_fluid_machine
from .fluid_backreaction import FluidConfig


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run SELECT-CARRY-BIND-WRITE-ASK-SELECT with the fluid memory itself as operator"
    )
    parser.add_argument("--fluid-grid", type=int, default=24)
    parser.add_argument("--fluid-train", type=int, default=210)
    parser.add_argument("--fluid-washout", type=int, default=700)
    parser.add_argument("--recall-steps", type=int, default=250)
    # Kept only so old CI/user commands remain source-compatible. The direct
    # fluid machine has no finite modal state-space dimension or cycle count.
    parser.add_argument("--space", type=int, default=256, help=argparse.SUPPRESS)
    parser.add_argument("--cycles", type=int, default=28, help=argparse.SUPPRESS)
    parser.add_argument("--out", type=Path, default=Path("results/direct_fluid.json"))
    args = parser.parse_args()

    config = FluidConfig(
        n=args.fluid_grid,
        train_steps=args.fluid_train,
        washout_steps=args.fluid_washout,
    )
    receipt = run_direct_fluid_machine(
        fluid_config=config,
        recall_steps=args.recall_steps,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
