#!/usr/bin/env python3
"""
データベースモジュールのテストスクリプト
"""

import os
import sys
from db import Database

# テスト用データベースパス
TEST_DB = "test_agent_77.db"


def test_database():
    """データベース機能のテスト"""
    print("=" * 50)
    print("Software Agent 77 - データベースモジュールテスト")
    print("=" * 50)

    # テスト用データベースを初期化
    db = Database(TEST_DB)

    # テスト1: ユーザー追加・取得
    print("\n📝 テスト1: ユーザー管理")
    user_id = db.add_or_update_user("123456", "TestUser", "ja")
    print(f"✓ ユーザー追加: ID={user_id}")

    user = db.get_user("123456")
    print(f"✓ ユーザー取得: {user['username']}, 言語={user['language']}")

    # テスト2: メッセージ保存・取得
    print("\n📝 テスト2: メッセージ管理")
    msg_id = db.save_message(
        "123456", "789012", "こんにちは、今日はいい天気ですね！",
        language="ja", intent="greeting", metadata={"emoji": "😊"}
    )
    print(f"✓ メッセージ保存: ID={msg_id}")

    messages = db.get_recent_messages("123456", "789012", limit=5)
    print(f"✓ メッセージ取得: {len(messages)}件")

    # テスト3: コンテキスト保存・取得
    print("\n📝 テスト3: コンテキスト管理")
    context_data = {"topic": "天気", "mood": "positive"}
    ctx_id = db.save_context("123456", "789012", context_data)
    print(f"✓ コンテキスト保存: ID={ctx_id}")

    context = db.get_context("123456", "789012")
    print(f"✓ コンテキスト取得: {context['context_data']}")

    # テスト4: 知識ベース
    print("\n📝 テスト4: 知識ベース")
    kb_id1 = db.add_knowledge(
        "general", "こんにちは", "こんにちは！何かお手伝いできることはありますか？",
        language="ja", keywords=["挨拶", "hello"]
    )
    print(f"✓ 知識追加 (日本語): ID={kb_id1}")

    kb_id2 = db.add_knowledge(
        "general", "hello", "Hello! How can I help you today?",
        language="en", keywords=["greeting", "hi"]
    )
    print(f"✓ 知識追加 (英語): ID={kb_id2}")

    knowledge = db.search_knowledge("こんにちは", language="ja")
    print(f"✓ 知識検索: {len(knowledge)}件")
    if knowledge:
        print(f"  - {knowledge[0]['answer']}")

    # テスト5: タスク管理
    print("\n📝 テスト5: タスク管理")
    task_id1 = db.add_task(
        "123456", "買い物に行く", "牛乳とパンを買う",
        priority=1
    )
    print(f"✓ タスク追加: ID={task_id1}")

    task_id2 = db.add_task(
        "123456", "メール返信", "明日までに返信",
        priority=2
    )
    print(f"✓ タスク追加: ID={task_id2}")

    tasks = db.get_tasks("123456", status="pending")
    print(f"✓ 未完了タスク取得: {len(tasks)}件")
    for task in tasks:
        print(f"  - {task['title']} (優先度: {task['priority']})")

    db.update_task_status(task_id1, "completed")
    print(f"✓ タスク完了: ID={task_id1}")

    tasks = db.get_tasks("123456", status="completed")
    print(f"✓ 完了タスク取得: {len(tasks)}件")

    # テスト6: 統計情報
    print("\n📝 テスト6: 統計情報")
    stats = db.get_stats()
    print("✓ データベース統計:")
    for key, value in stats.items():
        print(f"  - {key}: {value}")

    # テスト用データベースの削除
    os.remove(TEST_DB)
    print("\n✓ テスト用データベースを削除しました")

    print("\n" + "=" * 50)
    print("✅ すべてのテストが成功しました！")
    print("=" * 50)


if __name__ == "__main__":
    test_database()
