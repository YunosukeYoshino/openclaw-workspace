# Instapaper Summary Agent

Instapaper RSSから記事を取得して要約し、Discordに通知するエージェントです。

## Features

- Instapaper RSSフィードから記事を自動取得
- 記事の内容を要約（簡易実装）
- 重複URLのチェック・管理（SQLiteキャッシュ）
- Discord Webhook経由で通知送信
- 古いキャッシュの自動クリーンアップ（30日）

## Installation

```bash
cd agents/instapaper-summary-agent
pip install -r requirements.txt
```

## Configuration

環境変数を設定します：

```bash
export INSTAPAPER_RSS_URL="https://www.instapaper.com/rss/XXXXX/XXXXX"
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/XXXXX/XXXXX"
export INSTAPAPER_DB_PATH="./instapaper_cache.db"  # オプション
```

## Usage

### 手動実行

```bash
python agent.py
```

### Cron設定

毎日決まった時間に実行する場合：

```bash
# 毎日9:00 JSTに実行
0 9 * * * cd /path/to/workspace/agents/instapaper-summary-agent && /usr/bin/python3 agent.py >> logs/instapaper.log 2>&1
```

## Architecture

```
agent.py         # メインエージェント
  ├── db.py      # SQLiteデータベース（重複管理）
  ├── discord.py # Discord通知
  └── requirements.txt
```

## Files

- `agent.py` - メインのエージェントロジック
- `db.py` - URLキャッシュ・重複チェック
- `discord.py` - Discord Webhook送信
- `requirements.txt` - Python依存パッケージ

## Database

SQLiteを使用して処理済みURLを管理します：

```sql
CREATE TABLE urls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT UNIQUE NOT NULL,
    title TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Summary Strategy

現在は簡易的な要約を実装しています：
- 記事のHTMLから主要なテキストを抽出
- 最初の800文字程度を要約として使用

将来の拡張：
- AIによる高度な要約（OpenAI API等）
- 要約のパーソナライズ

## License

MIT
