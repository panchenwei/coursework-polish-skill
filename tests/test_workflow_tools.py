from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"


def run_script(name: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / name), *args],
        text=True,
        capture_output=True,
        check=False,
    )


class ControlLayerTests(unittest.TestCase):
    def test_initializer_preserves_existing_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            first = run_script("init_control_layer.py", str(root))
            self.assertEqual(first.returncode, 0, first.stderr)
            goal = root / ".assignment-polishing" / "goal_state.json"
            goal.write_text('{"custom": true}\n', encoding="utf-8")
            second = run_script("init_control_layer.py", str(root))
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(goal.read_text(encoding="utf-8"), '{"custom": true}\n')


class ScorecardTests(unittest.TestCase):
    def _scorecard(self, evidence: list[str]) -> dict:
        return {
            "criteria": [
                {
                    "id": "C1",
                    "official_quote": "Demonstrates a correct implementation.",
                    "authority": "rubric",
                    "locator": "p.2 row C1",
                    "max_score": 10,
                    "current_score": 10,
                    "highest_band": "Correct and fully evidenced",
                    "status": "PASS",
                    "evidence": evidence,
                    "root_cause": "",
                    "next_action": "",
                }
            ],
            "hard_gates": {"correctness": "PASS"},
        }

    def test_valid_scorecard(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "scorecard.json"
            path.write_text(json.dumps(self._scorecard(["tests/output.txt"])), encoding="utf-8")
            result = run_script("validate_scorecard.py", str(path), "--json")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(json.loads(result.stdout)["highest_band_ready"])

    def test_positive_score_requires_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "scorecard.json"
            path.write_text(json.dumps(self._scorecard([])), encoding="utf-8")
            result = run_script("validate_scorecard.py", str(path))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("without direct evidence", result.stdout)


class SubmissionTests(unittest.TestCase):
    def test_build_and_exact_audit(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "report.pdf"
            source.write_bytes(b"pdf-data")
            manifest = root / "manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "output_dir": "FINAL_SUBMISSION",
                        "items": [
                            {
                                "source": "report.pdf",
                                "destination": "Coursework.pdf",
                                "required": True,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            built = run_script(
                "build_submission.py",
                "--root",
                str(root),
                "--manifest",
                str(manifest),
            )
            self.assertEqual(built.returncode, 0, built.stderr)
            self.assertTrue((root / "FINAL_SUBMISSION" / "Coursework.pdf").is_file())
            self.assertTrue((root / "FINAL_SUBMISSION.audit.json").is_file())
            self.assertFalse((root / "FINAL_SUBMISSION" / "FINAL_SUBMISSION.audit.json").exists())

            (root / "FINAL_SUBMISSION" / "extra.txt").write_text("extra", encoding="utf-8")
            audited = run_script(
                "build_submission.py",
                "--root",
                str(root),
                "--manifest",
                str(manifest),
                "--audit-only",
            )
            self.assertNotEqual(audited.returncode, 0)
            self.assertIn("extra.txt", audited.stdout)

    def test_rejects_path_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "file.txt"
            source.write_text("x", encoding="utf-8")
            manifest = root / "manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "output_dir": "FINAL_SUBMISSION",
                        "items": [
                            {"source": "file.txt", "destination": "../escape.txt"}
                        ],
                    }
                ),
                encoding="utf-8",
            )
            result = run_script(
                "build_submission.py",
                "--root",
                str(root),
                "--manifest",
                str(manifest),
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((root.parent / "escape.txt").exists())


class InstallerTests(unittest.TestCase):
    def test_installs_main_skill_and_backups_existing(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            skills_root = Path(temp) / "skills"
            first = run_script(
                "install_skill.py",
                "--skills-root",
                str(skills_root),
                "--without-figgenie",
            )
            self.assertEqual(first.returncode, 0, first.stderr)
            target = skills_root / "assignment-polishing"
            self.assertTrue((target / "SKILL.md").is_file())
            second = run_script(
                "install_skill.py",
                "--skills-root",
                str(skills_root),
                "--without-figgenie",
            )
            self.assertEqual(second.returncode, 0, second.stderr)
            backups = list(skills_root.glob("assignment-polishing.backup-*"))
            self.assertEqual(len(backups), 1)

    def test_offline_install_reuses_existing_figgenie(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            skills_root = Path(temp) / "skills"
            figgenie = skills_root / "figgenie-paper-diagram"
            figgenie.mkdir(parents=True)
            (figgenie / "SKILL.md").write_text("existing\n", encoding="utf-8")
            result = run_script(
                "install_skill.py",
                "--skills-root",
                str(skills_root),
                "--offline",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["figgenie"]["status"], "existing")
            self.assertEqual(
                (figgenie / "SKILL.md").read_text(encoding="utf-8"), "existing\n"
            )


if __name__ == "__main__":
    unittest.main()
