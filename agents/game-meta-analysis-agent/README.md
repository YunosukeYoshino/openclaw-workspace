# Game Meta Analysis Agent

## 概要 / Overview

Analysis of game meta changes and trends

ゲームのメタ変化とトレンドの分析

## 機能 / Features

- Meta tracking and analysis
- Trend prediction
- Meta tier list management

## データベース構造 / Database Schema

- `game_meta_history`
- `meta_analysis_reports`

## インストール / Installation

```bash
pip install -r requirements.txt
```

## 使用方法 / Usage

### Python スクリプトとして

```python
from agent import GameMetaAnalysisAgent

agent = GameMetaAnalysisAgent()
result = agent.analyze({})
```

### Discord Bot として

```python
from discord.ext import commands
from discord import GameMetaAnalysisAgent

bot = commands.Bot(command_prefix='!')
GameMetaAnalysisAgent.setup(bot)
```

## ライセンス / License

MIT
