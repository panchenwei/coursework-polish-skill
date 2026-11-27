#!/usr/bin/env python3
"""Validate an evidence-backed official rubric scorecard."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


STATUSES = {
    "PASS",
    "PARTIAL",
    "FAIL",
    "NOT_VERIFIABLE",
    "NOT_APPLICABLE",
    "STALE",
    "CONFLICT",
}
REQUIRED_FIELDS = {
    "id",
    "official_quote",
    "authority",
    "locator",
    "max_score",
    "current_score",
    "highest_band",
    "status",
    "evidence",
    "root_cause",
    "next_action",
}


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate(data: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    criteria = data.get("criteria")
    if not isinstance(criteria, list):
        return {"valid": False, "errors": ["criteria must be a list"]}

    seen: set[str] = set()
    total_max = 0.0
    total_current = 0.0
    for index, item in enumerate(criteria):
        label = f"criteria[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be an object")
            continue
        missing = REQUIRED_FIELDS - item.keys()
        if missing:
            errors.append(f"{label} missing: {', '.join(sorted(missing))}")
            continue

        criterion_id = str(item["id"]).strip()
        if not criterion_id:
            errors.append(f"{label}.id must be non-empty")
        elif criterion_id in seen:
            errors.append(f"duplicate criterion id: {criterion_id}")
        seen.add(criterion_id)

        for field in ("official_quote", "authority", "locator", "highest_band"):
            if not _nonempty(item[field]):
                errors.append(f"{label}.{field} must be non-empty")

        try:
            max_score = float(item["max_score"])
            current_score = float(item["current_score"])
        except (TypeError, ValueError):
            errors.append(f"{label} scores must be numeric")
            continue
        if max_score < 0 or current_score < 0 or current_score > max_score:
            errors.append(f"{label} requires 0 <= current_score <= max_score")
        total_max += max_score
        total_current += current_score

        status = item["status"]
        if status not in STATUSES:
            errors.append(f"{label}.status is invalid: {status}")
        evidence = item["evidence"]
        if not isinstance(evidence, list):
            errors.append(f"{label}.evidence must be a list")
        elif current_score > 0 and not any(_nonempty(entry) for entry in evidence):
            errors.append(f"{label} has positive score without direct evidence")
        if status == "PASS" and current_score != max_score:
            errors.append(f"{label} marked PASS but is not at maximum score")
        if status == "NOT_APPLICABLE" and current_score != 0:
            errors.append(f"{label} marked NOT_APPLICABLE must score 0")

    hard_gates = data.get("hard_gates", {})
    if not isinstance(hard_gates, dict):
        errors.append("hard_gates must be an object")
        hard_gates = {}
    invalid_gates = {
        key: value for key, value in hard_gates.items() if value not in STATUSES
    }
    for key, value in invalid_gates.items():
        errors.append(f"hard_gates.{key} is invalid: {value}")

    criteria_ready = bool(criteria) and all(
        isinstance(item, dict)
        and item.get("status") in {"PASS", "NOT_APPLICABLE"}
        for item in criteria
    )
    gates_ready = bool(hard_gates) and all(
        value in {"PASS", "NOT_APPLICABLE"} for value in hard_gates.values()
    )
    return {
        "valid": not errors,
        "errors": errors,
        "total_current": total_current,
        "total_max": total_max,
        "highest_band_ready": not errors and criteria_ready and gates_ready,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scorecard", type=Path)
    parser.add_argument("--json", action="store_true", help="Emit JSON summary")
    args = parser.parse_args()
    try:
        data = json.loads(args.scorecard.read_text(encoding="utf-8"))
        result = validate(data)
    except (OSError, json.JSONDecodeError) as exc:
        parser.error(str(exc))

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Score: {result['total_current']:g}/{result['total_max']:g}")
        print(f"Highest-band ready: {result['highest_band_ready']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
