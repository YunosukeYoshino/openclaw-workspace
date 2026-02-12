#!/usr/bin/env python3
"""
Crypto Agent - Natural Language Processing
Supports Japanese and English
"""

import re
from datetime import datetime
from db import *

# Keywords for language detection
JP_KEYWORDS = ['価格', '保有', '通知', '追加', '一覧', 'エージェント', '暗号', '仮想']
EN_KEYWORDS = ['price', 'holding', 'alert', 'add', 'list', 'agent', 'crypto', 'cryptocurrency']

def detect_language(message):
    """言語を検出 / Detect language"""
    message_lower = message.lower()
    jp_score = sum(1 for kw in JP_KEYWORDS if kw in message)
    en_score = sum(1 for kw in EN_KEYWORDS if kw in message_lower)
    return 'jp' if jp_score >= en_score else 'en'

def parse_message(message, lang=None):
    """メッセージを解析 / Parse message"""
    lang = lang or detect_language(message)

    # Add holding (保有追加)
    if lang == 'jp':
        hold_match = re.match(r'(?:保有|holding)[:：]\s*(.+)', message, re.IGNORECASE)
    else:
        hold_match = re.match(r'(?:holding|add)[:：]\s*(.+)', message, re.IGNORECASE)

    if hold_match:
        return parse_add_holding(hold_match.group(1), lang)

    # Update price (価格更新)
    if lang == 'jp':
        price_match = re.match(r'(?:価格|price)[:：]\s*(.+)', message, re.IGNORECASE)
    else:
        price_match = re.match(r'(?:price|update)[:：]\s*(.+)', message, re.IGNORECASE)

    if price_match:
        return parse_update_price(price_match.group(1), lang)

    # Add alert (通知追加)
    if lang == 'jp':
        alert_match = re.match(r'(?:通知|alert)[:：]\s*(.+)', message, re.IGNORECASE)
    else:
        alert_match = re.match(r'(?:alert|notify)[:：]\s*(.+)', message, re.IGNORECASE)

    if alert_match:
        return parse_add_alert(alert_match.group(1), lang)

    # List holdings (保有一覧)
    if message.strip() in ['保有', '一覧', 'holdings', 'list', 'portfolio']:
        return {'action': 'list_holdings'}

    # List alerts (通知一覧)
    if message.strip() in ['通知', 'alerts', 'notifications']:
        return {'action': 'list_alerts'}

    # Portfolio value (ポートフォリオ価値)
    if message.strip() in ['価値', 'portfolio', 'value', 'total']:
        return {'action': 'portfolio_value'}

    # Check price (価格確認)
    if message.strip().startswith('価格:') or message.strip().startswith('price:'):
        if lang == 'jp':
            symbol = message.strip().split(':')[1].strip()
        else:
            symbol = message.strip().split(':')[1].strip()
        return {'action': 'check_price', 'symbol': symbol}

    return None

def parse_add_holding(content, lang):
    """保有追加を解析 / Parse add holding"""
    result = {'action': 'add_holding', 'symbol': None, 'amount': None, 'price': None}

    if lang == 'jp':
        # Symbol (シンボル)
        symbol_match = re.search(r'シンボル[:：]\s*(\w+)', content)
        if symbol_match:
            result['symbol'] = symbol_match.group(1).upper()
        else:
            # First word
            words = content.split()
            if words:
                result['symbol'] = words[0].upper()

        # Amount (数量)
        amount_match = re.search(r'数量[:：]\s*([\d.]+)', content)
        if amount_match:
            result['amount'] = float(amount_match.group(1))

        # Purchase price (購入価格)
        price_match = re.search(r'購入価格[:：]\s*([\d.]+)', content)
        if price_match:
            result['price'] = float(price_match.group(1))
    else:
        # Symbol
        symbol_match = re.search(r'symbol[:：]\s*(\w+)', content, re.IGNORECASE)
        if symbol_match:
            result['symbol'] = symbol_match.group(1).upper()
        else:
            words = content.split()
            if words:
                result['symbol'] = words[0].upper()

        # Amount
        amount_match = re.search(r'amount[:：]\s*([\d.]+)', content, re.IGNORECASE)
        if amount_match:
            result['amount'] = float(amount_match.group(1))

        # Purchase price
        price_match = re.search(r'(?:price|purchase)[:：]\s*([\d.]+)', content, re.IGNORECASE)
        if price_match:
            result['price'] = float(price_match.group(1))

    return result

