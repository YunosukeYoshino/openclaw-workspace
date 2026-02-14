# えっちAI動画アップスケーラーエージェント

AIによるえっちコンテンツ動画の高画質化を管理するエージェント

An agent that manages AI upscaling of erotic content videos. Provides features such as resolution enhancement, noise reduction, and sharpening.

## 機能

- エントリーの追加・取得・更新・削除
- タグによる分類・検索
- 統計情報の表示
- Discordボット連携

## インストール

```bash
cd erotic-ai-video-upscaler-agent
pip install -r requirements.txt
```

## 使用方法

### Python API

```python
from agent import EroticAiVideoUpscalerAgent

agent = EroticAiVideoUpscalerAgent()
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
