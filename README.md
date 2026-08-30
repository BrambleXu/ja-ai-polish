<div align="center">

![ja-ai-polish — Make Japanese Sound Natural](assets/ja-ai-polish-banner-en.png)

[![Agent Skill](https://img.shields.io/badge/Agent%20Skill-ja--ai--polish-635BFF?style=flat-square)](SKILL.md)
[![Eval cases: 92](https://img.shields.io/badge/eval%20cases-92-0EA5E9?style=flat-square)](evals/evals.json)
[![License: MIT](https://img.shields.io/badge/License-MIT-2EA44F?style=flat-square)](LICENSE)

[English](README.md) · [日本語](README.ja.md)

</div>

`ja-ai-polish` is an Agent Skill for reducing AI-sounding patterns and making Japanese read
naturally. It can write from a brief or polish an existing draft.

It adapts wording and structure to the actual scene, including work email, chat, social posts,
status updates, repository communication, technical articles, and public writing, while preserving
facts, register, terminology, responsibility, and authorial intent.

## What it does

| ✍️ Write | 🛠️ Edit | 🔎 Detect | 🎛️ Calibrate |
|---|---|---|---|
| Generate scene-appropriate Japanese from supplied facts and constraints. | Improve a Japanese draft with the smallest safe change. | Explain patterns and evidence without rewriting the text. | Follow repeated traits from 2–5 optional samples of the author's Japanese. |

## Suitable scope

Use it for work email, Slack or Teams messages, social posts, status updates, repository
maintenance, Qiita/Zenn articles, tutorials, blogs, note posts, and community writing. It also
removes AI-like physical line breaks across these scenes while preserving intentional formatting.

It also helps non-native Japanese writers improve their own drafts while preserving what they meant
and how they wanted to say it.

## Core principles

1. Diagnose visible behavior, not presumed authorship.
2. Preserve facts before improving style.
3. Treat a phrase as a signal, never as a banned word.
4. Route by scene and audience.
5. Prefer a supplied author voice to generic polish rules.
6. Audit every generated or edited result.

## Install

Paste this into Claude Code, Codex, or your favorite AI harness:

```text
Install this skill globally: https://github.com/BrambleXu/ja-ai-polish
```

For ChatGPT, Claude Code, Cursor, Hermes Agent, OpenClaw, and manual installation methods, see the
[installation guide](docs/install/en.md).

The installation guide is also available in [Japanese](docs/install/ja.md).

## Quick examples

**✍️ Direct generation**

```text
Use /ja-ai-polish to write a Japanese Slack update.
Facts: the API fix is complete; load testing is pending; Sato owns it and will finish by Thursday.
Return only the final message.
```

**🛠️ De-AI edit**

```text
Use /ja-ai-polish to make this Japanese draft less templated.
Preserve every number, product name, and commitment. Mode: edit; intensity: standard.

[draft]
```

**🔎 Diagnosis**

```text
Use /ja-ai-polish to diagnose this Japanese text. Do not rewrite it.
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

| Signal | Default action | Example 1 | Example 2 |
|---|---|---|---|
| Wordy grammar or nominalization | Restore a direct verb without lowering required formality | `確認を行います。` → `確認します。` | `データの分析を実施します。` → `データを分析します。` |
| Unsupported evaluation | Use an existing result, metric, or consequence; otherwise flag the gap | `処理時間が20%短くなり、非常に効果的です。` → `処理時間は20%短くなりました。` | `テストは50件すべて通過し、非常に優れた結果でした。` → `テストは50件すべて通過しました。` |
| Vague judgment or responsibility avoidance | State known conditions, judgment, or next action | `どちらを使うかはケースバイケースです。社内向けはA、社外向けはBを使います。` → `社内向けはA、社外向けはBを使います。` | `多くのエラーが発生し、件数は128件でした。` → `エラーが128件発生しました。` |
| Excess transitions | Remove connectors without a logical job | `速度が上がりました。さらに、メモリ使用量も減りました。` → `速度が上がり、メモリ使用量も減りました。` | `設定は簡単です。また、導入費用は無料です。` → `設定は簡単で、導入費用は無料です。` |
| Article navigation and reader management | Enter the content directly | `本記事ではNode.js 24とNode.js 22を比較します。` → `Node.js 24とNode.js 22を比較します。` | `本記事ではAPI v3.2の認証方法を比較します。` → `API v3.2の認証方法を比較します。` |
| Formulaic ending | End on an existing result, limit, decision, or next step | `次はWindows 11で検証する予定です。今後の発展が期待されます。` → `次はWindows 11で検証する予定です。` | `macOSでの検証は完了しました。ぜひ参考にしてください。` → `macOSでの検証は完了しました。` |
| Translationese or grand metaphor | Name the concrete actor and action | `キャッシュはDB負荷の軽減に重要な役割を果たします。` → `キャッシュはDB負荷を軽減します。` | `再ログインなしで画面を移動でき、シームレスな体験を実現します。` → `再ログインせずに画面を移動できます。` |
| Uniform sentence rhythm | Regroup information where meaning permits | `設定は簡単です。起動は速いです。料金は月額500円です。無料枠もあります。` → `設定は簡単で、起動も速いです。料金は月額500円で、無料枠もあります。` | `検索は速いです。設定は簡単です。料金は無料です。広告はありません。` → `検索は速く、設定も簡単です。料金は無料で、広告もありません。` |
| Unnatural line breaks or block-split sentences | Join ordinary prose and complete the lead around a useful block | `LLMに任せるより、\n**自分で書く**\nほうが合います。` → `LLMに任せるより、**自分で書く**ほうが合います。` | ``この方法なら、\n`npm test`\nを実行できます。`` → ``この方法なら、`npm test`を実行できます。`` |
| Missing specificity or stance | Use supplied actors, conditions, measures, and choices | `今回はAを選びます。総合的に判断することが重要です。` → `今回はAを選びます。` | `運用負荷はAが月2時間、Bが月8時間です。今回はAを選びますが、どちらにもメリットとデメリットがあります。` → `運用負荷はAが月2時間、Bが月8時間です。今回はAを選びます。` |
| Mechanical empathy | Respond to the concrete issue at the right distance | `素晴らしい質問ですね。上限は100件です。` → `上限は100件です。` | `興味深い観点です。原因は接続タイムアウトでした。` → `原因は接続タイムアウトでした。` |

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
| Technical article | technical accuracy, evidence, limits, executable detail, publishable Markdown headings |
| Public writing | grounded author voice and non-formulaic structure |

## Fidelity guarantee

Before writing, the skill builds an input ledger of names, facts, numbers, dates, code, terms,
actor-action-object relations, negation, conditions, uncertainty, and commitments. The output is
then checked against that ledger. Missing information is asked for or left visible—not invented.

## Author voice

Provide 2–5 samples to calibrate sentence rhythm, register, subject omission, directness,
punctuation, and the frequency of personal or evaluative language. The skill learns recurring
traits only; it does not reuse sample facts or memorable phrases.

## Evaluation status

The repository contains 92 self-authored or redistributable evaluation cases: 26 de-AI edits,
9 direct-generation cases, 21 false positives, 16 scene cases, 12 fidelity cases, and 8 voice
cases. Deterministic structure and fidelity checks run without an API key. Human blind-review
scores will be published after the release evaluation is completed; no result is claimed early.
See the [validation status and pending release gates](docs/validation.md).

The Pattern map examples in this README were tested with `gpt-5.6-luna / medium`.

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
