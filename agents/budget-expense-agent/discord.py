#!/usr/bin/env python3
"""
予算・支出管理エージェント #52 - Discord連携
"""

import re
from datetime import datetime
from db import *

def parse_message(message):
    """メッセージを解析"""
    # カテゴリー追加
    category_match = re.match(r'(?:カテゴリ|category)[：:]\s*(.+)', message, re.IGNORECASE)
    if category_match:
        return parse_add_category(category_match.group(1))

    # 支出追加
    expense_match = re.match(r'(?:支出|expense)[：:]\s*(\d+)', message, re.IGNORECASE)
    if expense_match:
        parsed = parse_add_expense(message)
        parsed['category_id'] = int(expense_match.group(1))
        return parsed

    # 一覧
    list_match = re.match(r'(?:(?:カテゴリ|category)(?:一覧|list)|list|categories)', message, re.IGNORECASE)
    if list_match:
        return {'action': 'list_categories'}

    # 支出一覧
    expenses_match = re.match(r'(?:(?:支出|expense)(?:一覧|list)|list|expenses)', message, re.IGNORECASE)
    if expenses_match:
        return {'action': 'list_expenses'}

    # カテゴリー別支出
    category_expenses_match = re.match(r'(?:カテゴリ|category)[：:]\s*(\d+)\s*(?:支出|expenses?)', message, re.IGNORECASE)
    if category_expenses_match:
        return {'action': 'category_expenses', 'category_id': int(category_expenses_match.group(1))}

    # 傾向
    trend_match = re.match(r'(?:傾向|trend)[：:]\s*(\d+)', message, re.IGNORECASE)
    if trend_match:
        return {'action': 'trend', 'category_id': int(trend_match.group(1))}

    # サマリー
    if message.strip() in ['サマリー', 'summary']:
        return {'action': 'summary'}

    return None

def parse_add_category(content):
    """カテゴリー追加を解析"""
    result = {'action': 'add_category', 'name': None, 'monthly_limit': None, 'description': None}

    # 名前 (最初の部分)
    name_match = re.match(r'^([^、,（\(【]+)', content)
    if name_match:
        result['name'] = name_match.group(1).strip()

    # 月次上限
    limit_match = re.search(r'(?:月次|monthly|上限|limit)[：:]?\s*(\d+)', content)
    if limit_match:
        result['monthly_limit'] = int(limit_match.group(1))

    # 説明
    desc_match = re.search(r'(?:説明|description|desc)[：:]\s*(.+)', content)
    if desc_match:
        result['description'] = desc_match.group(1).strip()

    # 名前がまだない場合、最初の項目より前を名前とする
    if not result['name']:
        for key in ['月次', 'monthly', '上限', 'limit', '説明', 'description', 'desc']:
            match = re.search(rf'{key}[：:]', content)
            if match:
                result['name'] = content[:match.start()].strip()
                break
        else:
            result['name'] = content.strip()

    return result

