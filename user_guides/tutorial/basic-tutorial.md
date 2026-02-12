# 基本チュートリアル / Basic Tutorial

## エージェントの使い方 / How to Use Agents

### エージェントの種類 / Agent Types

1. **管理エージェント** - システム管理・監視
2. **データエージェント** - データ収集・分析
3. **コミュニケーションエージェント** - 通知・メッセージング
4. **タスクエージェント** - 具体的なタスク実行

### エージェントの起動 / Starting an Agent

```bash
# 特定のエージェントを起動
python3 agents/<agent-name>/agent.py

# 引数を指定して起動
python3 agents/<agent-name>/agent.py --config config.json
```

### エージェントの設定 / Agent Configuration

各エージェントの `config.json` で動作を設定します：

```json
{
  "enabled": true,
  "log_level": "INFO",
  "settings": {
    "interval": 60
  }
}
```

### エージェントへの問い合わせ / Querying Agents

エージェントは自然言語で応答します：

- 「今日の天気を教えて」
- 「メールを送って」
- 「タスクを追加して」
