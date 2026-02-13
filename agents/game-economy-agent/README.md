# Game Economy Agent

## 概要 / Overview

In-game economy analysis and trading advice

ゲーム内経済分析とトレードアドバイス

## 機能 / Features

- Price tracking
- Market analysis
- Trading recommendations

## データベース構造 / Database Schema

- `market_data`
- `economy_analysis`

## インストール / Installation

```bash
pip install -r requirements.txt
```

## 使用方法 / Usage

### Python スクリプトとして

```python
from agent import GameEconomyAgent

agent = GameEconomyAgent()
result = agent.analyze({})
```

### Discord Bot として

```python
from discord.ext import commands
from discord import GameEconomyAgent

bot = commands.Bot(command_prefix='!')
GameEconomyAgent.setup(bot)
```

## ライセンス / License

MIT
