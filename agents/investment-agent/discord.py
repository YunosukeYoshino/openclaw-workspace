#!/usr/bin/env python3
"""
投資管理エージェント #53 - Discord連携
"""

import re
from datetime import datetime
from db import *

def parse_message(message):
    """メッセージを解析"""
    # 投資追加
    investment_match = re.match(r'(?:投資|investment)[：:]\s*(.+)', message, re.IGNORECASE)
    if investment_match:
        return parse_add_investment(investment_match.group(1))

    # 価格更新
    price_match = re.match(r'(?:価格更新|update price|price)[：:]\s*(\d+)\s*(\d+(?:\.\d+)?)', message, re.IGNORECASE)
    if price_match:
        return {'action': 'update_price', 'investment_id': int(price_match.group(1)), 'current_price': float(price_match.group(2))}

    # 配当追加
    dividend_match = re.match(r'(?:配当|dividend)[：:]\s*(\d+)\s*(\d+(?:\.\d+)?)', message, re.IGNORECASE)
    if dividend_match:
        parsed = parse_add_dividend(message)
        parsed['investment_id'] = int(dividend_match.group(1))
        parsed['amount'] = float(dividend_match.group(2))
        return parsed

    # 一覧
    list_match = re.match(r'(?:(?:投資|investment)(?:一覧|list)|list|investments)', message, re.IGNORECASE)
    if list_match:
        return {'action': 'list'}

    # タイプ別
    type_match = re.match(r'(?:タイプ|type)[：:]\s*(stock|bond|etf|mutual_fund|crypto|other)', message, re.IGNORECASE)
    if type_match:
        return {'action': 'list_by_type', 'type': type_match.group(1)}

    # 配前一覧
    dividends_match = re.match(r'(?:配当|dividend)(?:一覧|list)[：:]\s*(\d+)', message, re.IGNORECASE)
    if dividends_match:
        return {'action': 'list_dividends', 'investment_id': int(dividends_match.group(1))}

    # 損益
    pnl_match = re.match(r'(?:損益|pnl)[：:]\s*(\d+)', message, re.IGNORECASE)
    if pnl_match:
        return {'action': 'pnl', 'investment_id': int(pnl_match.group(1))}

    return None

def parse_add_investment(content):
    """投資追加を解析"""
    result = {'action': 'add', 'name': None, 'type': None, 'symbol': None,
              'shares': None, 'purchase_price': None, 'current_price': None,
              'currency': 'JPY', 'purchase_date': None, 'notes': None}

    # 名前 (最初の部分)
    name_match = re.match(r'^([^、,（\(【]+)', content)
    if name_match:
        result['name'] = name_match.group(1).strip()

    # タイプ
    type_match = re.search(r'(?:タイプ|type)[：:]\s*(stock|bond|etf|mutual_fund|crypto|other|株|債券|その他)', content)
    if type_match:
        type_str = type_match.group(1).lower()
        type_map = {
            'stock': 'stock', '株': 'stock',
            'bond': 'bond', '債券': 'bond',
            'etf': 'etf',
            'mutual_fund': 'mutual_fund',
            'crypto': 'crypto',
            'other': 'other', 'その他': 'other'
        }
        result['type'] = type_map.get(type_str, type_str)

    # シンボル
    symbol_match = re.search(r'(?:シンボル|symbol|コード|code)[：:]\s*([^、,]+)', content)
    if symbol_match:
        result['symbol'] = symbol_match.group(1).strip()

    # 株数
    shares_match = re.search(r'(?:株数|shares|数量)[：:]?\s*(\d+(?:\.\d+)?)', content)
    if shares_match:
        result['shares'] = float(shares_match.group(1))

    # 買付価格
    purchase_match = re.search(r'(?:買付|purchase|取得)[：:]\s*(\d+(?:\.\d+)?)', content)
    if purchase_match:
        result['purchase_price'] = float(purchase_match.group(1))

    # 現在価格
    current_match = re.search(r'(?:現在|current)[：:]\s*(\d+(?:\.\d+)?)', content)
    if current_match:
        result['current_price'] = float(current_match.group(1))

    # 通貨
    currency_match = re.search(r'(?:通貨|currency)[：:]\s*(JPY|USD|EUR|JPY|円|ドル|ユーロ)', content)
    if currency_match:
        currency_str = currency_match.group(1).upper()
        if currency_str in ['JPY', '円']:
            result['currency'] = 'JPY'
        elif currency_str in ['USD', 'ドル']:
            result['currency'] = 'USD'
        elif currency_str in ['EUR', 'ユーロ']:
            result['currency'] = 'EUR'

    # 買付日
    date_match = re.search(r'(?:買付日|purchase|取得日)[：:]\s*([^、,]+)', content)
    if date_match:
        result['purchase_date'] = parse_date(date_match.group(1).strip())

    # メモ
    notes_match = re.search(r'(?:メモ|備考|memo|note)[：:]\s*(.+)', content)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    # 名前がまだない場合、最初の項目より前を名前とする
    if not result['name']:
        for key in ['タイプ', 'type', 'シンボル', 'symbol', 'コード', 'code', '株数', 'shares', '数量',
                    '買付', 'purchase', '取得', '現在', 'current', '通貨', 'currency',
                    '買付日', 'purchase', '取得日', 'メモ', '備考', 'memo', 'note']:
            match = re.search(rf'{key}[：:]', content)
            if match:
                result['name'] = content[:match.start()].strip()
                break
        else:
            result['name'] = content.strip()

    return result

