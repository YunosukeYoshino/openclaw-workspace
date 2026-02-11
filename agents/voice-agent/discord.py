#!/usr/bin/env python3
"""
Voice Assistant Agent - Discord Integration
"""

import re
from datetime import datetime
from db import *

def parse_message(message):
    """Parse message"""
    # Add voice command
    command_match = re.match(r'(?:コマンド追加|add command|register command)[:：]\s*(.+)', message, re.IGNORECASE)
    if command_match:
        return parse_command_info(command_match.group(1))

    # Voice history
    if message.strip() in ['音声履歴', '履歴', 'voice history', 'history']:
        return {'action': 'history'}

    # List commands
    if message.strip() in ['コマンド一覧', 'コマンド', 'commands', 'list commands']:
        return {'action': 'list_commands'}

    # TTS history
    if message.strip() in ['TTS履歴', 'tts history', 'speech history']:
        return {'action': 'tts_history'}

    # Add vocabulary
    vocab_match = re.match(r'(?:語彙追加|add vocab|add word)[:：]\s*(.+)', message, re.IGNORECASE)
    if vocab_match:
        return parse_vocabulary(vocab_match.group(1))

    # List vocabulary
    vocab_list_match = re.match(r'(?:語彙一覧|vocab|vocabulary)[:：]?(?:\s*(.+))?', message)
    if vocab_list_match:
        category = vocab_list_match.group(1).strip() if vocab_list_match.group(1) else None
        return {'action': 'list_vocab', 'category': category}

    # Voice settings
    setting_match = re.match(r'(?:設定|setting|voice setting)[:：]\s*(.+)', message)
    if setting_match:
        return parse_setting(setting_match.group(1))

    # Delete command
    delete_match = re.match(r'(?:コマンド削除|delete command|remove command)[:：]\s*(.+)', message)
    if delete_match:
        return {'action': 'delete_command', 'name': delete_match.group(1).strip()}

    # Statistics
    if message.strip() in ['統計', 'stats', '音声統計']:
        return {'action': 'stats'}

    return None

def parse_command_info(content):
    """Parse voice command information"""
    result = {
        'action': 'add_command',
        'name': None,
        'pattern': None,
        'action_type': None,
        'params': None,
        'description': None
    }

    # Name (first part)
    name_match = re.match(r'^([^、,（\(]+)', content)
    if name_match:
        result['name'] = name_match.group(1).strip()
        content = content.replace(name_match.group(0), '').strip()

    # Pattern
    pattern_match = re.search(r'(?:パターン|pattern)[:：]\s*([^、,]+)', content, re.IGNORECASE)
    if pattern_match:
        result['pattern'] = pattern_match.group(1).strip()
        content = content.replace(pattern_match.group(0), '').strip()

    # Action type
    action_match = re.search(r'(?:アクション|action)[:：]\s*([^、,]+)', content, re.IGNORECASE)
    if action_match:
        result['action_type'] = action_match.group(1).strip()
        content = content.replace(action_match.group(0), '').strip()

    # Parameters
    param_match = re.search(r'(?:パラメータ|params|parameters)[:：]\s*(.+)', content, re.IGNORECASE)
    if param_match:
        result['params'] = param_match.group(1).strip()

    # Description
    desc_match = re.search(r'(?:説明|description)[:：]\s*(.+)', content, re.IGNORECASE)
    if desc_match:
        result['description'] = desc_match.group(1).strip()

    # If no explicit pattern, use the name as pattern
    if not result['pattern'] and result['name']:
        result['pattern'] = result['name']

    return result

def parse_vocabulary(content):
    """Parse vocabulary information"""
    result = {
        'action': 'add_vocab',
        'word': None,
        'pronunciation': None,
        'category': None
    }

    # Word (first part)
    word_match = re.match(r'^([^、,（\(]+)', content)
    if word_match:
        result['word'] = word_match.group(1).strip()
        content = content.replace(word_match.group(0), '').strip()

    # Pronunciation
    pron_match = re.search(r'(?:発音|pronunciation|pron)[:：]\s*([^、,]+)', content, re.IGNORECASE)
    if pron_match:
        result['pronunciation'] = pron_match.group(1).strip()
        content = content.replace(pron_match.group(0), '').strip()

    # Category
    cat_match = re.search(r'(?:カテゴリ|category)[:：]\s*([^、,]+)', content, re.IGNORECASE)
    if cat_match:
        result['category'] = cat_match.group(1).strip()

    return result

