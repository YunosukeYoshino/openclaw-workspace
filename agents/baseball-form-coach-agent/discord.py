#!/usr/bin/env python3
"""
野球フォームコーチエージェント - Discord連携
Baseball Form Coach Agent - Discord Integration
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
        return f"✅ 野球フォームコーチエージェント is online"

    if parsed['action'] == 'help':
        response = f"📖 **野球フォームコーチエージェント**\n\n"
        response += "**Features / 機能:**\n"
        response += "• フォーム分析 / Form analysis\\n"
        response += "• 改善提案 / Improvement recommendations\\n"
        response += "• ビデオフィードバック / Video feedback\\n"
        response += "• 進捗追跡 / Progress tracking\\n"
        response += "• コーチングチャット / Coaching chat\\n"
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
