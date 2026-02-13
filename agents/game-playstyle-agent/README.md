# Game Playstyle Agent

## 概要 / Overview

Player playstyle analysis and recommendations

プレイヤーのプレイスタイル分析と推薦

## 機能 / Features

- Playstyle detection
- Strategy recommendations
- Playstyle statistics

## データベース構造 / Database Schema

- `player_profiles`
- `playstyle_analysis`

## インストール / Installation

```bash
pip install -r requirements.txt
```

## 使用方法 / Usage

### Python スクリプトとして

```python
from agent import GamePlaystyleAgent

agent = GamePlaystyleAgent()
result = agent.analyze({})
```

### Discord Bot として

```python
from discord.ext import commands
from discord import GamePlaystyleAgent

bot = commands.Bot(command_prefix='!')
GamePlaystyleAgent.setup(bot)
```

## ライセンス / License

MIT
