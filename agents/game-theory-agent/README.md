# ゲーム理論エージェント / Game Theory Agent

プレイヤー間の意思決定、ナッシュ均衡の分析、協力・競争戦略の最適化

## 概要 / Overview

Analyzes player decisions, Nash equilibrium, and optimizes cooperation/competition strategies

## 機能 / Features

- 確率計算と期待値の算出
- Monte Carloシミュレーション
- メカニクスの分析とバランスチェック
- ゲーム理論の適用
- リプレイ分析とパターン認識
- Discord Bot インテグレーション

## インストール / Installation

```bash
pip install -r requirements.txt
```

## 使用方法 / Usage

### エージェントとして使用 / As Agent

```python
from agent import GameTheoryAgent

agent = GameTheoryAgent()
result = await agent.run("calculate probability")
```

### データベースとして使用 / As Database

```python
from db import GameTheoryAgentDatabase

db = GameTheoryAgentDatabase()
simulations = db.get_simulations("combat")
```

### Discord Bot として使用 / As Discord Bot

```bash
export DISCORD_TOKEN=your_bot_token
python discord.py
```

## コマンド / Commands

- `!modeling prob [event]` - 確率計算結果 / Probability calculations
- `!modeling sim [type]` - シミュレーション結果 / Simulations
- `!modeling mech` - メカニクス一覧 / Mechanics
- `!modeling theory` - ゲーム理論分析 / Game theory analyses
- `!modeling replay [game]` - リプレイ分析 / Replay analyses
- `!modeling calc <rate>` - 確率を計算 / Calculate probability

## データベース構造 / Database Schema

### probability_calculations
- id: プライマリキー
- event_name: イベント名
- success_rate: 成功率
- calculated_probability: 計算された確率
- trials: 試行回数

### simulations
- id: プライマリキー
- simulation_type: シミュレーションタイプ
- iterations: 反復回数
- average_result: 平均結果
- results_json: 結果（JSON）
- parameters: パラメータ（JSON）

### mechanics
- id: プライマリキー
- mechanic_name: メカニクス名
- formula: 数式
- balance_score: バランススコア
- description: 説明

### game_theory_analyses
- id: プライマリキー
- scenario_name: シナリオ名
- players_count: プレイヤー数
- nash_equilibrium: ナッシュ均衡
- optimal_strategy: 最適戦略

### replays
- id: プライマリキー
- game_name: ゲーム名
- player_name: プレイヤー名
- replay_path: リプレイパス
- analysis_results: 分析結果（JSON）
- patterns_found: 見つかったパターン（JSON）

## ライセンス / License

MIT License

## 作者 / Author

OpenClaw Project
