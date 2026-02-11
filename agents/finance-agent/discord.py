#!/usr/bin/env python3
"""
ファイナンスエージェント #38 - Discord連携
"""

import re
from datetime import datetime
from db import *

def parse_message(message):
    """メッセージを解析"""
    # 収入追加
    income_match = re.match(r'(?:収入|income)[：:]\s*(.+)', message, re.IGNORECASE)
    if income_match:
        parsed = parse_add_transaction(income_match.group(1))
        parsed['type'] = 'income'
        return parsed

    # 支出追加
    expense_match = re.match(r'(?:支出|expense|出費|cost)[：:]\s*(.+)', message, re.IGNORECASE)
    if expense_match:
        parsed = parse_add_transaction(expense_match.group(1))
        parsed['type'] = 'expense'
        return parsed

    # 更新
    update_match = re.match(r'(?:更新|update)[：:]\s*(\d+)\s*(.+)', message, re.IGNORECASE)
    if update_match:
        return {'action': 'update', 'trans_id': int(update_match.group(1)), 'content': update_match.group(2)}

    # 削除
    delete_match = re.match(r'(?:削除|delete|remove)[：:]\s*(\d+)', message, re.IGNORECASE)
    if delete_match:
        return {'action': 'delete', 'trans_id': int(delete_match.group(1))}

    # 予算追加
    budget_match = re.match(r'(?:予算|budget)[：:]\s*(.+)', message, re.IGNORECASE)
    if budget_match:
        return parse_add_budget(budget_match.group(1))

    # 検索
    search_match = re.match(r'(?:検索|search)[：:]\s*(.+)', message, re.IGNORECASE)
    if search_match:
        return {'action': 'search', 'keyword': search_match.group(1)}

    # 一覧
    list_match = re.match(r'(?:(?:取引|transaction)(?:一覧|list)|list|transactions)', message, re.IGNORECASE)
    if list_match:
        return {'action': 'list'}

    # 収入一覧
    if message.strip() in ['収入', 'income', '収入一覧']:
        return {'action': 'list_income'}

    # 支出一覧
    if message.strip() in ['支出', 'expense', '支出一覧']:
        return {'action': 'list_expense'}

    # 予算一覧
    if message.strip() in ['予算', 'budget', '予算一覧']:
        return {'action': 'list_budgets'}

    # 今月
    if message.strip() in ['今月', 'this month', '今月一覧']:
        return {'action': 'this_month'}

    # 統計
    if message.strip() in ['統計', 'stats', '金融統計']:
        return {'action': 'stats'}

    return None

def parse_add_transaction(content):
    """取引追加を解析"""
    result = {'action': 'add', 'date': None, 'type': None, 'category': None,
              'amount': None, 'description': None, 'tags': None}

    # 日付
    date_match = re.search(r'(?:日付|date)[：:]\s*([^、,]+)', content)
    if date_match:
        result['date'] = parse_date(date_match.group(1).strip())
    else:
        # デフォルトは今日
        result['date'] = datetime.now().strftime("%Y-%m-%d")

    # カテゴリ
    category_match = re.search(r'(?:カテゴリ|category)[：:]\s*([^、,]+)', content)
    if category_match:
        result['category'] = category_match.group(1).strip()

    # 金額
    amount_match = re.search(r'(?:金額|amount|￥|¥)[：:]?\s*(\d+)', content)
    if amount_match:
        result['amount'] = int(amount_match.group(1))

    # 説明
    description_match = re.search(r'(?:説明|description|内容|desc)[：:]\s*(.+)', content)
    if description_match:
        result['description'] = description_match.group(1).strip()

    # タグ
    tags_match = re.search(r'(?:タグ|tags)[：:]\s*(.+)', content)
    if tags_match:
        result['tags'] = tags_match.group(1).strip()

    # 説明がない場合、最初の項目より前を説明とする
    if not result['description']:
        for key in ['日付', 'date', 'カテゴリ', 'category', '金額', 'amount', '￥', '¥',
                    'タグ', 'tags']:
            match = re.search(rf'{key}[：:]', content)
            if match:
                result['description'] = content[:match.start()].strip()
                break
        else:
            result['description'] = content.strip()

    return result

