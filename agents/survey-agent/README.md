# Survey Agent (アンケート作成エージェント)

Create, distribute, and analyze surveys.

## 機能 / Features

- アンケート作成・配布 (Survey creation and distribution)
- 回答の収集 (Response collection)
- 結果の分析 (Results analysis)

## 使い方 / Usage

### アンケート作成 / Create Survey
```
アンケート作成: 顧客満足度調査
survey create: Customer satisfaction survey
```

### 質問追加 / Add Question
```
質問追加: アンケート 1 当社のサービスにどの程度満足していますか。タイプ: 評価
question add: Survey 1 How satisfied are you with our service? Type: rating
```

### アンケート開始 / Activate Survey
```
開始: アンケート 1
start: Survey 1
```

### 回答 / Submit Response
```
回答: アンケート 1 1: 5, 2: 非常に満足
respond: Survey 1 1: 5, 2: Very satisfied
```

### 分析 / Analyze
```
分析: アンケート 1
analyze: Survey 1
```

## データベース / Database

SQLiteベースのデータベース (`survey.db`) を使用します。
Uses SQLite-based database (`survey.db`).

### テーブル / Tables

- `surveys`: アンケート (Surveys)
- `questions`: 質問 (Questions)
- `responses`: 回答 (Responses)
- `answers`: 回答内容 (Answers)

## 質問タイプ / Question Types

- `text`: テキスト / Text
- `multiple_choice`: 選択肢 / Multiple choice
- `rating`: 評価 (1-5) / Rating
- `yes_no`: はい/いいえ / Yes/No
- `checkbox`: チェックボックス / Checkbox

## インストール / Installation

```bash
pip install -r requirements.txt
```

## 初期化 / Initialize

```bash
python db.py
```
