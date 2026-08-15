# 安装 ja-ai-polish

## 目录

- [1. 快速安装](#1-快速安装)
- [2. ChatGPT 和 Codex](#2-chatgpt-和-codex)
- [3. Claude Code](#3-claude-code)
- [4. Cursor](#4-cursor)
- [5. Hermes Agent](#5-hermes-agent)
- [6. OpenClaw](#6-openclaw)
- [7. 验证安装](#7-验证安装)
- [8. 常见问题与安全](#8-常见问题与安全)

## 1. 快速安装

Paste this into Claude Code, Codex, or your favorite AI harness:

> “Install this skill globally: https://github.com/BrambleXu/ja-ai-polish”

平台专用的安装方式、更新方式和故障排查见下面的章节。

## 2. ChatGPT 和 Codex

### ChatGPT Skills 界面

需要可使用 Skills 的 ChatGPT 套餐和账号。先从 GitHub Release 下载已发布的插件或 Skill 压缩包，然后进入
**Plugins → Skills → Create → Upload from your computer** 上传。上传前请检查压缩包内容；工作区管理员可能需要开放
Skill 创建或共享权限。

上传后会创建个人 Skill。账号权限允许时，可通过 Skill 菜单共享给工作区或指定人员。ChatGPT 不提供仓库内目录形式的项目级本地安装。

### Codex 本地源码安装

将经过检查的仓库 Clone 到 Codex Skill 目录：

```bash
git clone https://github.com/BrambleXu/ja-ai-polish.git \
  "$HOME/.codex/skills/ja-ai-polish"
```

如果客户端没有发现新 Skill，请重启。Release 附带经过验证的插件 ZIP 时，ChatGPT 或 Codex 插件安装优先使用该发布产物。

### 更新与卸载

本地 Codex Clone 使用以下命令更新经过检查的副本：

```bash
git -C "$HOME/.codex/skills/ja-ai-polish" pull --ff-only
```

ChatGPT 界面安装则检查并上传新的发布压缩包，验证新版本后从 Skills 菜单移除旧版本。卸载 Codex Clone 时，只删除
`$HOME/.codex/skills/ja-ai-polish`。

## 3. Claude Code

Claude Code 的个人 Skill 位于 `~/.claude/skills/`，项目 Skill 位于 `.claude/skills/`。选择一个范围安装，不要重复安装。

个人级，对所有项目可用：

```bash
mkdir -p "$HOME/.claude/skills"
git clone https://github.com/BrambleXu/ja-ai-polish.git \
  "$HOME/.claude/skills/ja-ai-polish"
```

项目级，与单个仓库共享：

```bash
mkdir -p .claude/skills
git clone https://github.com/BrambleXu/ja-ai-polish.git \
  .claude/skills/ja-ai-polish
```

在所选范围内执行 `git pull --ff-only` 更新。使用 `/ja-ai-polish` 显式调用，也可以让 Claude Code 根据 description 自动选择。
确认路径以 `ja-ai-polish/SKILL.md` 结尾；Clone 前检查第三方文件。

## 4. Cursor

Cursor 的项目 Skill 位于 `.cursor/skills/`，个人 Skill 位于 `~/.cursor/skills/`。选择一个范围：

```bash
mkdir -p "$HOME/.cursor/skills"
git clone https://github.com/BrambleXu/ja-ai-polish.git \
  "$HOME/.cursor/skills/ja-ai-polish"
```

项目级 Skill：

```bash
mkdir -p .cursor/skills
git clone https://github.com/BrambleXu/ja-ai-polish.git \
  .cursor/skills/ja-ai-polish
```

Cursor 也识别开放标准的 `.agents/skills/`，但同一个 Skill 只应安装到一个位置。使用 `git pull --ff-only` 更新，显式调用
使用 `/ja-ai-polish`；新增 Skill 后未显示时，新建 Agent 会话。Clone 前检查第三方文件。

## 5. Hermes Agent

使用包含 `hermes skills` 命令的当前 Hermes Agent。从经过检查的分支或版本标签安装根目录的 `SKILL.md`：

```bash
hermes skills install \
  https://raw.githubusercontent.com/BrambleXu/ja-ai-polish/main/SKILL.md
```

Hermes 会获取明确引用的支持文件，并将 Skill 安装到 `~/.hermes/skills/`。使用 `hermes skills list` 检查结果，使用
`/ja-ai-polish` 调用。使用 `hermes skills check` 和 `hermes skills update ja-ai-polish` 更新，使用
`hermes skills uninstall ja-ai-polish` 卸载。不要盲目绕过扫描结果。

## 6. OpenClaw

使用支持 `openclaw skills install` 的 OpenClaw。仓库根目录包含所需的 `SKILL.md`。将版本标签替换为经过检查的版本：

```bash
openclaw skills install git:BrambleXu/ja-ai-polish@v1.0.0
```

上面的命令安装到当前工作区的 `skills/`。加上 `--global` 可安装到 `~/.openclaw/skills/`，供所有本地 Agent 使用：

```bash
openclaw skills install git:BrambleXu/ja-ai-polish@v1.0.0 --global
```

Git 源码不受 `openclaw skills update` 跟踪；检查新源码后，使用新的版本标签重新安装。显式调用使用 `/ja-ai-polish`。
同名时，工作区 Skill 会覆盖全局版本。

## 7. 验证安装

显式调用 `ja-ai-polish`，完成下面三个小检查：

```text
write：使用 ja-ai-polish，根据以下事实写一封日语客户邮件：……
edit：使用 ja-ai-polish 去除模板化表达，保留全部事实：……
detect：使用 ja-ai-polish 检查下面的日语，只诊断，不改写：本記事では詳しく解説します。
```

detect 输出应报告可观察证据和稳定的 `JA-*` 规则 ID，不应判断文本一定由 AI 创作。write 和 edit 必须保留提供的事实、名称、数字、日期、代码、链接和不确定性。

## 8. 常见问题与安全

- 看不到 Skill 时，检查安装路径，然后重启客户端或新建 Agent 会话。
- 未触发时，使用 `/ja-ai-polish`，或显式写出 `ja-ai-polish` 并附上日语文本或 brief。
- 只安装或上传经过检查的源码、版本标签或发布压缩包。Skill 可能包含指令和代码，平台扫描不能替代自己的检查。
- Skill 运行时不需要密钥、网络调用或第三方依赖，只读取 Skill 入口和引用的运行时文件。

核对日期：2026-08-02。依据 [ChatGPT Skills 官方文档](https://help.openai.com/en/articles/20001066-skills-in-chatgpt/)、
[Claude Code Skills 官方文档](https://code.claude.com/docs/en/skills)、[Cursor Agent Skills 官方文档](https://cursor.com/docs/skills)、
[Hermes Agent Skills 官方文档](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills)和
[OpenClaw Skills 官方文档](https://docs.openclaw.ai/skills)。
