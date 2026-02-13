#!/usr/bin/env python3
"""
野球スタジアムアクセシビリティエージェント - Discord連携
Baseball Stadium Accessibility Agent - Discord Integration
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
        return f"✅ 野球スタジアムアクセシビリティエージェント is online"

    if parsed['action'] == 'help':
        response = f"📖 **野球スタジアムアクセシビリティエージェント**\n\n"
        response += "**Features / 機能:**\n"
        response += "• 車いす対応席の情報 / Wheelchair accessible seating\\n"
        response += "• バリアフリー施設の案内 / Barrier-free facility guidance\\n"
        response += "• サポートサービスの予約 / Support service booking\\n"
        response += "• 視覚・聴覚障害者支援 / Visual/hearing impairment support\\n"
        response += "• 多言語対応サービス / Multi-language services\\n"
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
