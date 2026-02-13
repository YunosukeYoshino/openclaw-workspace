# Game Balance Agent

## 概要 / Overview

Game balance analysis and patch impact assessment

ゲームバランス分析とパッチ影響評価

## 機能 / Features

- Patch analysis
- Balance assessment
- Power level tracking

## データベース構造 / Database Schema

- `patch_history`
- `balance_changes`

## インストール / Installation

```bash
pip install -r requirements.txt
```

## 使用方法 / Usage

### Python スクリプトとして

```python
from agent import GameBalanceAgent

agent = GameBalanceAgent()
result = agent.analyze({})
```

### Discord Bot として

```python
from discord.ext import commands
from discord import GameBalanceAgent

bot = commands.Bot(command_prefix='!')
GameBalanceAgent.setup(bot)
```

## ライセンス / License

MIT
