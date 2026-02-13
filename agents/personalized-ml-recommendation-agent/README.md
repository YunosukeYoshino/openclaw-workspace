# personalized-ml-recommendation-agent

🤖 機械学習推薦エージェント / Machine Learning Recommendation Agent

## 概要 (Overview)

このエージェントは、ユーザーの嗜好を分析し、パーソナライズされたレコメンデーションを提供します。

This agent analyzes user preferences and provides personalized recommendations.

## 機能 (Features)

- **嗜好管理** (Preference Management): ユーザーの好みを記録・管理
- **行動分析** (Behavior Analysis): ユーザーの行動履歴を分析
- **クロスカテゴリ推薦** (Cross-Category Recommendation): 複数カテゴリ間の関連性を考慮した推薦
- **機械学習推薦** (ML Recommendation): 行動データに基づく機械学習による推薦
- **フィードバック学習** (Feedback Learning): ユーザーフィードバックから学習して精度向上

## インストール (Installation)

```bash
pip install -r requirements.txt
```

## 使い方 (Usage)

### Python API

```python
from agent import PersonalizedMlRecommendationAgentAgent

# エージェント初期化
agent = PersonalizedMlRecommendationAgentAgent()

# 嗜好追加
agent.add_preference("baseball", "npb-2024", 5.0, "プロ野球,日本")
agent.add_preference("game", "pokemon-scarlet", 4.0, "RPG,ポケモン")

# 分析実行
analysis = agent.analyze_preferences()
print(analysis)

# 接続を閉じる
agent.get_close()
```

### Discord Bot

```
!pref add <category> <item_id> [rating] [tags]
!pref list [category]
!pref analyze [category]
!pref recommend [category]
!pref stats
```

## データベース (Database)

- `preferences`: 嗜好データ
- `behavior_logs`: 行動ログ
- `recommendations`: 推薦履歴

## 環境変数 (Environment Variables)

- `DISCORD_TOKEN`: Discordボットトークン

## ライセンス (License)

MIT License
