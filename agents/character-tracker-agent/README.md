# character-tracker-agent

アニメ・ゲームキャラクター追跡エージェント / Anime/Game character tracking agent

## 機能 / Features

### 日本語 / Japanese
- キャラクター情報の登録・管理
- 作品別キャラクターリスト
- キャラクター検索・フィルタリング
- キャラクタータグ・カテゴリ管理

### English / 英語
- Character registration and management
- Character lists by work
- Character search and filtering
- Character tags and category management

## インストール / Installation

```bash
pip install -r requirements.txt
```

## 使用方法 / Usage

### エージェント実行 / Running the Agent

```bash
python3 agent.py
```

### Discord Bot / Discord Bot

```bash
export DISCORD_TOKEN="your_bot_token"
python3 discord.py
```

## データベース / Database

SQLiteデータベースを使用しています。初回実行時に自動的に作成されます。

## コマンド / Commands

| コマンド / Command | 説明 / Description |
|-------------------|-------------------|
| `!add <name> <source> [description]` | キャラクターを追加 / Add character |
| `!list [source]` | キャラクターリスト表示 / List characters |
| `!search <query>` | キャラクター検索 / Search characters |
| `!stats` | 統計情報表示 / Show statistics |

## ライセンス / License

MIT License
