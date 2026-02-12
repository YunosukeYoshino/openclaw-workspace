#!/usr/bin/env python3
"""
誕生日管理エージェント #58 - Discord連携
"""

import re
from datetime import datetime, timedelta
from db import *

def parse_message(message):
    birthday_match = re.match(r'(?:誕生日|birthday|誕生)[：:]\s*(.+)', message, re.IGNORECASE)
    if birthday_match:
        return parse_add_birthday(birthday_match.group(1))

    gift_match = re.match(r'(?:ギフト|gift)[：:]\s*(\d+)\s*(.+)', message, re.IGNORECASE)
    if gift_match:
        parsed = parse_add_gift(gift_match.group(2))
        parsed['birthday_id'] = int(gift_match.group(1))
        return parsed

    list_match = re.match(r'(?:(?:誕生日|birthday)(?:一覧|list)|list|birthdays)', message, re.IGNORECASE)
    if list_match:
        return {'action': 'list'}

    upcoming_match = re.match(r'(?:来る|upcoming|次|next)[：:]\s*(\d+)', message, re.IGNORECASE)
    if upcoming_match:
        days = int(upcoming_match.group(1))
        return {'action': 'upcoming', 'days': days}

    if message.strip() in ['来月', 'next month', '次の月', '来月分']:
        return {'action': 'next_month'}

    gifts_match = re.match(r'(?:ギフト|gift)(?:履歴|history)[：:]\s*(\d+)', message, re.IGNORECASE)
    if gifts_match:
        return {'action': 'gifts', 'birthday_id': int(gifts_match.group(1))}

    update_match = re.match(r'(?:更新|update)[：:]\s*(\d+)\s*(.+)', message, re.IGNORECASE)
    if update_match:
        parsed = parse_update(update_match.group(2))
        parsed['birthday_id'] = int(update_match.group(1))
        return parsed

    month_match = re.match(r'(\d+)', message)
    if month_match:
        return {'action': 'month', 'month': int(month_match.group(1))}

    return None

def parse_add_birthday(content):
    result = {'action': 'add', 'name': None, 'birth_date': None, 'year': None, 'category': None, 'notes': None}

    name_match = re.match(r'^([^、,（\(【]+)', content)
    if name_match:
        result['name'] = name_match.group(1).strip()

    date_match = re.search(r'(?:日付|date|誕生日|birthday)[：:]\s*([^、,]+)', content)
    if date_match:
        result['birth_date'] = parse_date(date_match.group(1).strip())

    year_match = re.search(r'(?:年|year)[：:]?\s*(\d{4})', content)
    if year_match:
        result['year'] = int(year_match.group(1))

    category_match = re.search(r'(?:カテゴリ|category)[：:]\s*([^、,]+)', content)
    if category_match:
        result['category'] = category_match.group(1).strip()

    notes_match = re.search(r'(?:メモ|備考|memo|note)[：:]\s*(.+)', content)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    if not result['name']:
        for key in ['日付', 'date', '誕生日', 'birthday', '年', 'year', 'カテゴリ', 'category', 'メモ', '備考', 'memo', 'note']:
            match = re.search(rf'{key}[：:]', content)
            if match:
                result['name'] = content[:match.start()].strip()
                break
        else:
            result['name'] = content.strip()

    return result

def parse_add_gift(content):
    result = {'action': 'add_gift', 'year': None, 'gift': None, 'note': None}

    year_match = re.search(r'(?:年|year)[：:]?\s*(\d{4})', content)
    if year_match:
        result['year'] = int(year_match.group(1))
    else:
        result['year'] = datetime.now().year

    gift_match = re.search(r'(?:ギフト|gift)[：:]\s*(.+)', content)
    if gift_match:
        result['gift'] = gift_match.group(1).strip()

    note_match = re.search(r'(?:メモ|備考|memo|note)[：:]\s*(.+)', content)
    if note_match:
        result['note'] = note_match.group(1).strip()

    if not result['gift']:
        for key in ['年', 'year', 'メモ', '備考', 'memo', 'note']:
            match = re.search(rf'{key}[：:]', content)
            if match:
                result['gift'] = content[:match.start()].strip()
                break
        else:
            result['gift'] = content.strip()

    return result

def parse_update(content):
    result = {'action': 'update', 'name': None, 'birth_date': None, 'year': None, 'category': None, 'notes': None}

    name_match = re.search(r'(?:名前|name)[：:]\s*([^、,]+)', content)
    if name_match:
        result['name'] = name_match.group(1).strip()

    date_match = re.search(r'(?:日付|date)[：:]\s*([^、,]+)', content)
    if date_match:
        result['birth_date'] = parse_date(date_match.group(1).strip())

    year_match = re.search(r'(?:年|year)[：:]?\s*(\d{4})', content)
    if year_match:
        result['year'] = int(year_match.group(1))

    category_match = re.search(r'(?:カテゴリ|category)[：:]\s*([^、,]+)', content)
    if category_match:
        result['category'] = category_match.group(1).strip()

    notes_match = re.search(r'(?:メモ|備考|memo|note)[：:]\s*(.+)', content)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    return result

