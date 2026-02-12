# 外部サービス連携ガイド / External Service Integration Guide

## Slack連携 / Slack Integration

### ステップ1: Slack App作成 / Step 1: Create Slack App

1. https://api.slack.com/apps にアクセス
2. "Create New App" をクリック
3. OAuth Permissionsで以下を設定:
   - `chat:write`
   - `channels:read`

### ステップ2: トークン設定 / Step 2: Configure Token

```json
{
  "slack": {
    "bot_token": "xoxb-...",
    "channel_id": "C..."
  }
}
```

### ステップ3: メッセージ送信 / Step 3: Send Message

```python
from integrations.slack.slack_client import SlackClient

client = SlackClient("xoxb-...")
client.send_message("C...", "Hello from AI Agent!")
```

## Notion連携 / Notion Integration

### ステップ1: Integration作成 / Step 1: Create Integration

1. https://www.notion.so/my-integrations にアクセス
2. "New integration" をクリック
3. APIキーをコピー

### ステップ2: ページ共有 / Step 2: Share Page

Notionページでインテグレーションを共有

### ステップ3: データ書き込み / Step 3: Write Data

```python
from integrations.notion.notion_client import NotionClient

client = NotionClient("secret_...")
client.create_page("My Database", {
    "title": "New Item",
    "status": "In Progress"
})
```