def parse_setting(content):
    """Parse voice setting"""
    result = {'action': 'set_setting', 'user_id': 'default'}

    # Recognition language
    rec_lang_match = re.search(r'(?:認識|recognition|lang)[:：]\s*([^、,]+)', content, re.IGNORECASE)
    if rec_lang_match:
        result['recognition_language'] = rec_lang_match.group(1).strip()

    # TTS voice
    voice_match = re.search(r'(?:音声|voice|tts)[:：]\s*([^、,]+)', content, re.IGNORECASE)
    if voice_match:
        result['tts_voice_id'] = voice_match.group(1).strip()

    # Speed
    speed_match = re.search(r'(?:速度|speed)[:：]\s*([\d.]+)', content, re.IGNORECASE)
    if speed_match:
        result['tts_speed'] = float(speed_match.group(1))

    # Pitch
    pitch_match = re.search(r'(?:ピッチ|pitch)[:：]\s*([\d.]+)', content, re.IGNORECASE)
    if pitch_match:
        result['tts_pitch'] = float(pitch_match.group(1))

    # Auto response
    auto_match = re.search(r'(?:自動応答|auto(?:[-\s]?response)?)[:：]\s*(true|false|on|off|yes|no)', content, re.IGNORECASE)
    if auto_match:
        auto_val = auto_match.group(1).lower()
        result['auto_response'] = auto_val in ['true', 'on', 'yes']

    return result

