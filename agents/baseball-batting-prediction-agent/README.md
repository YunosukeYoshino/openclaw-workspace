# baseball-batting-prediction-agent

## Description / 概要

### English
Predict batting performance and analyze batter tendencies.

### 日本語
打撃成績を予測し、打者の傾向を分析。

## Features / 機能

### English
- Regression model for predictions
- SQLite database for storing predictions and training results
- Discord bot integration for notifications
- Comprehensive feature engineering

### 日本語
- Regressionモデルによる予測
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
from agent import BaseballBattingPredictionAgent

# Initialize agent
agent = BaseballBattingPredictionAgent()
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
from agent import BaseballBattingPredictionAgent

# エージェントを初期化
agent = BaseballBattingPredictionAgent()
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
- batter_stats\n- pitcher_type\n- ballpark\n- weather

### 日本語
モデルは以下の特徴量を使用します:
- batter_stats\n- pitcher_type\n- ballpark\n- weather

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
