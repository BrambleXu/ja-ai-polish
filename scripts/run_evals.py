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
HEADING_RE = re.compile(r"^ {0,3}(#{1,6})(?:\s+|$)(.*)$")
LIST_RE = re.compile(r"^ {0,3}(?:[-+*]|\d+[.)])\s+")
PROSE_TERMINATORS = "。！？!?」』）)]}』"
INCOMPLETE_LEAD_RE = re.compile(r"^(?:たとえば|例えば|その結果|一方で|一方|次に|具体的には)[、，,:：]?$|[、，,:：]$")
BLOCK_SUFFIX_RE = re.compile(r"^(?:という|といった|などと|などです)")
TRAILING_INLINE_MARKUP_RE = re.compile(r"(?:\*\*|__|~~|\*|_|`+)$")
LEADING_INLINE_MARKUP_RE = re.compile(r"^(?:\*\*|__|~~|\*|_|`+)")
PROSE_CONTINUATION_RE = re.compile(r"^(?:くらい|という|といった|など|ため|ので|のが|こと|もの|よう)")


def _classified_lines(text: str) -> list[tuple[str, str]]:
    """Classify source lines while treating fenced code as opaque."""
    entries: list[tuple[str, str]] = []
    in_fence = False
    for line in text.splitlines():
        stripped = line.strip()
        if in_fence:
            entries.append(("code", line))
            if stripped.startswith("```"):
                in_fence = False
            continue
        if stripped.startswith("```"):
            entries.append(("fence", line))
            in_fence = True
        elif not stripped:
            entries.append(("blank", line))
        elif HEADING_RE.match(line):
            entries.append(("heading", line))
        elif LIST_RE.match(line):
            entries.append(("list", line))
        elif stripped.startswith(">"):
            entries.append(("quote", line))
        elif stripped.startswith("|") and "|" in stripped[1:]:
            entries.append(("table", line))
        elif re.match(r"^ {0,3}!?\[[^]]*\]\([^)]*\)\s*$", line):
            entries.append(("image", line))
        else:
            entries.append(("prose", line))
    return entries


def _previous_nonblank(entries: list[tuple[str, str]], index: int) -> int | None:
    cursor = index - 1
    while cursor >= 0:
        if entries[cursor][0] != "blank":
            return cursor
        cursor -= 1
    return None


def _next_nonblank(entries: list[tuple[str, str]], index: int) -> int | None:
    cursor = index + 1
    while cursor < len(entries):
        if entries[cursor][0] != "blank":
            return cursor
        cursor += 1
    return None


def _visible_prose_end(line: str) -> str:
    """Remove closing inline Markdown markers before checking sentence punctuation."""
    visible = line.rstrip()
    while True:
        updated = TRAILING_INLINE_MARKUP_RE.sub("", visible).rstrip()
        if updated == visible:
            return visible
        visible = updated


def _visible_prose_start(line: str) -> str:
    """Remove opening inline Markdown markers before checking continuation syntax."""
    visible = line.lstrip()
    while True:
        updated = LEADING_INLINE_MARKUP_RE.sub("", visible).lstrip()
        if updated == visible:
            return visible
        visible = updated


