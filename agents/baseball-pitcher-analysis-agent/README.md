# baseball-pitcher-analysis-agent

⚾ 投手高度分析エージェント / Pitcher Advanced Analysis Agent

## 概要 (Overview)

このエージェントは、野球の高度なデータ分析を提供します。セイバーメトリクス、機械学習による予測、投手/打者/守備の詳細分析を行います。

This agent provides advanced baseball data analysis, including sabermetrics, machine learning predictions, and detailed pitcher/batter/fielding analysis.

## 機能 (Features)

### セイバーメトリクス (Sabermetrics)
- **OPS** (On-base Plus Slugging): 出塁率 + 長打率
- **wRC+** (Weighted Runs Created Plus): 調整された得点生産
- **FIP** (Fielding Independent Pitching): 守備から独立した投手指標
- **RC** (Runs Created): 得点貢献度

### 予測モデル (Prediction Models)
- 試合結果予測
- 選手成績予測
- モデル精度追跡

### 投手分析 (Pitcher Analysis)
- ERA, WHIP, FIP
- K/9, BB/9, HR/9
- 奪三振率, ゴロ率
- 平均球速

### 打者分析 (Batter Analysis)
- AVG, OBP, SLG, OPS
- wRC+, ISO, BABIP
- 硬打球率

### 守備分析 (Fielding Analysis)
- 守備率
- DRS (Defensive Runs Saved)
- UZR (Ultimate Zone Rating)
- OAA (Outs Above Average)

## インストール (Installation)

```bash
pip install -r requirements.txt
```

## 使い方 (Usage)

### Python API

```python
from agent import BaseballPitcherAnalysisAgentAgent

# エージェント初期化
agent = BaseballPitcherAnalysisAgentAgent()

# セイバーメトリクス追加
agent.add_sabermetric("player001", "山田太郎", "ヤンキース", 2024, "batting", "OPS", 0.923)

# セイバーメトリクス取得
metrics = agent.get_sabermetrics(player_id="player001")

# 計算
ops = agent.calculate_ops(0.380, 0.543)
fip = agent.calculate_fip(20, 50, 5, 200, 180)

# 接続を閉じる
agent.get_close()
```

### Discord Bot

```
!baseball player <player_id> [season]
!baseball top <season> <stat_name>
!baseball saber <player_id> [season]
!baseball model <model_name>
!baseball fielding <player_id> [season]
```

## データベース (Database)

- `sabermetrics`: セイバーメトリクスデータ
- `predictions`: 予測データ
- `pitcher_stats`: 投手統計
- `batter_stats`: 打者統計
- `fielding_stats`: 守備統計

## 環境変数 (Environment Variables)

- `DISCORD_TOKEN`: Discordボットトークン

## ライセンス (License)

MIT License
