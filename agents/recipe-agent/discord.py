#!/usr/bin/env python3
"""
Recipe Agent #29 - Discord Integration
"""

import re
from db import *

def parse_message(message):
    """Parse message"""
    # Add recipe
    add_match = re.match(r'(?:追加|add|new)[:：]\s*(.+)', message, re.IGNORECASE)
    if add_match:
        return parse_add(add_match.group(1))

    # Log cooking
    cook_match = re.match(r'(?:料理|cook|log)[:：]\s*(\d+)(?:\s*[,，]\s*(.+))?', message, re.IGNORECASE)
    if cook_match:
        return {'action': 'log_cooking', 'recipe_id': int(cook_match.group(1)), 'notes': cook_match.group(2)}

    # Update rating
    rating_match = re.match(r'(?:評価|rate|rating)[:：]\s*(\d+)\s*[,，]\s*(\d)', message, re.IGNORECASE)
    if rating_match:
        return {'action': 'update_rating', 'recipe_id': int(rating_match.group(1)), 'rating': int(rating_match.group(2))}

    # List recipes
    list_match = re.match(r'(?:一覧|list|recipes)(?:[:：]\s*(\w+))?', message, re.IGNORECASE)
    if list_match:
        category = list_match.group(1) if list_match.group(1) else None
        return {'action': 'list', 'category': category}

    # Search recipes
    search_match = re.match(r'(?:検索|search)[:：]\s*(.+)', message, re.IGNORECASE)
    if search_match:
        return {'action': 'search', 'keyword': search_match.group(1)}

    # View details
    view_match = re.match(r'(?:詳細|view|details)[:：]\s*(\d+)', message, re.IGNORECASE)
    if view_match:
        return {'action': 'view_details', 'recipe_id': int(view_match.group(1))}

    # View cooking logs
    logs_match = re.match(r'(?:履歴|logs|history)[:：]\s*(\d+)', message, re.IGNORECASE)
    if logs_match:
        return {'action': 'view_logs', 'recipe_id': int(logs_match.group(1))}

    # Stats
    if message.strip() in ['統計', 'stats']:
        return {'action': 'stats'}

    return None

def parse_add(content):
    """Parse add content"""
    result = {'action': 'add', 'name': None, 'description': None, 'cuisine': None, 'category': None, 'servings': None, 'prep_time': None, 'cook_time': None, 'difficulty': 'medium', 'ingredients': None, 'instructions': None, 'tags': None, 'notes': None}

    # Name
    name_match = re.match(r'^([^、,]+)', content)
    if name_match:
        result['name'] = name_match.group(1).strip()

    # Servings
    servings_match = re.search(r'人数|servings[:：]\s*(\d+)', content)
    if servings_match:
        result['servings'] = int(servings_match.group(1))

    # Prep time
    prep_match = re.search(r'下準備|prep[:：]\s*(\d+)', content)
    if prep_match:
        result['prep_time'] = int(prep_match.group(1))

    # Cook time
    cook_match = re.search(r'調理|cook[:：]\s*(\d+)', content)
    if cook_match:
        result['cook_time'] = int(cook_match.group(1))

    # Difficulty
    diff_match = re.search(r'難易度|difficulty[:：]\s*(easy|medium|hard|簡単|中級|上級)', content)
    if diff_match:
        diff = diff_match.group(1).lower()
        if diff in ['簡単', 'easy']:
            result['difficulty'] = 'easy'
        elif diff in ['上級', 'hard']:
            result['difficulty'] = 'hard'
        else:
            result['difficulty'] = 'medium'

    # Cuisine
    cuisine_match = re.search(r'料理|cuisine[:：]\s*(.+?)(?:[、,]|$)', content)
    if cuisine_match:
        result['cuisine'] = cuisine_match.group(1).strip()

    # Category
    cat_match = re.search(r'カテゴリ|category[:：]\s*(.+?)(?:[、,]|$)', content)
    if cat_match:
        result['category'] = cat_match.group(1).strip()

    # Ingredients
    ing_match = re.search(r'材料|ingredients[:：]\s*(.+)', content)
    if ing_match:
        result['ingredients'] = ing_match.group(1).strip()

    # Instructions
    inst_match = re.search(r'手順|instructions[:：]\s*(.+)', content)
    if inst_match:
        result['instructions'] = inst_match.group(1).strip()

    # Tags
    tags_match = re.search(r'タグ|tags[:：]\s*(.+)', content)
    if tags_match:
        result['tags'] = tags_match.group(1).strip()

    # Notes
    note_match = re.search(r'メモ|notes[:：]\s*(.+)', content)
    if note_match:
        result['notes'] = note_match.group(1).strip()

    return result

