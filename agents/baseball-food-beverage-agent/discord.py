#!/usr/bin/env python3
"""
野球スタジアムフード・ドリンクエージェント - Discord連携
Baseball Stadium Food and Beverage Agent - Discord Integration
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
        return f"✅ 野球スタジアムフード・ドリンクエージェント is online"

    if parsed['action'] == 'help':
        response = f"📖 **野球スタジアムフード・ドリンクエージェント**\n\n"
        response += "**Features / 機能:**\n"
        response += "• スタジアムフードメニューのカタログ / Food menu catalog\\n"
        response += "• 待ち時間の予測・監視 / Wait time prediction\\n"
        response += "• 事前注文機能の統合 / Pre-order integration\\n"
        response += "• 人気メニューのランキング / Popular menu rankings\\n"
        response += "• 食事タイミングの提案 / Meal timing recommendations\\n"
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
