#!/usr/bin/env python3
"""欠損エージェントを特定するスクリプト"""

import os
from pathlib import Path

def find_missing_agents():
    agents_dir = Path("/workspace/agents")
    missing_readme = []
    missing_db = []

    for agent_dir in sorted(agents_dir.iterdir()):
        if not agent_dir.is_dir():
            continue

        agent_name = agent_dir.name
        readme = agent_dir / "README.md"
        db = agent_dir / "db.py"

        if not readme.exists():
            missing_readme.append(agent_name)

        if not db.exists():
            missing_db.append(agent_name)

    return missing_readme, missing_db

if __name__ == "__main__":
    missing_readme, missing_db = find_missing_agents()

    print(f"\n📊 欠損エージェントの分析")
    print(f"\nREADME.md 欠損 ({len(missing_readme)}個):")
    for agent in missing_readme:
        print(f"  - {agent}")

    print(f"\ndb.py 欠損 ({len(missing_db)}個):")
    for agent in missing_db:
        print(f"  - {agent}")

    print(f"\n📝 総計:")
    print(f"  - README.md 欠損: {len(missing_readme)}個")
    print(f"  - db.py 欠損: {len(missing_db)}個")
    print(f"  - 合計補完タスク: {len(missing_readme) + len(missing_db)}個")
