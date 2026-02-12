#!/usr/bin/env python3
"""
External Integration Orchestrator
外部サービス統合プロジェクトのオーケストレーター

タスク:
1. google-calendar-integration - Google Calendar API統合
2. notion-integration - Notion API統合
3. slack-integration - Slack連携
4. teams-integration - Teams連携
5. webhook-integration - Webhook連携
"""

import os
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

class ExternalIntegrationOrchestrator:
    def __init__(self, base_dir: str = "/workspace/integrations"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)

        self.progress_file = Path("/workspace/external_integration_progress.json")
        self.progress = self.load_progress()

        # タスク定義
        self.tasks = [
            {
                "id": "google-calendar-integration",
                "name": "Google Calendar API統合",
                "description": "Google Calendar APIを統合して、カレンダーイベントの同期・管理を行う",
                "priority": 1,
                "estimated_time": "30分",
                "dependencies": []
            },
            {
                "id": "notion-integration",
                "name": "Notion API統合",
                "description": "Notion APIを統合して、データベース・ページの同期を行う",
                "priority": 2,
                "estimated_time": "30分",
                "dependencies": []
            },
            {
                "id": "slack-integration",
                "name": "Slack連携",
                "description": "Slack APIを統合して、通知・メッセージ送信を行う",
                "priority": 3,
                "estimated_time": "30分",
                "dependencies": []
            },
            {
                "id": "teams-integration",
                "name": "Teams連携",
                "description": "Microsoft Teams APIを統合して、通知・メッセージ送信を行う",
                "priority": 4,
                "estimated_time": "30分",
                "dependencies": []
            },
            {
                "id": "webhook-integration",
                "name": "Webhook連携",
                "description": "汎用的なWebhookシステムを実装して、外部サービスとの連携を行う",
                "priority": 5,
                "estimated_time": "30分",
                "dependencies": []
            }
        ]

    def load_progress(self) -> Dict:
        if self.progress_file.exists():
            with open(self.progress_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "started_at": None,
            "completed_at": None,
            "tasks": {},
            "total_tasks": len(self.tasks),
            "completed_tasks": 0
        }

    def save_progress(self):
        self.progress["total_tasks"] = len(self.tasks)
        self.progress["completed_tasks"] = sum(
            1 for task_id, status in self.progress["tasks"].items()
            if status.get("status") == "completed"
        )
        with open(self.progress_file, "w", encoding="utf-8") as f:
            json.dump(self.progress, f, ensure_ascii=False, indent=2)

    def start_project(self):
        self.progress["started_at"] = datetime.now().isoformat()
        self.save_progress()
        print(f"🚀 外部サービス統合プロジェクト開始: {self.progress['started_at']}")

    def complete_project(self):
        self.progress["completed_at"] = datetime.now().isoformat()
        self.save_progress()
        print(f"🎉 外部サービス統合プロジェクト完了: {self.progress['completed_at']}")

    def get_task_by_id(self, task_id: str) -> Optional[Dict]:
        for task in self.tasks:
            if task["id"] == task_id:
                return task
        return None

    def can_start_task(self, task: Dict) -> bool:
        if task["id"] in self.progress["tasks"]:
            return False
        for dep_id in task["dependencies"]:
            dep_status = self.progress["tasks"].get(dep_id, {}).get("status")
            if dep_status != "completed":
                return False
        return True

    def get_available_tasks(self) -> List[Dict]:
        available = []
        for task in self.tasks:
            if self.can_start_task(task):
                available.append(task)
        # 優先順位でソート
        available.sort(key=lambda x: x["priority"])
        return available

    def update_task_status(self, task_id: str, status: str, result: Optional[Dict] = None):
        if task_id not in self.progress["tasks"]:
            self.progress["tasks"][task_id] = {
                "started_at": None,
                "completed_at": None,
                "status": "pending"
            }

        if status == "in_progress" and not self.progress["tasks"][task_id]["started_at"]:
            self.progress["tasks"][task_id]["started_at"] = datetime.now().isoformat()

        self.progress["tasks"][task_id]["status"] = status

        if status == "completed":
            self.progress["tasks"][task_id]["completed_at"] = datetime.now().isoformat()

        if result:
            self.progress["tasks"][task_id]["result"] = result

        self.save_progress()

    def execute_task(self, task: Dict) -> bool:
        task_id = task["id"]
        print(f"\n📋 タスク開始: {task['name']} ({task_id})")

        self.update_task_status(task_id, "in_progress")

        # サブエージェントにタスクを委譲
        prompt = f"""
あなたは外部サービス統合のエキスパートです。

以下のタスクを実行してください：

タスク: {task['name']}
ID: {task['id']}
説明: {task['description']}

実行内容:
1. {self.base_dir}/ 下に適切なディレクトリを作成
2. APIクライアント/統合モジュールを実装
3. README.mdを作成（日本語と英語のバイリンガル）
4. requirements.txtを作成（必要な依存関係）
5. 簡単なテストスクリプトを作成

要件:
- 適切なエラーハンドリング
- 環境変数から設定を読み込む
- ログ機能
- ドキュメントの充実

完了したら、作成したファイルのパスを報告してください。
"""

        try:
            # サブエージェントを起動してタスクを実行
            result = subprocess.run(
                ["python3", "-m", "openclaw.cli", "chat", "-m", "zai/glm-4.7", "-t", prompt],
                cwd="/workspace",
                capture_output=True,
                text=True,
                timeout=3600  # 1時間タイムアウト
            )

            if result.returncode == 0:
                self.update_task_status(task_id, "completed", {
                    "output": result.stdout
                })
                print(f"✅ タスク完了: {task['name']}")
                return True
            else:
                self.update_task_status(task_id, "failed", {
                    "error": result.stderr
                })
                print(f"❌ タスク失敗: {task['name']}")
                return False

        except subprocess.TimeoutExpired:
            self.update_task_status(task_id, "failed", {
                "error": "Timeout"
            })
            print(f"❌ タスクタイムアウト: {task['name']}")
            return False
        except Exception as e:
            self.update_task_status(task_id, "failed", {
                "error": str(e)
            })
            print(f"❌ タスクエラー: {task['name']} - {e}")
            return False

    def run(self, batch_size: int = 2):
        self.start_project()

        while True:
            available = self.get_available_tasks()
            if not available:
                break

            # バッチサイズ分のタスクを並列実行
            batch = available[:batch_size]

            for task in batch:
                self.execute_task(task)

            # 少し待機
            time.sleep(5)

        self.complete_project()
        self.print_summary()

    def print_summary(self):
        print("\n" + "="*50)
        print("📊 外部サービス統合プロジェクト 進捗サマリー")
        print("="*50)
        print(f"開始時刻: {self.progress['started_at']}")
        print(f"完了時刻: {self.progress['completed_at']}")
        print(f"全タスク数: {self.progress['total_tasks']}")
        print(f"完了タスク: {self.progress['completed_tasks']}")
        print(f"進捗率: {self.progress['completed_tasks']}/{self.progress['total_tasks']} ({self.progress['completed_tasks']/self.progress['total_tasks']*100:.1f}%)")
        print("\nタスク詳細:")
        for task_id, status in self.progress["tasks"].items():
            task = self.get_task_by_id(task_id)
            status_icon = "✅" if status["status"] == "completed" else "❌"
            print(f"  {status_icon} {task['name']}: {status['status']}")
        print("="*50)

    def get_status(self) -> Dict:
        return self.progress


def main():
    orchestrator = ExternalIntegrationOrchestrator()

    import sys
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "status":
            print(json.dumps(orchestrator.get_status(), ensure_ascii=False, indent=2))
            return
        elif cmd == "reset":
            orchestrator.progress_file.unlink(missing_ok=True)
            print("✅ 進捗をリセットしました")
            return

    # プロジェクトを実行
    orchestrator.run(batch_size=2)


if __name__ == "__main__":
    main()
