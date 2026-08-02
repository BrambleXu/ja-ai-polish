# Install ja-ai-polish

[简体中文](zh-CN.md) | [日本語](ja.md)

Last verified: 2026-08-02 against the [ChatGPT Skills guide](https://help.openai.com/en/articles/20001066-skills-in-chatgpt/),
[Claude Code Skills guide](https://code.claude.com/docs/en/skills), [Cursor Agent Skills guide](https://cursor.com/docs/skills),
[Hermes Agent Skills guide](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills), and
[OpenClaw Skills guide](https://docs.openclaw.ai/skills).

## Contents

- [1. Quick install](#1-quick-install)
- [2. ChatGPT and Codex](#2-chatgpt-and-codex)
- [3. Claude Code](#3-claude-code)
- [4. Cursor](#4-cursor)
- [5. Hermes Agent](#5-hermes-agent)
- [6. OpenClaw](#6-openclaw)
- [7. Verify the installation](#7-verify-the-installation)
- [8. Troubleshooting and security](#8-troubleshooting-and-security)

## 1. Quick install

Paste this into Claude Code, Codex, or your favorite AI harness:

> "Install this skill globally: https://github.com/BrambleXu/ja-ai-polish"

For platform-specific methods, updates, and troubleshooting, use the sections below.

## 2. ChatGPT and Codex

### ChatGPT Skills UI

Use an eligible ChatGPT plan and account with Skills enabled. Download the published plugin or
Skill archive from the GitHub Release, then open **Plugins → Skills → Create → Upload from your
computer**. Review the archive before uploading it. Workspace administrators may need to allow
Skill creation or sharing.

An upload creates a personal Skill. Use the Skill menu to share it with the intended workspace or
people when your role allows it. ChatGPT does not install a repository-local project Skill.

### Codex local source install

Clone the reviewed repository into the Codex Skill directory:

```bash
git clone https://github.com/BrambleXu/ja-ai-polish.git \
  "$HOME/.codex/skills/ja-ai-polish"
```

Restart the client if it does not discover the new Skill. If a validated plugin ZIP is attached to
a release, prefer that artifact for ChatGPT or Codex plugin installation.

### Update and uninstall

For a local Codex clone, update the reviewed copy:

```bash
git -C "$HOME/.codex/skills/ja-ai-polish" pull --ff-only
```

For ChatGPT UI, review and upload the new release archive, then remove the old copy through the
Skills menu when the new version has passed verification. To uninstall the Codex clone, remove only
`$HOME/.codex/skills/ja-ai-polish`.

## 3. Claude Code

Claude Code supports personal Skills in `~/.claude/skills/` and project Skills in
`.claude/skills/`. Choose one scope rather than installing both.

Personal, available to all projects:

```bash
mkdir -p "$HOME/.claude/skills"
git clone https://github.com/BrambleXu/ja-ai-polish.git \
  "$HOME/.claude/skills/ja-ai-polish"
```

Project, shared with one repository:

```bash
mkdir -p .claude/skills
git clone https://github.com/BrambleXu/ja-ai-polish.git \
  .claude/skills/ja-ai-polish
```

Update the clone at the chosen scope with `git pull --ff-only`. Invoke it with `/ja-ai-polish`, or
let Claude Code select it when the request matches its description. Confirm that the path ends in
`ja-ai-polish/SKILL.md`. Review third-party files before cloning.

## 4. Cursor

Cursor supports project Skills in `.cursor/skills/` and personal Skills in `~/.cursor/skills/`.
Choose one scope:

```bash
mkdir -p "$HOME/.cursor/skills"
git clone https://github.com/BrambleXu/ja-ai-polish.git \
  "$HOME/.cursor/skills/ja-ai-polish"
```

For a project-only Skill:

```bash
mkdir -p .cursor/skills
git clone https://github.com/BrambleXu/ja-ai-polish.git \
  .cursor/skills/ja-ai-polish
```

Cursor also recognizes the open `.agents/skills/` layout, but install this Skill in only one
location. Update with `git pull --ff-only`, invoke it with `/ja-ai-polish`, and start a new Agent
session if a newly added Skill is not visible. Review third-party files before cloning.

## 5. Hermes Agent

Use a current Hermes Agent release with the `hermes skills` command. Install the root `SKILL.md`
from a reviewed branch or version tag:

```bash
hermes skills install \
  https://raw.githubusercontent.com/BrambleXu/ja-ai-polish/main/SKILL.md
```

Hermes fetches explicitly referenced support files and installs the Skill under
`~/.hermes/skills/`. Check the result with `hermes skills list` and invoke it with
`/ja-ai-polish`. Use `hermes skills check` and `hermes skills update ja-ai-polish` for updates;
use `hermes skills uninstall ja-ai-polish` to remove it. Review scan findings rather than bypassing
them blindly.

## 6. OpenClaw

Use an OpenClaw release with `openclaw skills install`. The repository root contains the required
`SKILL.md`. Replace the tag with a reviewed version:

```bash
openclaw skills install git:BrambleXu/ja-ai-polish@v1.0.0
```

The command installs into the active workspace's `skills/` directory. Add `--global` to install it
under `~/.openclaw/skills/` for all local agents:

```bash
openclaw skills install git:BrambleXu/ja-ai-polish@v1.0.0 --global
```

Git sources are not tracked by `openclaw skills update`; review the new source and reinstall with a
new version tag. Invoke the Skill with `/ja-ai-polish`. Workspace Skills override global copies of
the same name.

## 7. Verify the installation

Invoke `ja-ai-polish` explicitly and run three small checks:

```text
Write: Use ja-ai-polish to write a Japanese customer email from these facts: ...
Edit: Use ja-ai-polish to remove templated phrasing. Preserve every fact: ...
Detect: Use ja-ai-polish to diagnose this Japanese text without rewriting: 本記事では詳しく解説します。
```

The detect response should report observable evidence and stable `JA-*` rule IDs. It must not
claim that the text was written by AI. The write and edit responses must preserve supplied facts,
names, numbers, dates, code, links, and uncertainty.

## 8. Troubleshooting and security

- If the Skill is not visible, restart the client or start a new Agent session after checking the
  installation path.
- If it does not trigger, invoke `/ja-ai-polish` or explicitly name `ja-ai-polish` and include the
  Japanese text or a brief.
- Install or upload only a reviewed source, version tag, or release archive. Skills can contain
  instructions and code, so platform scanning does not replace your own review.
- The Skill runtime needs no secret, network call, or third-party dependency. It reads only the
  Skill entrypoint and referenced runtime files.
