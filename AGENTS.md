# Repository guidance

## Project identity and scope

- Use `ja-ai-polish` as the repository name and Skill name. Use `JA AI Polish` as the UI display
  name.
- Keep the project focused on writing natural Japanese and removing observable AI-writing patterns.
  Do not claim to identify whether AI authored a text or optimize for detector evasion.
- Preserve the platform-neutral Agent Skills core. Do not add platform-specific behavior to
  `SKILL.md` unless it is part of the shared open format.

## Sources of truth

- Treat `SKILL.md` as the runtime entry point and keep its frontmatter limited to `name` and
  `description`.
- Keep product UI metadata in `agents/openai.yaml`. Keep detailed runtime behavior in
  `references/` and load it progressively from `SKILL.md`.
- Keep the localized flows in `references/instructions/en.md` and `ja.md` semantically
  aligned. Preserve the stable `F01`–`F09` step IDs.
- Treat `references/de-ai-patterns.md`, `references/fidelity-contract.md`,
  `references/protected-spans.md`, and `references/voice-calibration.md` as behavioral contracts,
  not optional prose.

## Writing and rule changes

- Diagnose observable evidence in context. Never turn expressions into a simple banned-word list.
- Preserve facts, names, numbers, dates, versions, code, URLs, quotations, actor relationships,
  negation, conditions, uncertainty, commitments, register, and authorial intent.
- Prefer the smallest safe edit. Do not invent specificity, experience, emotion, opinions, causes,
  citations, or conclusions to make Japanese sound more human.
- For every added or changed `JA-*` rule, include a stable ID, a trigger example, an acceptable or
  false-positive example, a minimal edit strategy, and relevant Scene Pack exceptions.
- Keep author voice below fidelity and explicit user requirements, but above Scene Pack defaults
  and general polish rules.
- When a Scene Pack changes, edit only scene-specific guidance. Do not weaken global fidelity,
  false-positive, output, or voice-calibration contracts.

## Public and internal documentation

- Keep `README.md` and `README.ja.md` structurally and semantically aligned.
- Keep all 5 platform × 2 language installation documents aligned. Verify commands and paths
  against current official platform documentation and retain the verification date.
- Treat `docs/` as public OSS documentation. Treat the developer-material directory excluded by the
  root `.gitignore` as local-only: do not link to it from public files, track it in Git, or include
  it in release archives.
- Do not publish benchmark, platform smoke-test, or human-review results unless they were actually
  run and the evaluated revision and setup are recorded.

## Evaluation and packaging

- Add or update evaluation cases for every behavioral change. Include false-positive and fidelity
  regressions whenever a change could cause unnecessary edits or semantic drift.
- Keep evaluation data self-authored or explicitly redistributable and preserve its license marker.
- Do not edit `dist/` manually. Rebuild it with `python3 scripts/package_skill.py`.
- Keep release packages runtime-only: `SKILL.md`, `agents/`, and `references/`. Exclude public docs,
  developer docs, tests, evaluation data, and repository tooling.
- Before handing off a change, run:

  ```bash
  python3 scripts/lint_skill.py
  python3 scripts/check_fidelity.py
  python3 -m unittest discover -s tests -v
  python3 scripts/package_skill.py
  ```

## Change discipline and Git

- Make surgical changes and preserve existing structure unless the task requires otherwise.
- Do not modify unrelated wording, formatting, rules, examples, or evaluation expectations.
- Never create, amend, squash, rebase, or otherwise modify a Git commit automatically. Run
  `git commit` only when the user explicitly asks for a commit in the current request.
- Do not push, tag, publish a release, or change a remote unless the user explicitly asks.
