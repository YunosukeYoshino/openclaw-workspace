#!/usr/bin/env python3
"""
メモエージェント #2 - CLI
"""

import sys
from db import *

def print_memo(memo):
    """メモ表示"""
    id, title, content, category, created_at = memo
    print(f"\n📝 [{id}] {title or 'Untitled'}")
    print(f"   カテゴリ: {category or 'なし'}")
    print(f"   作成日: {created_at}")
    print(f"   内容: {content}...")

def cmd_add():
    """メモ追加"""
    print("\n✏️ メモ追加")
    title = input("タイトル (省略可): ") or None
    content = input("内容: ")
    category = input("カテゴリ (省略可): ") or None

    tags_str = input("タグ (カンマ区切り、省略可): ")
    tags = [t.strip() for t in tags_str.split(",")] if tags_str else None

    memo_id = add_memo(title, content, category, tags)
    print(f"\n✅ メモ #{memo_id} 追加完了")

def cmd_list():
    """メモ一覧"""
    print("\n📋 メモ一覧")
    memos = list_memos()
    if not memos:
        print("メモがありません")
    else:
        for memo in memos:
            print_memo(memo)

def cmd_search():
    """メモ検索"""
    keyword = input("\n🔍 検索キーワード: ")
    memos = search_memos(keyword)
    if not memos:
        print("見つかりませんでした")
    else:
        print(f"\n🔍 {len(memos)}件見つかりました")
        for memo in memos:
            print_memo(memo)

def cmd_categories():
    """カテゴリ一覧"""
    print("\n📁 カテゴリ一覧")
    categories = get_categories()
    if not categories:
        print("カテゴリがありません")
    else:
        for cat in categories:
            print(f"  - {cat[1]}")

def cmd_tags():
    """タグ一覧"""
    print("\�️ タグ一覧")
    tags = get_tags()
    if not tags:
        print("タグがありません")
    else:
        for tag in tags:
            print(f"  - {tag[1]}")

def main():
    init_db()

    while True:
        print("\n" + "="*50)
        print("🗒️ メモエージェント #2")
        print("="*50)
        print("1. メモ追加")
        print("2. メモ一覧")
        print("3. メモ検索")
        print("4. カテゴリ一覧")
        print("5. タグ一覧")
        print("0. 終了")

        choice = input("\n選択: ")

        if choice == "1":
            cmd_add()
        elif choice == "2":
            cmd_list()
        elif choice == "3":
            cmd_search()
        elif choice == "4":
            cmd_categories()
        elif choice == "5":
            cmd_tags()
        elif choice == "0":
            print("\n👋 さようなら！")
            break
        else:
            print("\n❌ 無効な選択")

if __name__ == '__main__':
    main()
