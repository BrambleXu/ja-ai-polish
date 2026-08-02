# Japanese de-AI patterns

## Contents

- Operating rule
- Paragraph score
- Rule catalog
- Trigger and false-positive examples
- Residual audit

## Operating rule

Diagnose observable writing behavior. Do not infer whether AI wrote the text. A phrase is evidence
only when its density, position, function, missing support, and scene make it a problem.

Normal Japanese such as `です・ます`, `一方`, `つまり`, `〜ておく`, `重要`, and `実施する` is
not prohibited. Keep it when it performs a real function.

## Paragraph score

| Category | Score |
|---|---|
| `JA-GRAM`, `JA-VAGUE`, `JA-HEDGE`, `JA-DISCOURSE`, `JA-META`, `JA-CLOSING`, `JA-TRANSLATION`, `JA-EMPATHY` | 1 independent signal = 1; 2 or more = 2; cap 2 per category per paragraph |
| `JA-SPECIFICITY` | 2 when a strong evaluation lacks an input-grounded actor, condition, metric, consequence, or action |
| `JA-STANCE` | 2 when advice is expected but the paragraph only balances possibilities without a condition or choice |
| `JA-RHYTHM` | 3 for a four-sentence window with mechanically similar lengths or endings |

Interpret totals:

- `0–2`: keep.
- `3–4`: low confidence; report in `detect`, keep in standard `edit`.
- `5+`: rewrite candidate, subject to the False Positive Gate, scene, voice, and fidelity contract.

## Rule catalog

| ID | 日本語名・説明 | Observable evidence | Default severity | Minimal strategy | False Positive Gate |
|---|---|---|---|---|---|
| `JA-GRAM-001` | 冗長な可能表現 — 短い可能形で足りる箇所を長くする | Repeated `〜することができます／可能です` where direct potential form carries the same meaning | medium | Use `〜できます` | Keep when possibility itself is contrasted or legally qualified |
| `JA-GRAM-002` | 過剰な名詞化 — 単純な動作を名詞と形式動詞に分ける | Dense noun + `行う／実施する／図る` hides a simple action | medium | Restore the direct verb | Keep established formal terminology in policy, contracts, or procedures |
| `JA-VAGUE-001` | 根拠のない評価 — 評価基準を示さず価値を断定する | `重要／効果的／最適／包括的` asserts value without an input-grounded reason | medium | State an existing consequence, metric, or condition; otherwise delete the empty evaluation without replacing it | Keep when the next sentence supplies the criterion or the term has a defined technical meaning |
| `JA-HEDGE-001` | 根拠に比べて弱い判断 — 観察済みの結論を不要にぼかす | `〜と言えるでしょう／考えられます` weakens a conclusion despite available evidence | medium | Name the evidence and calibrated conclusion | Keep genuine uncertainty, academic caution, and risk language |
| `JA-HEDGE-002` | 判断回避 — 求められた選択を一般論で避ける | `場合によります／一概には言えません` replaces a requested decision | high | State known branches and a conditional recommendation | Keep when the information truly cannot support a decision; report the missing input |
| `JA-DISCOURSE-001` | 接続語の過剰使用 — 明らかな関係まで毎回ラベル付けする | Repeated paragraph-initial `また／さらに／一方／つまり` labels relations already clear | medium | Remove labels without a logical job; keep true contrast | Keep connectors needed to prevent misreading, especially in formal argument |
| `JA-META-001` | 構成の予告 — 内容より先に文章の進行を説明する | `本記事では／以下の3点から／順番に見ていきましょう` announces structure instead of content | medium | Enter the subject or finding directly; do not substitute `説明します／お伝えします` | Keep short navigation in long reference material or accessibility-sensitive instructions |
| `JA-META-002` | 読者への過剰な前置き — 実際の準備ではなく案内として `〜ておく` を使う | `〜しておきたい／押さえておきましょう` is used as reader-management rather than preparation | low | State the premise or caution directly | Keep literal preparatory meaning such as `保存しておきます` |
| `JA-CLOSING-001` | 定型的な結び — 実質的な結論なしに文章を閉じる | `今後の発展が期待されます／ぜひ参考にしてください` ends without a conclusion | high | End with an existing decision, limitation, next step, or result; otherwise delete the shell | Keep an explicitly requested call to action supported by context |
| `JA-TRANSLATION-001` | 翻訳調・誇張表現 — 具体的な動作を英語的な比喩や抽象語に置き換える | Business-English calques or grand metaphors replace concrete action: `重要な役割を果たす`, `シームレスな体験`, `価値を創造する` | medium | Name the actor and actual action or effect already in the input | Keep accepted product terminology and intentional brand copy |
| `JA-RHYTHM-001` | 均一な文長 — 四文の長さと拍子が機械的にそろう | Four consecutive sentences have narrowly similar length and cadence | high | Combine, split, or reorder only where meaning permits | Keep checklists, specifications, safety instructions, and intentional parallelism |
| `JA-RHYTHM-002` | 句末の機械的反復 — 機能のない同一語尾が四文続く | Four consecutive sentences repeat the same ending without functional parallelism | medium | Vary syntax through natural information grouping | Keep consistent polite register; do not vary endings merely for decoration |
| `JA-SPECIFICITY-001` | 具体性の不足 — 強い主張に主体・条件・指標・結果・行動がない | Strong claim lacks actor, condition, metric, consequence, scene, or action present in the input | high | Supply only input-grounded specifics; otherwise flag the gap | Do not invent specifics to satisfy this rule |
| `JA-STANCE-001` | 立場の不足 — 判断が必要なのに条件や選択を示さない | A decision-oriented passage lists pros and cons but gives no choice or selection condition | high | State the input-grounded condition or author choice | Keep neutral comparison when the purpose is reference, not recommendation |
| `JA-EMPATHY-001` | 機械的な共感 — 関係に合わない一般的な称賛を置く | `素晴らしい質問ですね／興味深い観点です` adds generic praise mismatched to relationship | low–medium | Respond directly or acknowledge the concrete issue | Keep praise that is specific, sincere, and suitable for the relationship |

