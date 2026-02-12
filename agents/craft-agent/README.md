# craft-agent

## 概要 (Overview)

手芸・工作のプロジェクトと材料管理

Craft and DIY project and material management

## 機能 (Features)

- プロジェクトの計画と追跡 (Project planning and tracking)
- アイテム・材料の管理 (Item and material management)
- ログ・記録の保存 (Log and record keeping)
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

# プロジェクト追加 (Add project)
project_id = db.add_project(
    title="Example Project",
    description="Description",
    category="category"
)

# 一覧 (List)
projects = db.list_projects()

# 統計 (Statistics)
stats = db.get_statistics()
```

## ライセンス (License)

MIT
