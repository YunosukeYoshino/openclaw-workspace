#!/usr/bin/env python3
"""
File Management Agent - Discord Integration
"""

import re
import os
from datetime import datetime
from pathlib import Path
from db import *

def parse_message(message):
    """Parse message"""
    # File registration
    file_match = re.match(r'(?:ファイル|file|upload)[:：]\s*(.+)', message, re.IGNORECASE)
    if file_match:
        return parse_file_info(file_match.group(1))

    # Search
    search_match = re.match(r'(?:検索|search|find)[:：]\s*(.+)', message)
    if search_match:
        return {'action': 'search', 'keyword': search_match.group(1)}

    # Tag search
    tag_match = re.match(r'(?:タグ|tag)[:：]\s*(.+)', message)
    if tag_match:
        return {'action': 'search_tag', 'tag': tag_match.group(1)}

    # List
    if message.strip() in ['ファイル一覧', 'ファイル', 'files', 'list']:
        return {'action': 'list'}

    # Category list
    category_match = re.match(r'(?:カテゴリ|category)[:：]\s*(.+)', message)
    if category_match:
        return {'action': 'list_category', 'category': category_match.group(1)}

    # Add category
    add_cat_match = re.match(r'(?:カテゴリ追加|add category)[:：]\s*(.+)', message)
    if add_cat_match:
        return {'action': 'add_category', 'name': add_cat_match.group(1)}

    # Statistics
    if message.strip() in ['統計', 'stats', 'ファイル統計']:
        return {'action': 'stats'}

    return None

def parse_file_info(content):
    """Parse file information"""
    result = {
        'action': 'add',
        'filename': None,
        'filepath': None,
        'category': None,
        'tags': None,
        'description': None
    }

    # Filename (first part)
    filename_match = re.match(r'^([^、,（\(]+)', content)
    if filename_match:
        result['filename'] = filename_match.group(1).strip()
        content = content.replace(filename_match.group(0), '').strip()

    # Path
    path_match = re.search(r'パス[:：]\s*([^、,]+)', content)
    if path_match:
        result['filepath'] = path_match.group(1).strip()
        content = content.replace(path_match.group(0), '').strip()

    # Category
    category_match = re.search(r'カテゴリ[:：]\s*([^、,]+)', content)
    if category_match:
        result['category'] = category_match.group(1).strip()
        content = content.replace(category_match.group(0), '').strip()

    # Tags
    tags_match = re.search(r'タグ[:：]\s*([^、,]+)', content)
    if tags_match:
        result['tags'] = tags_match.group(1).strip()

    # Description
    desc_match = re.search(r'説明[:：]\s*(.+)', content)
    if desc_match:
        result['description'] = desc_match.group(1).strip()

    return result

