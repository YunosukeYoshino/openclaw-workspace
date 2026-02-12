#!/usr/bin/env python3
"""
言語学習エージェント #46 - Discord連携
"""

import re
from datetime import datetime, timedelta
from db import *

def parse_message(message):
    """メッセージを解析"""
    # 語彙追加
    vocab_match = re.match(r'(?:語彙|vocab|vocabulary|単語|word)[：:]\s*(.+)', message, re.IGNORECASE)
    if vocab_match:
        return {'action': 'add_vocabulary', 'content': vocab_match.group(1)}

    # 文法追加
    grammar_match = re.match(r'(?:文法|grammar)[：:]\s*(.+)', message, re.IGNORECASE)
    if grammar_match:
        return {'action': 'add_grammar', 'content': grammar_match.group(1)}

    # 練習追加
    practice_match = re.match(r'(?:練習|practice|study|学習)[：:]\s*(.+)', message, re.IGNORECASE)
    if practice_match:
        return {'action': 'add_practice', 'content': practice_match.group(1)}

    # 語彙検索
    search_match = re.match(r'(?:検索|search)[：:]\s*(.+)', message, re.IGNORECASE)
    if search_match:
        return {'action': 'search', 'keyword': search_match.group(1)}

    # 一覧
    if message.strip() in ['語彙', 'vocab', 'vocabulary', '単語', 'words']:
        return {'action': 'list_vocabulary'}

    if message.strip() in ['文法', 'grammar']:
        return {'action': 'list_grammar'}

    if message.strip() in ['練習', 'practice', '学習記録', 'study']:
        return {'action': 'list_practice'}

    # 進捗
    if message.strip() in ['進捗', 'progress', 'status']:
        return {'action': 'progress'}

    # 統計
    if message.strip() in ['統計', 'stats', 'statistics']:
        return {'action': 'stats'}

    # 今日
    if message.strip() in ['今日', 'today']:
        return {'action': 'today'}

    return None

def parse_vocabulary_content(content):
    """語彙追加内容を解析"""
    result = {'word': None, 'translation': None, 'language': None, 
              'part_of_speech': None, 'definition': None, 'example': None}

    # 言語
    lang_match = re.search(r'(?:言語|language)[：:]\s*(\w+)', content, re.IGNORECASE)
    if lang_match:
        result['language'] = lang_match.group(1).strip().lower()

    # 品詞
    pos_match = re.search(r'(?:品詞|part|pos)[：:]\s*(.+)', content, re.IGNORECASE)
    if pos_match:
        result['part_of_speech'] = pos_match.group(1).strip()

    # 翻訳
    trans_match = re.search(r'(?:翻訳|translation|訳)[：:]\s*(.+)', content, re.IGNORECASE)
    if trans_match:
        result['translation'] = trans_match.group(1).strip()

    # 定義
    def_match = re.search(r'(?:定義|definition|意味)[：:]\s*(.+)', content, re.IGNORECASE)
    if def_match:
        result['definition'] = def_match.group(1).strip()

    # 例文
    ex_match = re.search(r'(?:例文|example)[：:]\s*(.+)', content, re.IGNORECASE)
    if ex_match:
        result['example'] = ex_match.group(1).strip()

    # 最初の項目より前を単語とする
    for key in ['言語', 'language', '品詞', 'part', '翻訳', 'translation', '定義', 'definition', '例文', 'example']:
        match = re.search(rf'{key}[×:：]', content)
        if match:
            result['word'] = content[:match.start()].strip()
            break
    else:
        result['word'] = content.strip()

    return result

def parse_grammar_content(content):
    """文法追加内容を解析"""
    result = {'rule': None, 'explanation': None, 'language': None,
              'example': None, 'difficulty': 'intermediate'}

    # 言語
    lang_match = re.search(r'(?:言語|language)[：:]\s*(\w+)', content, re.IGNORECASE)
    if lang_match:
        result['language'] = lang_match.group(1).strip().lower()

    # 難易度
    diff_match = re.search(r'(?:難易度|difficulty|level)[：:]\s*(\w+)', content, re.IGNORECASE)
    if diff_match:
        result['difficulty'] = diff_match.group(1).strip().lower()

    # 例文
    ex_match = re.search(r'(?:例文|example)[：:]\s*(.+)', content, re.IGNORECASE)
    if ex_match:
        result['example'] = ex_match.group(1).strip()

    # 説明
    exp_match = re.search(r'(?:説明|explanation|意味)[：:]\s*(.+)', content, re.IGNORECASE)
    if exp_match:
        result['explanation'] = exp_match.group(1).strip()

    # 最初の項目より前をルールとする
    for key in ['言語', 'language', '説明', 'explanation', '例文', 'example']:
        match = re.search(rf'{key}[×:：]', content)
        if match:
            result['rule'] = content[:match.start()].strip()
            break
    else:
        result['rule'] = content.strip()

    return result

