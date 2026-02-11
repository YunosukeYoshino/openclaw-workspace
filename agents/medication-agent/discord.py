#!/usr/bin/env python3
"""
薬服用エージェント #49 - Discord連携
"""

import re
from datetime import datetime, timedelta
from db import *

def parse_message(message):
    """メッセージを解析"""
    # 追加
    add_match = re.match(r'(?:薬|med|medication|pill|飲んだ|took)[：:]\s*(.+)', message, re.IGNORECASE)
    if add_match:
        return {'action': 'add', 'content': add_match.group(1)}

    # 更新
    update_match = re.match(r'(?:更新|update)[：:]\s*(\d+)\s*(.+)', message, re.IGNORECASE)
    if update_match:
        return {'action': 'update', 'med_id': int(update_match.group(1)), 'content': update_match.group(2)}

    # 削除
    delete_match = re.match(r'(?:削除|delete|remove)[：:]\s*(\d+)', message, re.IGNORECASE)
    if delete_match:
        return {'action': 'delete', 'med_id': int(delete_match.group(1))}

    # 服用済み
    take_match = re.match(r'(?:服用|take|drank|飲んだ)[：:]\s*(\d+)', message, re.IGNORECASE)
    if take_match:
        return {'action': 'take', 'med_id': int(take_match.group(1))}

    # スキップ
    skip_match = re.match(r'(?:スキップ|skip|飛ばした)[：:]\s*(\d+)', message, re.IGNORECASE)
    if skip_match:
        return {'action': 'skip', 'med_id': int(skip_match.group(1))}

    # 検索
    search_match = re.match(r'(?:検索|search)[：:]\s*(.+)', message, re.IGNORECASE)
    if search_match:
        return {'action': 'search', 'keyword': search_match.group(1)}

    # 一覧
    if message.strip() in ['薬', 'med', 'medication', '薬記録', 'medications']:
        return {'action': 'list'}

    # 今日
    if message.strip() in ['今日', 'today']:
        return {'action': 'today'}

    # 統計
    if message.strip() in ['統計', 'stats', 'statistics']:
        return {'action': 'stats'}

    # 薬リスト
    if message.strip() in ['薬一覧', 'meds list', '名前']:
        return {'action': 'names'}

    return None

def parse_medication_content(content):
    """薬内容を解析"""
    result = {'name': None, 'dosage': None, 'unit': 'mg', 'frequency': None,
              'time_taken': None, 'date': None, 'notes': None,
              'prescribed_by': None, 'reason': None, 'taken': True}

    # 薬の名前
    name_match = re.search(r'(?:名前|name)[：:]\s*(.+)', content, re.IGNORECASE)
    if name_match:
        result['name'] = name_match.group(1).strip()

    # 用量
    dose_match = re.search(r'(?:用量|dosage|量)[×:]?\s*(\d+(?:\.\d+)?)', content, re.IGNORECASE)
    if dose_match:
        result['dosage'] = float(dose_match.group(1))

    # 単位
    unit_match = re.search(r'(?:単位|unit)[×:]?\s*(mg|g|ml|l|tablet|capsule|pill)', content, re.IGNORECASE)
    if unit_match:
        result['unit'] = unit_match.group(1).lower()

    # 頻度
    freq_match = re.search(r'(?:頻度|frequency)[：:]\s*(.+)', content, re.IGNORECASE)
    if freq_match:
        result['frequency'] = freq_match.group(1).strip()

    # 時間
    time_match = re.search(r'(?:時間|time)[：:]\s*(\d{1,2}:\d{2})', content, re.IGNORECASE)
    if time_match:
        result['time_taken'] = time_match.group(1).strip()

    # 日付
    date_match = re.search(r'(?:日付|date)[：:]\s*([^、,]+)', content, re.IGNORECASE)
    if date_match:
        result['date'] = parse_date(date_match.group(1).strip())

    # 処方者
    presc_match = re.search(r'(?:処方|prescribed|doctor|dr)[：:]\s*(.+)', content, re.IGNORECASE)
    if presc_match:
        result['prescribed_by'] = presc_match.group(1).strip()

    # 理由
    reason_match = re.search(r'(?:理由|reason|for|purpose)[：:]\s*(.+)', content, re.IGNORECASE)
    if reason_match:
        result['reason'] = reason_match.group(1).strip()

    # メモ
    notes_match = re.search(r'(?:メモ|memo|note)[：:]\s*(.+)', content, re.IGNORECASE)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    # 最初の項目より前を名前とする
    for key in ['名前', 'name', '用量', 'dosage', '頻度', 'frequency']:
        match = re.search(rf'{key}[×:：]', content)
        if match:
            result['name'] = content[:match.start()].strip()
            break
    else:
        result['name'] = content.strip()

    return result

def parse_update_content(content):
    """更新内容を解析"""
    result = parse_medication_content(content)

    # takenフラグはデフォルトでNoneにする
    result['taken'] = None

    return {k: v for k, v in result.items() if v is not None}

