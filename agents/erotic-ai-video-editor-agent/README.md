# えっちAI動画編集エージェント

AIによるえっちコンテンツ動画の編集を管理するエージェント

An agent that manages AI editing of erotic content videos. Provides features such as cut editing, transitions, and effect addition.

## 機能

- エントリーの追加・取得・更新・削除
- タグによる分類・検索
- 統計情報の表示
- Discordボット連携

## インストール

```bash
cd erotic-ai-video-editor-agent
pip install -r requirements.txt
```

## 使用方法

### Python API

```python
from agent import EroticAiVideoEditorAgent

agent = EroticAiVideoEditorAgent()
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
