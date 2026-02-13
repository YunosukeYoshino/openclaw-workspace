#!/usr/bin/env python3
"""
ゲーム予算管理エージェント - Discord連携
Game Budget Manager Agent - Discord Integration
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
        return f"✅ ゲーム予算管理エージェント is online"

    if parsed['action'] == 'help':
        response = f"📖 **ゲーム予算管理エージェント**\n\n"
        response += "**Features / 機能:**\n"
        response += "• 予算設定 / Budget setting\\n"
        response += "• 支出アラート / Spending alerts\\n"
        response += "• 予算進捗表示 / Budget progress display\\n"
        response += "• 予算超過警告 / Over-budget warnings\\n"
        response += "• 節約提案 / Saving suggestions\\n"
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
