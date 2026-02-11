# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## Lifelog (lifelog.py)

ライフログの記録・参照ツール。ワークスペース内の `lifelog.py` で SQLite ベースのエントリー管理を行う。

### Usage

```bash
python3 lifelog.py add <type> <content> [title] [tags]
python3 lifelog.py list [type]
python3 lifelog.py stats
```

### Entry Types

| Type | Purpose |
|------|---------|
| `idea` | アイデア、構想、思いつき |
| `goal` | 目標（年間、月間、短期） |
| `project` | 進行中のプロジェクト |
| `vision` | ロードマップ、長期ビジョン |
| `note` | メモ、進捗、状況記録 |
| `task` | 具体的なタスク、TODO |

### DB Schema (entries)

```sql
CREATE TABLE entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL CHECK(type IN ('idea','goal','project','vision','note','task')),
    title TEXT,
    content TEXT NOT NULL,
    status TEXT DEFAULT 'active' CHECK(status IN ('active','archived','completed')),
    priority INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Tags: `tags` テーブルと `entry_tags` で多対多紐付け。

### Examples

```bash
# タスク追加
python3 lifelog.py add task "Discord botの単体テストを書く" "bot-test" "dev,testing"

# アイデア追加
python3 lifelog.py add idea "音声要約エージェント" "voice-agent" "ai,agent"

# タスク一覧
python3 lifelog.py list task

# 全エントリー
python3 lifelog.py list
```

---

## Headless Browser (Sandbox Browser)

ブラウザ操作は **sandbox browser** (Docker コンテナ内の Chromium) を使うこと。ホスト側に Chromium やシステムライブラリ (libnspr4, libnss3 等) は不要。

### Architecture

- Docker イメージ: `openclaw-sandbox-browser:bookworm-slim`
- コンテナ内に Chromium + Xvfb + 全依存ライブラリがインストール済み
- エージェントからは `browser` ツール経由で自動的にコンテナが起動・接続される
- CDP (Chrome DevTools Protocol) でホストからコンテナ内 Chromium に接続

### Config (openclaw.json)

```json
"agents": {
  "defaults": {
    "sandbox": {
      "browser": {
        "enabled": true,
        "headless": true,
        "autoStart": true
      }
    }
  }
}
```

### Important

- スクショやウェブ操作には必ず `browser` ツールを使う (sandbox 経由で Docker 内 Chromium が使われる)
- ホスト環境で直接 `chromium` や Python Playwright を起動しない (WSL2 にはシステムライブラリが入っていない)
- コンテナは `autoStart: true` により必要時に自動起動する
- VNC (NoVNC) でブラウザの画面を確認することも可能 (headless=false + enableNoVnc=true 時)

---

Add whatever helps you do your job. This is your cheat sheet.
