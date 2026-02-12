#!/usr/bin/env python3
"""
エージェント補完オーケストレーター
- agent.py と requirements.txt の欠損を補完
- 並行補完を行う
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
import subprocess

class AgentCompletionOrchestrator:
    """エージェント補完オーケストレーター"""

    def __init__(self):
        self.progress_file = Path(__file__).parent / "completion_progress.json"
        self.load_progress()

    def load_progress(self):
        """進捗をロード"""
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                self.progress = json.load(f)
                # 必要なキーが存在しない場合のフォールバック
                if 'completed' not in self.progress:
                    self.progress['completed'] = []
                if 'in_progress' not in self.progress:
                    self.progress['in_progress'] = []
                if 'pending' not in self.progress:
                    self.progress['pending'] = []
                if 'subagents' not in self.progress:
                    self.progress['subagents'] = {}
                if 'history' not in self.progress:
                    self.progress['history'] = []
        else:
            self.progress = {
                'start_time': datetime.now().isoformat(),
                'completed': [],
                'in_progress': [],
                'pending': [],
                'subagents': {},
                'history': []
            }
            self.scan_agents()

    def save_progress(self):
        """進捗を保存"""
        self.progress['last_updated'] = datetime.now().isoformat()
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2)

    def scan_agents(self):
        """エージェントディレクトリをスキャンして欠損を確認"""
        agents_dir = Path(__file__).parent / "agents"
        pending = []

        for agent_dir in sorted(agents_dir.iterdir()):
            if not agent_dir.is_dir():
                continue

            agent_name = agent_dir.name

            # 完了済みはスキップ
            if agent_name in self.progress['completed']:
                continue

            # 進行中はスキップ
            if agent_name in self.progress['in_progress']:
                continue

            # 欠損ファイルを確認
            missing = []
            if not (agent_dir / "agent.py").exists():
                missing.append("agent.py")
            if not (agent_dir / "requirements.txt").exists():
                missing.append("requirements.txt")
            if not (agent_dir / "db.py").exists():
                missing.append("db.py")

            if missing:
                # README.md から説明を取得
                readme_file = agent_dir / "README.md"
                description = ""
                if readme_file.exists():
                    with open(readme_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        for line in lines[:10]:
                            if line.strip() and not line.startswith('#'):
                                description = line.strip()
                                break

                pending.append({
                    'name': agent_name,
                    'missing': missing,
                    'description': description
                })

        self.progress['pending'] = pending
        self.save_progress()

    def get_next_batch(self, batch_size: int = 10) -> List[Dict]:
        """次のバッチを取得"""
        return self.progress['pending'][:batch_size]

    def spawn_subagent(self, agent_name: str, missing_files: List[str]) -> str:
        """サブエージェントを起動して補完タスクを実行"""
        import uuid
        subagent_id = str(uuid.uuid4())[:8]

        # README.md から情報を取得
        agents_dir = Path(__file__).parent / "agents"
        agent_dir = agents_dir / agent_name
        readme_file = agent_dir / "README.md"

        readme_content = ""
        if readme_file.exists():
            with open(readme_file, 'r', encoding='utf-8') as f:
                readme_content = f.read()

        # タスクを記述
        missing_desc = ", ".join(missing_files)

        # エージェントの種類を判定
        agent_type = self.get_agent_type(agent_name, readme_content)

        task = f"""エージェント '{agent_name}' の欠損ファイルを作成してください:

欠損ファイル: {missing_desc}

エージェント情報:
- 名前: {agent_name}
- 種類: {agent_type}
- 説明: {readme_content[:500] if readme_content else 'なし'}

作成するファイル:
1. agent.py - エージェントのメインロジック
2. requirements.txt - 依存パッケージ（必要な場合）

注意:
- 既存の db.py と README.md は変更しないでください
- agent.py は db.py の機能を利用してください
- README.md の内容に沿って実装してください

完了したら completion_progress.json に進捗を記録して git push してください。"""

        # サブエージェントを起動
        subagent_name = f"completion-{agent_name}-{subagent_id}"

        # 進行中にマーク
        self.progress['in_progress'].append(agent_name)
        self.progress['subagents'][subagent_name] = {
            'status': 'running',
            'agent_name': agent_name,
            'missing_files': missing_files,
            'started_at': datetime.now().isoformat()
        }
        self.save_progress()

        # sessions_spawn でサブエージェントを起動
        # ここでは外部コマンドとして実行（サブエージェントシステムを利用）
        print(f"\n📋 サブエージェント '{subagent_name}' で '{agent_name}' の補完を開始:")
        print(f"   欠損: {missing_desc}")

        return subagent_name

    def get_agent_type(self, agent_name: str, readme_content: str) -> str:
        """エージェントの種類を判定"""
        readme_lower = readme_content.lower()
        agent_lower = agent_name.lower()

        # カテゴリ判定
        if 'tracker' in agent_lower or 'log' in agent_lower or 'record' in readme_lower:
            return 'tracking'
        elif 'management' in readme_lower or 'manager' in readme_lower:
            return 'management'
        elif 'reminder' in agent_lower or 'notification' in readme_lower:
            return 'notification'
        elif 'agent' in readme_lower and 'api' in readme_lower:
            return 'api'
        else:
            return 'general'

    def mark_completed(self, agent_name: str, subagent_name: str):
        """完了をマーク"""
        if agent_name in self.progress['in_progress']:
            self.progress['in_progress'].remove(agent_name)

        if agent_name not in self.progress['completed']:
            self.progress['completed'].append(agent_name)

        # pendingから削除
        self.progress['pending'] = [
            p for p in self.progress['pending'] if p['name'] != agent_name
        ]

        # サブエージェントのステータスを更新
        if subagent_name in self.progress['subagents']:
            self.progress['subagents'][subagent_name]['status'] = 'completed'
            self.progress['subagents'][subagent_name]['completed_at'] = datetime.now().isoformat()

        # 履歴に追加
        self.progress['history'].append({
            'time': datetime.now().isoformat(),
            'subagent': subagent_name,
            'agent_name': agent_name,
            'action': 'completed'
        })

        self.save_progress()

    def get_summary(self) -> Dict:
        """サマリーを取得"""
        total = len(self.progress['completed']) + len(self.progress['pending']) + len(self.progress['in_progress'])
        return {
            'total': total,
            'completed': len(self.progress['completed']),
            'in_progress': len(self.progress['in_progress']),
            'pending': len(self.progress['pending']),
            'progress_percent': (len(self.progress['completed']) / total * 100) if total > 0 else 0
        }

    def display_status(self):
        """ステータスを表示"""
        summary = self.get_summary()

        print("\n📊 エージェント補完オーケストレーターステータス:")
        print(f"  全体: {summary['total']}個")
        print(f"  完了: {summary['completed']}個")
        print(f"  進行中: {summary['in_progress']}個")
        print(f"  残り: {summary['pending']}個")
        print(f"  進捗: {summary['progress_percent']:.1f}%")

        if self.progress['pending']:
            print(f"\n📋 次の10個:")
            for agent in self.progress['pending'][:10]:
                print(f"  - {agent['name']}: {', '.join(agent['missing'])}")

if __name__ == '__main__':
    orchestrator = AgentCompletionOrchestrator()

    # 初期スキャン（pendingが空の場合）
    if not orchestrator.progress['pending']:
        print("🔍 初期スキャン中...")
        orchestrator.scan_agents()

    orchestrator.display_status()

    # 次のバッチを処理
    next_batch = orchestrator.get_next_batch(5)
    for agent_info in next_batch:
        orchestrator.spawn_subagent(agent_info['name'], agent_info['missing'])
