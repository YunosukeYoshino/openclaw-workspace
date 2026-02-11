#!/usr/bin/env python3
"""
料理エージェント #36 - Discord連携
"""

import re
from db import *

def parse_message(message):
    """メッセージを解析"""
    # レシピ追加
    recipe_match = re.match(r'(?:レシピ|recipe|料理)[：:]\s*(.+)', message, re.IGNORECASE)
    if recipe_match:
        return parse_add(recipe_match.group(1))

    # 更新
    update_match = re.match(r'(?:更新|update)[：:]\s*(\d+)\s*(.+)', message, re.IGNORECASE)
    if update_match:
        return {'action': 'update', 'recipe_id': int(update_match.group(1)), 'content': update_match.group(2)}

    # 削除
    delete_match = re.match(r'(?:削除|delete|remove)[：:]\s*(\d+)', message, re.IGNORECASE)
    if delete_match:
        return {'action': 'delete', 'recipe_id': int(delete_match.group(1))}

    # 検索
    search_match = re.match(r'(?:検索|search)[：:]\s*(.+)', message, re.IGNORECASE)
    if search_match:
        return {'action': 'search', 'keyword': search_match.group(1)}

    # 一覧
    list_match = re.match(r'(?:(?:レシピ|recipe|料理)(?:一覧|list)|list|recipes)', message, re.IGNORECASE)
    if list_match:
        return {'action': 'list'}

    # 簡単
    if message.strip() in ['簡単', 'easy']:
        return {'action': 'list_easy'}

    # 難しい
    if message.strip() in ['難しい', 'hard', 'hard mode']:
        return {'action': 'list_hard'}

    # タグ別
    tags_match = re.match(r'(?:タグ|tags)[：:]\s*(.+)', message, re.IGNORECASE)
    if tags_match:
        return {'action': 'list_by_tags', 'tags': tags_match.group(1)}

    # 統計
    if message.strip() in ['統計', 'stats', 'レシピ統計']:
        return {'action': 'stats'}

    return None

def parse_add(content):
    """レシピ追加を解析"""
    result = {'action': 'add', 'name': None, 'ingredients': None, 'steps': None, 'prep_time': None,
              'cook_time': None, 'servings': 1, 'difficulty': None, 'tags': None, 'notes': None}

    # 料理名 (最初の部分)
    name_match = re.match(r'^([^、,（\(【]+)', content)
    if name_match:
        result['name'] = name_match.group(1).strip()

    # 材料
    ingredients_match = re.search(r'(?:材料|ingredients?)[：:]\s*(.+)', content)
    if ingredients_match:
        result['ingredients'] = ingredients_match.group(1).strip()

    # 手順
    steps_match = re.search(r'(?:手順|steps?|作り方)[：:]\s*(.+)', content)
    if steps_match:
        result['steps'] = steps_match.group(1).strip()

    # 準備時間
    prep_match = re.search(r'(?:準備時間|prep time|下準備)[：:]?\s*(\d+)\s*(分|min|時間|h|hr)?', content)
    if prep_match:
        result['prep_time'] = int(prep_match.group(1))
        if '時間' in prep_match.group(2) or 'h' in prep_match.group(2).lower():
            result['prep_time'] *= 60  # 時間を分に変換

    # 調理時間
    cook_match = re.search(r'(?:調理時間|cook time|煮込み時間)[：:]?\s*(\d+)\s*(分|min|時間|h|hr)?', content)
    if cook_match:
        result['cook_time'] = int(cook_match.group(1))
        if '時間' in cook_match.group(2) or 'h' in cook_match.group(2).lower():
            result['cook_time'] *= 60  # 時間を分に変換

    # 人数
    servings_match = re.search(r'(?:人数|servings?|分)[：:]\s*(\d+)', content)
    if servings_match:
        result['servings'] = int(servings_match.group(1))

    # 難易度
    difficulty_match = re.search(r'(?:難易度|difficulty)[：:]\s*(簡単|easy|普通|medium|中|難しい|hard)', content)
    if difficulty_match:
        difficulty_map = {
            '簡単': 'easy', 'easy': 'easy',
            '普通': 'medium', 'medium': 'medium', '中': 'medium',
            '難しい': 'hard', 'hard': 'hard'
        }
        result['difficulty'] = difficulty_map.get(difficulty_match.group(1).lower())

    # タグ
    tags_match = re.search(r'(?:タグ|tags)[：:]\s*(.+)', content)
    if tags_match:
        result['tags'] = tags_match.group(1).strip()

    # メモ
    notes_match = re.search(r'(?:メモ|備考|memo|note)[：:]\s*(.+)', content)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    # 料理名がまだない場合、最初の項目より前を料理名とする
    if not result['name']:
        for key in ['材料', 'ingredients', '手順', 'steps', '作り方',
                    '準備時間', 'prep time', '下準備', '調理時間', 'cook time', '煮込み時間',
                    '人数', 'servings', '分', '難易度', 'difficulty', 'タグ', 'tags',
                    'メモ', '備考', 'memo', 'note']:
            match = re.search(rf'{key}[：:]', content)
            if match:
                result['name'] = content[:match.start()].strip()
                break
        else:
            result['name'] = content.strip()

    return result

