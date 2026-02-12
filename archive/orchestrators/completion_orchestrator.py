#!/usr/bin/env python3
"""
エージェント補完オーケストレーター
- 欠損ファイルを持つエージェントを特定
- サブエージェントで並行補完
- 進捗管理
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import subprocess
import os

class CompletionOrchestrator:
    """エージェント補完オーケストレーター"""

    def __init__(self):
        self.agents_dir = Path(__file__).parent / "agents"
        self.progress_file = Path(__file__).parent / "completion_progress.json"
        self.incomplete_agents = []
        self.load_progress()
        self.scan_incomplete()

    def load_progress(self):
        """進捗をロード"""
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                self.progress = json.load(f)
        else:
            self.progress = {
                'start_time': datetime.now().isoformat(),
                'completed': [],
                'in_progress': [],
                'batches': [],
                'last_updated': None
            }

    def save_progress(self):
        """進捗を保存"""
        self.progress['last_updated'] = datetime.now().isoformat()
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2)

    def scan_incomplete(self):
        """不完全なエージェントをスキャン"""
        self.incomplete_agents = []

        if not self.agents_dir.exists():
            print(f"❌ エージェントディレクトリが見つかりません: {self.agents_dir}")
            return

        for agent_dir in sorted(self.agents_dir.iterdir()):
            if not agent_dir.is_dir():
                continue

            agent_name = agent_dir.name
            missing = []

            # 必要なファイルをチェック
            required_files = ['agent.py', 'db.py', 'requirements.txt', 'README.md']

            for file_name in required_files:
                if not (agent_dir / file_name).exists():
                    missing.append(file_name)

            if missing:
                self.incomplete_agents.append({
                    'name': agent_name,
                    'missing': missing,
                    'completed': False
                })
            else:
                # 完了済み
                if agent_name not in self.progress.get('completed', []):
                    self.progress['completed'].append(agent_name)

    def get_next_batch(self, batch_size: int = 5) -> List[Dict]:
        """次のバッチを取得"""
        completed = set(self.progress.get('completed', []))
        in_progress = set(self.progress.get('in_progress', []))

        pending = []
        for agent in self.incomplete_agents:
            agent_name = agent['name']
            if agent_name not in completed and agent_name not in in_progress:
                pending.append(agent)

        return pending[:batch_size]

    def spawn_subagent_for_batch(self, batch: List[Dict]) -> str:
        """バッチ用のサブエージェントを生成"""
        if not batch:
            return None

        agent_names = [a['name'] for a in batch]
        batch_id = f"batch-{len(self.progress.get('batches', [])) + 1}"
        subagent_label = f"agent-completion-{batch_id}"

        # タスクを記述
        batch_summary = '\n'.join([
            f"- {a['name']}: 欠損ファイル: {', '.join(a['missing'])}"
            for a in batch
        ])

        task = f"""以下のエージェントを補完してください。各エージェントに対して、欠損ファイルを作成します。

エージェント:
{batch_summary}

各エージェントに対して:
1. agent.pyを作成（メインエントリーポイント）
2. db.pyを作成（SQLiteを使用）
3. requirements.txtを作成（必要なパッケージ）
4. README.mdが存在しない場合は作成（日本語と英語のバイリンガル）

補完が完了したら:
- completion_progress.jsonを更新して進捗を記録
- git add, git commit, git pushを実行

注意:
- 既存のファイルを上書きしないでください
- エージェント名を保持してください
- エラーが発生した場合は進捗ファイルに記録してください
"""

        # 進行中にマーク
        self.progress['in_progress'].extend(agent_names)
        self.progress['batches'].append({
            'id': batch_id,
            'agent_names': agent_names,
            'started_at': datetime.now().isoformat(),
            'status': 'running'
        })
        self.save_progress()

        # サブエージェントを生成
        try:
            from openclaw import spawn
            spawn(task, label=subagent_label)
            print(f"\n✅ サブエージェント '{subagent_label}' を生成しました")
            return subagent_label
        except Exception as e:
            print(f"❌ サブエージェント生成エラー: {e}")
            # エラー時は進行中から削除
            for agent_name in agent_names:
                if agent_name in self.progress['in_progress']:
                    self.progress['in_progress'].remove(agent_name)
            self.save_progress()
            return None

    def mark_completed(self, agent_names: List[str], batch_id: str):
        """完了をマーク"""
        for agent_name in agent_names:
            if agent_name not in self.progress.get('completed', []):
                self.progress['completed'].append(agent_name)

        # 進行中から削除
        for agent_name in agent_names:
            if agent_name in self.progress.get('in_progress', []):
                self.progress['in_progress'].remove(agent_name)

        # バッチを更新
        for batch in self.progress.get('batches', []):
            if batch['id'] == batch_id:
                batch['status'] = 'completed'
                batch['completed_at'] = datetime.now().isoformat()

        self.save_progress()

    def display_status(self):
        """ステータスを表示"""
        total = len(self.incomplete_agents)
        completed = len(self.progress.get('completed', []))
        in_progress = len(self.progress.get('in_progress', []))
        remaining = total - completed

        print("\n📊 エージェント補完オーケストレーター ステータス:")
        print(f"  全体: {total}個")
        print(f"  完了: {completed}個")
        print(f"  進行中: {in_progress}個")
        print(f"  残り: {remaining}個")
        print(f"  進捗: {(completed / total * 100):.1f}%" if total > 0 else "  進捗: 0%")

        if self.progress.get('in_progress'):
            print(f"\n🔄 進行中のエージェント:")
            for agent_name in self.progress['in_progress']:
                print(f"  - {agent_name}")

    def run_auto_completion(self, max_batches: int = 10, batch_size: int = 5):
        """自動補完を実行"""
        print("\n🚀 自動補完を開始します...")

        for i in range(max_batches):
            batch = self.get_next_batch(batch_size)

            if not batch:
                print("\n✅ すべてのエージェントが完了しました！")
                break

            print(f"\n📋 バッチ {i + 1}/{max_batches}:")
            self.spawn_subagent_for_batch(batch)

            # ステータス更新
            self.display_status()

        print(f"\n⏸️  {max_batches}バッチをキューに入れました。")

if __name__ == '__main__':
    orchestrator = CompletionOrchestrator()
    orchestrator.display_status()

    # 次のバッチを表示
    next_batch = orchestrator.get_next_batch()
    if next_batch:
        print(f"\n📋 次のバッチ ({len(next_batch)}個):")
        for agent in next_batch:
            print(f"  - {agent['name']}: {', '.join(agent['missing'])}")
    else:
        print("\n✅ すべてのエージェントが完了しています！")
