#!/usr/bin/env python3
"""
Translation Agent - Discord Integration
"""

import re
from datetime import datetime
from db import *

# Language code mapping
LANGUAGE_CODES = {
    'ja': 'Japanese', 'japanese': 'ja', '日本語': 'ja',
    'en': 'English', 'english': 'en', '英語': 'en',
    'zh': 'Chinese', 'chinese': 'zh', '中国語': 'zh',
    'ko': 'Korean', 'korean': 'ko', '韓国語': 'ko',
    'fr': 'French', 'french': 'fr', 'フランス語': 'fr',
    'de': 'German', 'german': 'de', 'ドイツ語': 'de',
    'es': 'Spanish', 'spanish': 'es', 'スペイン語': 'es',
    'it': 'Italian', 'italian': 'it', 'イタリア語': 'it',
    'pt': 'Portuguese', 'portuguese': 'pt', 'ポルトガル語': 'pt',
    'ru': 'Russian', 'russian': 'ru', 'ロシア語': 'ru',
}

def parse_message(message):
    """Parse message"""
    # Translation
    trans_match = re.match(r'(?:翻訳|translate|tr)[:：]\s*(.+)', message, re.IGNORECASE)
    if trans_match:
        return parse_translation(trans_match.group(1))

    # History
    if message.strip() in ['翻訳履歴', '履歴', 'history', 'translation history']:
        return {'action': 'history'}

    # Bookmarks
    if message.strip() in ['ブックマーク', '保存済み', 'bookmarks', 'saved']:
        return {'action': 'bookmarks'}

    # Bookmark
    bookmark_match = re.match(r'(?:ブックマーク|bookmark|save)[:：]\s*(\d+)(?:[:：]\s*(.+))?', message)
    if bookmark_match:
        name = bookmark_match.group(2).strip() if bookmark_match.group(2) else None
        return {'action': 'bookmark', 'translation_id': int(bookmark_match.group(1)), 'name': name}

    # Common phrases
    common_match = re.match(r'(?:定型文|common phrases|common)[:：]\s*([^、,]+)(?:[:：]\s*([^、,]+))?', message)
    if common_match:
        source_lang = normalize_language(common_match.group(1).strip())
        target_lang = normalize_language(common_match.group(2).strip()) if common_match.group(2) else 'en'
        return {'action': 'common', 'source_lang': source_lang, 'target_lang': target_lang}

    # Search
    search_match = re.match(r'(?:検索|search)[:：]\s*(.+)', message)
    if search_match:
        return {'action': 'search', 'keyword': search_match.group(1)}

    # Set preference
    pref_match = re.match(r'(?:設定|設定[:：]\s*言語|pref|preference|set lang)[:：]\s*([^、,]+)(?:[:：]\s*([^、,]+))?', message)
    if pref_match:
        source_lang = normalize_language(pref_match.group(1).strip())
        target_lang = normalize_language(pref_match.group(2).strip()) if pref_match.group(2) else None
        return {'action': 'set_pref', 'source_lang': source_lang, 'target_lang': target_lang}

    # Statistics
    if message.strip() in ['統計', 'stats', '翻訳統計']:
        return {'action': 'stats'}

    return None

def parse_translation(content):
    """Parse translation request"""
    result = {'action': 'translate', 'text': None, 'source_lang': None, 'target_lang': None}

    # Try to extract languages first
    lang_match = re.search(r'([^、,\s]+)\s*->\s*([^、,\s]+)', content)
    if lang_match:
        result['source_lang'] = normalize_language(lang_match.group(1).strip())
        result['target_lang'] = normalize_language(lang_match.group(2).strip())
        content = content.replace(lang_match.group(0), '').strip()
    else:
        # Try "from X to Y" format
        from_match = re.search(r'(?:from|から|より)[:：]\s*([^、,\s]+)', content, re.IGNORECASE)
        to_match = re.search(r'(?:to|に|へ)[:：]\s*([^、,\s]+)', content, re.IGNORECASE)

        if from_match:
            result['source_lang'] = normalize_language(from_match.group(1).strip())
            content = content.replace(from_match.group(0), '').strip()

        if to_match:
            result['target_lang'] = normalize_language(to_match.group(1).strip())
            content = content.replace(to_match.group(0), '').strip()

    # Remaining text is the content to translate
    if content:
        result['text'] = content.strip()

    return result

def normalize_language(lang):
    """Normalize language name/code"""
    if not lang:
        return None
    lang_lower = lang.lower()
    return LANGUAGE_CODES.get(lang_lower, lang_lower)

