#!/usr/bin/env python3
"""
資産管理エージェント #13 - Discord連携
"""

import re
from db import *

def parse_message(message):
    """メッセージを解析"""
    # 資産追加
    asset_match = re.match(r'(?:資産|asset)[:：]\s*(.+)', message, re.IGNORECASE)
    if asset_match:
        return parse_asset(asset_match.group(1))

    # 資産更新
    update_match = re.match(r'(?:更新|update)[:：]\s*(\d+)', message, re.IGNORECASE)
    if update_match:
        return {'action': 'update', 'asset_id': int(update_match.group(1))}

    # 検索
    search_match = re.match(r'検索[:：]\s*(.+)', message)
    if search_match:
        return {'action': 'search', 'keyword': search_match.group(1)}

    # 一覧
    if message.strip() in ['資産一覧', '一覧', 'list', 'assets']:
        return {'action': 'list'}

    # 統計
    if message.strip() in ['統計', 'stats', '資産統計']:
        return {'action': 'stats'}

    return None

def parse_asset(content):
    """資産を解析"""
    result = {'action': 'add_asset', 'type': None, 'name': None, 'amount': None, 'currency': 'JPY', 'memo': None}

    # 種類
    type_match = re.search(r'種類[:：]\s*([^、,]+)', content)
    if type_match:
        type_str = type_match.group(1).strip()
        type_map = {'現金': 'cash', '銀行': 'bank', '投資': 'investment', '不動産': 'property', 'デジタル': 'digital'}
        result['type'] = type_map.get(type_str, type_str)
        content = content.replace(type_match.group(0), '').strip()

    # 金額
    amount_match = re.search(r'金額[:：]\s*([0-9,.]+)', content)
    if amount_match:
        result['amount'] = float(amount_match.group(1).replace(',', ''))
        content = content.replace(amount_match.group(0), '').strip()

    # 通貨
    currency_match = re.search(r'通貨[:：]\s*([A-Z]{3})', content)
    if currency_match:
        result['currency'] = currency_match.group(1)
        content = content.replace(currency_match.group(0), '').strip()

    # メモ
    memo_match = re.search(r'メモ[:：]\s*(.+)', content)
    if memo_match:
        result['memo'] = memo_match.group(1).strip()

    # 名前 (残り全部)
    if not result['name']:
        result['name'] = content.strip()

    return result

def handle_message(message):
    """メッセージを処理"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'add_asset':
        if not parsed['name'] or not parsed['amount']:
            return "❌ 名前と金額を入力してください"

        asset_id = add_asset(
            parsed['type'] or 'other',
            parsed['name'],
            parsed['amount'],
            parsed['currency'],
            parsed['memo']
        )

        response = f"💰 資産 #{asset_id} 追加完了\n"
        response += f"名前: {parsed['name']}\n"
        response += f"金額: {parsed['amount']:,} {parsed['currency']}"
        if parsed['memo']:
            response += f"\nメモ: {parsed['memo']}"

        return response

    elif action == 'list':
        assets = list_assets()

        if not assets:
            return "💰 資産がありません"

        response = f"💰 資産一覧 ({len(assets)}件):\n"
        for asset in assets:
            response += format_asset(asset)

        return response

    elif action == 'stats':
        stats = get_total_assets()

        response = "💰 資産統計:\n"
        response += f"総資産: {stats['total']:,.0f} JPY\n\n"

        if stats['by_type']:
            response += "種類別:\n"
            for asset_type, total in stats['by_type'].items():
                response += f"  - {asset_type}: {total:,.0f} JPY\n"

        return response

    return None

def format_asset(asset):
    """資産をフォーマット"""
    id, asset_type, name, amount, currency, memo, created_at = asset

    type_icons = {'cash': '💵', 'bank': '🏦', 'investment': '📈', 'property': '🏠', 'digital': '₿'}
    type_icon = type_icons.get(asset_type, '💰')

    response = f"\n{type_icon} [{id}] {name}\n"
    response += f"    種類: {asset_type}\n"
    response += f"    金額: {amount:,.0f} {currency}"

    return response

if __name__ == '__main__':
    # テスト
    init_db()

    test_messages = [
        "資産: 銀行口座, 種類:銀行, 金額:1000000, メモ: メインバンク",
        "資産: 現金, 種類:現金, 金額:50000",
        "資産: 株式, 種類:投資, 金額:500000",
        "資産一覧",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
