#!/usr/bin/env python3
"""Check exact fidelity invariants in fixtures or a supplied before/after pair."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOKEN_PATTERNS = (
    re.compile(r"```[\s\S]*?```"),
    re.compile(r"https?://[^\s)>\]」]+"),
    re.compile(
        r"(?<![A-Z0-9._%+-])[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}(?![A-Z0-9.-])",
        re.IGNORECASE,
    ),
    re.compile(r"`[^`\n]+`"),
    re.compile(r"\b[A-Za-z]:\\(?:[^\\\s]+\\)*[^\\\s]+"),
    re.compile(r"(?<![:\w])/(?:[\w.@~+-]+/)*[\w@~+-]+(?:\.[\w@~+-]+)*"),
    re.compile(r"(?<![0-9a-f])[0-9a-f]{7,40}(?![0-9a-f])", re.IGNORECASE),
    re.compile(r"(?<!\w)#\d+(?!\d)"),
    re.compile(r"(?<![A-Z0-9])v?\d+(?:\.\d+){1,}(?![A-Z0-9])", re.IGNORECASE),
    re.compile(r"\d[\d,]*(?:\.\d+)?(?:%|円|万円|件|日間|時|ms|秒|分|月|日|年)"),
    re.compile(r"(?<!\d)\d{4}-\d{2}-\d{2}(?!\d)"),
    re.compile(r"「[^」]+」|“[^”]+”|\"[^\"\n]+\""),
)


def protected_tokens(text: str) -> Counter[str]:
    tokens: Counter[str] = Counter()
    for pattern in TOKEN_PATTERNS:
        tokens.update(pattern.findall(text))
    return tokens


def compare(source: str, candidate: str, allowed_omissions: set[str] | None = None) -> list[str]:
    allowed = allowed_omissions or set()
    source_tokens = protected_tokens(source)
    candidate_tokens = protected_tokens(candidate)
    errors: list[str] = []
    for token, expected_count in sorted(source_tokens.items()):
        if token in allowed:
            continue
        actual_count = candidate_tokens[token]
        if actual_count < expected_count:
            errors.append(
                f"protected token count decreased: {token!r} "
                f"(expected at least {expected_count}, got {actual_count})"
            )
    return errors


def check_fixture(case: dict[str, object]) -> list[str]:
    case_id = str(case["id"])
    input_data = case["input"]
    expected = case["expected"]
    assert isinstance(input_data, dict)
    assert isinstance(expected, dict)
    source = str(input_data.get("source", input_data.get("brief", "")))
    candidate = str(input_data.get("candidate", ""))
    errors = [f"{case_id}: {message}" for message in compare(source, candidate)]
    for value in expected.get("must_preserve", []):
        if value not in candidate:
            errors.append(f"{case_id}: missing required value or relation: {value}")
    for value in expected.get("forbidden", []):
        if value in candidate:
            errors.append(f"{case_id}: forbidden unsupported value present: {value}")
    return errors


def check_manifest() -> list[str]:
    data = json.loads((ROOT / "evals" / "evals.json").read_text(encoding="utf-8"))
    cases = [case for case in data if case.get("category") == "fidelity"]
    errors: list[str] = []
    modes = {case.get("mode") for case in cases}
    if modes != {"write", "edit"}:
        errors.append(f"fidelity suite must cover write and edit, got {sorted(modes)}")
    for case in cases:
        errors.extend(check_fixture(case))
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", help="Path to the brief or source text")
    parser.add_argument("--candidate", help="Path to generated or edited text")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if bool(args.source) != bool(args.candidate):
        print("ERROR: --source and --candidate must be supplied together")
        return 2
    if args.source:
        source = Path(args.source).read_text(encoding="utf-8")
        candidate = Path(args.candidate).read_text(encoding="utf-8")
        errors = compare(source, candidate)
        label = "supplied pair"
    else:
        errors = check_manifest()
        label = "13 fidelity fixtures"
    if errors:
        print("\n".join(f"ERROR: {message}" for message in errors))
        return 1
    print(f"OK: {label} preserved deterministic protected values")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