def parse_update(content):
    """更新内容を解析"""
    result = {}

    # 料理名
    name_match = re.search(r'(?:名前|name|料理名)[：:]\s*([^、,]+)', content)
    if name_match:
        result['name'] = name_match.group(1).strip()

    # 材料
    ingredients_match = re.search(r'(?:材料|ingredients?)[：:]\s*(.+)', content)
    if ingredients_match:
        result['ingredients'] = ingredients_match.group(1).strip()

    # 手順
    steps_match = re.search(r'(?:手順|steps?|作り方)[：:]\s*(.+)', content)
    if steps_match:
        result['steps'] = steps_match.group(1).strip()

    # 準備時間
    prep_match = re.search(r'(?:準備時間|prep time|下準備)[：:]?\s*(\d+)', content)
    if prep_match:
        result['prep_time'] = int(prep_match.group(1))

    # 調理時間
    cook_match = re.search(r'(?:調理時間|cook time|煮込み時間)[：:]?\s*(\d+)', content)
    if cook_match:
        result['cook_time'] = int(cook_match.group(1))

    # 人数
    servings_match = re.search(r'(?:人数|servings?|分)[：:]\s*(\d+)', content)
    if servings_match:
        result['servings'] = int(servings_match.group(1))

    # 難易度
    difficulty_match = re.search(r'(?:難易度|difficulty)[：:]\s*(簡単|easy|普通|medium|中|難しい|hard)', content)
    if difficulty_match:
        difficulty_map = {
            '簡単': 'easy', 'easy': 'easy',
            '普通': 'medium', 'medium': 'medium', '中': 'medium',
            '難しい': 'hard', 'hard': 'hard'
        }
        result['difficulty'] = difficulty_map.get(difficulty_match.group(1).lower())

    # タグ
    tags_match = re.search(r'(?:タグ|tags)[：:]\s*(.+)', content)
    if tags_match:
        result['tags'] = tags_match.group(1).strip()

    # メモ
    notes_match = re.search(r'(?:メモ|備考|memo|note)[：:]\s*(.+)', content)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    return result

