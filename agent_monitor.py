#!/usr/bin/env python3
"""
エージェント監視システム
- サブエージェントの状態監視
- エラー検出時の自動再起動
- 進捗管理
"""

import time
import json
from pathlib import Path
from datetime import datetime

# 監視設定
MONITOR_INTERVAL = 60  # 監視間隔（秒）
MAX_RESTART_ATTEMPTS = 3  # 最大再起動回数

# サブエージェント設定
SUBAGENTS = {
    'dev-subagent-1': {
        'session_key': 'agent:main:subagent:19ebb3c6-ffb1-467d-80d7-1e75f05fd3ba',
        'task': 'エージェント41-45の開発',
        'status': 'running',
        'restart_count': 0,
        'last_seen': datetime.now().isoformat()
    }
}

# 監視ログ
MONITOR_LOG = Path(__file__).parent / "monitor_log.json"

def init_monitor():
    """監視システム初期化"""
    if not MONITOR_LOG.exists():
        with open(MONITOR_LOG, 'w') as f:
            json.dump({
                'start_time': datetime.now().isoformat(),
                'subagents': SUBAGENTS,
                'restart_history': []
            }, f, indent=2)
    print("✅ 監視システム初期化完了")

def check_subagent_status():
    """サブエージェントの状態を確認"""
    with open(MONITOR_LOG, 'r') as f:
        data = json.load(f)

    results = []

    for name, info in data['subagents'].items():
        status = info['status']
        restart_count = info['restart_count']
        last_seen = info['last_seen']

        # 状態チェック
        if status == 'running':
            results.append(f"✅ {name}: 実行中 (再起動: {restart_count}回)")
        elif status == 'completed':
            results.append(f"🎉 {name}: 完了")
        elif status == 'error':
            results.append(f"❌ {name}: エラー (再起動: {restart_count}回)")
        elif status == 'stopped':
            results.append(f"⏸️ {name}: 停止")

    return results

def restart_subagent(name):
    """サブエージェントを再起動"""
    with open(MONITOR_LOG, 'r') as f:
        data = json.load(f)

    if name not in data['subagents']:
        return False, "サブエージェントが見つかりません"

    info = data['subagents'][name]

    # 再起動回数チェック
    if info['restart_count'] >= MAX_RESTART_ATTEMPTS:
        return False, f"最大再起動回数に到達しました ({MAX_RESTART_ATTEMPTS}回)"

    # 再起動
    info['status'] = 'restarting'
    info['restart_count'] += 1
    info['last_seen'] = datetime.now().isoformat()

    # 再起動履歴に追加
    data['restart_history'].append({
        'name': name,
        'time': datetime.now().isoformat(),
        'restart_count': info['restart_count']
    })

    with open(MONITOR_LOG, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"🔄 {name} を再起動中... (試行 {info['restart_count']}/{MAX_RESTART_ATTEMPTS})")

    # TODO: 実際の再起動処理をここに実装
    # sessions_spawnを再度呼び出すなど

    return True, f"{name} を再起動しました"

def monitor_loop():
    """監視ループ"""
    print("👁️ 監視ループ開始...")

    while True:
        try:
            # サブエージェントの状態を確認
            status = check_subagent_status()

            # ステータス表示
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n[{timestamp}] サブエージェント状態:")
            for line in status:
                print(f"  {line}")

        except Exception as e:
            print(f"❌ 監視中にエラーが発生: {e}")

        # 次のチェックまで待機
        time.sleep(MONITOR_INTERVAL)

if __name__ == '__main__':
    init_monitor()

    # ステータスを確認
    status = check_subagent_status()
    print("\n📊 サブエージェント状態:")
    for line in status:
        print(f"  {line}")

    # 監視ループを開始
    # monitor_loop()
