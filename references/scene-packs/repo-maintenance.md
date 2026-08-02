# Repository maintenance

- **Goal:** help contributors understand a problem or change, evidence, limits, and next action.
- **Audience:** users, contributors, reviewers, and maintainers.
- **Register:** peer-to-peer, precise, and calm.
- **Information order:** problem/change → reproduction or verification → limitations/compatibility
  → next action.
- **Structure:** use headings that map to real information; keep code near the relevant claim.
- **Personalization:** restrained maintainer voice; no customer-service praise.
- **Protect:** code, commands, paths, errors, versions, issue/PR numbers, API names, and compatibility
  statements.

## Common failures and exceptions

Remove repeated restatement, launch-event language, generic value claims, and praise that delays the
answer. A README should first answer what it is, who it is for, and what it solves. Release Notes
should foreground changes, verification, limits, and compatibility.

## Example

**Weak:** `素晴らしいご報告をありがとうございます。この重要な問題について調査を行います。`

**Better:** `報告ありがとうございます。v1.4.2で再現しました。Windowsのパス処理を確認します。`

**Accept:** a standard issue template whose repeated headings separate reproducible fields.

## Acceptance

Technical tokens remain exact, the maintenance state is explicit, and the reader knows the next
step without promotional filler.