def handle_message(message):
    """Handle message"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'add_command':
        if not parsed['name'] or not parsed['action_type']:
            return "❌ コマンド名とアクションタイプを入力してください (Enter command name and action type)"

        command_id = add_voice_command(
            parsed['name'],
            parsed['pattern'],
            parsed['action_type'],
            parsed.get('params'),
            parsed.get('description')
        )

        response = f"🎤 音声コマンド #{command_id} 作成完了\n"
        response += f"コマンド名: {parsed['name']}\n"
        response += f"パターン: {parsed['pattern']}\n"
        response += f"アクション: {parsed['action_type']}"
        if parsed.get('params'):
            response += f"\nパラメータ: {parsed['params']}"
        if parsed.get('description'):
            response += f"\n説明: {parsed['description']}"

        return response

    elif action == 'list_commands':
        commands = list_voice_commands()

        if not commands:
            return "🎤 コマンドがありません (No voice commands)"

        response = f"🎤 音声コマンド一覧 ({len(commands)}件):\n"
        for command in commands:
            response += format_voice_command(command)

        return response

    elif action == 'delete_command':
        name = parsed['name']

        # Find command by name
        commands = list_voice_commands()
        command_to_delete = None
        for cmd in commands:
            if cmd[1] == name:
                command_to_delete = cmd
                break

        if not command_to_delete:
            return f"❌ コマンド「{name}」が見つかりません (Command '{name}' not found)"

        delete_voice_command(command_to_delete[0])
        return f"✅ コマンド「{name}」を削除しました (Deleted command '{name}')"

    elif action == 'history':
        history = get_voice_history()

        if not history:
            return "📜 音声履歴がありません (No voice history)"

        response = f"📜 音声履歴 ({len(history)}件):\n"
        for item in history:
            response += format_voice_history(item)

        return response

    elif action == 'tts_history':
        history = get_tts_history()

        if not history:
            return "🔊 TTS履歴がありません (No TTS history)"

        response = f"🔊 TTS履歴 ({len(history)}件):\n"
        for item in history:
            response += format_tts_history(item)

        return response

    elif action == 'add_vocab':
        if not parsed['word']:
            return "❌ 単語を入力してください (Enter word)"

        success = add_custom_vocabulary(
            parsed['word'],
            parsed.get('pronunciation'),
            parsed.get('category')
        )

        if success:
            response = f"✅ 語彙「{parsed['word']}」を追加しました (Added vocabulary '{parsed['word']}')"
            if parsed.get('pronunciation'):
                response += f"\n発音: {parsed['pronunciation']}"
            if parsed.get('category'):
                response += f"\nカテゴリ: {parsed['category']}"
            return response
        else:
            return f"❌ 語彙「{parsed['word']}」は既に存在します (Vocabulary already exists)"

    elif action == 'list_vocab':
        category = parsed.get('category')
        vocab = get_custom_vocabulary(category)

        if not vocab:
            cat_msg = f"カテゴリ「{category}」の" if category else ""
            return f"📚 {cat_msg}語彙がありません (No vocabulary{' for ' + category if category else ''})"

        cat_msg = f"カテゴリ「{category}」の" if category else ""
        response = f"📚 {cat_msg}語彙 ({len(vocab)}件):\n"
        for word in vocab:
            response += format_vocabulary(word)

        return response

    elif action == 'set_setting':
        user_id = parsed.get('user_id', 'default')
        set_voice_setting(
            user_id,
            parsed.get('recognition_language'),
            parsed.get('tts_voice_id'),
            parsed.get('tts_speed'),
            parsed.get('tts_pitch'),
            parsed.get('auto_response')
        )

        response = "✅ 音声設定を保存しました (Voice settings saved):\n"
        if parsed.get('recognition_language'):
            response += f"  認識言語 / Recognition: {parsed['recognition_language']}\n"
        if parsed.get('tts_voice_id'):
            response += f"  TTS音声 / Voice: {parsed['tts_voice_id']}\n"
        if parsed.get('tts_speed'):
            response += f"  速度 / Speed: {parsed['tts_speed']}\n"
        if parsed.get('tts_pitch'):
            response += f"  ピッチ / Pitch: {parsed['tts_pitch']}\n"
        if 'auto_response' in parsed:
            auto_str = "ON" if parsed['auto_response'] else "OFF"
            response += f"  自動応答 / Auto response: {auto_str}"

        return response

    elif action == 'stats':
        stats = get_stats()

        response = "📊 音声統計 / Voice Statistics:\n"
        response += f"総インタラクション: {stats['total_interactions']}回 / Total interactions: {stats['total_interactions']}\n"
        response += f"成功した回数: {stats['successful_interactions']}回 / Successful: {stats['successful_interactions']}\n"
        response += f"アクティブコマンド: {stats['active_commands']}件 / Active commands: {stats['active_commands']}\n"
        response += f"TTS実行回数: {stats['tts_count']}回 / TTS count: {stats['tts_count']}\n"
        response += f"語彙数: {stats['vocab_count']}件 / Vocabulary: {stats['vocab_count']}\n"
        response += f"直近24時間: {stats['recent_interactions']}回 / Last 24h: {stats['recent_interactions']}\n"

        if stats['most_used_commands']:
            response += f"\n🔥 最も使用されたコマンド / Most used:\n"
            for name, count in stats['most_used_commands']:
                response += f"  {name}: {count}回\n"

        return response

    return None

def format_voice_command(command):
    """Format voice command entry"""
    id, name, pattern, action_type, params, description, created_at, usage_count, active = command

    response = f"\n[{id}] {name}\n"
    response += f"    パターン: {pattern}\n"
    response += f"    アクション: {action_type}\n"
    if params:
        response += f"    パラメータ: {params}\n"
    if description:
        response += f"    説明: {description}\n"
    response += f"    使用回数: {usage_count}"

    return response

def format_voice_history(item):
    """Format voice history entry"""
    id, transcription, recognized_command_id, action_executed, success, timestamp, command_name = item

    response = f"\n[{id}] {timestamp}\n"
    response += f"    認識: {transcription}\n"
    if command_name:
        response += f"    コマンド: {command_name}\n"
    if action_executed:
        response += f"    アクション: {action_executed}\n"
    status = "✅ 成功" if success else "❌ 失敗"
    response += f"    結果: {status}"

    return response

def format_tts_history(item):
    """Format TTS history entry"""
    id, text, voice_id, duration, file_path, created_at = item

    response = f"\n[{id}] {created_at}\n"
    response += f"    テキスト: {text[:50]}{'...' if len(text) > 50 else ''}\n"
    if voice_id:
        response += f"    音声: {voice_id}\n"
    if duration:
        response += f"    長さ: {duration:.2f}秒"

    return response

def format_vocabulary(word):
    """Format vocabulary entry"""
    id, word_text, pronunciation, category, created_at = word

    response = f"\n    {word_text}"
    if pronunciation:
        response += f" ({pronunciation})"
    if category:
        response += f" [{category}]"

    return response

if __name__ == '__main__':
    # Test
    import sqlite3

    init_db()

    test_messages = [
        "コマンド追加: 挨拶, パターン: おはよう, アクション: greeting, 説明: 朝の挨拶",
        "コマンド一覧",
        "語彙追加: AIエージェント, 発音: エーアイエージェント, カテゴリ: テクニカル",
        "語彙一覧",
        "設定: 認識: ja-JP, 音声: default",
        "音声履歴",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
