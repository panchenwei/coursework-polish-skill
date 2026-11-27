#!/usr/bin/env python3
"""Create non-submission control files for an assignment-polishing run."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


TEMPLATES = {
    "goal_state.json": {
        "user_outcome": "",
        "mode": "",
        "allowed_scope": [],
        "must_remain_unchanged": [],
        "official_target": "",
        "current_round": 0,
        "current_score_or_band": "",
        "hard_gates": {},
        "top_issue": "",
        "completion_condition": "",
        "blocker": None,
        "resume_step": "",
    },
    "scorecard.json": {
        "criteria": [],
        "hard_gates": {
            "course_intent": "NOT_VERIFIABLE",
            "correctness": "NOT_VERIFIABLE",
            "evidence": "NOT_VERIFIABLE",
            "citations": "NOT_VERIFIABLE",
            "cross_artifact_consistency": "NOT_VERIFIABLE",
            "ai_integrity": "NOT_VERIFIABLE",
            "submission_package": "NOT_VERIFIABLE",
        },
    },
    "iteration_log.json": {"rounds": []},
    "claim_evidence.json": {"claims": []},
    "submission_manifest.json": {
        "output_dir": "FINAL_SUBMISSION",
        "items": [],
    },
}


def initialize(root: Path, control_name: str) -> tuple[list[Path], list[Path]]:
    root = root.resolve()
    if not root.is_dir():
        raise ValueError(f"Project root does not exist or is not a directory: {root}")
    if Path(control_name).name != control_name or control_name in {"", ".", ".."}:
        raise ValueError("Control directory must be a single safe directory name")

    control = root / control_name
    control.mkdir(exist_ok=True)
    created: list[Path] = []
    skipped: list[Path] = []
    for name, payload in TEMPLATES.items():
        target = control / name
        if target.exists():
            skipped.append(target)
            continue
        target.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        created.append(target)
    return created, skipped


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Initialize assignment-polishing control files without overwriting existing work."
    )
    parser.add_argument("root", type=Path, help="Coursework project root")
    parser.add_argument(
        "--control-dir",
        default=".assignment-polishing",
        help="Internal control directory name (default: .assignment-polishing)",
    )
    args = parser.parse_args()
    try:
        created, skipped = initialize(args.root, args.control_dir)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))

    for path in created:
        print(f"CREATED {path}")
    for path in skipped:
        print(f"PRESERVED {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