def parse_add_dividend(content):
    """配当追加を解析"""
    result = {'action': 'add_dividend', 'payment_date': None, 'reinvested': False, 'notes': None}

    # 支払日
    date_match = re.search(r'(?:支払日|payment|date)[：:]\s*([^、,]+)', content)
    if date_match:
        result['payment_date'] = parse_date(date_match.group(1).strip())

    # 再投資
    reinvest_match = re.search(r'(?:再投資|reinvest)', content)
    if reinvest_match:
        result['reinvested'] = True

    # メモ
    notes_match = re.search(r'(?:メモ|備考|memo|note)[：:]\s*(.+)', content)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    return result

def parse_date(date_str):
    """日付を解析"""
    today = datetime.now()

    # 今日
    if '今日' in date_str:
        return today.strftime("%Y-%m-%d")

    # 昨日
    if '昨日' in date_str:
        from datetime import timedelta
        return (today - timedelta(days=1)).strftime("%Y-%m-%d")

    # 明日
    if '明日' in date_str:
        from datetime import timedelta
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")

    # 日付形式
    date_match = re.match(r'(\d{4})-(\d{1,2})-(\d{1,2})', date_str)
    if date_match:
        return f"{date_match.group(1)}-{date_match.group(2).zfill(2)}-{date_match.group(3).zfill(2)}"

    date_match = re.match(r'(\d{1,2})/(\d{1,2})', date_str)
    if date_match:
        month = int(date_match.group(1))
        day = int(date_match.group(2))
        return datetime(today.year, month, day).strftime("%Y-%m-%d")

    return None

