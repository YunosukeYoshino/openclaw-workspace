#!/usr/bin/env python3
"""
エージェント補完スクリプト
- 指定されたエージェントの欠損ファイルを補完する
"""

import subprocess
import sys
from pathlib import Path

def complete_agent(agent_name: str, task_type: str) -> bool:
    """エージェントを補完する"""
    agents_dir = Path("/workspace/agents")
    agent_dir = agents_dir / agent_name

    if not agent_dir.exists():
        print(f"❌ Agent directory '{agent_dir}' does not exist")
        return False

    if task_type == "readme":
        readme_path = agent_dir / "README.md"
        if readme_path.exists():
            print(f"⏭️  README.md already exists for {agent_name}")
            return True

        result = subprocess.run(
            ["python3", "/workspace/generate_readme.py", agent_name],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"✅ Created README.md for {agent_name}")
            return True
        else:
            print(f"❌ Failed to create README.md for {agent_name}: {result.stderr}")
            return False

    elif task_type == "db":
        db_path = agent_dir / "db.py"
        if db_path.exists():
            print(f"⏭️  db.py already exists for {agent_name}")
            return True

        result = subprocess.run(
            ["python3", "/workspace/generate_db.py", agent_name],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"✅ Created db.py for {agent_name}")
            return True
        else:
            print(f"❌ Failed to create db.py for {agent_name}: {result.stderr}")
            return False

    return False

def main():
    """メイン処理"""
    if len(sys.argv) < 3:
        print("Usage: python3 complete_agents.py <task_type> <agent1> <agent2> ...")
        print("  task_type: readme or db")
        return

    task_type = sys.argv[1]
    agents = sys.argv[2:]

    if task_type not in ["readme", "db"]:
        print(f"❌ Invalid task_type: {task_type}")
        return

    print(f"\n🔧 Starting completion task: {task_type}")
    print(f"   Agents: {', '.join(agents)}\n")

    success_count = 0
    for agent_name in agents:
        if complete_agent(agent_name, task_type):
            success_count += 1

    print(f"\n📊 Completion Summary:")
    print(f"   Success: {success_count}/{len(agents)}")
    print(f"   Failed: {len(agents) - success_count}/{len(agents)}")

if __name__ == '__main__':
    main()