def parse_date(date_str):
    today = datetime.now()

    if '今日' in date_str:
        return today.strftime("%m-%d")
    if '明日' in date_str:
        return (today + timedelta(days=1)).strftime("%m-%d")

    date_match = re.match(r'(\d{1,2})/(\d{1,2})', date_str)
    if date_match:
        month = int(date_match.group(1))
        day = int(date_match.group(2))
        return f"{month:02d}-{day:02d}"

    return None

def handle_message(message):
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'add':
        if not parsed['name']:
            return "❌ 名前を入力してください"

        birthday_id = add_birthday(
            parsed['name'],
            parsed['birth_date'],
            parsed['year'],
            parsed['category'],
            parsed['notes']
        )

        response = f"🎂 誕生日 #{birthday_id} 追加完了\n"
        response += f"名前: {parsed['name']}\n"
        if parsed['birth_date']:
            response += f"誕生日: {parsed['birth_date']}\n"
        if parsed['year']:
            response += f"年: {parsed['year']}\n"
        if parsed['category']:
            response += f"カテゴリ: {parsed['category']}\n"
        if parsed['notes']:
            response += f"メモ: {parsed['notes']}"

        return response

    elif action == 'add_gift':
        if not parsed['gift']:
            return "❌ ギフトを入力してください"

        gift_id = add_gift(
            parsed['birthday_id'],
            parsed['year'],
            parsed['gift'],
            parsed['note']
        )

        return f"🎁 ギフト #{gift_id} 追加完了"

    elif action == 'update':
        update_birthday(
            parsed['birthday_id'],
            name=parsed['name'],
            birth_date=parsed['birth_date'],
            year=parsed['year'],
            category=parsed['category'],
            notes=parsed['notes']
        )

        return f"✅ 誕生日 #{parsed['birthday_id']} 更新完了"

    elif action == 'list':
        birthdays = list_birthdays()

        if not birthdays:
            return "🎂 誕生日がありません"

        response = f"🎂 誕生日 ({len(birthdays)}人):\n"
        for birthday in birthdays:
            response += format_birthday(birthday)

        return response

    elif action == 'month':
        month = parsed['month']
        if month < 1 or month > 12:
            return "❌ 無効な月です"

        birthdays = list_birthdays(month=f"{month:02d}")

        if not birthdays:
            return f"🎂 {month}月の誕生日はありません"

        response = f"🎂 {month}月の誕生日 ({len(birthdays)}人):\n"
        for birthday in birthdays:
            response += format_birthday(birthday)

        return response

    elif action == 'upcoming':
        days = parsed['days']
        birthdays = get_upcoming(days)

        if not birthdays:
            return f"🎂 今後{days}日以内の誕生日はありません"

        response = f"🎂 今後{days}日以内の誕生日 ({len(birthdays)}人):\n"
        for birthday in birthdays:
            response += format_birthday(birthday)

        return response

    elif action == 'next_month':
        next_month = (datetime.now().replace(day=1) + timedelta(days=32)).replace(day=1).month
        birthdays = list_birthdays(month=f"{next_month:02d}")

        if not birthdays:
            return f"🎂 来月の誕生日はありません"

        response = f"🎂 来月の誕生日 ({len(birthdays)}人):\n"
        for birthday in birthdays:
            response += format_birthday(birthday)

        return response

    elif action == 'gifts':
        gifts = get_gifts(parsed['birthday_id'])

        birthday_id = parsed['birthday_id']
        birthday_name = f"誕生日#{birthday_id}"
        birthdays = list_birthdays()
        for b in birthdays:
            if b[0] == birthday_id:
                birthday_name = b[1]
                break

        if not gifts:
            return f"🎁 {birthday_name}のギフト履歴がありません"

        response = f"🎁 {birthday_name}のギフト履歴 ({len(gifts)}件):\n"
        for gift in gifts:
            response += format_gift(gift)

        return response

    return None

def format_birthday(birthday):
    id, name, birth_date, year, category, notes, created_at = birthday

    today = datetime.now()
    birth_month, birth_day = map(int, birth_date.split('-'))
    this_year_birthday = datetime(today.year, birth_month, birth_day)

    if this_year_birthday >= today:
        age = this_year_birthday.year - (year if year else this_year_birthday.year)
    else:
        age = this_year_birthday.year - (year if year else this_year_birthday.year) - 1

    if age < 0:
        age_text = "👶"
    elif age < 18:
        age_text = "👧"
    elif age < 30:
        age_text = "👨"
    elif age < 50:
        age_text = "👩"
    else:
        age_text = "👴"

    response = f"{age_text} [{id}] {name} ({age}歳) - {birth_date}"

    if category:
        response += f" [{category}]"

    response += "\n"

    if notes:
        response += f"  📝 {notes[:50]}{'...' if len(notes) > 50 else ''}\n"

    return response

def format_gift(gift):
    id, birthday_id, year, gift, note, created_at = gift

    response = f"🎁 [{id}] {year}年: {gift}"

    if note:
        response += f" ({note[:30]}{'...' if len(note) > 30 else ''})"

    response += "\n"

    return response

if __name__ == '__main__':
    init_db()

    test_messages = [
        "誕生日: 山田, 日付: 5/20, 年: 1985",
        "誕生日: 鈴木, 日付: 8/10, 年: 1990",
        "誕生日一覧",
        "来る 30",
        "ギフト: 1 今年, ギフト: 本",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
