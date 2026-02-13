#!/usr/bin/env python3
"""
ゲーム支出トラッカーエージェント - Discord連携
Game Spending Tracker Agent - Discord Integration
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
        return f"✅ ゲーム支出トラッカーエージェント is online"

    if parsed['action'] == 'help':
        response = f"📖 **ゲーム支出トラッカーエージェント**\n\n"
        response += "**Features / 機能:**\n"
        response += "• 支出追跡 / Expense tracking\\n"
        response += "• 購入履歴 / Purchase history\\n"
        response += "• カテゴリ別分析 / Category-based analysis\\n"
        response += "• 月次レポート / Monthly reports\\n"
        response += "• 支出予測 / Expense forecasting\\n"
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
