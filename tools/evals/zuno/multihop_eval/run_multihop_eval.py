from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Placeholder multi-hop eval runner for Phase D.")
    parser.add_argument("--dataset", required=True, choices=["hotpotqa", "twowiki", "musique"])
    parser.add_argument("--mode", required=True, choices=["baseline_rag", "local_graphrag", "deep_graphrag"])
    parser.add_argument("--split", default="dev")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--input", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=Path("reports/evals/multihop"))
    args = parser.parse_args()
    raise SystemExit(
        json.dumps(
            {
                "status": "not_implemented_until_phase_d",
                "dataset": args.dataset,
                "mode": args.mode,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()