def handle_message(message):
    """Handle message"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'add':
        if not parsed['filename']:
            return "❌ ファイル名を入力してください (Japanese: ファイル名が必要です / English: Filename required)"

        # Get file info
        filepath = parsed.get('filepath', parsed['filename'])
        file_size = None
        file_type = None

        # Try to get actual file info if path exists
        if Path(filepath).exists():
            file_size = Path(filepath).stat().st_size
            file_type = Path(filepath).suffix

        file_id = add_file(
            parsed['filename'],
            filepath,
            parsed.get('category'),
            parsed.get('tags'),
            parsed.get('description'),
            file_size,
            file_type
        )

        response = f"📁 ファイル #{file_id} 登録完了\n"
        response += f"ファイル名: {parsed['filename']}\n"
        if parsed.get('category'):
            response += f"カテゴリ: {parsed['category']}\n"
        if parsed.get('tags'):
            response += f"タグ: {parsed['tags']}\n"
        if file_size:
            response += f"サイズ: {format_size(file_size)}"
        if file_type:
            response += f"\nタイプ: {file_type}"

        return response

    elif action == 'search':
        keyword = parsed['keyword']
        files = search_files(keyword)

        if not files:
            return f"🔍 「{keyword}」の検索結果: 見つかりませんでした (No results found for '{keyword}')"

        response = f"🔍 「{keyword}」の検索結果 ({len(files)}件):\n"
        for file in files:
            response += format_file(file)

        return response

    elif action == 'search_tag':
        tag = parsed['tag']
        files = search_by_tag(tag)

        if not files:
            return f"🏷️ タグ「{tag}」のファイル: 見つかりませんでした (No files found with tag '{tag}')"

        response = f"🏷️ タグ「{tag}」のファイル ({len(files)}件):\n"
        for file in files:
            response += format_file(file)

        return response

    elif action == 'list':
        files = list_files()

        if not files:
            return "📁 ファイルがありません (No files)"

        response = f"📁 ファイル一覧 ({len(files)}件):\n"
        for file in files:
            response += format_file(file)

        return response

    elif action == 'list_category':
        category = parsed['category']
        files = list_files(category=category)

        if not files:
            return f"📁 カテゴリ「{category}」のファイル: 見つかりませんでした (No files in category '{category}')"

        response = f"📁 カテゴリ「{category}」のファイル ({len(files)}件):\n"
        for file in files:
            response += format_file(file)

        return response

    elif action == 'add_category':
        name = parsed['name']
        desc_match = re.match(r'([^、,]+)(?:[:：]\s*(.+))?', name)
        if desc_match:
            category_name = desc_match.group(1).strip()
            description = desc_match.group(2).strip() if desc_match.group(2) else None

            category_id = add_category(category_name, description)
            if category_id:
                return f"✅ カテゴリ #{category_id} 作成完了: {category_name}"
            else:
                return f"❌ カテゴリ「{category_name}」は既に存在します (Category already exists)"

    elif action == 'stats':
        stats = get_stats()

        response = "📊 ファイル統計 / File Statistics:\n"
        response += f"全ファイル数: {stats['total']}件 / Total files: {stats['total']}\n"
        response += f"総サイズ: {format_size(stats['total_size'])} / Total size: {format_size(stats['total_size'])}\n"
        response += f"総ダウンロード数: {stats['total_downloads']}回 / Total downloads: {stats['total_downloads']}\n"

        if stats['by_category']:
            response += f"\nカテゴリ別 / By category:\n"
            for cat, count in stats['by_category'].items():
                response += f"  {cat}: {count}件\n"

        if stats['most_downloaded']:
            response += f"\n🔥 最もダウンロードされたファイル / Most downloaded:\n"
            for name, count in stats['most_downloaded']:
                response += f"  {name}: {count}回\n"

        return response

    return None

def format_file(file):
    """Format file entry"""
    id, filename, filepath, category, tags, description, file_size, file_type, upload_date, download_count, status = file

    response = f"\n[{id}] {filename}\n"
    if filepath:
        response += f"    パス: {filepath}\n"
    if category:
        response += f"    カテゴリ: {category}\n"
    if tags:
        response += f"    タグ: {tags}\n"
    if file_size:
        response += f"    サイズ: {format_size(file_size)}\n"
    if file_type:
        response += f"    タイプ: {file_type}\n"
    response += f"    アップロード: {upload_date}\n"
    if download_count > 0:
        response += f"    ダウンロード数: {download_count}"

    return response

def format_size(size_bytes):
    """Format file size"""
    if size_bytes is None:
        return "Unknown"

    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"

if __name__ == '__main__':
    # Test
    init_db()

    test_messages = [
        "ファイル: ドキュメント.pdf, パス:/docs/document.pdf, カテゴリ:仕事, タグ:work,pdf",
        "ファイル: 写真.jpg, パス:/photos/photo.jpg, カテゴリ:写真",
        "ファイル: プレゼンテーション.pptx, タグ:work,presentation",
        "検索: ドキュメント",
        "タグ: work",
        "ファイル一覧",
        "カテゴリ追加: 仕事, 説明: 仕事関連のファイル",
        "カテゴリ: 仕事",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
