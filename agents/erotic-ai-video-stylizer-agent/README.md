# えっちAI動画スタイライザーエージェント

AIによるえっちコンテンツ動画のスタイル変換を管理するエージェント

An agent that manages AI style transformation of erotic content videos. Provides style conversion features such as anime style, retro style, and art style.

## 機能

- エントリーの追加・取得・更新・削除
- タグによる分類・検索
- 統計情報の表示
- Discordボット連携

## インストール

```bash
cd erotic-ai-video-stylizer-agent
pip install -r requirements.txt
```

## 使用方法

### Python API

```python
from agent import EroticAiVideoStylizerAgent

agent = EroticAiVideoStylizerAgent()
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