def parse_update_price(content, lang):
    """価格更新を解析 / Parse update price"""
    result = {'action': 'update_price', 'symbol': None, 'price': None}

    parts = content.split()
    if len(parts) >= 2:
        result['symbol'] = parts[0].upper()
        result['price'] = float(parts[1])

    return result

def parse_add_alert(content, lang):
    """通知追加を解析 / Parse add alert"""
    result = {'action': 'add_alert', 'symbol': None, 'target_price': None, 'type': None}

    if lang == 'jp':
        # Symbol
        symbol_match = re.search(r'シンボル[:：]\s*(\w+)', content)
        if symbol_match:
            result['symbol'] = symbol_match.group(1).upper()

        # Target price
        price_match = re.search(r'(?:価格|目標価格)[:：]\s*([\d.]+)', content)
        if price_match:
            result['target_price'] = float(price_match.group(1))

        # Type (above/below)
        if '以上' in content or 'over' in content.lower():
            result['type'] = 'above'
        elif '以下' in content or 'under' in content.lower():
            result['type'] = 'below'
    else:
        # Symbol
        symbol_match = re.search(r'symbol[:：]\s*(\w+)', content, re.IGNORECASE)
        if symbol_match:
            result['symbol'] = symbol_match.group(1).upper()

        # Target price
        price_match = re.search(r'(?:price|target)[:：]\s*([\d.]+)', content, re.IGNORECASE)
        if price_match:
            result['target_price'] = float(price_match.group(1))

        # Type
        if 'above' in content.lower() or 'over' in content.lower():
            result['type'] = 'above'
        elif 'below' in content.lower() or 'under' in content.lower():
            result['type'] = 'below'

    return result

