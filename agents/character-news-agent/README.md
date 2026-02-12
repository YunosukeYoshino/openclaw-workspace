# character-news-agent

キャラクターニュース・情報収集エージェント / Character news and information collection agent

## 機能 / Features

### 日本語 / Japanese
- キャラクター関連ニュース収集
- 新作アニメ・ゲーム情報
- キャラクターグッズ情報
- イベント・コラボ情報

### English / 英語
- Character-related news collection
- New anime/game information
- Character goods information
- Event and collaboration information

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
