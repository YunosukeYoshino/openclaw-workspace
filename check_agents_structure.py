#!/usr/bin/env python3
"""
エージェントの構造を確認
"""

from pathlib import Path

AGENTS_DIR = Path("/workspace/agents")

def check_agent_structure(agent_name):
    """エージェントの構造を確認"""
    agent_dir = AGENTS_DIR / agent_name

    files = {
        'agent.py': (agent_dir / "agent.py").exists(),
        'db.py': (agent_dir / "db.py").exists(),
        'README.md': (agent_dir / "README.md").exists(),
        'requirements.txt': (agent_dir / "requirements.txt").exists(),
    }

    return files

def main():
    """全エージェントの構造を確認"""
    agent_dirs = [d for d in AGENTS_DIR.iterdir() if d.is_dir() and not d.name.startswith('.')]

    print(f"📊 エージェント構造確認")
    print(f"📁 エージェント数: {len(agent_dirs)}個")
    print()

    results = {
        'complete': 0,
        'incomplete': 0,
        'details': []
    }

    for agent_dir in sorted(agent_dirs):
        agent_name = agent_dir.name
        files = check_agent_structure(agent_name)

        all_files = all(files.values())
        status = "✅ 完了" if all_files else "⚠️ 未完成"

        if all_files:
            results['complete'] += 1
        else:
            results['incomplete'] += 1

        result_detail = {
            'name': agent_name,
            'files': files,
            'complete': all_files
        }
        results['details'].append(result_detail)

        missing = [k for k, v in files.items() if not v]
        if missing:
            print(f"{status} {agent_name} - 欠損: {', '.join(missing)}")
        else:
            print(f"{status} {agent_name}")

    print()
    print("="*50)
    print("📊 結果サマリ")
    print("="*50)
    print(f"✅ 完了: {results['complete']}個")
    print(f"⚠️ 未完成: {results['incomplete']}個")
    print(f"📈 完成率: {results['complete'] / len(agent_dirs) * 100:.1f}%")

    return results

if __name__ == '__main__':
    main()
