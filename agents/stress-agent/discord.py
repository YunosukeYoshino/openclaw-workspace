#!/usr/bin/env python3
"""
ストレスレベル記録エージェント #63 - Discord連携
"""

import re
from datetime import datetime
from db import *

def parse_message(message):
    """メッセージを解析"""
    # ストレス追加
    stress_match = re.match(r'(?:ストレス|stress)[：:]\s*(.+)', message, re.IGNORECASE)
    if stress_match:
        return parse_stress(stress_match.group(1))

    # リラックス方法追加
    relax_match = re.match(r'(?:リラックス|relax|relaxation)[：:]\s*(.+)', message, re.IGNORECASE)
    if relax_match:
        return parse_relaxation(relax_match.group(1))

    # ストレス一覧
    if message.strip() in ['ストレス一覧', 'ストレス', 'stress', 'stress list']:
        return {'action': 'list_stress'}

    # リラックス方法一覧
    if message.strip() in ['リラックス一覧', 'リラックス', 'relaxation', 'relax list']:
        return {'action': 'list_relax'}

    # 統計
    if message.strip() in ['統計', 'stats', 'ストレス統計']:
        return {'action': 'stats'}

    return None

def parse_stress(content):
    """ストレス情報を解析"""
    result = {'action': 'add_stress', 'level': None, 'trigger': None, 'category': None, 'symptoms': None, 'notes': None}

    # レベル (1-10)
    level_match = re.search(r'(\d+)', content)
    if level_match:
        result['level'] = int(level_match.group(1))
        result['level'] = max(1, min(10, result['level']))

    # カテゴリ
    category_map = {
        '仕事': 'work', 'work': 'work', '業務': 'work',
        '個人的': 'personal', 'personal': 'personal', '個人': 'personal',
        '健康': 'health', 'health': 'health',
        'お金': 'finance', 'finance': 'finance', '金銭': 'finance', '経済': 'finance',
        '人間関係': 'relationship', 'relationship': 'relationship',
    }

    for key, value in category_map.items():
        if key in content:
            result['category'] = value
            break

    # 要因/トリガー
    trigger_match = re.search(r'(?:要因|trigger|cause)[：:]\s*([^、,カテゴリ]+)', content, re.IGNORECASE)
    if trigger_match:
        result['trigger'] = trigger_match.group(1).strip()

    # 症状
    symptoms_match = re.search(r'(?:症状|symptoms?)[：:]\s*([^、,メモ]+)', content, re.IGNORECASE)
    if symptoms_match:
        result['symptoms'] = symptoms_match.group(1).strip()

    # メモ
    notes_match = re.search(r'(?:メモ|memo|note)[：:]\s*(.+)', content, re.IGNORECASE)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    # レベルがまだない場合、デフォルト5
    if result['level'] is None:
        result['level'] = 5

    return result

def parse_relaxation(content):
    """リラックス方法を解析"""
    result = {'action': 'add_relaxation', 'name': None, 'category': None, 'effectiveness': 3, 'notes': None}

    # 名前（最初の項目）
    name_match = re.search(r'^(.*?)(?:[、,]|カテゴリ|有効性|メモ|$)', content)
    if name_match:
        result['name'] = name_match.group(1).strip()

    # 有効性
    eff_match = re.search(r'(?:有効性|effectiveness|rating)[：:]\s*(\d+)', content, re.IGNORECASE)
    if eff_match:
        result['effectiveness'] = int(eff_match.group(1))
        result['effectiveness'] = max(1, min(5, result['effectiveness']))

    # カテゴリ
    cat_match = re.search(r'(?:カテゴリ|category)[：:]\s*([^、,メモ]+)', content, re.IGNORECASE)
    if cat_match:
        result['category'] = cat_match.group(1).strip()

    # メモ
    notes_match = re.search(r'(?:メモ|memo|note)[：:]\s*(.+)', content, re.IGNORECASE)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    return result

