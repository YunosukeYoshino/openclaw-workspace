# えっちコンテンツフィードバックエージェント

Erotic Content Feedback Agent

## 概要 (Overview)

えっちコンテンツのフィードバック、評価、改善提案を管理するエージェント

## 機能 (Features)

- フィードバック管理
- 評価収集
- 改善提案
- 統計分析

## インストール (Installation)

```bash
pip install -r requirements.txt
```

## 使用方法 (Usage)

### 基本的な使用 (Basic Usage)

```python
from agent import EroticFeedbackAgent

agent = EroticFeedbackAgent()
```

### Discord Botとして使用 (Using as Discord Bot)

```bash
python discord.py
```

## データベース構造 (Database Schema)

### feedback
フィードバックテーブル

### reviews
レビューテーブル

## コマンド (Commands)

- `!add_feedback <name> <data>` - Add Feedback
- `!list_feedbacks [limit]` - List All Feedback
- `!add_review <name> <data>` - Add Review
- `!list_reviewss [limit]` - List All Reviews

## ライセンス (License)

MIT License
