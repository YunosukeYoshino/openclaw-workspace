#!/usr/bin/env python3
"""
クロスカテゴリ拡張統合エージェント作成スクリプト
"""

import os
import json
from pathlib import Path
from datetime import datetime

# 既存の完全なエージェントからテンプレートをコピー
SOURCE_AGENT = "cross-category-integration-agent"

AGENTS_TO_CREATE = [
    "cross-category-ai-prediction-agent",
    "cross-category-event-agent",
    "cross-category-analysis-agent",
    "cross-category-visualization-agent",
    "cross-category-automation-agent",
]

AGENTS_DIR = Path("/workspace/agents")

def get_template_content(filename, new_agent_name, agent_type):
    """テンプレートコンテンツを取得して調整"""
    source_path = AGENTS_DIR / SOURCE_AGENT / filename
    if not source_path.exists():
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

    # agent.pyの場合は説明も置換
    if filename == "agent.py":
        description_map = {
            "cross-category-ai-prediction-agent": "クロスカテゴリAI予測エージェント - 全カテゴリのデータを学習して未来を予測",
            "cross-category-event-agent": "クロスカテゴリイベントエージェント - カテゴリを超えたイベントを検知・通知",
            "cross-category-analysis-agent": "クロスカテゴリアナリティクスエージェント - 全カテゴリのデータを統合分析",
            "cross-category-visualization-agent": "クロスカテゴリ可視化エージェント - 複雑なデータ関係を美しく可視化",
            "cross-category-automation-agent": "クロスカテゴリ自動化エージェント - 統合されたタスクを自動化",
        }
        description = description_map.get(new_agent_name, agent_type)
        content = content.replace("エージェント統合 - 野球、ゲーム、えっちコンテンツの統合管理", description)

    return content

def create_agent(agent_name, agent_type):
    """エージェントを作成"""
    agent_dir = AGENTS_DIR / agent_name

    if agent_dir.exists():
        print(f"⏭️  {agent_name} already exists, skipping...")
        return True

    print(f"🔧 Creating {agent_name}...")

    # 必要なファイル
    needed_files = ["agent.py", "db.py", "discord.py", "README.md", "requirements.txt"]

    for filename in needed_files:
        target_path = agent_dir / filename
        if target_path.exists():
            print(f"  ⏭️  {filename} already exists, skipping...")
            continue

        content = get_template_content(filename, agent_name, agent_type)
        if content is None:
            print(f"  ❌ Failed to get content for {filename}")
            return False

        agent_dir.mkdir(parents=True, exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  ✅ Created {filename}")

    print(f"✅ {agent_name} created successfully")
    return True

def main():
    """メイン関数"""
    print("🚀 Cross-Category Extended Integration Agent Creation")
    print("=" * 60)

    completed = 0
    failed = 0

    for agent_name in AGENTS_TO_CREATE:
        agent_type = agent_name.split("-")[2]  # ai-prediction, event, etc.
        if create_agent(agent_name, agent_type):
            completed += 1
        else:
            failed += 1
        print()

    print("=" * 60)
    print(f"📊 Creation Summary:")
    print(f"  Total: {len(AGENTS_TO_CREATE)}")
    print(f"  Completed: {completed}")
    print(f"  Failed: {failed}")
    print(f"  Success Rate: {completed / len(AGENTS_TO_CREATE) * 100:.1f}%")

if __name__ == "__main__":
    main()