def handle_message(message):
    """メッセージを処理"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'add_stress':
        if parsed['level'] is None:
            return "❌ ストレスレベルを入力してください（1-10）"

        stress_id = add_stress(
            parsed['level'],
            parsed['trigger'],
            parsed['category'],
            parsed['symptoms'],
            parsed['notes']
        )

        level_bar = '█' * parsed['level'] + '░' * (10 - parsed['level'])
        category_text = {
            'work': '💼 仕事',
            'personal': '👤 個人的',
            'health': '💊 健康',
            'finance': '💰 金銭',
            'relationship': '👥 人間関係',
            'other': '📝 その他'
        }.get(parsed['category'], '')

        response = f"😰 ストレス #{stress_id} 追加完了\n"
        response += f"レベル: {parsed['level']}/10 {level_bar}\n"
        if category_text:
            response += f"カテゴリ: {category_text}\n"
        if parsed['trigger']:
            response += f"要因: {parsed['trigger']}\n"
        if parsed['symptoms']:
            response += f"症状: {parsed['symptoms']}\n"
        if parsed['notes']:
            response += f"メモ: {parsed['notes']}"

        return response

    elif action == 'add_relaxation':
        if not parsed['name']:
            return "❌ リラックス方法の名前を入力してください"

        method_id = add_relaxation_method(
            parsed['name'],
            parsed['category'],
            parsed['effectiveness'],
            parsed['notes']
        )

        stars = '⭐' * parsed['effectiveness']

        response = f"🧘 リラックス方法 #{method_id} 追加完了\n"
        response += f"方法: {parsed['name']}\n"
        response += f"有効性: {parsed['effectiveness']}/5 {stars}"
        if parsed['category']:
            response += f"\nカテゴリ: {parsed['category']}"
        if parsed['notes']:
            response += f"\nメモ: {parsed['notes']}"

        return response

    elif action == 'list_stress':
        stress = list_stress()

        if not stress:
            return "😰 ストレス記録がありません"

        response = f"😰 ストレス記録 ({len(stress)}件):\n"
        for s in stress:
            response += format_stress(s)

        return response

    elif action == 'list_relax':
        methods = list_relaxation_methods()

        if not methods:
            return "🧘 リラックス方法がありません"

        response = f"🧘 リラックス方法 ({len(methods)}件):\n"
        for method in methods:
            response += format_relaxation(method)

        return response

    elif action == 'stats':
        stats = get_stats(days=7)

        response = "📊 週間ストレス統計:\n"
        response += f"記録数: {stats['total']}件\n"
        response += f"平均レベル: {stats['avg_level']}/10\n"
        response += f"最高: {stats['max']}/10\n"
        response += f"最低: {stats['min']}/10\n\n"

        if stats['by_category']:
            response += "カテゴリ別:\n"
            category_text = {
                'work': '💼 仕事',
                'personal': '👤 個人的',
                'health': '💊 健康',
                'finance': '💰 金銭',
                'relationship': '👥 人間関係',
                'other': '📝 その他'
            }
            for cat in stats['by_category']:
                text = category_text.get(cat['category'], cat['category'])
                response += f"  - {text}: 平均 {cat['avg']}/10 ({cat['count']}件)\n"

        return response

    return None

def format_stress(stress):
    """ストレス記録をフォーマット"""
    id, level, trigger, category, symptoms, notes, created_at = stress

    level_bar = '█' * level + '░' * (10 - level)
    category_text = {
        'work': '💼 仕事',
        'personal': '👤 個人的',
        'health': '💊 健康',
        'finance': '💰 金銭',
        'relationship': '👥 人間関係',
        'other': '📝 その他'
    }.get(category, '')

    response = f"\n😰 [{id}] {level}/10 {level_bar}"
    if category_text:
        response += f" | {category_text}"
    if trigger:
        response += f"\n    要因: {trigger}"
    if symptoms:
        response += f"\n    症状: {symptoms}"
    if notes:
        response += f"\n    メモ: {notes}"
    response += f"\n    日時: {created_at}"

    return response

def format_relaxation(method):
    """リラックス方法をフォーマット"""
    id, name, category, effectiveness, notes, created_at = method

    stars = '⭐' * effectiveness

    response = f"\n🧘 [{id}] {name}"
    response += f"\n    有効性: {effectiveness}/5 {stars}"
    if category:
        response += f"\n    カテゴリ: {category}"
    if notes:
        response += f"\n    メモ: {notes}"
    response += f"\n    登録日: {created_at}"

    return response

if __name__ == '__main__':
    init_db()

    test_messages = [
        "ストレス: 7, 要因: 締め切り, カテゴリ: 仕事",
        "ストレス: 3, カテゴリ: 個人的, メモ: 周末なのでリラックス",
        "リラックス: 瞑想, 有効性: 5, カテゴリ: マインドフルネス",
        "ストレス一覧",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
