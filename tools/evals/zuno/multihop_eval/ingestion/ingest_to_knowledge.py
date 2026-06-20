from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Preview benchmark corpus ingestion payloads for future Zuno knowledge import.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--knowledge-name", required=True)
    args = parser.parse_args()

    print(
        json.dumps(
            {
                "status": "not_implemented",
                "knowledge_name": args.knowledge_name,
                "input": str(args.input),
                "message": "Use benchmark-corpus-ingestion-plan.md for the current recommended ingestion path.",
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
