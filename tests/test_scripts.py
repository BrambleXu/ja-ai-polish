from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts.check_fidelity import compare


ROOT = Path(__file__).resolve().parents[1]


def run_script(name: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts" / name), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class ScriptTests(unittest.TestCase):
    def test_lint_skill(self) -> None:
        result = run_script("lint_skill.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_fidelity_fixtures(self) -> None:
        result = run_script("check_fidelity.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("13 fidelity fixtures", result.stdout)

    def test_fidelity_detects_broader_tokens_and_counts(self) -> None:
        source = (
            "連絡先はops@example.com。/srv/app/config.yml を確認。"
            "commit abcdef123 を2回参照: `abcdef123` と `abcdef123`。\n"
            "```bash\npython3 /srv/app/check.py\n```"
        )
        candidate = (
            "連絡先はdev@example.com。/srv/app/config.yaml を確認。"
            "commit abcdef123 を参照: `abcdef123`。\n"
            "```bash\npython3 /srv/app/check.py --force\n```"
        )
        errors = "\n".join(compare(source, candidate))
        self.assertIn("ops@example.com", errors)
        self.assertIn("/srv/app/config.yml", errors)
        self.assertIn("`abcdef123`", errors)
        self.assertIn("```bash", errors)

    def test_package_is_runtime_only(self) -> None:
        result = run_script("package_skill.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        archive = ROOT / "dist" / "ja-ai-polish.zip"
        with zipfile.ZipFile(archive) as handle:
            names = handle.namelist()
        self.assertIn("ja-ai-polish/SKILL.md", names)
        self.assertIn("ja-ai-polish/agents/openai.yaml", names)
        self.assertIn("ja-ai-polish/references/instructions/en.md", names)
        self.assertIn("ja-ai-polish/references/instructions/ja.md", names)
        self.assertNotIn("ja-ai-polish/references/instructions/zh-CN.md", names)
        self.assertTrue(any(name.startswith("ja-ai-polish/references/") for name in names))
        self.assertFalse(any("docs_dev" in name for name in names))
        self.assertFalse(any(name.startswith("ja-ai-polish/docs/") for name in names))
        self.assertFalse(any(name.startswith("ja-ai-polish/evals/") for name in names))

    def test_eval_manifest_preparation(self) -> None:
        result = run_script("run_evals.py", "--agent", "chatgpt", "--suite", "write")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Prepared 9 cases", result.stdout)
        payload = json.loads(result.stdout.rsplit("\nPrepared ", 1)[0])
        self.assertEqual(payload["status"], "prepared-not-executed")
        self.assertEqual(len(payload["cases"]), 9)

    def test_detect_suite_is_derived_from_positive_and_false_positive_cases(self) -> None:
        result = run_script("run_evals.py", "--agent", "chatgpt", "--suite", "detect")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Prepared 57 cases", result.stdout)
        payload = json.loads(result.stdout.rsplit("\nPrepared ", 1)[0])
        self.assertEqual(len(payload["cases"]), 57)
        self.assertTrue(all(case["mode"] == "detect" for case in payload["cases"]))

    def test_scored_eval_requires_provenance_and_writes_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            results = temp / "results.json"
            report = temp / "report.md"
            results.write_text(
                json.dumps(
                    [
                        {
                            "id": "write-001",
                            "output": "API、負荷試験、佐藤、木曜",
                            "observed": {},
                        }
                    ],
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            missing_meta = run_script(
                "run_evals.py",
                "--agent",
                "chatgpt",
                "--suite",
                "write",
                "--results",
                str(results),
            )
            self.assertEqual(missing_meta.returncode, 2)

            scored = run_script(
                "run_evals.py",
                "--agent",
                "chatgpt",
                "--suite",
                "write",
                "--results",
                str(results),
                "--revision",
                "archive-sha256:test",
                "--evaluator-setup",
                "manual ChatGPT session, default settings",
                "--output",
                str(report),
            )
            self.assertEqual(scored.returncode, 0, scored.stdout + scored.stderr)
            markdown = report.read_text(encoding="utf-8")
            self.assertIn("archive-sha256:test", markdown)
            self.assertIn("## Unrun cases", markdown)
            self.assertIn("`write-002`", markdown)

    def test_isolated_runner_saves_raw_results(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            runner = temp / "runner.py"
            raw_results = temp / "raw.json"
            report = temp / "report.json"
            runner.write_text(
                "import json, sys\n"
                "case = json.load(sys.stdin)\n"
                "print(json.dumps({'output': 'runner output', 'mode': case['mode']}))\n",
                encoding="utf-8",
            )
            result = run_script(
                "run_evals.py",
                "--agent",
                "claude-code",
                "--suite",
                "write",
                "--runner-command",
                f"{sys.executable} {runner}",
                "--revision",
                "test-revision",
                "--evaluator-setup",
                "test runner",
                "--raw-results-output",
                str(raw_results),
                "--output",
                str(report),
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("Ran and scored 9 isolated cases", result.stdout)
            self.assertEqual(len(json.loads(raw_results.read_text(encoding="utf-8"))), 9)
            payload = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual(payload["raw_results"], str(raw_results))


if __name__ == "__main__":
    unittest.main()
