#!/usr/bin/env python3
"""Validate this skill repository's structure, links and Python tools."""

from __future__ import annotations

import py_compile
import re
import sys
from pathlib import Path


REQUIRED_REFERENCES = {
    f"references/{number:02d}-{name}.md"
    for number, name in (
        (1, "authority-and-control"),
        (2, "code-iteration"),
        (3, "experiment-and-evidence"),
        (4, "report-polish"),
        (5, "document-and-presentation"),
        (6, "submission-and-review"),
        (7, "cpt204-lessons"),
        (8, "templates"),
        (9, "full-score-iteration"),
        (10, "ai-instruction-and-trace-audit"),
        (11, "figgenie-integration"),
    )
}
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    skill = root / "SKILL.md"
    if not skill.is_file():
        return ["SKILL.md is missing"]
    text = skill.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "name: assignment-polishing" not in text:
        errors.append("SKILL.md frontmatter is missing the expected name")
    if "description:" not in text.split("---", 2)[1]:
        errors.append("SKILL.md frontmatter description is missing")

    for relative in sorted(REQUIRED_REFERENCES):
        if not (root / relative).is_file():
            errors.append(f"required reference missing: {relative}")

    markdown_files = [skill, *sorted((root / "references").glob("*.md"))]
    for markdown in markdown_files:
        body = markdown.read_text(encoding="utf-8")
        for match in LINK_RE.finditer(body):
            target = match.group(1).split("#", 1)[0].strip()
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            resolved = (markdown.parent / target).resolve()
            if not resolved.exists():
                errors.append(
                    f"broken link in {markdown.relative_to(root)}: {match.group(1)}"
                )

    openai_yaml = root / "agents" / "openai.yaml"
    if not openai_yaml.is_file():
        errors.append("agents/openai.yaml is missing")
    elif "$assignment-polishing" not in openai_yaml.read_text(encoding="utf-8"):
        errors.append("agents/openai.yaml default prompt must mention $assignment-polishing")

    for script in sorted((root / "scripts").glob("*.py")):
        try:
            py_compile.compile(str(script), doraise=True)
        except py_compile.PyCompileError as exc:
            errors.append(f"Python compile failed for {script.name}: {exc.msg}")
    return errors


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    errors = validate(root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Repository validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
