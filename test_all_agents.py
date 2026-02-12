#!/usr/bin/env python3
"""
全AIエージェント統合テスト
"""

from pathlib import Path
import subprocess
import json

AGENTS_DIR = Path("/workspace/agents")
RESULTS_DIR = Path("/workspace/test-results")

# 結果ディレクトリ
RESULTS_DIR.mkdir(exist_ok=True)

def test_agent(agent_name):
    """エージェントをテスト"""
    agent_dir = AGENTS_DIR / agent_name

    # db.pyが存在するか確認
    db_file = agent_dir / "db.py"
    discord_file = agent_dir / "discord.py"

    if not db_file.exists():
        return {
            'name': agent_name,
            'status': 'skip',
            'reason': 'db.py not found'
        }

    if not discord_file.exists():
        return {
            'name': agent_name,
            'status': 'skip',
            'reason': 'discord.py not found'
        }

    # テスト実行
    try:
        result = subprocess.run(
            ['python3', 'discord.py'],
            cwd=str(agent_dir),
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            return {
                'name': agent_name,
                'status': 'success',
                'output': result.stdout
            }
        else:
            return {
                'name': agent_name,
                'status': 'error',
                'error': result.stderr
            }
    except subprocess.TimeoutExpired:
        return {
            'name': agent_name,
            'status': 'timeout',
            'error': 'Test timeout'
        }
    except Exception as e:
        return {
            'name': agent_name,
            'status': 'exception',
            'error': str(e)
        }

def main():
    """全エージェントテスト"""
    agent_dirs = [d for d in AGENTS_DIR.iterdir() if d.is_dir()]

    print(f"🧪 全エージェント統合テスト")
    print(f"📊 エージェント数: {len(agent_dirs)}個")
    print()

    results = []
    success_count = 0
    error_count = 0

    for agent_dir in agent_dirs:
        agent_name = agent_dir.name
        print(f"🧪 テスト中: {agent_name}...")

        result = test_agent(agent_name)
        results.append(result)

        if result['status'] == 'success':
            print(f"✅ {agent_name}: 成功")
            success_count += 1
        elif result['status'] == 'skip':
            print(f"⏭️ {agent_name}: スキップ ({result['reason']})")
        else:
            print(f"❌ {agent_name}: 失敗 ({result['status']})")
            error_count += 1

    # 結果保存
    results_file = RESULTS_DIR / "test-results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    # サマリ
    print()
    print("="*50)
    print("📊 テスト結果サマリ")
    print("="*50)
    print(f"✅ 成功: {success_count}個")
    print(f"❌ 失敗: {error_count}個")
    print(f"⏭️ スキップ: {len(results) - success_count - error_count}個")
    print(f"📈 成功率: {success_count / len(results) * 100:.1f}%")
    print()
    print(f"📁 結果保存: {results_file}")

if __name__ == '__main__':
    main()
