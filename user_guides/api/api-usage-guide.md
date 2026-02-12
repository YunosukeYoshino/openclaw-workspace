# API使用ガイド / API Usage Guide

## APIエンドポイント / API Endpoints

### エージェント一覧 / List Agents

```bash
curl http://localhost:8000/api/agents
```

### エージェント詳細 / Agent Details

```bash
curl http://localhost:8000/api/agents/{agent_id}
```

### エージェント起動 / Start Agent

```bash
curl -X POST http://localhost:8000/api/agents/{agent_id}/start
```

### エージェント停止 / Stop Agent

```bash
curl -X POST http://localhost:8000/api/agents/{agent_id}/stop
```

### ステータス確認 / Status Check

```bash
curl http://localhost:8000/api/status
```

### 認証 / Authentication

```bash
# トークン取得
curl -X POST http://localhost:8000/api/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'

# トークン使用
curl http://localhost:8000/api/agents \
  -H "Authorization: Bearer YOUR_TOKEN"
```