def parse_add_expense(content):
    """支出追加を解析"""
    result = {'action': 'add_expense', 'amount': None, 'description': None, 'date': None}

    # 金額
    amount_match = re.search(r'(?:金額|amount|￥|¥)[：:]?\s*(\d+)', content)
    if amount_match:
        result['amount'] = int(amount_match.group(1))

    # 説明
    desc_match = re.search(r'(?:説明|description|desc|内容)[：:]\s*(.+)', content)
    if desc_match:
        result['description'] = desc_match.group(1).strip()

    # 日付
    date_match = re.search(r'(?:日付|date)[：:]\s*([^、,]+)', content)
    if date_match:
        result['date'] = parse_date(date_match.group(1).strip())

    # 説明がない場合、日付より前を説明とする
    if not result['description']:
        for key in ['日付', 'date', '金額', 'amount', '￥', '¥']:
            match = re.search(rf'{key}[：:]', content)
            if match:
                result['description'] = content[:match.start()].strip()
                break
        else:
            result['description'] = content.strip()

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

    if action == 'add_category':
        if not parsed['name']:
            return "❌ カテゴリー名を入力してください"

        category_id = add_category(
            parsed['name'],
            parsed['monthly_limit'],
            parsed['description']
        )

        response = f"✅ カテゴリー #{category_id} 追加完了\n"
        response += f"名前: {parsed['name']}\n"
        if parsed['monthly_limit']:
            response += f"月次上限: ¥{parsed['monthly_limit']:,}\n"
        if parsed['description']:
            response += f"説明: {parsed['description']}"

        return response

    elif action == 'add_expense':
        if not parsed['amount']:
            return "❌ 金額を入力してください"

        expense_id = add_expense(
            parsed['category_id'],
            parsed['amount'],
            parsed['description'],
            parsed['date']
        )

        category_id = parsed['category_id']
        category_name = f"カテゴリー#{category_id}"
        categories = list_categories()
        for c in categories:
            if c[0] == category_id:
                category_name = c[1]
                break

        return f"✅ 支出 #{expense_id} 追加完了: ¥{parsed['amount']:,} ({category_name})"

    elif action == 'list_categories':
        categories = list_categories()

        if not categories:
            return "📋 カテゴリーがありません"

        response = f"📋 カテゴリー一覧 ({len(categories)}件):\n"
        for category in categories:
            response += format_category(category)

        return response

    elif action == 'list_expenses':
        expenses = list_expenses()

        if not expenses:
            return "💸 支出がありません"

        response = f"💸 支出一覧 ({len(expenses)}件):\n"
        for expense in expenses:
            response += format_expense(expense)

        return response

    elif action == 'category_expenses':
        expenses = list_expenses(category_id=parsed['category_id'])

        category_id = parsed['category_id']
        category_name = f"カテゴリー#{category_id}"
        categories = list_categories()
        for c in categories:
            if c[0] == category_id:
                category_name = c[1]
                break

        if not expenses:
            return f"💸 {category_name}の支出がありません"

        response = f"💸 {category_name}の支出 ({len(expenses)}件):\n"
        for expense in expenses:
            response += format_expense(expense)

        return response

    elif action == 'trend':
        category_id = parsed['category_id']
        trend = get_spending_trend(category_id, months=6)

        category_name = f"カテゴリー#{category_id}"
        categories = list_categories()
        for c in categories:
            if c[0] == category_id:
                category_name = c[1]
                break

        if not trend:
            return f"📈 {category_name}の支出傾向データがありません"

        response = f"📈 {category_name}の支出傾向 (6ヶ月間):\n"
        for month, total in trend:
            response += f"  {month}: ¥{total:,}\n"

        return response

    elif action == 'summary':
        categories = list_categories()
        current_month = datetime.now().strftime("%Y-%m")

        if not categories:
            return "📊 サマリーがありません"

        response = f"📊 {current_month}のサマリー:\n"
        total_spent = 0
        total_limit = 0

        for category in categories:
            category_id = category[0]
            category_name = category[1]
            monthly_limit = category[2]
            spent = get_monthly_spending(category_id)

            total_spent += spent
            if monthly_limit:
                total_limit += monthly_limit
                pct = (spent / monthly_limit) * 100 if monthly_limit > 0 else 0
                status = "✅" if pct < 80 else "⚠️" if pct < 100 else "❌"
                response += f"  {status} {category_name}: ¥{spent:,}/¥{monthly_limit:,} ({pct:.0f}%)\n"
            else:
                response += f"  💸 {category_name}: ¥{spent:,}\n"

        if total_limit > 0:
            total_pct = (total_spent / total_limit) * 100
            response += f"\n  合計: ¥{total_spent:,}/¥{total_limit:,} ({total_pct:.0f}%)\n"
        else:
            response += f"\n  合計: ¥{total_spent:,}\n"

        return response

    return None

def format_category(category):
    """カテゴリーをフォーマット"""
    id, name, monthly_limit, description, created_at = category

    response = f"\n[{id}] {name}\n"

    parts = []
    if monthly_limit:
        parts.append(f"💰 ¥{monthly_limit:,}/月")
    if description:
        parts.append(f"📝 {description[:50]}{'...' if len(description) > 50 else ''}")

    if parts:
        response += f"  {' '.join(parts)}\n"

    return response

def format_expense(expense):
    """支出をフォーマット"""
    id, category_id, amount, description, date, created_at, category_name = expense

    cat_name = category_name or "未分類"

    response = f"\n[{id}] {date} - ¥{amount:,} ({cat_name})\n"

    if description:
        response += f"  {description[:50]}{'...' if len(description) > 50 else ''}\n"

    return response

if __name__ == '__main__':
    # テスト
    init_db()

    test_messages = [
        "カテゴリ: 食費, 月次: 50000, 説明: 食料品・外食",
        "支出: 1, 金額: 1500, 説明: コンビニ",
        "カテゴリ一覧",
        "支出一覧",
        "サマリー",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
