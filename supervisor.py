#!/usr/bin/env python3
"""
エージェント開発スーパーバイザー
- サブエージェントの監視
- エラー検出と自動回復
- 全体的な進捗管理
"""

import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

class Supervisor:
    """スーパーバイザー"""

    def __init__(self):
        self.config_file = Path(__file__).parent / "supervisor_config.json"
        self.log_file = Path(__file__).parent / "supervisor_log.json"
        self.config = {}
        self.subagents = {}
        self.load_config()

    def load_config(self):
        """設定をロード"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
                self.subagents = self.config.get('subagents', {})
        else:
            self.init_config()

    def init_config(self):
        """設定を初期化"""
        config = {
            'start_time': datetime.now().isoformat(),
            'heartbeat_interval': 300,  # 5分
            'max_restarts': 3,
            'subagents': {}
        }
        self.save_config(config)

    def save_config(self, config=None):
        """設定を保存"""
        config = config or {
            'subagents': self.subagents,
            'last_updated': datetime.now().isoformat()
        }
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)

    def register_subagent(self, name: str, session_key: str, task: str):
        """サブエージェントを登録"""
        self.subagents[name] = {
            'session_key': session_key,
            'task': task,
            'status': 'running',
            'heartbeat': datetime.now().isoformat(),
            'restart_count': 0,
            'registered_at': datetime.now().isoformat()
        }
        self.save_config()
        print(f"✅ サブエージェント '{name}' を登録しました")
        return True

    def check_heartbeat(self, name: str) -> bool:
        """サブエージェントのハートビートをチェック"""
        if name not in self.subagents:
            return False

        subagent = self.subagents[name]
        heartbeat = datetime.fromisoformat(subagent['heartbeat'])
        age = (datetime.now() - heartbeat).total_seconds()

        return age < self.config.get('heartbeat_interval', 300) * 2

    def update_heartbeat(self, name: str):
        """サブエージェントのハートビートを更新"""
        if name in self.subagents:
            self.subagents[name]['heartbeat'] = datetime.now().isoformat()
            self.save_config()
            return True
        return False

    def restart_subagent(self, name: str) -> bool:
        """サブエージェントを再起動"""
        if name not in self.subagents:
            print(f"❌ サブエージェント '{name}' が見つかりません")
            return False

        subagent = self.subagents[name]

        # 再起動回数チェック
        if subagent['restart_count'] >= self.config.get('max_restarts', 3):
            print(f"❌ '{name}' の最大再起動回数に到達しました")
            self.log_event('restart_failed', name, 'max_restarts_reached')
            return False

        # 再起動処理
        print(f"🔄 '{name}' を再起動します (試行 {subagent['restart_count'] + 1})")

        # TODO: 実際の再起動処理
        # sessions_spawnなどを使用

        subagent['restart_count'] += 1
        subagent['status'] = 'restarting'
        self.save_config()

        self.log_event('restart', name, {
            'attempt': subagent['restart_count'],
            'task': subagent['task']
        })

        return True

    def log_event(self, event_type: str, subagent: str, data: dict = None):
        """イベントをログ"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'subagent': subagent,
            'data': data or {}
        }

        logs = []
        if self.log_file.exists():
            with open(self.log_file, 'r') as f:
                logs = json.load(f)

        logs.append(log_entry)

        # 最新100件のみ保持
        if len(logs) > 100:
            logs = logs[-100:]

        with open(self.log_file, 'w') as f:
            json.dump(logs, f, indent=2)

    def get_status(self) -> Dict:
        """ステータスを取得"""
        running = 0
        error = 0
        completed = 0

        for name, subagent in self.subagents.items():
            status = subagent['status']
            if status == 'running':
                if self.check_heartbeat(name):
                    running += 1
                else:
                    error += 1
            elif status == 'completed':
                completed += 1
            elif status == 'error':
                error += 1

        return {
            'total': len(self.subagents),
            'running': running,
            'error': error,
            'completed': completed
        }

    def monitor_loop(self):
        """監視ループ"""
        print("👁️ スーパーバイザー監視ループ開始...")

        while True:
            try:
                # ステータスチェック
                status = self.get_status()

                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"\n[{timestamp}] ステータス:")
                print(f"  全体: {status['total']}")
                print(f"  実行中: {status['running']}")
                print(f"  エラー: {status['error']}")
                print(f"  完了: {status['completed']}")

                # エラーがあれば再起動を試行
                for name, subagent in self.subagents.items():
                    if subagent['status'] == 'running':
                        if not self.check_heartbeat(name):
                            print(f"⚠️ '{name}' のハートビートが途切れています")
                            self.restart_subagent(name)

            except Exception as e:
                print(f"❌ 監視中にエラーが発生: {e}")
                self.log_event('monitor_error', 'supervisor', {'error': str(e)})

            # 待機
            time.sleep(self.config.get('heartbeat_interval', 300))

if __name__ == '__main__':
    supervisor = Supervisor()

    # サブエージェントを登録
    supervisor.register_subagent(
        'dev-subagent-1',
        'agent:main:subagent:19ebb3c6-ffb1-467d-80d7-1e75f05fd3ba',
        'エージェント41-45の開発'
    )

    # ステータス表示
    status = supervisor.get_status()
    print("\n📊 スーパーバイザーステータス:")
    for key, value in status.items():
        print(f"  {key}: {value}")

    # 監視ループを開始
    supervisor.monitor_loop()
