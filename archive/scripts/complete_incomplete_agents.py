#!/usr/bin/env python3
"""
不完全なエージェント補完スクリプト
"""

import os
from pathlib import Path

# 既存の完全なエージェントからテンプレートをコピー
SOURCE_AGENTS = {
    "baseball": "baseball-player-agent",
    "erotic": "erotic-artwork-agent",
    "game": "game-stats-agent",
}

INCOMPLETE_AGENTS = [
    "baseball-draft-agent",
    "baseball-medical-agent",
    "baseball-overseas-agent",
    "baseball-strategy-agent",
    "baseball-training-agent",
    "erotic-community-agent",
    "erotic-creator-agent",
    "erotic-event-agent",
    "erotic-platform-agent",
    "erotic-series-agent",
    "game-collaboration-agent",
    "game-event-agent",
    "game-livestream-agent",
    "game-marketplace-agent",
    "game-tournament-agent",
]

AGENTS_DIR = Path("/workspace/agents")

def get_source_agent(agent_name):
    """エージェントの種類に基づいてソースエージェントを決定"""
    if agent_name.startswith("baseball-"):
        return SOURCE_AGENTS["baseball"]
    elif agent_name.startswith("erotic-"):
        return SOURCE_AGENTS["erotic"]
    elif agent_name.startswith("game-"):
        return SOURCE_AGENTS["game"]
    return SOURCE_AGENTS["game"]  # Default

def get_template_content(source_agent, filename, target_agent_name):
    """テンプレートコンテンツを取得して調整"""
    source_path = AGENTS_DIR / source_agent / filename
    if not source_path.exists():
        return None

    with open(source_path, "r", encoding="utf-8") as f:
        content = f.read()

    # エージェント名を置換
    old_name = source_agent.replace("-", "_")
    new_name_pascal = target_agent_name.replace("-", " ").title().replace(" ", "")
    new_name_snake = target_agent_name.replace("-", "_")

    content = content.replace(old_name, new_name_snake)
    content = content.replace(source_agent.replace("-", "_").replace("_", " ").title().replace(" ", ""), new_name_pascal)
    content = content.replace(source_agent, target_agent_name)

    return content

def complete_agent(agent_name):
    """エージェントを補完"""
    agent_dir = AGENTS_DIR / agent_name

    if not agent_dir.exists():
        print(f"❌ Agent directory not found: {agent_name}")
        return False

    # 既存のファイル確認
    existing_files = set(os.listdir(agent_dir))
    needed_files = set(["agent.py", "db.py", "discord.py", "README.md", "requirements.txt"])
    missing_files = needed_files - existing_files

    if not missing_files:
        print(f"⏭️  {agent_name} already complete, skipping...")
        return True

    print(f"🔧 Completing {agent_name}... Missing: {missing_files}")

    source_agent = get_source_agent(agent_name)

    try:
        for filename in missing_files:
            content = get_template_content(source_agent, filename, agent_name)
            if content is None:
                print(f"  ❌ Failed to get content for {filename}")
                return False

            with open(agent_dir / filename, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"  ✅ Created {filename}")

        print(f"✅ {agent_name} completed successfully")
        return True

    except Exception as e:
        print(f"❌ Error completing {agent_name}: {e}")
        return False

def main():
    """メイン関数"""
    import os
    print("🚀 Incomplete Agent Completion")
    print("=" * 60)

    completed = 0
    failed = 0

    for agent_name in INCOMPLETE_AGENTS:
        if complete_agent(agent_name):
            completed += 1
        else:
            failed += 1
        print()

    print("=" * 60)
    print(f"📊 Completion Summary:")
    print(f"  Total: {len(INCOMPLETE_AGENTS)}")
    print(f"  Completed: {completed}")
    print(f"  Failed: {failed}")
    print(f"  Success Rate: {completed / len(INCOMPLETE_AGENTS) * 100:.1f}%")

if __name__ == "__main__":
    main()
