#!/usr/bin/env python3
"""Build or audit an exact-whitelist final submission directory."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import uuid
from pathlib import Path, PurePosixPath
from typing import Any


FORBIDDEN_PARTS = {
    ".git",
    ".idea",
    ".vscode",
    "__macosx",
    "__pycache__",
    "node_modules",
}
FORBIDDEN_NAMES = {".ds_store", "thumbs.db", ".env"}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo", ".tmp", ".bak", ".swp"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def safe_destination(value: str) -> PurePosixPath:
    destination = PurePosixPath(value.replace("\\", "/"))
    if not value or destination.is_absolute() or ".." in destination.parts:
        raise ValueError(f"Unsafe destination path: {value!r}")
    for part in destination.parts:
        lowered = part.lower()
        if lowered in FORBIDDEN_PARTS or lowered in FORBIDDEN_NAMES:
            raise ValueError(f"Forbidden submission path component: {part}")
        if lowered.startswith("~$") or Path(lowered).suffix in FORBIDDEN_SUFFIXES:
            raise ValueError(f"Forbidden temporary/internal file: {part}")
    return destination


def load_manifest(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("items"), list):
        raise ValueError("Manifest must be an object with an items list")
    output_dir = data.get("output_dir", "FINAL_SUBMISSION")
    safe_destination(str(output_dir))
    return data


def resolve_items(root: Path, manifest: dict[str, Any]) -> list[dict[str, Any]]:
    root = root.resolve()
    resolved: list[dict[str, Any]] = []
    destinations: set[str] = set()
    for index, item in enumerate(manifest["items"]):
        if not isinstance(item, dict):
            raise ValueError(f"items[{index}] must be an object")
        source_text = item.get("source")
        destination_text = item.get("destination")
        if not isinstance(source_text, str) or not isinstance(destination_text, str):
            raise ValueError(f"items[{index}] requires source and destination strings")
        source = (root / source_text).resolve()
        if not _within(source, root):
            raise ValueError(f"Source escapes project root: {source_text}")
        destination = safe_destination(destination_text)
        destination_key = destination.as_posix().casefold()
        if destination_key in destinations:
            raise ValueError(f"Duplicate destination: {destination}")
        destinations.add(destination_key)
        required = bool(item.get("required", True))
        if not source.exists():
            if required:
                raise FileNotFoundError(f"Required source is missing: {source_text}")
            continue
        if not source.is_file():
            raise ValueError(
                f"Manifest sources must be files, not directories: {source_text}. "
                "List each submitted file explicitly."
            )
        resolved.append(
            {
                "source": source,
                "source_relative": source.relative_to(root).as_posix(),
                "destination": destination,
            }
        )
    return resolved


def expected_map(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {item["destination"].as_posix(): item for item in items}


def audit(output: Path, items: list[dict[str, Any]]) -> dict[str, Any]:
    expected = expected_map(items)
    actual_paths = sorted(
        path.relative_to(output).as_posix()
        for path in output.rglob("*")
        if path.is_file()
    )
    actual = set(actual_paths)
    expected_paths = set(expected)
    missing = sorted(expected_paths - actual)
    extra = sorted(actual - expected_paths)
    files = []
    for relative in sorted(actual & expected_paths):
        path = output / Path(relative)
        files.append(
            {
                "path": relative,
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
                "source": expected[relative]["source_relative"],
            }
        )
    return {
        "valid": not missing and not extra,
        "output_dir": str(output),
        "missing": missing,
        "extra": extra,
        "files": files,
    }


def build(root: Path, manifest_path: Path, audit_only: bool = False) -> dict[str, Any]:
    root = root.resolve()
    if not root.is_dir():
        raise ValueError(f"Project root is not a directory: {root}")
    manifest = load_manifest(manifest_path)
    items = resolve_items(root, manifest)
    output_rel = safe_destination(str(manifest.get("output_dir", "FINAL_SUBMISSION")))
    output = (root / Path(output_rel.as_posix())).resolve()
    if not _within(output, root) or output == root:
        raise ValueError("Output directory must be a child of the project root")

    if audit_only:
        if not output.is_dir():
            raise FileNotFoundError(f"Submission directory does not exist: {output}")
        return audit(output, items)

    if output.exists():
        raise FileExistsError(
            f"Refusing to overwrite existing submission directory: {output}. "
            "Archive or remove it explicitly, then rebuild."
        )

    staging = output.parent / f".{output.name}.staging-{uuid.uuid4().hex}"
    staging.mkdir(parents=False)
    try:
        for item in items:
            destination = staging / Path(item["destination"].as_posix())
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item["source"], destination)
        result = audit(staging, items)
        if not result["valid"]:
            raise RuntimeError(f"Staging audit failed: {result}")
        staging.rename(output)
        result = audit(output, items)
    except Exception:
        if staging.exists():
            shutil.rmtree(staging)
        raise
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True, help="Coursework root")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--audit-only", action="store_true")
    parser.add_argument(
        "--audit-report",
        type=Path,
        help="External audit JSON path; defaults beside the submission directory",
    )
    args = parser.parse_args()
    try:
        result = build(args.root, args.manifest, args.audit_only)
        report = args.audit_report
        if report is None:
            output_name = Path(result["output_dir"]).name
            report = args.root.resolve() / f"{output_name}.audit.json"
        report = report.resolve()
        output = Path(result["output_dir"]).resolve()
        if _within(report, output):
            raise ValueError("Audit report must remain outside the submission directory")
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"AUDIT_REPORT {report}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
