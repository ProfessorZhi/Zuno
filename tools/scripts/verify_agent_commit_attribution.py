from __future__ import annotations

import argparse
import re
import subprocess
import sys
from typing import List, Optional


ALLOWED_AGENTS = {
    "Antigravity",
    "Qoder",
    "Codex",
    "Trae",
    "ChatGPT-Docs",
    "Human",
}

ALLOWED_MODES = {
    "Standard-Conversation",
    "Expert-Team",
    "Codex",
    "Standard",
    "Docs-Maintenance",
    "Human",
}

BOT_AUTHORS = {
    "github-actions[bot]",
    "dependabot[bot]",
}


def run_git_command(args: List[str]) -> str:
    res = subprocess.run(
        ["git"] + args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )
    return res.stdout.strip()


def parse_commit_trailers(commit_msg: str) -> dict[str, str]:
    trailers: dict[str, str] = {}
    for line in commit_msg.splitlines():
        line = line.strip()
        if ":" in line:
            parts = line.split(":", 1)
            key = parts[0].strip()
            val = parts[1].strip()
            if key in (
                "Agent",
                "Agent-Mode",
                "Human-Owner",
                "Architecture-Reviewer",
                "Work-Package",
            ):
                trailers[key] = val
    return trailers


def verify_commit_attribution(
    base_sha: Optional[str] = None,
    head_sha: Optional[str] = None,
    allow_human_only: bool = False,
) -> bool:
    if not base_sha or not head_sha:
        # Default to previous commit if no range provided
        git_range = "HEAD~1..HEAD"
    else:
        git_range = f"{base_sha}..{head_sha}"

    try:
        commit_shas_str = run_git_command(["log", "--format=%H", git_range])
    except Exception as exc:
        print(f"Error fetching commit list for range {git_range}: {exc}", file=sys.stderr)
        return False

    if not commit_shas_str:
        print(f"No commits found in range {git_range}.")
        return True

    commit_shas = [c.strip() for c in commit_shas_str.splitlines() if c.strip()]
    errors: List[str] = []

    for sha in commit_shas:
        # Check parents to skip merge commits
        parents_str = run_git_command(["log", "--format=%P", "-n", "1", sha])
        parents = parents_str.split()
        if len(parents) > 1:
            continue  # Merge commit, skip

        author = run_git_command(["log", "--format=%an", "-n", "1", sha])
        if author in BOT_AUTHORS:
            continue  # Bot commit, skip

        commit_msg = run_git_command(["log", "--format=%B", "-n", "1", sha])
        trailers = parse_commit_trailers(commit_msg)

        if allow_human_only and trailers.get("Agent") == "Human":
            continue

        required_keys = ["Agent", "Agent-Mode", "Human-Owner", "Architecture-Reviewer", "Work-Package"]
        missing_keys = [k for k in required_keys if k not in trailers or not trailers[k]]

        if missing_keys:
            errors.append(f"Commit {sha[:8]} missing required trailers: {missing_keys}")
            continue

        agent = trailers["Agent"]
        mode = trailers["Agent-Mode"]

        if agent not in ALLOWED_AGENTS:
            errors.append(f"Commit {sha[:8]} has invalid Agent: '{agent}'. Allowed: {sorted(ALLOWED_AGENTS)}")
        if mode not in ALLOWED_MODES:
            errors.append(f"Commit {sha[:8]} has invalid Agent-Mode: '{mode}'. Allowed: {sorted(ALLOWED_MODES)}")

    if errors:
        print("Agent Commit Attribution Verification Failed:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return False

    print(f"Agent Commit Attribution Verification Passed for {len(commit_shas)} commit(s) in {git_range}.")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify Agent Commit Attribution Trailers")
    parser.add_argument("--base", help="Base commit SHA")
    parser.add_argument("--head", help="Head commit SHA")
    parser.add_argument("--allow-human-only", action="store_true", help="Allow human-only commits")

    args = parser.parse_args()

    # If base/head are not supplied in CI or local run, evaluate against origin/main if possible
    base = args.base
    head = args.head or "HEAD"
    if not base:
        try:
            base = run_git_command(["merge-base", "origin/main", head])
        except Exception:
            base = "HEAD~1"

    success = verify_commit_attribution(base, head, allow_human_only=args.allow_human_only)
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
