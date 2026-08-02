# Protected spans

## Contents

- Default protection
- Boundary protection
- User overrides
- Audit procedure

## Default protection

Protect these spans before diagnosis:

- fenced and inline code;
- shell commands, flags, file paths, URLs, email addresses, issue/PR references, and commit hashes;
- names, organization names, product names, versions, API names, and domain terms;
- dates, times, prices, percentages, quantities, units, IDs, and error messages;
- direct quotations, citation labels, and attributed sources;
- placeholders such as `<NAME>`, `{deadline}`, `TODO`, and `[要確認]`.

Do not “correct” spelling inside a protected span unless the user identifies that span as editable.

## Boundary protection

Protect the proposition around each token, not only the token:

- bind a number to what it measures;
- bind a date to its event;
- bind an action to its actor and object;
- bind a quotation to its speaker or source;
- bind a version to its product;
- bind a condition or negation to the clause it governs.

## User overrides

Treat explicitly quoted no-change text as highest priority. If the user asks to edit a normally
protected value, change only that value and re-audit its bound proposition.

## Audit procedure

Create a before/after checklist. Compare exact strings first, then compare their proposition
bindings. When a protected item appears multiple times, preserve the relevant occurrence count
unless repetition itself is explicitly in scope.