def handle_message(message):
    """メッセージを処理"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'add':
        if not parsed['name'] or not parsed['type']:
            return "❌ 名前とタイプを入力してください"

        investment_id = add_investment(
            parsed['name'],
            parsed['type'],
            parsed['symbol'],
            parsed['shares'],
            parsed['purchase_price'],
            parsed['current_price'],
            parsed['currency'],
            parsed['purchase_date'],
            parsed['notes']
        )

        type_text = {'stock': '株', 'bond': '債券', 'etf': 'ETF', 'mutual_fund': '投資信託', 'crypto': '暗号資産', 'other': 'その他'}.get(parsed['type'], parsed['type'])

        response = f"💼 投資 #{investment_id} 追加完了\n"
        response += f"名前: {parsed['name']}\n"
        response += f"タイプ: {type_text}\n"
        if parsed['symbol']:
            response += f"シンボル: {parsed['symbol']}\n"
        if parsed['shares']:
            response += f"株数: {parsed['shares']}\n"
        if parsed['purchase_price']:
            response += f"買付価格: ¥{parsed['purchase_price']:,}\n"
        if parsed['current_price']:
            response += f"現在価格: ¥{parsed['current_price']:,}\n"
        if parsed['currency']:
            response += f"通貨: {parsed['currency']}\n"
        if parsed['purchase_date']:
            response += f"買付日: {parsed['purchase_date']}\n"
        if parsed['notes']:
            response += f"メモ: {parsed['notes']}"

        return response

    elif action == 'update_price':
        update_price(parsed['investment_id'], parsed['current_price'])
        return f"✅ 投資 #{parsed['investment_id']} の現在価格を ¥{parsed['current_price']:,} に更新しました"

    elif action == 'add_dividend':
        dividend_id = add_dividend(
            parsed['investment_id'],
            parsed['amount'],
            'JPY',
            parsed['payment_date'],
            parsed['reinvested'],
            parsed['notes']
        )

        reinvested_text = " (再投資)" if parsed['reinvested'] else ""

        return f"💰 配当 #{dividend_id} 追加完了: ¥{parsed['amount']:,}{reinvested_text}"

    elif action == 'list':
        investments = list_investments()

        if not investments:
            return "💼 投資がありません"

        response = f"💼 投資一覧 ({len(investments)}件):\n"
        for investment in investments:
            response += format_investment(investment)

        return response

    elif action == 'list_by_type':
        investments = list_investments(investment_type=parsed['type'])

        if not investments:
            return f"💼 {parsed['type']}の投資がありません"

        response = f"💼 {parsed['type']}の投資 ({len(investments)}件):\n"
        for investment in investments:
            response += format_investment(investment)

        return response

    elif action == 'list_dividends':
        dividends = get_dividends(parsed['investment_id'])

        if not dividends:
            return f"💰 配当記録がありません"

        response = f"💰 配当記録 ({len(dividends)}件):\n"
        for dividend in dividends:
            response += format_dividend(dividend)

        return response

    elif action == 'pnl':
        pnl = calculate_pnl(parsed['investment_id'])

        if not pnl:
            return f"📊 投資 #{parsed['investment_id']} の損益計算ができません"

        investment_id = parsed['investment_id']
        investments = list_investments()
        for inv in investments:
            if inv[0] == investment_id:
                inv_name = inv[1]
                break

        pnl_icon = "📈" if pnl['pnl'] >= 0 else "📉"

        return f"{pnl_icon} {inv_name}の損益:\n" \
               f"  取得額: ¥{pnl['purchase_value']:,.0f}\n" \
               f"  現在額: ¥{pnl['current_value']:,.0f}\n" \
               f"  損益: ¥{pnl['pnl']:,.0f} ({pnl['pnl_pct']:.2f}%)"

    return None

def format_investment(investment):
    """投資をフォーマット"""
    id, name, type, symbol, shares, purchase_price, current_price, currency, purchase_date, notes, created_at = investment

    type_icons = {'stock': '📈', 'bond': '📜', 'etf': '💼', 'mutual_fund': '📊', 'crypto': '₿', 'other': '📦'}
    type_icon = type_icons.get(type, '💰')

    response = f"\n{type_icon} [{id}] {name}"

    if symbol:
        response += f" ({symbol})"
    if type:
        response += f" [{type}]"

    response += "\n"

    parts = []
    if shares:
        parts.append(f"{shares}株")
    if purchase_price:
        parts.append(f"買付: ¥{purchase_price:,}")
    if current_price:
        parts.append(f"現在: ¥{current_price:,}")

    if parts:
        response += f"  {' '.join(parts)}\n"

    return response

def format_dividend(dividend):
    """配当をフォーマット"""
    id, investment_id, amount, currency, payment_date, reinvested, notes, created_at = dividend

    reinvested_text = " (再投資)" if reinvested else ""

    response = f"💰 [{id}] ¥{amount:,}{reinvested_text}"

    if payment_date:
        response += f" - {payment_date}"

    if notes:
        response += f": {notes[:30]}{'...' if len(notes) > 30 else ''}"

    response += "\n"

    return response

if __name__ == '__main__':
    # テスト
    init_db()

    test_messages = [
        "投資: Apple, タイプ: stock, シンボル: AAPL, 株数: 10, 買付: 15000, 現在: 17000",
        "価格更新: 1 18000",
        "配当: 1 500, 支払日: 今日",
        "投資一覧",
        "損益: 1",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
