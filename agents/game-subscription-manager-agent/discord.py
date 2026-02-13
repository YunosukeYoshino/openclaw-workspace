#!/usr/bin/env python3
"""
ゲームサブスクリプション管理エージェント - Discord連携
Game Subscription Manager Agent - Discord Integration
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
        return f"✅ ゲームサブスクリプション管理エージェント is online"

    if parsed['action'] == 'help':
        response = f"📖 **ゲームサブスクリプション管理エージェント**\n\n"
        response += "**Features / 機能:**\n"
        response += "• サブスクリプション管理 / Subscription management\\n"
        response += "• 更新リマインダー / Renewal reminders\\n"
        response += "• コスト分析 / Cost analysis\\n"
        response += "• 最適化提案 / Optimization suggestions\\n"
        response += "• 解約追跡 / Cancellation tracking\\n"
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
