# English runtime flow

Use these stable steps in order. Complete each criterion before continuing.

## F01 — Resolve language

Use English for questions, diagnostics, headings, and notes. Keep the target text in Japanese.

**Complete when:** one instruction language is fixed.

## F02 — Resolve mode

Infer inputs from natural language; require no command syntax:

- `brief` for `write`; `text` for `edit` or `detect`;
- `mode`: `auto | write | edit | detect`, default `auto`;
- `scene`: one supported scene or `auto`;
- `intensity`: `minimal | standard | aggressive`, `edit` only, default `standard`;
- `scope`: `normal | bounded`, `edit` only;
- `voice_samples`: 2–5 optional Japanese samples;
- `output`: final text plus short notes, or final text only.

Choose `write` for a brief without a draft, `edit` for a requested rewrite, and `detect` for
diagnosis without rewriting. Use `bounded` above about 3,000 Japanese characters, for an explicit
length constraint, public long-form text, or a likely complete-sentence deletion.

**Complete when:** the mode and required input are known.

## F03 — Resolve scene

Honor an explicit scene; otherwise infer channel, audience relationship, and purpose. Load exactly
one Scene Pack. Ask only when the choice would materially change register or output; otherwise use
the strongest evidence and default an unclassified article to `public-writing`.

**Complete when:** one scene is selected or one material ambiguity has been asked about.

## F04 — Build the ledger

Extract protected spans, facts, opinions, actor-action-object relations, conditions, negation,
commitments, uncertainty, and constraints from the brief or source.

Ask only for a missing item that would materially change a fact, responsibility, register, or
result. Leave an explicit placeholder when the user declines.

**Complete when:** every claim that must survive is represented.

## F05 — Diagnose

Apply the naturalness and scene-fit gate, then the pattern score and False Positive Gate paragraph
by paragraph. In `write`, run them after the first draft.

- `0–2`: keep.
- `3–4`: report in `detect`; keep in standard `edit`; allow a careful aggressive edit.
- `5+`: rewrite candidate, still gated by scene, voice, and fidelity.

Confirm density, position, function, scene fit, and edit cost. A single phrase is weak evidence
unless `JA-USAGE-001` has both a contextual mismatch and a proposition-equivalent idiomatic
alternative. Keep already-good Japanese.

**Complete when:** every proposed change has observable evidence and a stable rule ID, and every
false-positive candidate has been tested.

## F06 — Calibrate

When voice samples exist, extract only repeated style traits. Resolve conflicts using the priority
order in `SKILL.md`. Keep the voice over Scene Pack defaults; explicit audience and relationship
requirements remain higher priority. Copy no sample facts or memorable phrases.

**Complete when:** the applicable voice and scene constraints are explicit.

## F07 — Generate or edit

For `write`, draft directly from the ledger and scene. Use only supplied actors, conditions,
actions, consequences, and decisions. Ask about or visibly leave unsupported gaps.

For `edit`, make the smallest authorized change:

- `minimal`: local changes, no paragraph reordering;
- `standard`: adjust syntax, transitions, and repetition without losing an independent fact;
- `aggressive`: reorganize and compress repetition without factual drift;
- `bounded`: keep possible complete-sentence deletions in the draft and quote them separately.

Delete an unsupported evaluation or generic closing shell instead of paraphrasing it. Preserve any
fact embedded in that sentence as a direct statement. Remove a short text's meta-introduction
instead of changing `解説します` to `説明します／お伝えします`.

Apply high-confidence `JA-USAGE-001` findings directly in `write` and `edit`. Replace only the
smallest scene-mismatched phrase, preserve the proposition and register, and introduce no action or
experience absent from the ledger.

Apply the global layout integrity gate while generating or editing: keep ordinary prose on one
physical line, and make any sentence before or after a list, quote, or table grammatically complete.
Preserve real scene boundaries, templates, code, and user-requested social formatting. When the
scene is `technical-article` and the user requests a complete Markdown article, also load its
H1/H2/H3 contract; do not apply that heading contract to other scenes.

For `detect`, return evidence, severity, rule ID, explanation, and suggestion. Return no rewritten
draft and make no authorship claim.

**Complete when:** the Japanese draft satisfies the requested mode, scene, and scope.

## F08 — Audit

Compare the draft with the ledger:

- exact values, dates, versions, names, terms, URLs, paths, commands, code, and quotations;
- actors, actions, objects, responsibility, negation, conditions, commitments, and uncertainty;
- every evaluation, effect, cause, and conclusion against a specific ledger item;
- register, scene constraints, and all authorized or bounded deletions.

Treat completion, release, or a passed test as status, not evidence of effectiveness or value. Then
run the naturalness and scene-fit gate, layout integrity gate, and residual de-AI audit. Recheck
paragraphs at `5+` and repair only safe discrepancies. Confirm that a usage edit did not invent an
action or experience, and that joining a line did not erase a real scene boundary or protected value.

**Complete when:** no protected value or relation drift remains and no unexplained paragraph scores
5 or more.

## F09 — Render

Use the localized output contract and the user's next action. For `publish` or `copy`, return only the
artifact; for `collaborative-edit` or `review`, brief commentary may appear outside the artifact.
For a complete `technical-article` Markdown artifact, begin with its single `#` title and use the
scene-specific H2/H3 contract. Other scenes do not inherit those heading rules.

**Complete when:** all headings and explanations are English and the target text remains Japanese.
