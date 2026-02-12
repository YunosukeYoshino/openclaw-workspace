# note-taking-agent

## 概要 (Overview)

メモ・ノートの記録と整理

Memo and note recording and organization

## 機能 (Features)

- タスクの作成・追跡・完了 (Task creation, tracking, and completion)
- 時間追跡・記録 (Time tracking and recording)
- 優先度管理 (Priority management)
- 期限管理 (Due date management)
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

# タスク追加 (Add task)
task_id = db.add_task(
    title="Example Task",
    description="Description",
    priority=2
)

# 一覧 (List)
tasks = db.list_tasks(status='pending')

# 完了 (Complete)
db.update_task(task_id, status='completed')

# 統計 (Statistics)
stats = db.get_statistics()
```

## ライセンス (License)

MIT
