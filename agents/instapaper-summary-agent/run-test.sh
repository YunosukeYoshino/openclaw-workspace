#!/bin/bash
# Instapaper Summary Agent - Test Run Script

# ディレクトリ移動
cd "$(dirname "$0")"

# ログディレクトリ作成
mkdir -p logs

# 環境変数設定（必要に応じて編集）
export INSTAPAPER_RSS_URL="${INSTAPAPER_RSS_URL:-https://www.instapaper.com/rss/15272848/zQbybGzs6xEQQfBTqOG0PvSLN8}"
export DISCORD_WEBHOOK_URL="${DISCORD_WEBHOOK_URL:-}"
export INSTAPAPER_DB_PATH="./instapaper_cache.db"

# 実行
echo "Starting Instapaper Summary Agent..."
python3 agent.py

echo "Done."
