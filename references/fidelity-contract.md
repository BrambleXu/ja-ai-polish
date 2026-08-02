# Fidelity contract

## Contents

- Input ledger
- Priority
- Permitted operations
- Mandatory audit
- Uncertainty

## Input ledger

Build the ledger before writing:

| Branch | Evidence boundary |
|---|---|
| `write` | Facts, opinions, actors, actions, objects, dates, constraints, forbidden content, and voice samples explicitly supplied in the brief |
| `edit` | Facts, opinions, relations, modality, register, and protected spans present in the source |
| `detect` | Source text; quote evidence exactly and make no content claims beyond it |

Represent at least:

- names, organizations, products, terms, numbers, dates, prices, units, and versions;
- commands, paths, URLs, code, quotations, and attributed sources;
- actor → action → object relations;
- negation, conditions, causality, possibility, obligation, permission, and commitment;
- user-specified no-change text.

## Priority

1. Preserve facts and protected spans.
2. Follow explicit requirements and audience.
3. Follow repeated voice traits.
4. Apply the Scene Pack.
5. Apply general pattern rules.

## Permitted operations

- Reorder only when the logical and temporal relations remain unchanged.
- Compress repetition only when no independent proposition disappears.
- Replace an abstraction with a concrete fact only when that fact already exists in the input.
- Keep uncertainty at the same strength; do not convert a hypothesis into a fact or a plan into a
  commitment.
- Preserve the source register unless the user explicitly requests a change.

## Mandatory audit

Compare the candidate against the ledger and verify:

1. Every protected token is byte-for-byte intact where required.
2. Every number still modifies the same fact.
3. Actors, actions, objects, ownership, and responsibility are unchanged.
4. Negation, conditions, causality, possibility, obligation, and deadlines retain their force.
5. No input fact needed for the purpose has disappeared.
6. No unsupported fact, experience, opinion, citation, emotion, or conclusion has appeared.
7. Any bounded deletion candidate is quoted verbatim outside the candidate draft.

## Uncertainty

For `edit`, preserve the original expression and report a fidelity warning when a safe
interpretation is unavailable. For `write`, leave a visible placeholder or ask one focused
question. Never fill a gap for fluency.

