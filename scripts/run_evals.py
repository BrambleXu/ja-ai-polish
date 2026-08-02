#!/usr/bin/env python3
"""Prepare eval prompts or score externally collected model outputs."""

from __future__ import annotations

import argparse
import copy
import json
import re
import shlex
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = ("edit", "write", "detect", "false-positive", "scene", "fidelity", "voice")
RULE_ID_RE = re.compile(r"JA-[A-Z]+-\d{3}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", required=True, choices=("chatgpt", "claude-code"))
    parser.add_argument("--suite", default="all", choices=("all",) + CATEGORIES)
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--results", type=Path, help="JSON array containing id, output, and optional observed fields")
    source.add_argument(
        "--runner-command",
        help=(
            "Command launched once per case. It receives one case as JSON on stdin and must return "
            "a JSON object containing output and optional observed fields."
        ),
    )
    parser.add_argument("--revision", help="Evaluated commit, archive checksum, or revision label")
    parser.add_argument("--evaluator-setup", help="Model/version, settings, and invocation environment")
    parser.add_argument("--raw-results-output", type=Path, help="Save raw outputs from --runner-command")
    parser.add_argument("--output", type=Path, help="Write JSON, or Markdown when the suffix is .md")
    args = parser.parse_args()
    if (args.results or args.runner_command) and (not args.revision or not args.evaluator_setup):
        parser.error("--results and --runner-command require --revision and --evaluator-setup")
    if args.raw_results_output and not args.runner_command:
        parser.error("--raw-results-output requires --runner-command")
    return args


def load_cases(suite: str) -> list[dict[str, object]]:
    cases = json.loads((ROOT / "evals" / "evals.json").read_text(encoding="utf-8"))
    if suite == "detect":
        detect_cases: list[dict[str, object]] = []
        for case in cases:
            if case["category"] not in {"edit", "false-positive"}:
                continue
            variant = copy.deepcopy(case)
            variant["mode"] = "detect"
            variant["id"] = f"detect-{case['id']}"
            if case["category"] == "false-positive":
                variant["expected"]["rules"] = []
            detect_cases.append(variant)
        return detect_cases
    if suite == "all":
        return cases
    return [case for case in cases if case["category"] == suite]


def deterministic_expectations(
    case: dict[str, object], result: dict[str, object]
) -> tuple[list[str], list[str], list[str]]:
    expected = case["expected"]
    assert isinstance(expected, dict)
    required: list[str] = []
    forbidden: list[str] = []
    manual: list[str] = []
    for key in ("must_include", "preserve", "must_preserve"):
        required.extend(str(value) for value in expected.get(key, []))
    forbidden.extend(str(value) for value in expected.get("forbidden", []))
    result_mode = result.get("mode", case.get("mode"))
    if result_mode != "detect" and expected.get("rules"):
        manual.append("Confirm that edits correspond to the expected rule set.")
    if expected.get("keep") and result_mode != "detect":
        input_data = case.get("input", {})
        if isinstance(input_data, dict) and isinstance(input_data.get("text"), str):
            required.append(str(input_data["text"]))
    for key in ("must_not_invent", "avoid", "reason", "register", "structure", "voice", "traits"):
        if key in expected:
            manual.append(f"Review expectation `{key}`: {expected[key]}")
    return required, forbidden, manual


def run_isolated(cases: list[dict[str, object]], runner_command: str) -> list[dict[str, object]]:
    command = shlex.split(runner_command)
    if not command:
        raise ValueError("--runner-command cannot be empty")
    results: list[dict[str, object]] = []
    for case in cases:
        completed = subprocess.run(
            command,
            input=json.dumps(case, ensure_ascii=False),
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                f"runner failed for {case['id']} with exit {completed.returncode}: "
                f"{completed.stderr.strip()}"
            )
        try:
            result = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"runner returned invalid JSON for {case['id']}: {exc}") from exc
        if not isinstance(result, dict) or not isinstance(result.get("output"), str):
            raise RuntimeError(f"runner result for {case['id']} must contain a string output")
        result["id"] = case["id"]
        result.setdefault("mode", case.get("mode"))
        results.append(result)
    return results