def parse_practice_content(content):
    """練習追加内容を解析"""
    result = {'practice_type': None, 'language': None, 'duration': None,
              'content': None, 'date': None, 'notes': None, 'rating': None}

    # 言語
    lang_match = re.search(r'(?:言語|language)[：:]\s*(\w+)', content, re.IGNORECASE)
    if lang_match:
        result['language'] = lang_match.group(1).strip().lower()

    # タイプ
    type_match = re.search(r'(?:タイプ|type|種類)[：:]\s*(.+)', content, re.IGNORECASE)
    if type_match:
        result['practice_type'] = type_match.group(1).strip()

    # 時間
    dur_match = re.search(r'(?:時間|duration|分|min|minutes?)[：:]?\s*(\d+)', content, re.IGNORECASE)
    if dur_match:
        result['duration'] = int(dur_match.group(1))

    # 評価
    rating_match = re.search(r'(?:評価|rating|点数)[：:]?\s*(\d)', content, re.IGNORECASE)
    if rating_match:
        result['rating'] = int(rating_match.group(1))

    # 日付
    date_match = re.search(r'(?:日付|date)[：:]\s*([^、,]+)', content, re.IGNORECASE)
    if date_match:
        result['date'] = parse_date(date_match.group(1).strip())

    # 内容
    content_match = re.search(r'(?:内容|content|what)[：:]\s*(.+)', content, re.IGNORECASE)
    if content_match:
        result['content'] = content_match.group(1).strip()

    # メモ
    notes_match = re.search(r'(?:メモ|memo|note)[：:]\s*(.+)', content, re.IGNORECASE)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    # 最初の項目より前をタイプとする
    for key in ['言語', 'language', 'タイプ', 'type', '時間', 'duration', '内容', 'content']:
        match = re.search(rf'{key}[×:：]', content)
        if match:
            result['practice_type'] = content[:match.start()].strip()
            break
    else:
        result['practice_type'] = content.strip()

    return result

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

    if action == 'add_vocabulary':
        content = parse_vocabulary_content(parsed['content'])

        if not content['word']:
            return "❌ 単語を入力してください"

        vocab_id = add_vocabulary(
            word=content['word'],
            translation=content['translation'],
            language=content['language'],
            part_of_speech=content['part_of_speech'],
            definition=content['definition'],
            example=content['example']
        )

        response = f"📚 語彙 #{vocab_id} 追加完了\n"
        response += f"単語: {content['word']}\n"
        if content['translation']:
            response += f"翻訳: {content['translation']}\n"
        if content['language']:
            response += f"言語: {content['language']}\n"
        if content['definition']:
            response += f"定義: {content['definition']}\n"
        if content['example']:
            response += f"例文: {content['example']}"

        return response

    elif action == 'add_grammar':
        content = parse_grammar_content(parsed['content'])

        if not content['rule']:
            return "❌ 文法ルールを入力してください"

        if not content['language']:
            return "❌ 言語を指定してください"

        grammar_id = add_grammar(
            rule=content['rule'],
            explanation=content['explanation'],
            language=content['language'],
            example=content['example'],
            difficulty=content['difficulty']
        )

        response = f"📝 文法 #{grammar_id} 追加完了\n"
        response += f"ルール: {content['rule']}\n"
        response += f"言語: {content['language']}\n"
        if content['explanation']:
            response += f"説明: {content['explanation']}\n"
        if content['example']:
            response += f"例文: {content['example']}\n"
        response += f"難易度: {content['difficulty']}"

        return response

    elif action == 'add_practice':
        content = parse_practice_content(parsed['content'])

        if not content['practice_type']:
            return "❌ 練習内容を入力してください"

        if not content['language']:
            return "❌ 言語を指定してください"

        practice_id = add_practice(
            practice_type=content['practice_type'],
            language=content['language'],
            duration=content['duration'],
            content=content['content'],
            date=content['date'],
            notes=content['notes'],
            rating=content['rating']
        )

        response = f"✍️ 練習 #{practice_id} 追加完了\n"
        response += f"タイプ: {content['practice_type']}\n"
        response += f"言語: {content['language']}\n"
        if content['duration']:
            response += f"時間: {content['duration']}分\n"
        if content['content']:
            response += f"内容: {content['content']}\n"
        if content['date']:
            response += f"日付: {content['date']}\n"
        if content['rating']:
            response += f"評価: {content['rating']}/5"

        return response

    elif action == 'search':
        keyword = parsed['keyword']
        results = search_vocabulary(keyword)

        if not results:
            return f"🔍 「{keyword}」の検索結果: 見つかりませんでした"

        response = f"🔍 「{keyword}」の検索結果 ({len(results)}件):\n"
        for vocab in results:
            response += format_vocabulary(vocab)

        return response

    elif action == 'list_vocabulary':
        vocab_list = list_vocabulary()

        if not vocab_list:
            return "📚 語彙がありません"

        response = f"📚 語彙一覧 ({len(vocab_list)}件):\n"
        for vocab in vocab_list:
            response += format_vocabulary(vocab)

        return response

    elif action == 'list_grammar':
        grammar_list = list_grammar()

        if not grammar_list:
            return "📝 文法がありません"

        response = f"📝 文法一覧 ({len(grammar_list)}件):\n"
        for grammar in grammar_list:
            response += format_grammar(grammar)

        return response

    elif action == 'list_practice':
        practice_list = list_practice()

        if not practice_list:
            return "✍️ 練習記録がありません"

        response = f"✍️ 練習記録 ({len(practice_list)}件):\n"
        for practice in practice_list:
            response += format_practice(practice)

        return response

    elif action == 'progress':
        progress_list = get_progress()

        if not progress_list:
            return "📊 進捗がありません"

        response = "📊 進捗:\n"
        for progress in progress_list:
            response += format_progress(progress)

        return response

    elif action == 'stats':
        stats = get_stats()

        response = "📊 統計情報:\n"
        response += f"語彙数: {stats['vocabulary_count']}語\n"
        response += f"文法数: {stats['grammar_count']}個\n"
        response += f"総練習時間: {stats['total_practice_minutes']}分\n"
        response += f"練習回数: {stats['practice_count']}回\n"
        response += f"今日の練習: {stats['today_practice']}回"

        return response

    elif action == 'today':
        today = datetime.now().strftime("%Y-%m-%d")
        practice_list = list_practice(date=today)

        if not practice_list:
            return f"✍️ 今日の練習記録はありません"

        response = f"✍️ 今日の練習 ({len(practice_list)}件):\n"
        for practice in practice_list:
            response += format_practice(practice, show_date=False)

        return response

    return None