def handle_message(message):
    """メッセージを処理 / Handle message"""
    lang = detect_language(message)
    parsed = parse_message(message, lang)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'add_holding':
        if not parsed['symbol'] or not parsed['amount']:
            return lang_response(lang, '❌ シンボルと数量を入力してください / Please enter symbol and amount')

        holding_id = add_holding(
            parsed['symbol'],
            parsed['amount'],
            parsed['price']
        )

        response = lang_response(lang, f'💰 保有資産 #{holding_id} 追加完了 / Added holding #{holding_id}\n')
        response += lang_response(lang, f'シンボル: {parsed["symbol"]} / Symbol: {parsed["symbol"]}\n')
        response += lang_response(lang, f'数量: {parsed["amount"]} / Amount: {parsed["amount"]}')
        if parsed['price']:
            response += lang_response(lang, f'\n購入価格: ${parsed["price"]} / Purchase price: ${parsed["price"]}')
        return response

    elif action == 'update_price':
        if not parsed['symbol'] or not parsed['price']:
            return lang_response(lang, '❌ シンボルと価格を入力してください / Please enter symbol and price')

        update_price(parsed['symbol'], parsed['price'])

        response = lang_response(lang, f'📊 価格を更新 / Price updated\n')
        response += lang_response(lang, f'{parsed["symbol"]}: ${parsed["price"]}')
        return response

    elif action == 'add_alert':
        if not parsed['symbol'] or not parsed['target_price'] or not parsed['type']:
            return lang_response(lang, '❌ シンボル、目標価格、通知タイプを入力してください / Please enter symbol, target price, and alert type')

        alert_id = add_alert(parsed['symbol'], parsed['target_price'], parsed['type'])

        type_text = '以上' if parsed['type'] == 'above' else '以下' if lang == 'jp' else 'above or below'
        response = lang_response(lang, f'🔔 通知 #{alert_id} 設定完了 / Alert #{alert_id} set\n')
        response += lang_response(lang, f'{parsed["symbol"]} {parsed["target_price"]}${type_text}')
        return response

    elif action == 'list_holdings':
        holdings = list_holdings()

        if not holdings:
            return lang_response(lang, '💰 保有資産がありません / No holdings found')

        response = lang_response(lang, f'💰 保有資産一覧 ({len(holdings)}件) / Holdings ({len(holdings)} items):\n')
        for holding in holdings:
            response += format_holding(holding, lang)

        return response

    elif action == 'list_alerts':
        alerts = list_alerts()

        if not alerts:
            return lang_response(lang, '🔔 通知がありません / No alerts found')

        response = lang_response(lang, f'🔔 通知一覧 ({len(alerts)}件) / Alerts ({len(alerts)} items):\n')
        for alert in alerts:
            response += format_alert(alert, lang)

        return response

    elif action == 'portfolio_value':
        portfolio = get_portfolio_value()

        response = lang_response(lang, f'💵 ポートフォリオ価値 / Portfolio Value\n')
        response += lang_response(lang, f'総額: ${portfolio["total"]:.2f} / Total: ${portfolio["total"]:.2f}\n')
        for detail in portfolio['details']:
            response += f'\n{detail["symbol"]}: ${detail["value"]:.2f} ({detail["amount"]} @ ${detail["current_price"]:.2f})'

        return response

    elif action == 'check_price':
        latest = get_latest_price(parsed['symbol'])

        if not latest:
            return lang_response(lang, f'📊 {parsed["symbol"]} の価格データがありません / No price data for {parsed["symbol"]}')

        price, timestamp = latest
        return lang_response(lang, f'📊 {parsed["symbol"]} 価格: ${price} (更新: {timestamp}) / Price: ${price} (Updated: {timestamp})')

    return None

def format_holding(holding, lang):
    """保有資産をフォーマット / Format holding"""
    id, symbol, amount, purchase_price, purchase_date = holding

    if lang == 'jp':
        response = f'\n[{id}] {symbol}\n'
        response += f'    数量: {amount}\n'
        if purchase_price:
            response += f'    購入価格: ${purchase_price}\n'
        response += f'    購入日: {purchase_date}'
    else:
        response = f'\n[{id}] {symbol}\n'
        response += f'    Amount: {amount}\n'
        if purchase_price:
            response += f'    Purchase price: ${purchase_price}\n'
        response += f'    Purchase date: {purchase_date}'

    return response

def format_alert(alert, lang):
    """通知をフォーマット / Format alert"""
    id, symbol, target_price, alert_type, status, created_at = alert

    if lang == 'jp':
        type_text = '以上' if alert_type == 'above' else '以下'
        response = f'\n[{id}] {symbol}\n'
        response += f'    目標価格: ${target_price}{type_text}\n'
        response += f'    状態: {status}\n'
        response += f'    作成日: {created_at}'
    else:
        type_text = 'above' if alert_type == 'above' else 'below'
        response = f'\n[{id}] {symbol}\n'
        response += f'    Target: ${target_price} {type_text}\n'
        response += f'    Status: {status}\n'
        response += f'    Created: {created_at}'

    return response

def lang_response(lang, text):
    """言語に応じた応答を生成 / Generate language-specific response"""
    return text

if __name__ == '__main__':
    # Initialize database
    init_db()

    # Test messages
    test_messages = [
        "保有: BTC, 数量: 0.5, 購入価格: 50000",
        "price: ETH 3500",
        "add alert BTC 55000 above",
        "holdings",
        "alerts",
        "portfolio",
        "価格: BTC",
    ]

    for msg in test_messages:
        print(f"\n入力 / Input: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
