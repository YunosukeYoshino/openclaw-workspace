# baseball-ml-prediction-agent

## Description / 概要

### English
ML-based game prediction agent with team stats, player performance, weather data.

### 日本語
試合結果を予測するMLモデル。チーム統計、選手成績、気象データなどを入力。

## Features / 機能

### English
- Classification model for predictions
- SQLite database for storing predictions and training results
- Discord bot integration for notifications
- Comprehensive feature engineering

### 日本語
- Classificationモデルによる予測
- 予測結果と訓練データを保存するSQLiteデータベース
- 通知用Discordボット連携
- 包括的な特徴量エンジニアリング

## Installation / インストール

### English
1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables:
```bash
export DISCORD_TOKEN=your_discord_bot_token
export DISCORD_CHANNEL_ID=your_channel_id
```

### 日本語
1. 依存パッケージをインストール:
```bash
pip install -r requirements.txt
```

2. 環境変数を設定:
```bash
export DISCORD_TOKEN=your_discord_bot_token
export DISCORD_CHANNEL_ID=your_channel_id
```

## Usage / 使用方法

### English
```python
from agent import BaseballMlPredictionAgent

# Initialize agent
agent = BaseballMlPredictionAgent()
agent.initialize()

# Make prediction
input_data = {
    "sample_feature": 1.0
}
result = agent.predict(input_data)
print(result)
```

### 日本語
```python
from agent import BaseballMlPredictionAgent

# エージェントを初期化
agent = BaseballMlPredictionAgent()
agent.initialize()

# 予測を実行
input_data = {
    "sample_feature": 1.0
}
result = agent.predict(input_data)
print(result)
```

## Model Features / モデル特徴量

### English
The model uses the following features:
- team_stats\n- player_stats\n- weather\n- h2h_record

### 日本語
モデルは以下の特徴量を使用します:
- team_stats\n- player_stats\n- weather\n- h2h_record

## API Reference / APIリファレンス

### English

#### `predict(input_data: Dict[str, Any]) -> Dict[str, Any]`
Make a prediction using the trained model.

- `input_data`: Input features for prediction
- Returns: Prediction result with prediction_id, prediction, features, and timestamp

#### `train(training_data: List[Dict[str, Any]]) -> Dict[str, Any]`
Train the model with provided training data.

- `training_data`: List of training samples
- Returns: Training result with accuracy and timestamp

#### `evaluate(test_data: List[Dict[str, Any]]) -> Dict[str, Any]`
Evaluate the model performance on test data.

- `test_data`: List of test samples
- Returns: Evaluation metrics (precision, recall, f1_score)

### 日本語

#### `predict(input_data: Dict[str, Any]) -> Dict[str, Any]`
訓練済みモデルで予測を実行します。

- `input_data`: 予測用の入力特徴量
- 戻り値: prediction_id、prediction、features、timestampを含む予測結果

#### `train(training_data: List[Dict[str, Any]]) -> Dict[str, Any]`
提供された訓練データでモデルを訓練します。

- `training_data`: 訓練サンプルのリスト
- 戻り値: 正解率とタイムスタンプを含む訓練結果

#### `evaluate(test_data: List[Dict[str, Any]]) -> Dict[str, Any]`
テストデータでモデルの性能を評価します。

- `test_data`: テストサンプルのリスト
- 戻り値: 評価指標（precision、recall、f1_score）

## Database Schema / データベーススキーマ

### English
The SQLite database contains the following tables:

- `predictions`: Stores prediction results
- `training_results`: Stores training metrics
- `evaluation_results`: Stores evaluation metrics

### 日本語
SQLiteデータベースには以下のテーブルが含まれます:

- `predictions`: 予測結果を保存
- `training_results`: 訓練メトリクスを保存
- `evaluation_results`: 評価メトリクスを保存

## Discord Integration / Discord連携

### English
The agent can send prediction results to Discord:
- Set `DISCORD_TOKEN` environment variable
- Set `DISCORD_CHANNEL_ID` environment variable
- Call `start_discord_bot()` to start the bot

### 日本語
エージェントは予測結果をDiscordに送信できます:
- `DISCORD_TOKEN`環境変数を設定
- `DISCORD_CHANNEL_ID`環境変数を設定
- `start_discord_bot()`を呼び出してボットを起動

## License / ライセンス

MIT License
