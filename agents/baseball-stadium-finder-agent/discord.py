#!/usr/bin/env python3
"""
野球スタジアム検索・情報エージェント - Discord連携
Baseball Stadium Finder and Information Agent - Discord Integration
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
        return f"✅ 野球スタジアム検索・情報エージェント is online"

    if parsed['action'] == 'help':
        response = f"📖 **野球スタジアム検索・情報エージェント**\n\n"
        response += "**Features / 機能:**\n"
        response += "• スタジアム検索・フィルタリング機能 / Stadium search and filtering\\n"
        response += "• 座席エリア情報の提供 / Seat area information\\n"
        response += "• アクセス方法・交通手段の提案 / Access and transportation\\n"
        response += "• 周辺施設情報 / Nearby facilities\\n"
        response += "• チケット価格帯の比較 / Ticket price comparison\\n"
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
