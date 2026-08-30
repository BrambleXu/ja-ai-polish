# Output formats

Render the same semantic fields in the selected instruction language.

| Field ID | English | 日本語 |
|---|---|---|
| `final_text` | Final text | 完成稿 |
| `generation_notes` | Generation notes | 生成メモ |
| `edit_notes` | Edit notes | 修正内容 |
| `suggested_deletions` | Suggested deletions | 削除候補 |
| `fidelity_warnings` | Fidelity warnings | 忠実性に関する注意 |
| `severity` | Severity | 重要度 |
| `rule_id` | Rule ID | ルール ID |
| `source_excerpt` | Source excerpt | 原文の該当箇所 |
| `explanation` | Explanation | 問題の説明 |
| `suggestion` | Suggestion | 修正案 |

## write

Return `final_text`, then `generation_notes`. Add `fidelity_warnings` only for unresolved ambiguity.

## edit

Return `final_text`, then concise `edit_notes`. Add `suggested_deletions` only in bounded mode and
quote candidates verbatim. Add `fidelity_warnings` only for unresolved ambiguity.

## detect

Return a table with `severity`, `rule_id`, `source_excerpt`, `explanation`, and `suggestion`. Do not
return `final_text`.

## Final-text-only requests

Return only the Japanese result, without a heading. Still perform all internal audits.

## Next-action output

Choose the output envelope from the user's explicit request first, then from the next action:

- `publish` or `copy`: return only the target artifact. Start with the artifact itself; do not add a
  preface, notes, an `##` wrapper, or an outer code fence.
- `collaborative-edit`: return the edited artifact and, when useful, brief edit notes outside it.
- `review`: return a concise diagnosis; include an edited artifact only when requested.

For a complete `technical-article` Markdown artifact, the artifact itself must begin with its single
`#` title. This Markdown heading requirement does not apply to other scenes. In every scene, apply
the global layout integrity gate: keep ordinary prose lines intact and keep block-boundary sentences
grammatically complete. Preserve real scene boundaries, templates, lists, code, and user-requested
social formatting.
