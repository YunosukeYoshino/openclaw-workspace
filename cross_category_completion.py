#!/usr/bin/env python3
"""
クロスカテゴリエージェント補完スクリプト

不完全なcross-categoryエージェントを補完する。
"""

import os
import shutil
from pathlib import Path

# 既存の完全なエージェントからテンプレートをコピー
SOURCE_AGENT = "cross-category-integration-agent"
AGENTS_TO_COMPLETE = [
    "cross-category-analytics-agent",
    "cross-category-recommendation-agent",
    "cross-category-search-agent",
    "cross-category-sync-agent",
    "cross-category-trend-agent",
]

AGENTS_DIR = Path("/workspace/agents")

def get_template_content(filename, new_agent_name):
    """テンプレートコンテンツをエージェント名に合わせて調整"""
    source_path = AGENTS_DIR / SOURCE_AGENT / filename
    if not source_path.exists():
        print(f"❌ Source file not found: {source_path}")
        return None

    with open(source_path, "r", encoding="utf-8") as f:
        content = f.read()

    # エージェント名を置換
    old_name = SOURCE_AGENT.replace("-", "_")
    new_name_pascal = new_agent_name.replace("-", " ").title().replace(" ", "")
    new_name_snake = new_agent_name.replace("-", "_")

    content = content.replace(old_name, new_name_snake)
    content = content.replace("CrossCategoryIntegrationAgent", new_name_pascal)
    content = content.replace("cross_category_integration_agent", new_name_snake)
    content = content.replace("cross-category-integration-agent", new_agent_name)

    return content

def complete_agent(agent_name):
    """エージェントを補完"""
    agent_dir = AGENTS_DIR / agent_name

    if not agent_dir.exists():
        print(f"❌ Agent directory not found: {agent_name}")
        return False

    print(f"🔧 Completing {agent_name}...")

    # 必要なファイル
    needed_files = ["db.py", "discord.py", "README.md", "requirements.txt"]

    for filename in needed_files:
        target_path = agent_dir / filename
        if target_path.exists():
            print(f"  ⏭️  {filename} already exists, skipping...")
            continue

        content = get_template_content(filename, agent_name)
        if content is None:
            print(f"  ❌ Failed to get content for {filename}")
            return False

        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  ✅ Created {filename}")

    print(f"✅ {agent_name} completed successfully")
    return True

def main():
    """メイン関数"""
    print("🚀 Cross-Category Agent Completion")
    print("=" * 50)

    completed = 0
    failed = 0

    for agent_name in AGENTS_TO_COMPLETE:
        if complete_agent(agent_name):
            completed += 1
        else:
            failed += 1
        print()

    print("=" * 50)
    print(f"📊 Completion Summary:")
    print(f"  Total: {len(AGENTS_TO_COMPLETE)}")
    print(f"  Completed: {completed}")
    print(f"  Failed: {failed}")
    print(f"  Success Rate: {completed / len(AGENTS_TO_COMPLETE) * 100:.1f}%")

if __name__ == "__main__":
    main()
