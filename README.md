# ja-ai-polish

[English](README.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md)

Write natural Japanese from a brief, or remove templated AI-writing patterns from a Japanese draft
without changing its facts, register, terminology, responsibility, or authorial intent.

`ja-ai-polish` diagnoses observable writing problems. It does not determine whether AI wrote a text
and does not optimize for detector evasion.

## What it does

- **Write:** generate scene-appropriate Japanese directly from supplied facts and constraints.
- **Edit:** improve AI-generated or other Japanese drafts with the smallest safe change.
- **Detect:** explain patterns and evidence without rewriting the text.
- **Calibrate:** follow repeated traits from 2–5 optional samples of the author's Japanese.

## Suitable scope

Use it for work email, Slack or Teams messages, social posts, status updates, repository
maintenance, Qiita/Zenn articles, tutorials, blogs, note posts, and community writing.

## Core principles

1. Diagnose visible behavior, not presumed authorship.
2. Preserve facts before improving style.
3. Treat a phrase as a signal, never as a banned word.
4. Route by scene and audience.
5. Prefer a supplied author voice to generic polish rules.
6. Audit every generated or edited result.

## Quick examples

Direct generation:

```text
Use ja-ai-polish to write a Japanese Slack update.
Facts: the API fix is complete; load testing is pending; Sato owns it and will finish by Thursday.
Return only the final message.
```

De-AI edit:

```text
Use ja-ai-polish to make this Japanese draft less templated.
Preserve every number, product name, and commitment. Mode: edit; intensity: standard.

[draft]
```

Diagnosis:

```text
Use ja-ai-polish to diagnose this Japanese text. Do not rewrite it.
```

## Modes

| Mode | Input | Result |
|---|---|---|
| `write` | Brief with purpose, audience, facts, and constraints | Japanese final text plus short generation notes |
| `edit` | Japanese draft | Minimally changed final text plus edit notes |
| `detect` | Japanese draft | Severity, rule ID, evidence, explanation, and suggestion |
| `auto` | Natural-language request | Routes to one of the modes above |

`edit` supports `minimal`, `standard`, and `aggressive` intensity. Long or deletion-sensitive text
uses `bounded`, which lists possible full-sentence deletions instead of silently removing them.

## Pattern map

| Signal | Default action | Example |
|---|---|---|
| Wordy grammar or nominalization | Restore a direct verb without lowering required formality | `確認を行います` → `確認します` |
| Unsupported evaluation | Use an existing result, metric, or consequence; otherwise flag the gap | `非常に効果的です` → state the observed effect |
| Vague judgment or responsibility avoidance | State known conditions, judgment, or next action | `場合によります` → name the known branches |
| Excess transitions | Remove connectors without a logical job | repeated `さらに／一方／つまり` → natural linkage |
| Article navigation and reader management | Enter the content directly | `本記事では〜を解説します` → state the subject |
| Formulaic ending | End on an existing result, limit, decision, or next step | `今後の発展が期待されます` → state the known plan |
| Translationese or grand metaphor | Name the concrete actor and action | `重要な役割を果たす` → state what it does |
| Uniform sentence rhythm | Regroup information where meaning permits | four matching `〜です` sentences → natural variation |
| Missing specificity or stance | Use supplied actors, conditions, measures, and choices | `総合的に判断することが重要` → state the choice |
| Mechanical empathy | Respond to the concrete issue at the right distance | `素晴らしい質問ですね` → answer directly |

These expressions are not banned. A rewrite is considered only when density, position, function,
missing support, and other signals combine. See [the complete pattern rules](references/de-ai-patterns.md).

## Scene Packs

| Scene | Optimizes for |
|---|---|
| Work email | purpose, request, owner, deadline, appropriate politeness |
| Chat message | actionable context and concise coordination |
| Social post | grounded updates or opinions without engagement bait |
| Status update | completed work, blockers, risk, owners, next steps |
| Repository maintenance | reproducibility, verification, compatibility, contributor action |
| Technical article | technical accuracy, evidence, limits, executable detail |
| Public writing | grounded author voice and non-formulaic structure |

## Fidelity guarantee

Before writing, the skill builds an input ledger of names, facts, numbers, dates, code, terms,
actor-action-object relations, negation, conditions, uncertainty, and commitments. The output is
then checked against that ledger. Missing information is asked for or left visible—not invented.

## Author voice

Provide 2–5 samples to calibrate sentence rhythm, register, subject omission, directness,
punctuation, and the frequency of personal or evaluative language. The skill learns recurring
traits only; it does not reuse sample facts or memorable phrases.

## Install

Paste this into Claude Code, Codex, or your favorite AI harness:

> "Install this skill globally: https://github.com/BrambleXu/ja-ai-polish"

For ChatGPT, Claude Code, Cursor, Hermes Agent, OpenClaw, and manual installation methods, see the
[installation guide](docs/install/en.md).

Language versions:

| Language | Guide |
|---|---|
| English | [Install](docs/install/en.md) |
| 简体中文 | [安装](docs/install/zh-CN.md) |
| 日本語 | [インストール](docs/install/ja.md) |

## Evaluation status

The repository contains 88 self-authored or redistributable evaluation cases: 24 de-AI edits,
8 direct-generation cases, 20 false positives, 16 scene cases, 12 fidelity cases, and 8 voice
cases. Deterministic structure and fidelity checks run without an API key. Human blind-review
scores will be published after the release evaluation is completed; no result is claimed early.
See the [validation status and pending release gates](docs/validation.md).

## Known limits

- Naturalness is contextual and cannot be reduced to a phrase blacklist.
- Sparse briefs cannot produce grounded specificity.
- Legal, HR, academic, and other high-risk formal text needs a qualified human review.
- The skill improves writing quality; it does not prove authorship.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Contributions should include a trigger example, a
false-positive example, and a fidelity regression whenever a rule changes.

## License

[MIT](LICENSE)
