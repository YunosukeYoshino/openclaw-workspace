#!/usr/bin/env python3
"""
野球スキル評価エージェント - Discord連携
Baseball Skill Assessment Agent - Discord Integration
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
        return f"✅ 野球スキル評価エージェント is online"

    if parsed['action'] == 'help':
        response = f"📖 **野球スキル評価エージェント**\n\n"
        response += "**Features / 機能:**\n"
        response += "• スキル評価テスト / Skill assessment tests\\n"
        response += "• 成長記録 / Growth records\\n"
        response += "• 比較分析 / Comparative analysis\\n"
        response += "• レーダーチャート表示 / Radar chart visualization\\n"
        response += "• 評価レポート / Assessment reports\\n"
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