def parse_date(date_str):
    """日付を解析"""
    today = datetime.now()

    if '今日' in date_str:
        return today.strftime("%Y-%m-%d")
    if '昨日' in date_str:
        return (today - timedelta(days=1)).strftime("%Y-%m-%d")
    if '明日' in date_str:
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")

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
        content = parse_medication_content(parsed['content'])

        if not content['name']:
            return "❌ 薬の名前を入力してください"

        med_id = add_medication(
            name=content['name'],
            dosage=content['dosage'],
            unit=content['unit'],
            frequency=content['frequency'],
            time_taken=content['time_taken'],
            date=content['date'],
            notes=content['notes'],
            prescribed_by=content['prescribed_by'],
            reason=content['reason'],
            taken=content['taken']
        )

        response = f"💊 薬 #{med_id} 記録完了\n"
        response += f"名前: {content['name']}\n"
        if content['dosage']:
            response += f"用量: {content['dosage']}{content['unit']}\n"
        if content['frequency']:
            response += f"頻度: {content['frequency']}\n"
        if content['time_taken']:
            response += f"時間: {content['time_taken']}\n"
        if content['reason']:
            response += f"理由: {content['reason']}\n"
        if content['prescribed_by']:
            response += f"処方: {content['prescribed_by']}"
        if content['date']:
            response += f"\n日付: {content['date']}"

        return response

    elif action == 'update':
        updates = parse_update_content(parsed['content'])

        if not updates:
            return "❌ 更新内容がありません"

        update_medication(parsed['med_id'], **updates)

        response = f"✅ 薬 #{parsed['med_id']} 更新完了"

        return response

    elif action == 'delete':
        delete_medication(parsed['med_id'])
        return f"🗑️ 薬 #{parsed['med_id']} 削除完了"

    elif action == 'take':
        mark_taken(parsed['med_id'], taken=True)
        return f"✅ 薬 #{parsed['med_id']} 服用済みにマークしました"

    elif action == 'skip':
        mark_skipped(parsed['med_id'])
        return f"⏭️ 薬 #{parsed['med_id']} スキップにマークしました"

    elif action == 'search':
        keyword = parsed['keyword']
        medications = search_medications(keyword)

        if not medications:
            return f"🔍 「{keyword}」の検索結果: 見つかりませんでした"

        response = f"🔍 「{keyword}」の検索結果 ({len(medications)}件):\n"
        for med in medications:
            response += format_medication(med)

        return response

    elif action == 'list':
        medications = list_medications()

        if not medications:
            return "💊 薬の記録がありません"

        response = f"💊 薬の記録 ({len(medications)}件):\n"
        for med in medications:
            response += format_medication(med)

        return response

    elif action == 'names':
        names = get_medication_names()

        if not names:
            return "📋 薬がありません"

        response = "📋 薬一覧:\n"
        for name, count, avg_dosage in names:
            response += f"  • {name}"
            if avg_dosage:
                response += f" (平均: {avg_dosage:.1f})"
            response += f" - {count}回\n"

        return response

    elif action == 'today':
        date = datetime.now().strftime("%Y-%m-%d")
        medications = get_by_date(date)

        if not medications:
            return f"💊 今日の薬の記録はありません"

        response = f"💊 今日の薬 ({len(medications)}件):\n"
        for med in medications:
            response += format_medication(med, show_date=False)

        return response

    elif action == 'stats':
        stats = get_stats()

        response = "📊 統計情報:\n"
        response += f"総記録数: {stats['total_records']}回\n"
        response += f"服用済み: {stats['taken']}回\n"
        response += f"スキップ: {stats['skipped']}回\n"
        response += f"服用率: {stats['adherence']:.1f}%\n"
        response += f"一意な薬: {stats['unique_medications']}種類\n"
        response += f"今日: {stats['today_taken']}/{stats['today_total']}回"
        if stats['today_skipped']:
            response += f" (スキップ: {stats['today_skipped']})"

        return response

    return None

def format_medication(med, show_date=True):
    """薬をフォーマット"""
    id, name, dosage, unit, frequency, time_taken, date, notes, prescribed_by, reason, taken, skipped, created_at = med

    if taken:
        status_emoji = "✅"
    elif skipped:
        status_emoji = "⏭️"
    else:
        status_emoji = "⏳"

    response = ""
    if show_date:
        response = f"\n{status_emoji} [{id}] {date} {time_taken} - {name}\n"
    else:
        response = f"\n{status_emoji} [{id}] {time_taken} - {name}\n"

    if dosage:
        response += f"    用量: {dosage}{unit}"

    if frequency:
        response += f"\n    頻度: {frequency}"

    if reason:
        response += f"\n    理由: {reason}"

    if prescribed_by:
        response += f"\n    処方: {prescribed_by}"

    if notes:
        response += f"\n    📝 {notes}"

    return response

if __name__ == '__main__':
    init_db()

    test_messages = [
        "薬: イブプロフェン, 用量: 200, 理由: 頭痛",
        "薬: ビタミンC, 用量: 1000, 頻度: 1日1回",
        "薬: 薬A, 日付: 今日",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
