# Validation status

Last updated: 2026-08-30.

This page separates checks that are reproducible in the repository from release gates that still
need an external platform or human reviewer. An unchecked gate is not a failed result, but no score
is claimed until the required evidence exists.

## Reproducible local checks

| Check | Status | Command |
|---|---|---|
| Skill, rules, localized flows, README structure, install matrix, links, and eval schema | Passed | `python3 scripts/lint_skill.py` |
| Protected-value fidelity fixtures | Passed | `python3 scripts/check_fidelity.py` |
| Script regression tests | Passed | `python3 -m unittest discover -s tests -v` |
| Runtime-only package excluding internal developer material, public docs, tests, and eval data | Passed | `python3 scripts/package_skill.py` |
| Evaluation manifests without an execution claim | Passed | `python3 scripts/run_evals.py --agent chatgpt --suite all` |
| One-process-per-case external runner protocol and JSON/Markdown reports | Passed | `python3 -m unittest tests.test_scripts.ScriptTests.test_isolated_runner_saves_raw_results -v` |

The evaluation corpus contains 103 base cases. The derived `detect` suite reuses 32 positive edit
cases and 25 false-positive cases, producing 57 rule-ID classification cases without duplicating
the source corpus.

## Release gates not yet claimed

| Gate | Current status | Evidence required |
|---|---|---|
| ChatGPT release-candidate regression, two runs | Not run | Raw outputs, exact Skill revision, model/settings, and scored report |
| Claude Code release-candidate regression, two runs | Not run | Raw outputs, exact Skill revision, model/settings, and scored report |
| False-positive retention at least 90% | Pending model runs and human review | Per-case edit decisions and reviewer notes |
| Detect precision at least 85% and recall at least 75% | Pending detect runs and adjudication | Rule-ID report plus reviewed labels |
| Native-Japanese blind preference and quality review | Not run | Three reviewers, blinded samples, rubric, and aggregate report |
| ChatGPT, Claude Code, Cursor, Hermes Agent, and OpenClaw install/update/uninstall smoke tests | Not run | Platform versions, scope, commands or UI steps, and observed results |

The repository does not use AI-detector scores as a release metric. Model output quality and
installation compatibility can change, so reports must identify the evaluated revision and setup.

## External runner protocol

`scripts/run_evals.py --runner-command` starts the supplied command once per case. Each fresh
process receives one case object as JSON on standard input and must return one JSON object:

```json
{
  "output": "the complete agent response",
  "observed": {
    "route": "optional route label",
    "register": "optional register label"
  }
}
```

The harness saves raw outputs under `evals/runs/` by default and produces an automated report.
Cases marked for manual review still require a human decision; an automated pass is not a
publication-quality judgment.
