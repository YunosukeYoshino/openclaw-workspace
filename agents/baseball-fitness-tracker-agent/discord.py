#!/usr/bin/env python3
"""
野球フィットネストラッカーエージェント - Discord連携
Baseball Fitness Tracker Agent - Discord Integration
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
        return f"✅ 野球フィットネストラッカーエージェント is online"

    if parsed['action'] == 'help':
        response = f"📖 **野球フィットネストラッカーエージェント**\n\n"
        response += "**Features / 機能:**\n"
        response += "• フィットネスデータ追跡 / Fitness data tracking\\n"
        response += "• ウェアラブル統合 / Wearable integration\\n"
        response += "• トレーニングログ / Training logs\\n"
        response += "• 目標設定 / Goal setting\\n"
        response += "• 分析・レポート / Analysis and reporting\\n"
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
