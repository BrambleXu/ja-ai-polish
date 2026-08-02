# Detect example

**Request (English):**

> Diagnose this Japanese paragraph without rewriting it:
> 本記事では3つの観点から詳しく解説します。さらに、この方法は非常に効果的です。今後の発展が期待されます。

**Output:**

| Severity | Rule ID | Source excerpt | Explanation | Suggestion |
|---|---|---|---|---|
| medium | `JA-META-001` | `本記事では3つの観点から詳しく解説します` | Announces structure without content. | Open with the actual subject or finding. |
| medium | `JA-VAGUE-001` | `非常に効果的です` | Gives no criterion or result. | Supply an existing metric or consequence; otherwise remove it. |
| high | `JA-CLOSING-001` | `今後の発展が期待されます` | Ends with a template rather than a conclusion. | State an existing next step, limit, result, or decision. |
