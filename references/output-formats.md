# Output formats

Render the same semantic fields in the selected instruction language.

| Field ID | English | 简体中文 | 日本語 |
|---|---|---|---|
| `final_text` | Final text | 成稿 | 完成稿 |
| `generation_notes` | Generation notes | 生成说明 | 生成メモ |
| `edit_notes` | Edit notes | 修改说明 | 修正内容 |
| `suggested_deletions` | Suggested deletions | 建议删除 | 削除候補 |
| `fidelity_warnings` | Fidelity warnings | 忠实性提醒 | 忠実性に関する注意 |
| `severity` | Severity | 严重度 | 重要度 |
| `rule_id` | Rule ID | 规则 ID | ルール ID |
| `source_excerpt` | Source excerpt | 原文证据 | 原文の該当箇所 |
| `explanation` | Explanation | 问题说明 | 問題の説明 |
| `suggestion` | Suggestion | 修改建议 | 修正案 |

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

