# コンプライアンスモニターエージェント

コンプライアンスの監視・管理を担当するエージェント

An agent responsible for monitoring and managing compliance. Provides features such as regulatory requirement checks, violation detection, and improvement recommendations.

## 機能

- エントリーの追加・取得・更新・削除
- タグによる分類・検索
- 統計情報の表示
- Discordボット連携

## インストール

```bash
cd compliance-monitor-agent
pip install -r requirements.txt
```

## 使用方法

### Python API

```python
from agent import ComplianceMonitorAgent

agent = ComplianceMonitorAgent()
entry_id = agent.add_entry("サンプル", "これはサンプルエントリーです", tags=["sample", "test"])
print(f"作成されたエントリーID: {entry_id}")
agent.close()
```

### Discord Bot

```bash
export DISCORD_BOT_TOKEN="your_bot_token_here"
python discord.py
```

## ライセンス

MIT License
