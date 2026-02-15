#!/usr/bin/env python3
"""
全エージェント検証スクリプト
"""

from pathlib import Path

AGENTS_DIR = Path("/workspace/agents")
REQUIRED_FILES = ["agent.py", "db.py", "discord.py", "README.md", "requirements.txt"]

def verify_agent(agent_dir: Path) -> dict:
    """エージェントを検証"""
    result = {
        "name": agent_dir.name,
        "exists": agent_dir.exists(),
        "files": {},
        "complete": False,
    }

    if not agent_dir.exists():
        return result

    for filename in REQUIRED_FILES:
        filepath = agent_dir / filename
        result["files"][filename] = filepath.exists()

    # Complete if all required files exist
    result["complete"] = all(result["files"].values())

    return result

def main():
    """メイン関数"""
    print("🔍 全エージェント検証")
    print("=" * 60)

    agent_dirs = sorted([d for d in AGENTS_DIR.iterdir() if d.is_dir()])

    complete_agents = []
    incomplete_agents = []
    missing_files_summary = {}

    for agent_dir in agent_dirs:
        result = verify_agent(agent_dir)

        if result["complete"]:
            complete_agents.append(result["name"])
        else:
            incomplete_agents.append(result["name"])
            # Track missing files
            for filename, exists in result["files"].items():
                if not exists:
                    if filename not in missing_files_summary:
                        missing_files_summary[filename] = []
                    missing_files_summary[filename].append(result["name"])

    print(f"📊 検証結果:")
    print(f"  総エージェント数: {len(agent_dirs)}")
    print(f"  完全なエージェント: {len(complete_agents)}")
    print(f"  不完全なエージェント: {len(incomplete_agents)}")
    print()

    if incomplete_agents:
        print(f"❌ 不完全なエージェント一覧 ({len(incomplete_agents)}個):")
        for name in incomplete_agents[:20]:  # Show first 20
            print(f"  - {name}")
        if len(incomplete_agents) > 20:
            print(f"  ... さらに {len(incomplete_agents) - 20} 個")
        print()

        print(f"📋 欠損ファイルのサマリー:")
        for filename, agents in missing_files_summary.items():
            print(f"  {filename}: {len(agents)}個のエージェントで欠損")
        print()
    else:
        print(f"✅ すべてのエージェントが完全です！")
        print()

    print("=" * 60)
    print(f"🎉 完了率: {len(complete_agents) / len(agent_dirs) * 100:.1f}%")

    # Save results
    results = {
        "total_agents": len(agent_dirs),
        "complete_agents": len(complete_agents),
        "incomplete_agents": len(incomplete_agents),
        "completion_rate": len(complete_agents) / len(agent_dirs) * 100,
        "complete_list": complete_agents,
        "incomplete_list": incomplete_agents,
        "missing_files_summary": missing_files_summary,
    }

    import json
    with open("/workspace/verification_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"📁 結果を保存: /workspace/verification_results.json")

if __name__ == "__main__":
    main()