## Trigger and false-positive examples

| ID | Rewrite candidate | Acceptable use |
|---|---|---|
| `JA-GRAM-001` | `設定を変更することができます。` → `設定は変更できます。` | `変更できる場合とできない場合があります。` contrasts possibility |
| `JA-GRAM-002` | `内容の確認を行います。` → `内容を確認します。` | `避難訓練を実施します。` is a conventional event description |
| `JA-VAGUE-001` | `この設定は非常に重要です。` without a reason | `この設定は重要です。無効にすると外部から閲覧できます。` |
| `JA-HEDGE-001` | `主因だと考えられるでしょう。` despite decisive logs | `現時点では主因の一つと考えています。調査は継続中です。` |
| `JA-HEDGE-002` | `ケースバイケースです。` as the whole recommendation | `利用人数と権限要件が未定のため、現時点では判断できません。` |
| `JA-DISCOURSE-001` | Every paragraph begins `さらに` or `一方` | One `一方` marks a real trade-off between accuracy and cost |
| `JA-META-001` | `本記事では3つの特徴を解説します。` before a short post | A long manual lists its chapters to help navigation |
| `JA-META-002` | `ここで注意点を確認しておきましょう。` → `注意点は1つです。` | `念のためログを保存しておきます。` |
| `JA-CLOSING-001` | `今後ますます重要になるでしょう。` | `次回リリースは10月です。` already carries a real next step |
| `JA-TRANSLATION-001` | `検索で新たな価値を創造します。` | A brand guide explicitly requires its established slogan |
| `JA-RHYTHM-001` | Four same-length benefit sentences | Four short emergency steps intentionally use parallel form |
| `JA-RHYTHM-002` | Four descriptive sentences all end in `〜です` | A requirements list consistently uses `〜すること` |
| `JA-SPECIFICITY-001` | `この手法は非常に効果的です。` with no evidence | `nDCG@10は0.61から0.69に上がりました。` |
| `JA-STANCE-001` | `メリットもデメリットもあり、総合判断が重要です。` | A glossary neutrally compares two methods without advising |
| `JA-EMPATHY-001` | `素晴らしい質問ですね。` before every answer | `ご指摘の点が今回の主な論点です。` names the issue |

## Residual audit

After generating or editing, score again. Recheck any paragraph at `5+`. Make only a safe,
localized correction. Allowlist intentional scene or voice behavior instead of degrading facts,
register, accessibility, or useful parallel structure.

Audit semantic substitutions as well as phrases. `完了／公開／合格` does not support
`効果的／成功／高品質／価値がある`; a rewrite that adds such an evaluation fails fidelity even
when it sounds natural. Replacing `解説します` with `説明します／お伝えします` also leaves the
same meta-writing pattern in place.