def handle_message(message):
    """Handle message"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'add':
        if not parsed['name']:
            return "❌ レシピ名を入力してください"

        recipe_id = add_recipe(
            parsed['name'],
            parsed['description'],
            parsed['cuisine'],
            parsed['category'],
            parsed['servings'],
            parsed['prep_time'],
            parsed['cook_time'],
            parsed['difficulty'],
            parsed['ingredients'],
            parsed['instructions'],
            parsed['tags'],
            notes=parsed['notes']
        )

        response = f"🍳 レシピ #{recipe_id} 追加完了\n"
        response += f"名前: {parsed['name']}\n"
        if parsed['category']:
            response += f"カテゴリ: {parsed['category']}\n"
        if parsed['difficulty']:
            diff_map = {'easy': '簡単', 'medium': '中級', 'hard': '上級'}
            response += f"難易度: {diff_map.get(parsed['difficulty'], parsed['difficulty'])}"

        return response

    elif action == 'log_cooking':
        log_id = log_cooking(parsed['recipe_id'], notes=parsed['notes'])
        return f"👨‍🍳 レシピ #{parsed['recipe_id']} の料理を記録 (ログ #{log_id})"

    elif action == 'update_rating':
        rating = parsed['rating']
        if rating < 1 or rating > 5:
            return "❌ 評価は1-5で指定してください"

        update_rating(parsed['recipe_id'], rating)
        return f"⭐ レシピ #{parsed['recipe_id']} の評価を {rating} に更新"

    elif action == 'list':
        recipes = list_recipes(category=parsed['category'])

        if not recipes:
            return f"🍳 レシピがありません"

        category_text = f" ({parsed['category']})" if parsed['category'] else ""
        response = f"🍳 レシピ一覧{category_text} ({len(recipes)}件):\n"
        for recipe in recipes:
            response += format_recipe(recipe)

        return response

    elif action == 'search':
        recipes = search_recipes(parsed['keyword'])

        if not recipes:
            return f"🔍 「{parsed['keyword']}」の検索結果: 見つかりませんでした"

        response = f"🔍 「{parsed['keyword']}」の検索結果 ({len(recipes)}件):\n"
        for recipe in recipes:
            response += format_recipe(recipe)

        return response

    elif action == 'view_details':
        recipe = get_recipe_details(parsed['recipe_id'])

        if not recipe:
            return f"❌ レシピ #{parsed['recipe_id']} が見つかりません"

        response = format_recipe_details(recipe)

        return response

    elif action == 'view_logs':
        logs = get_cooking_logs(parsed['recipe_id'])

        if not logs:
            return f"📝 レシピ #{parsed['recipe_id']} の料理履歴はありません"

        response = f"📝 レシピ #{parsed['recipe_id']} の料理履歴 ({len(logs)}件):\n"
        for log in logs:
            response += format_cook_log(log)

        return response

    elif action == 'stats':
        stats = get_stats()

        response = "📊 レシピ統計:\n"
        response += f"全レシピ: {stats['total_recipes']}件\n"
        response += f"簡単: {stats['easy']}件\n"
        response += f"中級: {stats['medium']}件\n"
        response += f"上級: {stats['hard']}件\n"
        response += f"平均評価: {stats['average_rating']}⭐\n"
        response += f"総料理回数: {stats['total_cooks']}回"

        return response

    return None

def format_recipe(recipe):
    """Format recipe (summary)"""
    id, name, description, cuisine, category, servings, prep_time, cook_time, difficulty, tags, rating, created_at = recipe

    diff_map = {'easy': '🟢', 'medium': '🟡', 'hard': '🔴'}
    diff_icon = diff_map.get(difficulty, '❓')

    rating_stars = '⭐' * rating if rating else ''

    response = f"\n{diff_icon} [{id}] {name} {rating_stars}\n"
    if cuisine:
        response += f"    {cuisine}"
    if category:
        response += f" / {category}"
    response += "\n"

    return response

def format_recipe_details(recipe):
    """Format recipe (full details)"""
    id, name, description, cuisine, category, servings, prep_time, cook_time, difficulty, ingredients, instructions, tags, source, rating, notes, created_at = recipe

    diff_map = {'easy': '🟢 簡単', 'medium': '🟡 中級', 'hard': '🔴 上級'}
    diff_text = diff_map.get(difficulty, difficulty)

    response = f"\n🍳 [{id}] {name}\n"
    response += f"    難易度: {diff_text}"
    if rating:
        response += f" | 評価: {'⭐' * rating}\n"
    else:
        response += "\n"

    if cuisine or category:
        response += f"    ジャンル: {cuisine or ''} {f'/{category}' if category else ''}\n"
    if servings:
        response += f"    人数: {servings}人\n"
    if prep_time:
        response += f"    下準備: {prep_time}分\n"
    if cook_time:
        response += f"    調理時間: {cook_time}分\n"
    if ingredients:
        response += f"\n    材料:\n    {ingredients}\n"
    if instructions:
        response += f"\n    手順:\n    {instructions}\n"

    return response

def format_cook_log(log):
    """Format cooking log"""
    id, cook_date, notes, rating, modifications, created_at = log

    response = f"\n    📅 {cook_date}"
    if rating:
        response += f" {'⭐' * rating}"
    if notes:
        response += f"\n    メモ: {notes}"
    if modifications:
        response += f"\n    変更点: {modifications}"

    return response

if __name__ == '__main__':
    init_db()

    test_messages = [
        "追加: カレー, カテゴリ: 料理, 難易度: 簡単, 人数: 4",
        "追加: パスタ, カテゴリ: イタリア料理, 難易度: 中級",
        "一覧",
        "一覧: 料理",
        "詳細: 1",
        "料理: 1, 非常においしかった",
        "評価: 1, 5",
        "履歴: 1",
        "検索: カレー",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
