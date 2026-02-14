# エッジCDNマネージャーエージェント

エッジコンテンツデリバリーネットワークの管理を担当するエージェント

An agent responsible for managing edge content delivery networks. Provides features such as caching, delivery optimization, and origin management.

## 機能

- エントリーの追加・取得・更新・削除
- タグによる分類・検索
- 統計情報の表示
- Discordボット連携

## インストール

```bash
cd edge-cdn-manager-agent
pip install -r requirements.txt
```

## 使用方法

### Python API

```python
from agent import EdgeCdnManagerAgent

agent = EdgeCdnManagerAgent()
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
