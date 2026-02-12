
# 統合システムドキュメント

## システム概要

本システムは以下のコンポーネントで構成されています:

1. **AIエージェント群** (119エージェント)
   - 各エージェントは自律的に動作
   - SQLiteベースのデータ管理
   - Discordインターフェース

2. **オーケストレーションシステム**
   - orchestrator.py - メインオーケストレーター
   - supervisor.py - サブエージェント監視
   - dev_progress_tracker.py - 進捗管理

3. **Webダッシュボード**
   - FastAPIバックエンド
   - Chart.js可視化
   - リアルタイムステータス監視

4. **統合システム**
   - EventBus - イベントPub/Sub
   - MessageBus - 非同期メッセージング
   - WorkflowEngine - ワークフロー自動化
   - AgentDiscovery - 動的エージェント検出

5. **外部サービス統合**
   - Google Calendar
   - Notion
   - Slack
   - Teams
   - 汎用Webhook

## アーキテクチャ

```
┌─────────────────────────────────────────────────────────┐
│                     Webダッシュボード                      │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  オーケストレーター                        │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
┌───────▼──────┐ ┌──▼──────────┐ ┌▼─────────────┐
│ AIエージェント │ │ 統合システム   │ │ 外部サービス   │
└──────────────┘ └─────────────┘ └──────────────┘
        │
        └───────────┐
                    │
              ┌─────▼─────┐
              │   SQLite  │
              │ データベース│
              └───────────┘
```

## APIリファレンス

### オーケストレーター

`python3 orchestrator.py` - メインオーケストレーター実行

`python3 check_progress.py` - 進捗確認

### Webダッシュボード

`cd dashboard && python3 api.py` - APIサーバー起動

- `GET /api/agents` - エージェント一覧
- `GET /api/agents/{id}` - エージェント詳細
- `POST /api/agents/{id}/start` - エージェント起動
- `POST /api/agents/{id}/stop` - エージェント停止

### 統合システム

```python
from event_bus.event_bus import EventBus
bus = EventBus()

# イベント購読
def handler(event):
    print(f"Received: {event}")
bus.subscribe("agent.completed", handler)

# イベント発行
bus.publish("agent.completed", {"agent_id": "test-agent"})
```

## 設定

### openclaw.json

```json
{
  "agents": {
    "defaults": {
      "model": "zai/glm-4.7",
      "thinking": "low"
    }
  }
}
```

## デプロイ

### ローカルデプロイ

```bash
# 依存パッケージのインストール
pip install -r requirements.txt

# オーケストレーター起動
python3 orchestrator.py
```

### Dockerデプロイ（予定）

```bash
docker build -t ai-agent-system .
docker run -d -p 8000:8000 ai-agent-system
```

## モニタリング

- Webダッシュボード: `http://localhost:8000`
- ログ: `logs/orchestrator.log`
- 進捗: `dev_progress.json`

## トラブルシューティング

### エージェントが起動しない

1. `logs/orchestrator.log`を確認
2. エージェントのdb.py構造を確認
3. 依存パッケージがインストールされているか確認

### Webダッシュボードが接続できない

1. APIサーバーが起動しているか確認
2. ポート8000が使用可能か確認
3. CORS設定を確認
