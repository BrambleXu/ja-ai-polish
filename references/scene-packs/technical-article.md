# Technical article

- **Goal:** explain an implementation, result, or technical choice accurately and densely.
- **Audience:** Qiita, Zenn, tutorial, engineering blog, or internal technical readers.
- **Register:** clear technical Japanese; separate observation, opinion, and general fact.
- **Information order:** problem/context → method → evidence/result → limitation → grounded choice.
- **Structure:** use headings for reader retrieval, not identical paragraph templates.
- **Personalization:** permit grounded first-hand judgment only when present in the input.
- **Protect:** code, commands, versions, paths, APIs, metrics, prerequisites, warnings, and sources.
- **Line integrity:** apply the global layout gate to ordinary prose. For a complete publishable
  Markdown article, use one H1, H2 for major sections, and H3 only for a genuine child topic under H2;
  do not create micro-sections when a prose transition is enough.

## Common failures and exceptions

Remove TED-like titles, industry-level significance claims, empty summaries, vague attribution, and
mechanical paragraph symmetry. Do not turn a personal choice into a universal best practice or
invent implementation experience.

## Markdown layout contract

Apply this contract only when the user requests a complete, publish-ready, or copy-ready Markdown
article. Do not force it onto a title candidate, excerpt, single section, summary, or diagnosis.

- The first non-empty line is the only `#` title.
- Use `##` for major sections.
- Use `###` only for a genuine child topic under the preceding `##`.
- Do not use `####` or deeper headings by default.
- Prefer a prose transition when another heading is not needed for reader retrieval.
- Do not create a heading for every short point or one/two-line paragraph.
- Keep ordinary prose paragraphs on one physical line, with one blank line between real paragraphs.
- Headings, list items, quotes, tables, images, and fenced code use their own Markdown block syntax.
- Preserve all code-block line breaks exactly.
- A block introduction must be a complete sentence; never finish its grammar after a list or quote.

The global `JA-LAYOUT-001` and `JA-LAYOUT-002` gate still applies. These examples are bad:

```markdown
ただ、生成された文章をそのまま使おうとすると、

> 文法的には正しい。意味も通じる。でも、なんとなくAIが書いた感じがする。

ということがよくあります。
```

```markdown
たとえば、

- 必要以上に丁寧
- 抽象的な表現が多い

といった文章です。
```

Rewrite the first as an inline complete sentence, or finish the lead before retaining a useful
quote. Rewrite the second as:

```markdown
よくある特徴には、次のようなものがあります。

- 必要以上に丁寧
- 抽象的な表現が多い
```

Do not ban `たとえば`、`その結果`、or `一方で`; keep them when they express a real relation in a
complete sentence.

## Output mode

- For `publish` or `copy`, return only the article artifact, beginning with `#`; do not add `以下は
  成稿です`, notes, or an outer code fence.
- For `collaborative-edit` or `review`, brief commentary is allowed outside the article when the
  user asks for it.

## Example

**Weak:** `本記事では革新的なRAGの可能性を多角的に解説します。`

**Better:** `FAQ 200件でBM25とハイブリッド検索を比較しました。nDCG@10と運用コストを記録します。`

**Accept:** a contents overview in a long tutorial where readers need non-linear navigation.

## Acceptance

Commands and conditions are executable as written, evidence supports conclusions, limitations
remain visible, ordinary prose is not manually wrapped, block-boundary sentences are complete, and
complete Markdown articles use shallow meaning-based `#`/`##`/`###` structure.
