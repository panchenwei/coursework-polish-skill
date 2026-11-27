#!/usr/bin/env python3
"""Install assignment-polishing and optionally ensure FigGenie is available."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


FIGGENIE_REPO = "https://github.com/Sleepy-Avacado/FigGenie-paper-diagram-skill.git"
MAIN_ENTRIES = ("SKILL.md", "README.md", "agents", "references", "scripts")


def figgenie_dependency_status() -> dict[str, object]:
    required = {"lxml": "lxml", "Pillow": "PIL", "playwright": "playwright"}
    optional = {"fontTools": "fontTools", "python-pptx": "pptx"}
    missing_required = [
        label for label, module in required.items() if importlib.util.find_spec(module) is None
    ]
    missing_optional = [
        label for label, module in optional.items() if importlib.util.find_spec(module) is None
    ]
    return {
        "missing_required_python_packages": missing_required,
        "missing_optional_python_packages": missing_optional,
        "chromium_note": "Run 'playwright install chromium' if FigGenie rendering reports no browser.",
    }


def find_system_chromium() -> Path | None:
    configured = os.environ.get("FIGGENIE_CHROMIUM")
    if configured and Path(configured).is_file():
        return Path(configured)
    candidates = []
    if os.name == "nt":
        candidates = [
            Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
            Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
            Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
            Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        ]
    elif sys.platform == "darwin":
        candidates = [
            Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
            Path("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
        ]
    else:
        for executable in ("google-chrome", "chromium", "chromium-browser", "microsoft-edge"):
            found = shutil.which(executable)
            if found:
                candidates.append(Path(found))
    return next((path for path in candidates if path.is_file()), None)


def configure_figgenie_browser() -> dict[str, str | None]:
    browser = find_system_chromium()
    if browser is None:
        return {
            "status": "not-found",
            "path": None,
            "next_action": "Run 'python -m playwright install chromium'.",
        }
    os.environ["FIGGENIE_CHROMIUM"] = str(browser)
    if os.name == "nt":
        import winreg

        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            winreg.SetValueEx(
                key, "FIGGENIE_CHROMIUM", 0, winreg.REG_SZ, str(browser)
            )
        status = "configured-user-environment"
    else:
        status = "available-for-current-process"
    return {"status": status, "path": str(browser), "next_action": None}


def install_figgenie_dependencies() -> dict[str, object]:
    packages = ["lxml", "pillow", "playwright", "fonttools", "python-pptx"]
    subprocess.run(
        [sys.executable, "-m", "pip", "install", *packages],
        check=True,
    )
    return {
        "python_packages": "installed",
        "browser": configure_figgenie_browser(),
        "status": figgenie_dependency_status(),
    }


def default_skills_root() -> Path:
    codex_home = os.environ.get("CODEX_HOME")
    base = Path(codex_home).expanduser() if codex_home else Path.home() / ".codex"
    return base / "skills"


def copy_skill(source: Path, target: Path, backup: bool = True) -> Path | None:
    source = source.resolve()
    target = target.resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    staging = target.parent / f".{target.name}.installing"
    if staging.exists():
        raise FileExistsError(f"Stale installation staging path exists: {staging}")
    staging.mkdir()
    try:
        for name in MAIN_ENTRIES:
            item = source / name
            if not item.exists():
                if name == "README.md":
                    continue
                raise FileNotFoundError(f"Required skill entry is missing: {item}")
            destination = staging / name
            if item.is_dir():
                shutil.copytree(
                    item,
                    destination,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"),
                )
            else:
                shutil.copy2(item, destination)

        backup_path: Path | None = None
        if target.exists():
            if backup:
                stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
                backup_path = target.parent / f"{target.name}.backup-{stamp}"
                if backup_path.exists():
                    raise FileExistsError(f"Backup path already exists: {backup_path}")
                target.rename(backup_path)
            else:
                shutil.rmtree(target)
        try:
            staging.rename(target)
        except Exception:
            if backup_path and backup_path.exists() and not target.exists():
                backup_path.rename(target)
            raise
        return backup_path
    finally:
        if staging.exists():
            shutil.rmtree(staging)


def copy_figgenie(source: Path, target: Path) -> None:
    staging = target.parent / f".{target.name}.installing"
    if staging.exists():
        raise FileExistsError(f"Stale FigGenie staging path exists: {staging}")
    shutil.copytree(source, staging)
    staging.rename(target)


def ensure_figgenie(
    repo_root: Path,
    skills_root: Path,
    offline: bool,
    refresh: bool,
) -> dict[str, str]:
    target = skills_root / "figgenie-paper-diagram"
    if target.exists() and not refresh:
        return {"status": "existing", "path": str(target)}
    if target.exists() and refresh:
        raise FileExistsError(
            "Refusing to overwrite an existing FigGenie installation automatically. "
            "Archive it explicitly before using --refresh-figgenie."
        )

    vendor = repo_root / "vendor" / "figgenie-paper-diagram"
    if vendor.is_dir():
        copy_figgenie(vendor, target)
        return {"status": "installed-from-vendor", "path": str(target)}
    if offline:
        raise FileNotFoundError(
            "FigGenie is not installed and no vendored copy exists; offline mode forbids download."
        )

    with tempfile.TemporaryDirectory(prefix="figgenie-install-") as temp_dir:
        checkout = Path(temp_dir) / "repo"
        subprocess.run(
            ["git", "clone", "--depth", "1", FIGGENIE_REPO, str(checkout)],
            check=True,
        )
        source = checkout / "skills" / "figgenie-paper-diagram"
        if not source.is_dir():
            raise FileNotFoundError(f"Official FigGenie skill was not found at {source}")
        copy_figgenie(source, target)
    return {"status": "installed-from-official-repo", "path": str(target)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skills-root", type=Path, default=default_skills_root())
    parser.add_argument("--without-figgenie", action="store_true")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--no-backup", action="store_true")
    parser.add_argument("--refresh-figgenie", action="store_true")
    parser.add_argument(
        "--install-figgenie-deps",
        action="store_true",
        help="Install FigGenie Python dependencies and configure an existing system browser when possible",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    skills_root = args.skills_root.expanduser().resolve()
    main_target = skills_root / "assignment-polishing"
    try:
        backup_path = copy_skill(repo_root, main_target, backup=not args.no_backup)
        result: dict[str, object] = {
            "assignment_polishing": {
                "status": "installed",
                "path": str(main_target),
                "backup": str(backup_path) if backup_path else None,
            }
        }
        if args.without_figgenie:
            result["figgenie"] = {"status": "skipped"}
        else:
            figgenie_result = ensure_figgenie(
                repo_root, skills_root, args.offline, args.refresh_figgenie
            )
            figgenie_result["dependencies"] = figgenie_dependency_status()
            if args.install_figgenie_deps:
                figgenie_result["dependency_install"] = install_figgenie_dependencies()
            result["figgenie"] = figgenie_result
    except (OSError, subprocess.CalledProcessError) as exc:
        parser.error(str(exc))

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