def handle_message(message):
    """メッセージを処理"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'add':
        if not parsed['name']:
            return "❌ 料理名を入力してください"

        recipe_id = add_recipe(
            parsed['name'],
            parsed['ingredients'],
            parsed['steps'],
            parsed['prep_time'],
            parsed['cook_time'],
            parsed['servings'],
            parsed['difficulty'],
            parsed['tags'],
            parsed['notes']
        )

        response = f"🍳 レシピ #{recipe_id} 追加完了\n"
        response += f"料理名: {parsed['name']}\n"
        if parsed['difficulty']:
            difficulty_text = {'easy': '簡単', 'medium': '普通', 'hard': '難しい'}[parsed['difficulty']]
            response += f"難易度: {difficulty_text}\n"
        if parsed['prep_time'] or parsed['cook_time']:
            time_parts = []
            if parsed['prep_time']:
                time_parts.append(f"準備{parsed['prep_time']}分")
            if parsed['cook_time']:
                time_parts.append(f"調理{parsed['cook_time']}分")
            response += f"時間: {' + '.join(time_parts)}\n"
        if parsed['servings'] > 1:
            response += f"人数: {parsed['servings']}人分\n"
        if parsed['ingredients']:
            response += f"材料: {parsed['ingredients'][:100]}...\n"
        if parsed['tags']:
            response += f"タグ: {parsed['tags']}"

        return response

    elif action == 'update':
        updates = parse_update(parsed['content'])

        if not updates:
            return "❌ 更新内容がありません"

        update_recipe(parsed['recipe_id'], **updates)

        response = f"✅ レシピ #{parsed['recipe_id']} 更新完了"

        return response

    elif action == 'delete':
        delete_recipe(parsed['recipe_id'])
        return f"🗑️ レシピ #{parsed['recipe_id']} 削除完了"

    elif action == 'search':
        keyword = parsed['keyword']
        recipes = search_recipes(keyword)

        if not recipes:
            return f"🔍 「{keyword}」の検索結果: 見つかりませんでした"

        response = f"🔍 「{keyword}」の検索結果 ({len(recipes)}件):\n"
        for recipe in recipes:
            response += format_recipe(recipe)

        return response

    elif action == 'list':
        recipes = list_recipes()

        if not recipes:
            return "🍳 レシピがありません"

        response = f"🍳 レシピ一覧 ({len(recipes)}件):\n"
        for recipe in recipes:
            response += format_recipe(recipe)

        return response

    elif action == 'list_easy':
        recipes = list_recipes(difficulty='easy')

        if not recipes:
            return "🍳 簡単なレシピはありません"

        response = f"🍳 簡単なレシピ ({len(recipes)}件):\n"
        for recipe in recipes:
            response += format_recipe(recipe)

        return response

    elif action == 'list_hard':
        recipes = list_recipes(difficulty='hard')

        if not recipes:
            return "🍳 難しいレシピはありません"

        response = f"🍳 難しいレシピ ({len(recipes)}件):\n"
        for recipe in recipes:
            response += format_recipe(recipe)

        return response

    elif action == 'list_by_tags':
        recipes = list_recipes(tags=parsed['tags'])

        if not recipes:
            return f"🍳 「{parsed['tags']}」のレシピはありません"

        response = f"🍳 {parsed['tags']}のレシピ ({len(recipes)}件):\n"
        for recipe in recipes:
            response += format_recipe(recipe)

        return response

    elif action == 'stats':
        stats = get_stats()

        response = "📊 レシピ統計:\n"
        response += f"全レシピ数: {stats['total']}件\n"
        response += f"簡単: {stats['easy']}件\n"
        response += f"普通: {stats['medium']}件\n"
        response += f"難しい: {stats['hard']}件"

        return response

    return None

def format_recipe(recipe):
    """レシピをフォーマット"""
    id, name, ingredients, steps, prep_time, cook_time, servings, difficulty, tags, notes, created_at = recipe

    # 難易度表示
    difficulty_icons = {'easy': '🟢', 'medium': '🟡', 'hard': '🔴'}
    difficulty_icon = difficulty_icons.get(difficulty, '⚪')

    response = f"\n{difficulty_icon} [{id}] {name}\n"

    parts = []
    if prep_time or cook_time:
        time_parts = []
        if prep_time:
            time_parts.append(f"準備{prep_time}分")
        if cook_time:
            time_parts.append(f"調理{cook_time}分")
        parts.append(' '.join(time_parts))
    if servings > 1:
        parts.append(f"{servings}人分")
    if tags:
        parts.append(f"🏷️ {tags}")

    if parts:
        response += f"    {' '.join(parts)}\n"

    if ingredients:
        response += f"    🥘 {ingredients[:100]}{'...' if len(ingredients) > 100 else ''}\n"

    return response

if __name__ == '__main__':
    # テスト
    init_db()

    test_messages = [
        "レシピ: カレー, 難易度: 簡単, 材料: ニンジン、ジャガイモ、カレールー",
        "レシピ: パスタ, 難易度: 普通, 材料: パスタ、トマトソース",
        "簡単",
        "検索: カレー",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