def parse_add_budget(content):
    """予算追加を解析"""
    result = {'action': 'add_budget', 'category': None, 'amount': None, 'period': 'monthly',
              'start_date': None, 'end_date': None}

    # カテゴリ
    category_match = re.search(r'(?:カテゴリ|category)[：:]\s*([^、,]+)', content)
    if category_match:
        result['category'] = category_match.group(1).strip()

    # 金額
    amount_match = re.search(r'(?:金額|amount|￥|¥)[：:]?\s*(\d+)', content)
    if amount_match:
        result['amount'] = int(amount_match.group(1))

    # 期間
    period_match = re.search(r'(?:期間|period)[：:]\s*(daily|weekly|monthly|yearly|日次|週次|月次|年次)', content)
    if period_match:
        period_map = {
            'daily': 'daily', '日次': 'daily',
            'weekly': 'weekly', '週次': 'weekly',
            'monthly': 'monthly', '月次': 'monthly',
            'yearly': 'yearly', '年次': 'yearly'
        }
        result['period'] = period_map.get(period_match.group(1).lower(), 'monthly')

    # カテゴリがない場合、最初の項目より前をカテゴリとする
    if not result['category']:
        for key in ['カテゴリ', 'category', '金額', 'amount', '￥', '¥', '期間', 'period']:
            match = re.search(rf'{key}[：:]', content)
            if match:
                result['category'] = content[:match.start()].strip()
                break
        else:
            result['category'] = content.strip()

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
        if not parsed['amount']:
            return "❌ 金額を入力してください"

        trans_id = add_transaction(
            parsed['date'],
            parsed['type'],
            parsed['amount'],
            parsed['category'],
            parsed['description'],
            parsed['tags']
        )

        type_text = {'income': '収入', 'expense': '支出', 'transfer': '送金'}.get(parsed['type'], parsed['type'])

        response = f"💰 {type_text} #{trans_id} 追加完了\n"
        response += f"日付: {parsed['date']}\n"
        response += f"金額: ¥{parsed['amount']:,}\n"
        if parsed['category']:
            response += f"カテゴリ: {parsed['category']}\n"
        if parsed['description']:
            response += f"説明: {parsed['description']}\n"
        if parsed['tags']:
            response += f"タグ: {parsed['tags']}"

        return response

    elif action == 'update':
        # 取引更新（簡易実装）
        return f"✅ 取引 #{parsed['trans_id']} 更新機能は準備中です"

    elif action == 'delete':
        delete_transaction(parsed['trans_id'])
        return f"🗑️ 取引 #{parsed['trans_id']} 削除完了"

    elif action == 'add_budget':
        if not parsed['category'] or not parsed['amount']:
            return "❌ カテゴリと金額を入力してください"

        budget_id = add_budget(
            parsed['category'],
            parsed['amount'],
            parsed['period'],
            parsed['start_date'],
            parsed['end_date']
        )

        period_text = {'daily': '日次', 'weekly': '週次', 'monthly': '月次', 'yearly': '年次'}.get(parsed['period'], parsed['period'])

        response = f"💰 予算 #{budget_id} 追加完了\n"
        response += f"カテゴリ: {parsed['category']}\n"
        response += f"金額: ¥{parsed['amount']:,}\n"
        response += f"期間: {period_text}"

        return response

    elif action == 'search':
        keyword = parsed['keyword']
        transactions = search_transactions(keyword)

        if not transactions:
            return f"🔍 「{keyword}」の検索結果: 見つかりませんでした"

        response = f"🔍 「{keyword}」の検索結果 ({len(transactions)}件):\n"
        for trans in transactions:
            response += format_transaction(trans)

        return response

    elif action == 'list':
        transactions = list_transactions()

        if not transactions:
            return "💰 取引がありません"

        response = f"💰 取引一覧 ({len(transactions)}件):\n"
        for trans in transactions:
            response += format_transaction(trans)

        return response

    elif action == 'list_income':
        transactions = list_transactions(type='income')

        if not transactions:
            return "💰 収入がありません"

        response = f"💰 収入 ({len(transactions)}件):\n"
        for trans in transactions:
            response += format_transaction(trans)

        return response

    elif action == 'list_expense':
        transactions = list_transactions(type='expense')

        if not transactions:
            return "💰 支出がありません"

        response = f"💰 支出 ({len(transactions)}件):\n"
        for trans in transactions:
            response += format_transaction(trans)

        return response

    elif action == 'list_budgets':
        budgets = list_budgets()

        if not budgets:
            return "💰 予算がありません"

        response = f"💰 予算一覧 ({len(budgets)}件):\n"
        for budget in budgets:
            response += format_budget(budget)

        return response

    elif action == 'this_month':
        current_month = datetime.now().strftime("%Y-%m")
        from datetime import timedelta
        first_day = f"{current_month}-01"
        next_month = datetime(datetime.now().year, datetime.now().month + 1, 1).strftime("%Y-%m-%d") if datetime.now().month < 12 else f"{datetime.now().year + 1}-01-01"

        transactions = list_transactions(date_from=first_day, date_to=next_month)

        if not transactions:
            return f"💰 今月の取引はありません"

        response = f"💰 今月の取引 ({len(transactions)}件):\n"
        for trans in transactions:
            response += format_transaction(trans)

        return response

    elif action == 'stats':
        stats = get_stats()

        response = "📊 金融統計:\n"
        response += f"全取引数: {stats['total_transactions']}件\n"
        response += f"今月の収入: ¥{stats['month_income']:,}\n"
        response += f"今月の支出: ¥{stats['month_expense']:,}\n"
        response += f"今月の収支: ¥{stats['month_balance']:,}"

        if stats['month_balance'] > 0:
            response += " 📈"
        elif stats['month_balance'] < 0:
            response += " 📉"

        if stats['expenses_by_category']:
            response += "\n\nカテゴリ別支出:\n"
            for category, amount in stats['expenses_by_category'][:5]:
                response += f"  {category}: ¥{amount:,}\n"

        return response

    return None

def format_transaction(trans):
    """取引をフォーマット"""
    id, date, type, category, amount, description, tags, created_at = trans

    type_icons = {'income': '📈', 'expense': '📉', 'transfer': '💸'}
    type_icon = type_icons.get(type, '💰')

    response = f"\n{type_icon} [{id}] {date} - ¥{amount:,}\n"

    parts = []
    if category:
        parts.append(f"📁 {category}")
    if description:
        parts.append(f"📝 {description[:50]}{'...' if len(description) > 50 else ''}")

    if parts:
        response += f"    {' '.join(parts)}\n"

    return response

def format_budget(budget):
    """予算をフォーマット"""
    id, category, amount, period, start_date, end_date, created_at = budget

    period_text = {'daily': '日次', 'weekly': '週次', 'monthly': '月次', 'yearly': '年次'}.get(period, period)

    response = f"\n📊 [{id}] {category}\n"
    response += f"    予算: ¥{amount:,} / {period_text}\n"

    return response

if __name__ == '__main__':
    # テスト
    init_db()

    test_messages = [
        "収入: 給料, 金額: 300000, カテゴリ: 給与",
        "支出: コーヒー, 金額: 500, カテゴリ: 食費",
        "予算: 食費, 金額: 50000, 期間: 月次",
        "今月",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
