#!/usr/bin/env python3
"""Validate the public ja-ai-polish skill, docs, and evaluation manifest."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_INSTALL_DOCS = {
    "en.md",
    "zh-CN.md",
    "ja.md",
}
EXPECTED_EVAL_COUNTS = {
    "edit": 26,
    "write": 9,
    "false-positive": 21,
    "scene": 16,
    "fidelity": 12,
    "voice": 8,
}
FLOW_IDS = [f"F{number:02d}" for number in range(1, 10)]
OUTPUT_FIELD_IDS = [
    "final_text",
    "generation_notes",
    "edit_notes",
    "suggested_deletions",
    "fidelity_warnings",
    "severity",
    "rule_id",
    "source_excerpt",
    "explanation",
    "suggestion",
]
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def parse_frontmatter(path: Path, errors: list[str]) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        fail(errors, f"{path.relative_to(ROOT)}: missing opening frontmatter marker")
        return {}
    try:
        end = lines.index("---", 1)
    except ValueError:
        fail(errors, f"{path.relative_to(ROOT)}: missing closing frontmatter marker")
        return {}
    data: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip():
            continue
        if ":" not in line:
            fail(errors, f"{path.relative_to(ROOT)}: malformed frontmatter line: {line}")
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def check_links(errors: list[str]) -> None:
    for path in sorted(ROOT.rglob("*.md")):
        if "docs_dev" in path.parts or "dist" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        if "docs_dev/" in text:
            fail(errors, f"{path.relative_to(ROOT)}: public file references docs_dev/")
        for target in LINK_RE.findall(text):
            clean = target.split("#", 1)[0]
            if not clean or clean.startswith(("http://", "https://", "mailto:", "#")):
                continue
            resolved = (path.parent / clean).resolve()
            try:
                resolved.relative_to(ROOT)
            except ValueError:
                fail(errors, f"{path.relative_to(ROOT)}: link escapes repository: {target}")
                continue
            if not resolved.exists():
                fail(errors, f"{path.relative_to(ROOT)}: broken link: {target}")
        for line_number, line in enumerate(text.splitlines(), 1):
            if line.rstrip() != line:
                fail(errors, f"{path.relative_to(ROOT)}:{line_number}: trailing whitespace")


def check_flows(errors: list[str]) -> None:
    required_terms = {
        "auto",
        "write",
        "edit",
        "detect",
        "minimal",
        "standard",
        "aggressive",
        "bounded",
        "public-writing",
    }
    for name in ("en.md", "zh-CN.md", "ja.md"):
        path = ROOT / "references" / "instructions" / name
        text = path.read_text(encoding="utf-8")
        ids = re.findall(r"^## (F\d{2})\b", text, re.MULTILINE)
        if ids != FLOW_IDS:
            fail(errors, f"{path.relative_to(ROOT)}: expected stable IDs {FLOW_IDS}, got {ids}")
        missing_terms = sorted(term for term in required_terms if f"`{term}`" not in text)
        if missing_terms:
            fail(errors, f"{path.relative_to(ROOT)}: missing shared flow terms {missing_terms}")


def check_output_formats(errors: list[str]) -> None:
    path = ROOT / "references" / "output-formats.md"
    text = path.read_text(encoding="utf-8")
    rows = re.findall(
        r"^\| `([^`]+)` \| ([^|]+) \| ([^|]+) \| ([^|]+) \|$",
        text,
        re.MULTILINE,
    )
    ids = [row[0] for row in rows]
    if ids != OUTPUT_FIELD_IDS:
        fail(errors, f"{path.relative_to(ROOT)}: expected output fields {OUTPUT_FIELD_IDS}, got {ids}")
    for field_id, *translations in rows:
        if any(not value.strip() for value in translations):
            fail(errors, f"{path.relative_to(ROOT)}: incomplete translation for {field_id}")


def check_skill_routes(errors: list[str]) -> None:
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    targets = set(LINK_RE.findall(text))
    expected = {
        "references/instructions/en.md",
        "references/instructions/zh-CN.md",
        "references/instructions/ja.md",
        "references/de-ai-patterns.md",
        "references/fidelity-contract.md",
        "references/protected-spans.md",
        "references/output-formats.md",
        "references/voice-calibration.md",
        *{
            f"references/scene-packs/{name}.md"
            for name in (
                "work-email",
                "chat-message",
                "social-post",
                "status-update",
                "repo-maintenance",
                "technical-article",
                "public-writing",
            )
        },
    }
    missing = sorted(expected - targets)
    if missing:
        fail(errors, f"SKILL.md: missing progressive-disclosure routes {missing}")


def check_agent_metadata(errors: list[str]) -> None:
    path = ROOT / "agents" / "openai.yaml"
    if not path.exists():
        fail(errors, "agents/openai.yaml: missing UI metadata")
        return
    text = path.read_text(encoding="utf-8")
    expected = {
        'display_name: "JA AI Polish"',
        'short_description: "Write and humanize natural Japanese text"',
        'default_prompt: "Use $ja-ai-polish to write or polish natural Japanese while preserving facts and voice."',
    }
    missing = sorted(value for value in expected if value not in text)
    if missing:
        fail(errors, f"agents/openai.yaml: missing expected interface values {missing}")


def check_rules(errors: list[str]) -> None:
    path = ROOT / "references" / "de-ai-patterns.md"
    text = path.read_text(encoding="utf-8")
    catalog = text.split("## Rule catalog", 1)[-1].split("## Trigger", 1)[0]
    ids = re.findall(r"^\| `(JA-[A-Z]+-\d{3})` \|", catalog, re.MULTILINE)
    if len(ids) < 11:
        fail(errors, "references/de-ai-patterns.md: fewer than 11 operational rules")
    duplicates = [rule_id for rule_id, count in Counter(ids).items() if count > 1]
    if duplicates:
        fail(errors, f"references/de-ai-patterns.md: duplicate catalog IDs: {duplicates}")
    categories = {rule_id.rsplit("-", 1)[0] for rule_id in ids}
    expected = {
        "JA-GRAM",
        "JA-VAGUE",
        "JA-HEDGE",
        "JA-DISCOURSE",
        "JA-META",
        "JA-CLOSING",
        "JA-TRANSLATION",
        "JA-RHYTHM",
        "JA-SPECIFICITY",
        "JA-STANCE",
        "JA-EMPATHY",
        "JA-LAYOUT",
    }
    if categories != expected:
        fail(errors, f"references/de-ai-patterns.md: category mismatch: {sorted(categories)}")
    for rule_id in ids:
        example_count = len(re.findall(rf"^\| `{re.escape(rule_id)}` \|", text, re.MULTILINE))
        if example_count < 2:
            fail(errors, f"{rule_id}: missing trigger/false-positive example row")


def check_docs(errors: list[str]) -> None:
    actual = {path.name for path in (ROOT / "docs" / "install").glob("*.md")}
    if actual != EXPECTED_INSTALL_DOCS:
        fail(errors, f"docs/install: expected {sorted(EXPECTED_INSTALL_DOCS)}, got {sorted(actual)}")
    toc_headings = {
        "en.md": "Contents",
        "zh-CN.md": "目录",
        "ja.md": "目次",
    }
    platform_terms = {
        "ChatGPT",
        "Claude Code",
        "Cursor",
        "Hermes Agent",
        "OpenClaw",
    }
    for path in (ROOT / "docs" / "install").glob("*.md"):
        text = path.read_text(encoding="utf-8")
        for number in range(1, 9):
            if not re.search(rf"^## {number}\.", text, re.MULTILINE):
                fail(errors, f"{path.relative_to(ROOT)}: missing section {number}")
        toc_heading = toc_headings.get(path.name)
        if toc_heading and not re.search(rf"^## {re.escape(toc_heading)}$", text, re.MULTILINE):
            fail(errors, f"{path.relative_to(ROOT)}: missing table-of-contents heading {toc_heading}")
        missing_platforms = sorted(term for term in platform_terms if term not in text)
        if missing_platforms:
            fail(errors, f"{path.relative_to(ROOT)}: missing platform sections {missing_platforms}")


def check_readmes(errors: list[str]) -> None:
    expected_headings = {
        "README.md": [
            "What it does",
            "Suitable scope",
            "Core principles",
            "Install",
            "Quick examples",
            "Modes",
            "Pattern map",
            "Scene Packs",
            "Fidelity guarantee",
            "Author voice",
            "Evaluation status",
            "Known limits",
            "Contributing",
            "License",
        ],
        "README.zh-CN.md": [
            "功能",
            "适用范围",
            "核心原则",
            "安装",
            "快速示例",
            "write / edit / detect 模式",
            "模式地图",
            "Scene Pack",
            "忠实性保证",
            "作者声音校准",
            "评测状态",
            "已知限制",
            "贡献方式",
            "License",
        ],
        "README.ja.md": [
            "できること",
            "対象範囲",
            "基本原則",
            "インストール",
            "すぐに試す",
            "write / edit / detect モード",
            "パターンマップ",
            "Scene Pack",
            "忠実性の保証",
            "書き手の声",
            "評価状況",
            "既知の制約",
            "コントリビューション",
            "License",
        ],
    }
    for name, headings in expected_headings.items():
        text = (ROOT / name).read_text(encoding="utf-8")
        actual = re.findall(r"^## (.+)$", text, re.MULTILINE)
        if actual != headings:
            fail(errors, f"{name}: heading structure differs: {actual}")


def check_evals(errors: list[str]) -> None:
    path = ROOT / "evals" / "evals.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(errors, f"evals/evals.json: {exc}")
        return
    if not isinstance(data, list):
        fail(errors, "evals/evals.json: top level must be an array")
        return
    ids: set[str] = set()
    counts: Counter[str] = Counter()
    for index, case in enumerate(data):
        if not isinstance(case, dict):
            fail(errors, f"evals/evals.json[{index}]: case must be an object")
            continue
        missing = {"id", "category", "mode", "prompt_language", "input", "expected", "license"} - case.keys()
        if missing:
            fail(errors, f"evals/evals.json[{index}]: missing {sorted(missing)}")
        case_id = case.get("id")
        if case_id in ids:
            fail(errors, f"evals/evals.json: duplicate id {case_id}")
        ids.add(case_id)
        counts[case.get("category")] += 1
        if case.get("license") not in {"self-authored", "redistributable"}:
            fail(errors, f"{case_id}: unsupported license marker")
    if dict(counts) != EXPECTED_EVAL_COUNTS:
        fail(errors, f"eval counts: expected {EXPECTED_EVAL_COUNTS}, got {dict(counts)}")
    if len(data) != 92:
        fail(errors, f"evals/evals.json: expected 92 cases, got {len(data)}")
    scenes = {
        "work-email",
        "chat-message",
        "social-post",
        "status-update",
        "repo-maintenance",
        "technical-article",
        "public-writing",
    }
    scene_cases = [case for case in data if case.get("category") == "scene"]
    for case in scene_cases:
        case_id = str(case.get("id"))
        input_data = case.get("input")
        expected = case.get("expected")
        if not isinstance(input_data, dict) or not isinstance(expected, dict):
            continue
        contract = expected.get("line_integrity")
        if not isinstance(contract, dict):
            fail(errors, f"{case_id}: scene case must define line_integrity")
            continue
        if contract.get("enabled") is not True:
            fail(errors, f"{case_id}: line_integrity.enabled must be true")
        scene = contract.get("scene")
        if scene not in scenes:
            fail(errors, f"{case_id}: unsupported line_integrity scene {scene!r}")
        if input_data.get("scene") in scenes and scene != input_data.get("scene"):
            fail(errors, f"{case_id}: line_integrity scene does not match input scene")
        for key in ("allow_intentional_line_breaks", "semantic_review"):
            if not isinstance(contract.get(key), bool):
                fail(errors, f"{case_id}: line_integrity.{key} must be boolean")
        article = expected.get("article_markdown")
        if article is not None:
            if scene != "technical-article" or not isinstance(article, dict):
                fail(errors, f"{case_id}: article_markdown is only valid for technical-article")
            else:
                for key in ("complete_article", "artifact_only", "semantic_structure_review"):
                    if not isinstance(article.get(key), bool):
                        fail(errors, f"{case_id}: article_markdown.{key} must be boolean")
                if article.get("next_action") not in {"publish", "copy", "collaborative-edit", "review"}:
                    fail(errors, f"{case_id}: unsupported article_markdown.next_action")
                if article.get("next_action") in {"publish", "copy"} and article.get("artifact_only") is not True:
                    fail(errors, f"{case_id}: publish/copy article must be artifact_only")
        elif scene == "technical-article" and case_id in {"scene-011", "scene-012"}:
            fail(errors, f"{case_id}: technical article scene case missing article_markdown")


def check_git_isolation(errors: list[str]) -> None:
    if not (ROOT / ".git").exists():
        print("NOTE: Git index isolation was not checked because this directory has no .git metadata")
        return
    result = subprocess.run(
        ["git", "ls-files", "docs_dev"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        fail(errors, f"git ls-files docs_dev failed: {result.stderr.strip()}")
    elif result.stdout.strip():
        fail(errors, f"docs_dev is tracked by Git: {result.stdout.strip().splitlines()}")


def main() -> int:
    errors: list[str] = []
    skill = ROOT / "SKILL.md"
    frontmatter = parse_frontmatter(skill, errors)
    if frontmatter.get("name") != "ja-ai-polish":
        fail(errors, "SKILL.md: name must be ja-ai-polish")
    if set(frontmatter) != {"name", "description"}:
        fail(errors, f"SKILL.md: only name and description are allowed, got {sorted(frontmatter)}")
    if len(skill.read_text(encoding="utf-8").splitlines()) > 300:
        fail(errors, "SKILL.md: exceeds 300 lines")
    ignore = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    for entry in ("/docs_dev/", "/dist/"):
        if entry not in ignore:
            fail(errors, f".gitignore: missing {entry}")
    check_links(errors)
    check_flows(errors)
    check_output_formats(errors)
    check_skill_routes(errors)
    check_agent_metadata(errors)
    check_rules(errors)
    check_docs(errors)
    check_readmes(errors)
    check_evals(errors)
    check_git_isolation(errors)
    if errors:
        print("\n".join(f"ERROR: {message}" for message in errors))
        return 1
    print("OK: skill, references, docs, links, and 92 eval cases are consistent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
