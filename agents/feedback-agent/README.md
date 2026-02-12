# Feedback Agent (フィードバック収集エージェント)

Collect, analyze, and generate reports from user feedback.

## 機能 / Features

- フィードバック収集 (Feedback collection)
- フィードバック分析 (Feedback analysis)
- レポート生成 (Report generation)
- コメント管理 (Comment management)

## 使い方 / Usage

### フィードバック追加 / Add Feedback
```
フィードバック: UIが使いにくい。タイプ: 改善、感情: ネガティブ
feedback: UI is hard to use. Type: improvement, Sentiment: negative
```

### フィードバック一覧 / List Feedback
```
一覧: 新規
list: new
```

### 分析 / Analyze
```
分析: 30
analyze: 30
```

### レポート生成 / Generate Report
```
レポート: 7
report: 7
```

### コメント追加 / Add Comment
```
コメント: フィードバック 1 確認しました
comment: Feedback 1 Reviewed
```

## データベース / Database

SQLiteベースのデータベース (`feedback.db`) を使用します。
Uses SQLite-based database (`feedback.db`).

### テーブル / Tables

- `feedback`: フィードバック (Feedback entries)
- `feedback_comments`: コメント (Comments)
- `analysis_results`: 分析結果 (Analysis results)

## インストール / Installation

```bash
pip install -r requirements.txt
```

## 初期化 / Initialize

```bash
python db.py
```