def score(cases: list[dict[str, object]], raw: list[dict[str, object]]) -> dict[str, object]:
    results = {item["id"]: item for item in raw}
    rows: list[dict[str, object]] = []
    rule_tp = 0
    rule_fp = 0
    rule_fn = 0
    for case in cases:
        case_id = str(case["id"])
        result = results.get(case_id)
        if result is None:
            rows.append({"id": case_id, "status": "missing"})
            continue
        output = str(result.get("output", ""))
        required, forbidden, manual = deterministic_expectations(case, result)
        missing = [value for value in required if value not in output]
        present_forbidden = [value for value in forbidden if value in output]
        expected = case["expected"]
        assert isinstance(expected, dict)
        expected_rules = {str(value) for value in expected.get("rules", [])}
        observed_rules = set(RULE_ID_RE.findall(output))
        missing_rules: list[str] = []
        unexpected_rules: list[str] = []
        if result.get("mode", case.get("mode")) == "detect":
            missing_rules = sorted(expected_rules - observed_rules)
            unexpected_rules = sorted(observed_rules - expected_rules)
            rule_tp += len(expected_rules & observed_rules)
            rule_fp += len(observed_rules - expected_rules)
            rule_fn += len(expected_rules - observed_rules)
        observed = result.get("observed", {})
        metadata_mismatches: list[str] = []
        if not isinstance(observed, dict):
            metadata_mismatches.append("observed must be an object")
            observed = {}
        for key in ("route", "register", "structure", "voice"):
            if key in expected and key in observed and observed[key] != expected[key]:
                metadata_mismatches.append(f"{key}: expected {expected[key]!r}, got {observed[key]!r}")
            elif key in expected and key not in observed:
                manual.append(f"Record observed `{key}` and compare with {expected[key]!r}.")
        status = (
            "pass"
            if not missing and not present_forbidden and not missing_rules and not unexpected_rules
            else "fail"
        )
        if metadata_mismatches:
            status = "fail"
        rows.append(
            {
                "id": case_id,
                "status": status,
                "missing": missing,
                "forbidden_present": present_forbidden,
                "missing_rule_ids": missing_rules,
                "unexpected_rule_ids": unexpected_rules,
                "metadata_mismatches": metadata_mismatches,
                "manual_checks": manual,
                "human_review_required": bool(manual),
            }
        )
    counts = {status: sum(row["status"] == status for row in rows) for status in ("pass", "fail", "missing")}
    counts["manual_review_pending"] = sum(bool(row.get("human_review_required")) for row in rows)
    precision = rule_tp / (rule_tp + rule_fp) if rule_tp + rule_fp else None
    recall = rule_tp / (rule_tp + rule_fn) if rule_tp + rule_fn else None
    return {
        "summary": counts,
        "detect_metrics": {
            "true_positive_rule_ids": rule_tp,
            "false_positive_rule_ids": rule_fp,
            "false_negative_rule_ids": rule_fn,
            "precision": precision,
            "recall": recall,
        },
        "unrun_cases": [row["id"] for row in rows if row["status"] == "missing"],
        "cases": rows,
    }


def render_markdown(payload: dict[str, object]) -> str:
    report = payload.get("report")
    if not isinstance(report, dict):
        return "# Evaluation manifest\n\nNo scored results were supplied.\n"
    summary = report["summary"]
    assert isinstance(summary, dict)
    lines = [
        "# ja-ai-polish evaluation report",
        "",
        f"- Agent: `{payload['agent']}`",
        f"- Suite: `{payload['suite']}`",
        f"- Revision: `{payload['revision']}`",
        f"- Evaluator setup: {payload['evaluator_setup']}",
        "- Automated checks only: human review remains required where marked.",
        "",
        "## Summary",
        "",
        "| Pass | Fail | Missing | Manual review pending |",
        "|---:|---:|---:|---:|",
        (
            f"| {summary['pass']} | {summary['fail']} | {summary['missing']} | "
            f"{summary['manual_review_pending']} |"
        ),
        "",
        "## Detect metrics",
        "",
        "| Rule-ID TP | Rule-ID FP | Rule-ID FN | Precision | Recall |",
        "|---:|---:|---:|---:|---:|",
    ]
    metrics = report["detect_metrics"]
    assert isinstance(metrics, dict)

    def metric(value: object) -> str:
        return "n/a" if value is None else f"{value:.3f}" if isinstance(value, float) else str(value)

    lines.extend(
        [
            (
                f"| {metrics['true_positive_rule_ids']} | {metrics['false_positive_rule_ids']} | "
                f"{metrics['false_negative_rule_ids']} | {metric(metrics['precision'])} | "
                f"{metric(metrics['recall'])} |"
            ),
            "",
            "Metrics are populated for detect-mode result sets; `n/a` means there were no scorable",
            "rule-ID decisions.",
            "",
            "## Cases",
            "",
            "| ID | Status | Manual review |",
            "|---|---|---|",
        ]
    )
    cases = report["cases"]
    assert isinstance(cases, list)
    for row in cases:
        manual = "yes" if row.get("human_review_required") else "no"
        lines.append(f"| `{row['id']}` | {row['status']} | {manual} |")
    unrun = report["unrun_cases"]
    assert isinstance(unrun, list)
    lines.extend(["", "## Unrun cases", "", ", ".join(f"`{case_id}`" for case_id in unrun) or "None.", ""])
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    cases = load_cases(args.suite)
    if args.runner_command:
        try:
            raw = run_isolated(cases, args.runner_command)
        except (OSError, RuntimeError, ValueError) as exc:
            raise SystemExit(f"ERROR: {exc}") from exc
        raw_output = args.raw_results_output or (
            ROOT / "evals" / "runs" / f"{args.agent}-{args.suite}-results.json"
        )
        raw_output.parent.mkdir(parents=True, exist_ok=True)
        raw_output.write_text(json.dumps(raw, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        payload: dict[str, object] = {
            "agent": args.agent,
            "suite": args.suite,
            "revision": args.revision,
            "evaluator_setup": args.evaluator_setup,
            "automated_checks_only": True,
            "raw_results": str(raw_output),
            "report": score(cases, raw),
        }
        message = f"Ran and scored {len(cases)} isolated cases; human review remains required"
    elif args.results:
        raw = json.loads(args.results.read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            raise SystemExit("ERROR: --results must contain a JSON array")
        payload: dict[str, object] = {
            "agent": args.agent,
            "suite": args.suite,
            "revision": args.revision,
            "evaluator_setup": args.evaluator_setup,
            "automated_checks_only": True,
            "report": score(cases, raw),
        }
        message = f"Scored {len(cases)} cases; human review remains required"
    else:
        payload = {
            "agent": args.agent,
            "suite": args.suite,
            "status": "prepared-not-executed",
            "note": "Submit these cases to the named platform, then rerun with --results.",
            "cases": cases,
        }
        message = f"Prepared {len(cases)} cases for {args.agent}; no model execution was claimed"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        if args.output.suffix.lower() == ".md":
            args.output.write_text(render_markdown(payload), encoding="utf-8")
        else:
            args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    print(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
