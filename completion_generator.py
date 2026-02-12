#!/usr/bin/env python3
"""
エージェント補完ジェネレーター
- agent.py と requirements.txt のテンプレートを使って欠損ファイルを作成
"""

from pathlib import Path
import json

# agent.py テンプレート（format用プレースホルダー）
AGENT_PY_TEMPLATE = '''#!/usr/bin/env python3
"""
{description}
"""

from pathlib import Path
from datetime import datetime
from db import Database
import json

class {class_name}:
    """{class_name} - {description}"""

    def __init__(self, db_path: str = None):
        """初期化"""
        if db_path is None:
            db_path = Path(__file__).parent / "{name}.db"
        self.db = Database(str(db_path))
        self.table_name = "{table_name}"
        self._initialize_schema()

    def _initialize_schema(self):
        """データベーススキーマ初期化"""
        sql = f\"\"\"
            CREATE TABLE IF NOT EXISTS {{self.table_name}} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        \"\"\"
        self.db.execute(sql)

    def add(self, content: str, metadata: dict = None) -> int:
        """レコードを追加"""
        metadata_json = json.dumps(metadata) if metadata else None
        return self.db.insert(
            self.table_name,
            {"content": content, "metadata": metadata_json}
        )

    def get(self, record_id: int) -> dict:
        """レコードを取得"""
        return self.db.get_by_id(self.table_name, record_id)

    def list_all(self, limit: int = 100) -> list:
        """全レコードを取得"""
        return self.db.list_all(self.table_name, limit=limit)

    def update(self, record_id: int, content: str = None, metadata: dict = None) -> bool:
        """レコードを更新"""
        updates = {}
        if content is not None:
            updates["content"] = content
        if metadata is not None:
            updates["metadata"] = json.dumps(metadata)
        updates["updated_at"] = datetime.now().isoformat()

        return self.db.update(self.table_name, record_id, updates)

    def delete(self, record_id: int) -> bool:
        """レコードを削除"""
        return self.db.delete(self.table_name, record_id)

    def search(self, query: str) -> list:
        """レコードを検索"""
        return self.db.search(self.table_name, "content", query)


if __name__ == "__main__":
    agent = {class_name}()
    print(f"{{class_name}} initialized")
'''

# requirements.txt テンプレート
REQUIREMENTS_TEMPLATE = '''# Dependencies for {name}
openai>=1.0.0
python-dotenv>=1.0.0
'''

def get_agent_info(agent_name: str, readme_path: Path) -> tuple:
    """README.mdからエージェント情報を取得"""
    description = agent_name.replace("-", " ").title()
    class_name = "".join(word.capitalize() for word in agent_name.split("-"))
    table_name = agent_name.replace("-", "_")

    if readme_path.exists():
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # タイトルを取得
            lines = content.split('\n')
            for line in lines[:20]:
                if line.strip() and not line.startswith('#'):
                    description = line.strip()
                    break

    return class_name, description, table_name

def generate_agent_file(agent_name: str, agents_dir: Path):
    """agent.py を生成"""
    agent_dir = agents_dir / agent_name
    readme_path = agent_dir / "README.md"
    agent_py_path = agent_dir / "agent.py"

    class_name, description, table_name = get_agent_info(agent_name, readme_path)

    # replace() を使用（format() の辞書問題を回避）
    content = AGENT_PY_TEMPLATE.replace("{name}", agent_name)
    content = content.replace("{class_name}", class_name)
    content = content.replace("{description}", description)
    content = content.replace("{table_name}", table_name)

    with open(agent_py_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✅ Created: {agent_name}/agent.py")
    return True

def generate_requirements_file(agent_name: str, agents_dir: Path):
    """requirements.txt を生成"""
    agent_dir = agents_dir / agent_name
    requirements_path = agent_dir / "requirements.txt"

    content = REQUIREMENTS_TEMPLATE.format(name=agent_name)

    with open(requirements_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✅ Created: {agent_name}/requirements.txt")
    return True

def main():
    """メイン処理"""
    agents_dir = Path(__file__).parent / "agents"
    completion_progress = Path(__file__).parent / "completion_progress.json"

    # 進捗をロード
    if completion_progress.exists():
        with open(completion_progress, 'r') as f:
            progress = json.load(f)
    else:
        progress = {'completed': []}

    completed = set(progress.get('completed', []))

    print("🔧 エージェント補完中...\n")

    # agents ディレクトリ内の各エージェントを処理
    for agent_dir in sorted(agents_dir.iterdir()):
        if not agent_dir.is_dir():
            continue

        agent_name = agent_dir.name

        # 完了済みはスキップ
        if agent_name in completed:
            continue

        # 欠損ファイルを確認して生成
        if not (agent_dir / "agent.py").exists():
            try:
                generate_agent_file(agent_name, agents_dir)
            except Exception as e:
                print(f"❌ Failed to create {agent_name}/agent.py: {e}")

        if not (agent_dir / "requirements.txt").exists():
            try:
                generate_requirements_file(agent_name, agents_dir)
            except Exception as e:
                print(f"❌ Failed to create {agent_name}/requirements.txt: {e}")

        # 完了に追加
        if (agent_dir / "agent.py").exists() and (agent_dir / "requirements.txt").exists():
            completed.add(agent_name)
            # progress['completed'] に追加
            if 'completed' not in progress:
                progress['completed'] = []
            if agent_name not in progress['completed']:
                progress['completed'].append(agent_name)

    # 進捗を保存
    progress['completed'] = sorted(list(completed))
    with open(completion_progress, 'w') as f:
        json.dump(progress, f, indent=2)

    print(f"\n✅ 補完完了: {len(completed)}個のエージェント")

if __name__ == '__main__':
    main()