def handle_message(message, user_id='default'):
    """Handle message"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'translate':
        text = parsed.get('text')
        if not text:
            return "❌ 翻訳テキストを入力してください (Enter text to translate)"

        # Get default preferences if not specified
        if not parsed.get('source_lang') or not parsed.get('target_lang'):
            pref = get_language_preference(user_id)
            if pref:
                if not parsed.get('source_lang'):
                    parsed['source_lang'] = pref[0]
                if not parsed.get('target_lang'):
                    parsed['target_lang'] = pref[1]

        source_lang = parsed.get('source_lang', 'auto')
        target_lang = parsed.get('target_lang', 'en')

        # Perform translation (placeholder)
        translated = perform_translation(text, source_lang, target_lang)

        # Save to history
        translation_id = add_translation(text, translated, source_lang, target_lang)

        response = f"🌐 翻訳 / Translation #{translation_id}\n"
        response += f"{source_lang.upper()} -> {target_lang.upper()}\n\n"
        response += f"原文 / Original:\n{text}\n\n"
        response += f"翻訳 / Translated:\n{translated}"

        return response

    elif action == 'history':
        history = get_translation_history()

        if not history:
            return "📜 翻訳履歴がありません (No translation history)"

        response = f"📜 翻訳履歴 ({len(history)}件):\n"
        for trans in history:
            response += format_translation_history(trans)

        return response

    elif action == 'bookmarks':
        bookmarks = get_bookmarked_translations()

        if not bookmarks:
            return "⭐ ブックマークがありません (No bookmarks)"

        response = f"⭐ ブックマーク ({len(bookmarks)}件):\n"
        for bookmark in bookmarks:
            response += format_bookmark(bookmark)

        return response

    elif action == 'bookmark':
        translation_id = parsed['translation_id']
        name = parsed.get('name')

        if not name:
            # Get source text from history
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('SELECT source_text FROM translation_history WHERE id = ?', (translation_id,))
            result = cursor.fetchone()
            conn.close()

            if result:
                name = result[0][:30]
            else:
                return "❌ 翻訳が見つかりません (Translation not found)"

        bookmark_id = bookmark_translation(translation_id, name)

        if bookmark_id:
            return f"✅ ブックマーク #{bookmark_id} 作成完了 (Bookmark created)"
        else:
            return "❌ 既にブックマークされています (Already bookmarked)"

    elif action == 'common':
        source_lang = parsed['source_lang']
        target_lang = parsed['target_lang']

        common = get_common_translations(source_lang, target_lang)

        if not common:
            return f"📚 定型文がありません (No common phrases for {source_lang} -> {target_lang})"

        response = f"📚 定型文 / Common Phrases ({source_lang.upper()} -> {target_lang.upper()}) ({len(common)}件):\n"
        for phrase in common:
            response += format_common_phrase(phrase)

        return response

    elif action == 'search':
        keyword = parsed['keyword']
        results = search_translations(keyword)

        if not results:
            return f"🔍 「{keyword}」の検索結果: 見つかりませんでした (No results for '{keyword}')"

        response = f"🔍 「{keyword}」の検索結果 ({len(results)}件):\n"
        for result in results:
            response += format_translation_history(result)

        return response

    elif action == 'set_pref':
        source_lang = parsed['source_lang']
        target_lang = parsed['target_lang']

        set_language_preference(user_id, source_lang, target_lang)

        response = "✅ 言語設定を保存しました (Language preferences saved):\n"
        if source_lang:
            response += f"  入力言語 / Source: {source_lang}\n"
        if target_lang:
            response += f"  出力言語 / Target: {target_lang}"

        return response

    elif action == 'stats':
        stats = get_stats()

        response = "📊 翻訳統計 / Translation Statistics:\n"
        response += f"総翻訳回数: {stats['total_translations']}回 / Total translations: {stats['total_translations']}\n"
        response += f"ブックマーク数: {stats['bookmarked']}件 / Bookmarks: {stats['bookmarked']}\n"
        response += f"定型文数: {stats['common_translations']}件 / Common phrases: {stats['common_translations']}\n"
        response += f"直近7日間: {stats['recent_translations']}回 / Last 7 days: {stats['recent_translations']}\n"

        if stats['by_language_pair']:
            response += f"\n言語ペア別 / By language pair:\n"
            for pair, count in list(stats['by_language_pair'].items())[:5]:
                response += f"  {pair}: {count}回\n"

        return response

    return None

def perform_translation(text, source_lang, target_lang):
    """Perform translation (placeholder)"""
    # In a real implementation, you would integrate with a translation API
    # For now, return a placeholder response

    return f"[Translated from {source_lang} to {target_lang}]: {text}"

def format_translation_history(trans):
    """Format translation history entry"""
    id, source_text, translated_text, source_lang, target_lang, timestamp, bookmarked = trans

    response = f"\n[{id}] {source_lang.upper()} -> {target_lang.upper()}\n"
    response += f"    原文: {source_text[:50]}{'...' if len(source_text) > 50 else ''}\n"
    response += f"    翻訳: {translated_text[:50]}{'...' if len(translated_text) > 50 else ''}\n"
    response += f"    日時: {timestamp}"
    if bookmarked:
        response += " ⭐"

    return response

def format_bookmark(bookmark):
    """Format bookmark entry"""
    id, name, note, created_at, source_text, translated_text, source_lang, target_lang = bookmark

    response = f"\n[#{id}] {name}\n"
    response += f"    {source_lang.upper()} -> {target_lang.upper()}\n"
    response += f"    原文: {source_text[:40]}{'...' if len(source_text) > 40 else ''}\n"
    response += f"    翻訳: {translated_text[:40]}{'...' if len(translated_text) > 40 else ''}"
    if note:
        response += f"\n    メモ: {note}"

    return response

def format_common_phrase(phrase):
    """Format common phrase entry"""
    id, phrase_text, source_lang, translated, target_lang, usage_count = phrase

    response = f"\n    {phrase_text} → {translated}"
    if usage_count > 1:
        response += f" ({usage_count}回)"

    return response

if __name__ == '__main__':
    # Test
    import sqlite3

    init_db()

    test_messages = [
        "翻訳: Hello World -> 日本語",
        "翻訳: from Japanese to English: こんにちは",
        "翻訳履歴",
        "ブックマーク",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
