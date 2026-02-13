#!/usr/bin/env python3
"""
野球ドリルライブラリエージェント - Discord連携
Baseball Drill Library Agent - Discord Integration
"""

import re

def parse_message(message):
    """メッセージを解析"""
    if message.strip().lower() in ['status', 'ステータス']:
        return {'action': 'status'}
    if message.strip().lower() in ['help', 'ヘルプ']:
        return {'action': 'help'}
    return None

def handle_message(message):
    """メッセージを処理"""
    parsed = parse_message(message)

    if not parsed:
        return None

    if parsed['action'] == 'status':
        return f"✅ 野球ドリルライブラリエージェント is online"

    if parsed['action'] == 'help':
        response = f"📖 **野球ドリルライブラリエージェント**\n\n"
        response += "**Features / 機能:**\n"
        response += "• ドリルライブラリ / Drill library\\n"
        response += "• 動画チュートリアル / Video tutorials\\n"
        response += "• 難易度別分類 / Difficulty-based classification\\n"
        response += "• 目的別ドリル検索 / Purpose-based drill search\\n"
        response += "• お気に入り機能 / Favorites\\n"
        return response

    return None

if __name__ == '__main__':
    test_messages = ['status', 'help']
    for msg in test_messages:
        print(f"Input: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
        print()