def validate_line_integrity(text: str, contract: dict[str, object]) -> list[str]:
    """Return stable cross-scene layout error codes."""
    if not isinstance(contract, dict) or contract.get("enabled") is not True:
        return []
    entries = _classified_lines(text)
    errors: list[str] = []
    blank_run = 0
    for index, (kind, line) in enumerate(entries):
        if kind == "blank":
            blank_run += 1
            if blank_run > 1:
                errors.append("excess-blank-lines")
            continue
        blank_run = 0
        if kind != "prose":
            continue
        previous = _previous_nonblank(entries, index)
        if previous is not None and entries[previous][0] == "prose":
            previous_text = _visible_prose_end(entries[previous][1])
            intentional_breaks = contract.get("allow_intentional_line_breaks") is True
            adjacent_prose = previous == index - 1
            if previous_text.endswith(("、", "，", ",")) and (
                adjacent_prose or not intentional_breaks
            ):
                errors.append("dangling-comma-break")
            continues_across_blank = not intentional_breaks and (
                INCOMPLETE_LEAD_RE.search(previous_text) is not None
                or PROSE_CONTINUATION_RE.match(_visible_prose_start(line)) is not None
            )
            if not previous_text.endswith(tuple(PROSE_TERMINATORS)) and (
                adjacent_prose or continues_across_blank
            ):
                errors.append("wrapped-prose")

    block_kinds = {"list", "quote", "table"}
    for index, (kind, _line) in enumerate(entries):
        if kind not in block_kinds:
            continue
        previous = _previous_nonblank(entries, index)
        if previous is not None and entries[previous][0] == "prose":
            lead = entries[previous][1].strip()
            if INCOMPLETE_LEAD_RE.search(lead):
                errors.append("incomplete-block-introduction")
        following = _next_nonblank(entries, index)
        if following is not None and entries[following][0] == "prose":
            suffix = entries[following][1].strip()
            if BLOCK_SUFFIX_RE.match(suffix):
                errors.append("block-suffix-continuation")
    return list(dict.fromkeys(errors))


def validate_article_markdown(text: str, contract: dict[str, object]) -> list[str]:
    """Return stable technical-article Markdown error codes."""
    if not isinstance(contract, dict) or contract.get("complete_article") is not True:
        return []
    entries = _classified_lines(text)
    errors: list[str] = []
    headings: list[tuple[int, int]] = []
    first_nonempty: int | None = None
    for index, (kind, line) in enumerate(entries):
        if kind in {"blank", "code", "fence"}:
            continue
        if first_nonempty is None:
            first_nonempty = index
        if kind == "heading":
            match = HEADING_RE.match(line)
            assert match is not None
            headings.append((index, len(match.group(1))))
    h1_count = sum(level == 1 for _index, level in headings)
    if h1_count == 0:
        errors.append("missing-h1")
    if h1_count > 1:
        errors.append("multiple-h1")
    if first_nonempty is not None and (not headings or headings[0][0] != first_nonempty or headings[0][1] != 1):
        errors.append("h1-not-first")
    seen_h2 = False
    previous_heading = False
    previous_heading_level: int | None = None
    for _index, level in headings:
        if level == 2:
            seen_h2 = True
        if level == 3 and not seen_h2:
            errors.append("orphan-h3")
        if level >= 4:
            errors.append("heading-too-deep")
        if previous_heading and previous_heading_level != 1:
            errors.append("empty-heading-chain")
        previous_heading = True
        previous_heading_level = level
        # The next non-heading content resets the chain; handled in a second pass below.
        cursor = _index + 1
        while cursor < len(entries) and entries[cursor][0] == "blank":
            cursor += 1
        if cursor < len(entries) and entries[cursor][0] not in {"heading", "blank"}:
            previous_heading = False
    if contract.get("artifact_only") is True:
        prefix = text.lstrip().splitlines()
        if prefix and prefix[0].strip().startswith("```"):
            errors.append("artifact-wrapper-present")
        if re.search(r"(?:以下は(?:成稿|完成稿)|Here(?: is| are) the|以下の文章)", text, re.IGNORECASE):
            errors.append("artifact-wrapper-present")
    return list(dict.fromkeys(errors))


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
    for key in (
        "must_not_invent",
        "avoid",
        "reason",
        "register",
        "structure",
        "voice",
        "traits",
        "line_integrity",
        "article_markdown",
    ):
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
        line_integrity_errors: list[str] = []
        article_markdown_errors: list[str] = []
        line_contract = expected.get("line_integrity")
        if isinstance(line_contract, dict):
            line_integrity_errors = validate_line_integrity(output, line_contract)
        article_contract = expected.get("article_markdown")
        if isinstance(article_contract, dict):
            article_markdown_errors = validate_article_markdown(output, article_contract)
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
            if (
                not missing
                and not present_forbidden
                and not missing_rules
                and not unexpected_rules
                and not line_integrity_errors
                and not article_markdown_errors
            )
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
                "line_integrity_errors": line_integrity_errors,
                "article_markdown_errors": article_markdown_errors,
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
