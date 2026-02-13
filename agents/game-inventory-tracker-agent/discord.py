#!/usr/bin/env python3
"""
ゲーム在庫トラッカーエージェント - Discord連携
Game Inventory Tracker Agent - Discord Integration
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
        return f"✅ ゲーム在庫トラッカーエージェント is online"

    if parsed['action'] == 'help':
        response = f"📖 **ゲーム在庫トラッカーエージェント**\n\n"
        response += "**Features / 機能:**\n"
        response += "• 在庫管理 / Inventory management\\n"
        response += "• アイテム価値追跡 / Item value tracking\\n"
        response += "• 通貨残高管理 / Currency balance management\\n"
        response += "• アイテム履歴 / Item history\\n"
        response += "• 価値変動分析 / Value fluctuation analysis\\n"
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
