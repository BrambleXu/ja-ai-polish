---
name: ja-ai-polish
description: Write and humanize Japanese text by removing observable AI-writing patterns while preserving facts, voice, and scene fit. Use when generating natural Japanese from a brief, improving AI-generated Japanese, removing AI tone, or diagnosing templated Japanese in emails, messages, social posts, repository communication, technical articles, and public writing. Does not determine whether text was written by AI.
---

# JA AI Polish

Produce publishable Japanese through a diagnosis-first editing process. Treat “AI-like” as a
set of observable writing problems, never as proof of authorship.

## Route the request

1. Select the instruction language.
   - Honor an explicit `en`, `zh-CN`, or `ja` request.
   - Otherwise use the main language of the user's request.
   - For a genuinely ambiguous mixed-language request, reuse the latest explicit conversation
     language or ask once.
   - Load exactly one flow: [English](references/instructions/en.md),
     [简体中文](references/instructions/zh-CN.md), or
     [日本語](references/instructions/ja.md).
2. Select the mode.
   - `write`: a brief is present and no draft is supplied.
   - `edit`: a draft is supplied and the user wants it made natural or less templated.
   - `detect`: the user asks for diagnosis without a rewrite.
   - `auto`: apply the rules above.
3. Select the scene.
   - Honor an explicit scene.
   - Otherwise infer it from channel, audience relationship, purpose, then structure.
   - Default an unclassified article to `public-writing`.
   - Load exactly one matching Scene Pack:
     [work email](references/scene-packs/work-email.md),
     [chat message](references/scene-packs/chat-message.md),
     [social post](references/scene-packs/social-post.md),
     [status update](references/scene-packs/status-update.md),
     [repository maintenance](references/scene-packs/repo-maintenance.md),
     [technical article](references/scene-packs/technical-article.md), or
     [public writing](references/scene-packs/public-writing.md).

## Read the references required by the branch

- Always read [Fidelity contract](references/fidelity-contract.md) and
  [Protected spans](references/protected-spans.md).
- For `write`, `edit`, or `detect`, read
  [Japanese de-AI patterns](references/de-ai-patterns.md).
- When formatting the answer, read [Output formats](references/output-formats.md).
- When the user supplies 2–5 writing samples, read
  [Voice calibration](references/voice-calibration.md).
- Read an example only when the current branch is unclear:
  [write](references/examples/write.md), [edit](references/examples/edit.md),
  [detect](references/examples/detect.md), [bounded](references/examples/bounded.md), or
  [voice calibration](references/examples/voice-calibration.md).

After routing, use the selected localized file as the only primary workflow. Execute its
`F01`–`F09` steps in order. Do not substitute an English workflow for the Chinese or Japanese file.

## Keep these invariants

Use this priority order:

1. Facts and protected spans
2. Explicit user requirements and audience
3. Repeated traits in voice samples
4. The selected Scene Pack
5. General de-AI patterns

Build an input ledger before generating or editing. Lock facts, numbers, names, terms, actor-action-
object relations, negation, conditions, commitments, uncertainty, and explicit no-change spans.

Ground every output claim in the brief (`write`) or source (`edit`). Keep uncertainty at the same
strength. Add no invented facts, experiences, opinions, first-person voice, emotion, humor,
citations, causes, or conclusions.

Treat status as status: completion, release, passage of a test, or task closure is not evidence of
quality, effectiveness, success, importance, or user value. Never infer one from the other.

Use paragraph scores only as candidates: `0–2` keep; `3–4` report in `detect` and keep in standard
`edit`; `5+` may be rewritten only after the False Positive, scene, voice, and fidelity gates.
Treat a single phrase as weak evidence. Keep severity independent from edit intensity.

Preserve already-good Japanese. Delete unsupported evaluation or generic closing shells instead of
replacing them with synonyms. In short text, remove meta-introductions completely rather than
changing `解説します` to `説明します／お伝えします`.

Audit protected values, relations, modality, register, deletions, and every evaluation or conclusion
before returning. Then re-score the result and make only a fidelity-safe residual correction.

Render all user-facing questions, headings, diagnostics, and notes in the selected instruction
language. Keep the requested target text in Japanese. A final-text-only request suppresses notes,
not either internal audit.