def format_vocabulary(vocab):
    """語彙をフォーマット"""
    id, word, translation, language, part_of_speech, definition, example, mastery_level = vocab

    mastery_stars = "⭐" * mastery_level

    response = f"\n📚 [{id}] {word}"
    if translation:
        response += f" → {translation}"
    if language:
        response += f" ({language})"
    if part_of_speech:
        response += f" [{part_of_speech}]"
    response += f"\n    {mastery_stars}"
    if definition:
        response += f"\n    {definition}"
    if example:
        response += f"\n    例: {example}"

    return response

def format_grammar(grammar):
    """文法をフォーマット"""
    id, rule, explanation, language, example, difficulty = grammar

    difficulty_emoji = {
        'beginner': '🌱',
        'intermediate': '🌿',
        'advanced': '🌳'
    }

    response = f"\n📝 [{id}] {rule} ({language})"
    response += f" {difficulty_emoji.get(difficulty, '📋')}\n"
    if explanation:
        response += f"    {explanation}\n"
    if example:
        response += f"    例: {example}"

    return response

def format_practice(practice, show_date=True):
    """練習をフォーマット"""
    id, practice_type, language, duration, content, date, notes, rating = practice

    rating_stars = "⭐" * (rating or 0)

    response = f"\n✍️ [{id}] {practice_type} ({language})"
    if show_date:
        response += f" - {date}"
    if duration:
        response += f" ({duration}分)"
    if rating:
        response += f" {rating_stars}"
    if content:
        response += f"\n    {content}"
    if notes:
        response += f"\n    📝 {notes}"

    return response

def format_progress(progress):
    """進捗をフォーマット"""
    id, language, level, xp, streak, last_practice, goal_xp, updated_at = progress

    progress_percent = min(100, (xp / goal_xp) * 100) if goal_xp > 0 else 0

    response = f"\n🔹 {language} ({level})\n"
    response += f"    XP: {xp}/{goal_xp} ({progress_percent:.1f}%)\n"
    response += f"    🔥 {streak}日連続\n"
    if last_practice:
        response += f"    最終練習: {last_practice}"

    return response

if __name__ == '__main__':
    init_db()

    test_messages = [
        "語彙: apple, 言語: english, 翻訳: りんご, 品詞: 名詞",
        "文法: 過去形, 言語: english, 説明: 過去の出来事",
        "練習: リーディング, 言語: english, 時間: 30, 内容: news article",
        "語彙",
        "進捗",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
