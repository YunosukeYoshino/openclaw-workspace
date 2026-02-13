#!/usr/bin/env python3
"""
野球ファン体験エージェント - Discord連携
Baseball Fan Experience Agent - Discord Integration
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
        return f"✅ 野球ファン体験エージェント is online"

    if parsed['action'] == 'help':
        response = f"📖 **野球ファン体験エージェント**\n\n"
        response += "**Features / 機能:**\n"
        response += "• ファン体験イベントの案内 / Fan experience events\\n"
        response += "• 記念品・グッズ情報の収集 / Merchandise information\\n"
        response += "• スタジアムクイズ・ゲーム / Stadium quizzes and games\\n"
        response += "• AR/VR体験機能 / AR/VR experience features\\n"
        response += "• ファン参加型コンテンツ / Fan participation content\\n"
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
