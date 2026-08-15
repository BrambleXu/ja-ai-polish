# ja-ai-polish のインストール

## 目次

- [1. 簡単なインストール](#1-簡単なインストール)
- [2. ChatGPT と Codex](#2-chatgpt-と-codex)
- [3. Claude Code](#3-claude-code)
- [4. Cursor](#4-cursor)
- [5. Hermes Agent](#5-hermes-agent)
- [6. OpenClaw](#6-openclaw)
- [7. インストール確認](#7-インストール確認)
- [8. トラブルシューティングと安全](#8-トラブルシューティングと安全)

## 1. 簡単なインストール

Paste this into Claude Code, Codex, or your favorite AI harness:

> 「Install this skill globally: https://github.com/BrambleXu/ja-ai-polish」

プラットフォーム別の方法、更新、トラブルシューティングは以下の各節を参照してください。

## 2. ChatGPT と Codex

### ChatGPT Skills UI

Skills を利用できる ChatGPT プランとアカウントが必要です。GitHub Release から公開済みのプラグインまたは Skill アーカイブを
ダウンロードし、**Plugins → Skills → Create → Upload from your computer** からアップロードします。アップロード前に内容を確認してください。
ワークスペースでは管理者が Skill の作成や共有を許可する必要があります。

アップロードすると個人 Skill になります。権限があれば Skill メニューからワークスペースや対象者に共有できます。ChatGPT には
リポジトリ内フォルダを使うプロジェクト単位のローカルインストールはありません。

### Codex のローカルソースインストール

確認済みのリポジトリを Codex の Skill ディレクトリへ Clone します。

```bash
git clone https://github.com/BrambleXu/ja-ai-polish.git \
  "$HOME/.codex/skills/ja-ai-polish"
```

新しい Skill が見つからない場合はクライアントを再起動します。Release に検証済みのプラグイン ZIP が添付されている場合は、
ChatGPT または Codex のプラグインインストールにその成果物を使います。

### 更新とアンインストール

Codex のローカル Clone は次のコマンドで更新します。

```bash
git -C "$HOME/.codex/skills/ja-ai-polish" pull --ff-only
```

ChatGPT UI は新しいリリースアーカイブを確認してアップロードし、新版の確認後に Skills メニューから旧版を削除します。Codex の
Clone をアンインストールするときは `$HOME/.codex/skills/ja-ai-polish` だけを削除してください。

## 3. Claude Code

Claude Code の個人 Skill は `~/.claude/skills/`、プロジェクト Skill は `.claude/skills/` に置きます。どちらか一方を選びます。

個人用、すべてのプロジェクトで利用：

```bash
mkdir -p "$HOME/.claude/skills"
git clone https://github.com/BrambleXu/ja-ai-polish.git \
  "$HOME/.claude/skills/ja-ai-polish"
```

プロジェクト用、一つのリポジトリで共有：

```bash
mkdir -p .claude/skills
git clone https://github.com/BrambleXu/ja-ai-polish.git \
  .claude/skills/ja-ai-polish
```

選んだ範囲で `git pull --ff-only` を実行して更新します。`/ja-ai-polish` で明示的に呼び出すか、description に一致する依頼で
自動選択させます。パスが `ja-ai-polish/SKILL.md` で終わることを確認し、Clone 前に第三者ファイルを確認してください。

## 4. Cursor

Cursor のプロジェクト Skill は `.cursor/skills/`、個人 Skill は `~/.cursor/skills/` に置きます。どちらか一方を選びます。

```bash
mkdir -p "$HOME/.cursor/skills"
git clone https://github.com/BrambleXu/ja-ai-polish.git \
  "$HOME/.cursor/skills/ja-ai-polish"
```

プロジェクト専用にする場合：

```bash
mkdir -p .cursor/skills
git clone https://github.com/BrambleXu/ja-ai-polish.git \
  .cursor/skills/ja-ai-polish
```

Cursor はオープン標準の `.agents/skills/` も認識しますが、同じ Skill を複数の場所へ入れないでください。`git pull --ff-only` で更新し、
`/ja-ai-polish` で呼び出します。追加後に表示されない場合は新しい Agent セッションを開始します。Clone 前に第三者ファイルを確認してください。

## 5. Hermes Agent

`hermes skills` コマンドを含む現在の Hermes Agent を使います。確認済みのブランチまたはバージョンタグから、ルートの `SKILL.md` をインストールします。

```bash
hermes skills install \
  https://raw.githubusercontent.com/BrambleXu/ja-ai-polish/main/SKILL.md
```

Hermes は明示的に参照された補助ファイルを取得し、Skill を `~/.hermes/skills/` にインストールします。`hermes skills list` で確認し、
`/ja-ai-polish` で呼び出します。更新には `hermes skills check` と `hermes skills update ja-ai-polish`、削除には
`hermes skills uninstall ja-ai-polish` を使います。スキャン結果を無条件に回避しないでください。

## 6. OpenClaw

`openclaw skills install` に対応する OpenClaw を使います。リポジトリのルートには必要な `SKILL.md` があります。タグを確認済みの値に置き換えます。

```bash
openclaw skills install git:BrambleXu/ja-ai-polish@v1.0.0
```

上のコマンドは現在のワークスペースの `skills/` にインストールします。すべてのローカル Agent で使う場合は `--global` を付け、
`~/.openclaw/skills/` にインストールします。

```bash
openclaw skills install git:BrambleXu/ja-ai-polish@v1.0.0 --global
```

Git ソースは `openclaw skills update` の追跡対象外です。新しいタグで再インストールし、`/ja-ai-polish` で呼び出します。同名の場合は
ワークスペース Skill がグローバル版より優先されます。

## 7. インストール確認

`ja-ai-polish` を明示的に呼び出し、次の三つを確認します。

```text
write：ja-ai-polish を使い、次の事実から日本語の顧客メールを書いてください：……
edit：ja-ai-polish を使い、定型的な表現を抑えてください。事実はすべて維持してください：……
detect：ja-ai-polish を使い、次の日本語を書き換えずに診断してください：本記事では詳しく解説します。
```

detect の結果には観察可能な根拠と安定した `JA-*` ルール ID が含まれる必要があります。AI が書いたと断定してはいけません。write と edit は、
与えられた事実、名前、数字、日付、コード、リンク、不確実性を維持する必要があります。

## 8. トラブルシューティングと安全

- Skill が表示されない場合はパスを確認し、クライアントを再起動するか新しい Agent セッションを開始します。
- 呼び出されない場合は `/ja-ai-polish` を使うか、`ja-ai-polish` を明示して日本語本文または brief を添えます。
- 確認済みのソース、バージョンタグ、リリースアーカイブだけをインストールまたはアップロードしてください。Skill には指示やコードを含められるため、
  プラットフォームのスキャンだけでは不十分です。
- Skill の実行時に秘密情報、ネットワーク接続、第三者依存は必要ありません。入口と参照されたランタイムファイルだけを読み込みます。

確認日：2026-08-02。[ChatGPT Skills 公式ガイド](https://help.openai.com/en/articles/20001066-skills-in-chatgpt/)、
[Claude Code Skills 公式ガイド](https://code.claude.com/docs/en/skills)、[Cursor Agent Skills 公式ガイド](https://cursor.com/docs/skills)、
[Hermes Agent Skills 公式ガイド](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills)、
[OpenClaw Skills 公式ガイド](https://docs.openclaw.ai/skills)に基づきます。
