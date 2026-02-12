# meal-planning-agent

## 概要 (Overview)

週間献立の計画・レシピ管理・買い物リスト生成

Weekly meal planning, recipe management, and shopping list generation

## 機能 (Features)

- 家事タスク管理 (Household chore management)
- ショッピングリスト管理 (Shopping list management)
- 請求管理・リマインダー (Bill management and reminders)
- 予算・支出追跡 (Budget and expense tracking)
- スケジュール管理 (Schedule management)
- 統計情報の表示 (Statistics display)
- Discord Botによる自然言語操作 (Natural language control via Discord Bot)

## インストール (Installation)

```bash
pip install -r requirements.txt
```

## 使用方法 (Usage)

```python
from db import Database

db = Database()

# 家事追加 (Add chore)
chore_id = db.add_chore(
    title="掃除",
    category="cleaning",
    priority=2
)

# 一覧 (List)
chores = db.list_chores(status='pending')

# 完了 (Complete)
db.update_chore(chore_id, status='completed')

# 統計 (Statistics)
stats = db.get_statistics()
```

## ライセンス (License)

MIT
