#!/usr/bin/env python3
"""
Document Agent - Discord Bot Interface
Natural language interface for document management
"""

import sqlite3
from pathlib import Path
from datetime import datetime
import re
from typing import Optional, List, Dict, Any, Tuple
import json

DB_PATH = Path(__file__).parent / "document.db"

# Language detection patterns
JAPANESE_PATTERN = re.compile(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]')
ENGLISH_PATTERN = re.compile(r'[a-zA-Z]')

def detect_language(text: str) -> str:
    """Detect if text is primarily Japanese or English"""
    if not text:
        return 'en'

    japanese_chars = len(JAPANESE_PATTERN.findall(text))
    english_chars = len(ENGLISH_PATTERN.findall(text))

    if japanese_chars > english_chars:
        return 'ja'
    return 'en'

class DocumentNLPProcessor:
    """Natural language processor for document management"""

    def __init__(self, language: str = 'ja'):
        self.language = language
        self._init_patterns()

    def _init_patterns(self):
        """Initialize language-specific patterns"""
        if self.language == 'ja':
            self.ADD_PATTERNS = [
                r'追加|書類追加|ドキュメント追加|新規作成|作成|登録',
                r'title[:\uff1a](.+?)(?:\s|$)', r'タイトル[:\uff1a](.+?)(?:\s|$)',
                r'content[:\uff1a](.+)', r'内容[:\uff1a](.+)',
                r'category[:\uff1a](.+?)(?:\s|$)', r'カテゴリ[:\uff1a](.+?)(?:\s|$)',
                r'tags?[:\uff1a](.+)', r'タグ[:\uff1a](.+)',
            ]
            self.UPDATE_PATTERNS = [
                r'更新|変更|修正|編集',
                r'id[:\uff1a](\d+)', r'ID[:\uff1a](\d+)',
            ]
            self.DELETE_PATTERNS = [
                r'削除|消去',
                r'id[:\uff1a](\d+)', r'ID[:\uff1a](\d+)',
            ]
            self.SEARCH_PATTERNS = [
                r'検索|探す|見つける',
            ]
            self.LIST_PATTERNS = [
                r'一覧|リスト|すべて|全部|list|show|all',
            ]
            self.STATS_PATTERNS = [
                r'統計|集計|ステータス|status|stats|summary',
            ]
            self.ARCHIVE_PATTERNS = [
                r'アーカイブ|archive',
            ]
        else:
            self.ADD_PATTERNS = [
                r'add|create|new|register',
                r'title[:\uff1a](.+?)(?:\s|$)',
                r'content[:\uff1a](.+)',
                r'category[:\uff1a](.+?)(?:\s|$)',
                r'tags?[:\uff1a](.+)',
            ]
            self.UPDATE_PATTERNS = [
                r'update|change|modify|edit',
                r'id[:\uff1a](\d+)',
            ]
            self.DELETE_PATTERNS = [
                r'delete|remove',
                r'id[:\uff1a](\d+)',
            ]
            self.SEARCH_PATTERNS = [
                r'search|find|look for',
            ]
            self.LIST_PATTERNS = [
                r'list|show|all',
            ]
            self.STATS_PATTERNS = [
                r'stats|statistics|summary|status',
            ]
            self.ARCHIVE_PATTERNS = [
                r'archive',
            ]

    def process_message(self, message: str) -> Dict[str, Any]:
        """Process user message and extract intent and parameters"""
        message = message.strip().lower()
        intent = 'unknown'
        params = {}

        # Detect action
        for pattern in self.ADD_PATTERNS:
            if re.search(pattern, message):
                intent = 'add'
                break
        else:
            for pattern in self.UPDATE_PATTERNS:
                if re.search(pattern, message):
                    intent = 'update'
                    break
            else:
                for pattern in self.DELETE_PATTERNS:
                    if re.search(pattern, message):
                        intent = 'delete'
                        break
                else:
                    for pattern in self.SEARCH_PATTERNS:
                        if re.search(pattern, message):
                            intent = 'search'
                            break
                    else:
                        for pattern in self.LIST_PATTERNS:
                            if re.search(pattern, message):
                                intent = 'list'
                                break
                        else:
                            for pattern in self.STATS_PATTERNS:
                                if re.search(pattern, message):
                                    intent = 'stats'
                                    break
                            else:
                                for pattern in self.ARCHIVE_PATTERNS:
                                    if re.search(pattern, message):
                                        intent = 'archive'
                                        break

        # Extract parameters
        if intent == 'add':
            title_match = re.search(r'title[:\uff1a](.+?)(?:\s+content[:\uff1a]|$|tag|カテゴリ|category)', message, re.IGNORECASE)
            if title_match:
                params['title'] = title_match.group(1).strip()

            content_match = re.search(r'content[:\uff1a](.+?)(?:\s+tag|タグ|category|カテゴリ|$)', message, re.IGNORECASE | re.DOTALL)
            if content_match:
                params['content'] = content_match.group(1).strip()

            cat_match = re.search(r'category[:\uff1a](.+?)(?:\s+tag|タグ|$)', message, re.IGNORECASE)
            if not cat_match:
                cat_match = re.search(r'カテゴリ[:\uff1a](.+?)(?:\s+tag|タグ|$)', message, re.IGNORECASE)
            if cat_match:
                params['category'] = cat_match.group(1).strip()

            tag_match = re.search(r'tags?[:\uff1a](.+)', message, re.IGNORECASE)
            if not tag_match:
                tag_match = re.search(r'タグ[:\uff1a](.+)', message, re.IGNORECASE)
            if tag_match:
                tags_str = tag_match.group(1).strip()
                params['tags'] = [t.strip() for t in re.split(r'[,、;；]', tags_str)]

        elif intent == 'update':
            id_match = re.search(r'id[:\uff1a](\d+)', message, re.IGNORECASE)
            if id_match:
                params['id'] = int(id_match.group(1))

            title_match = re.search(r'title[:\uff1a](.+?)(?:\s+content|category|tag|$)', message, re.IGNORECASE)
            if title_match:
                params['title'] = title_match.group(1).strip()

            content_match = re.search(r'content[:\uff1a](.+)', message, re.IGNORECASE | re.DOTALL)
            if content_match:
                params['content'] = content_match.group(1).strip()

            cat_match = re.search(r'category[:\uff1a](.+)', message, re.IGNORECASE)
            if cat_match:
                params['category'] = cat_match.group(1).strip()

        elif intent == 'delete':
            id_match = re.search(r'id[:\uff1a](\d+)', message, re.IGNORECASE)
            if id_match:
                params['id'] = int(id_match.group(1))

        elif intent == 'search':
            search_terms = re.sub(r'(検索|search|探す|find|見つける|for|title:|content:|タイトル:|内容:)', '', message).strip()
            if search_terms:
                params['query'] = search_terms

            title_match = re.search(r'title[:\uff1a](.+)', message, re.IGNORECASE)
            if title_match:
                params['title'] = title_match.group(1).strip()

            content_match = re.search(r'content[:\uff1a](.+)', message, re.IGNORECASE)
            if content_match:
                params['content'] = content_match.group(1).strip()

        elif intent == 'list':
            cat_match = re.search(r'category[:\uff1a](.+)', message, re.IGNORECASE)
            if not cat_match:
                cat_match = re.search(r'カテゴリ[:\uff1a](.+)', message, re.IGNORECASE)
            if cat_match:
                params['category'] = cat_match.group(1).strip()

            tag_match = re.search(r'tag[:\uff1a](.+)', message, re.IGNORECASE)
            if tag_match:
                params['tag'] = tag_match.group(1).strip()

        elif intent == 'archive':
            id_match = re.search(r'id[:\uff1a](\d+)', message, re.IGNORECASE)
            if id_match:
                params['id'] = int(id_match.group(1))

        return {'intent': intent, 'params': params}

class DocumentDiscordBot:
    """Discord bot interface for document management"""

    def __init__(self):
        self.language = 'ja'

    def _get_conn(self):
        """Get database connection"""
        return sqlite3.connect(DB_PATH)

    def handle_message(self, message: str) -> str:
        """Handle incoming Discord message"""
        self.language = detect_language(message)
        processor = DocumentNLPProcessor(self.language)
        result = processor.process_message(message)

        handlers = {
            'add': self._handle_add,
            'update': self._handle_update,
            'delete': self._handle_delete,
            'search': self._handle_search,
            'list': self._handle_list,
            'stats': self._handle_stats,
            'category': self._handle_category,
            'archive': self._handle_archive,
        }

        handler = handlers.get(result['intent'], self._handle_unknown)
        return handler(result['params'])

    def _handle_add(self, params: Dict[str, Any]) -> str:
        if 'title' not in params or 'content' not in params:
            if self.language == 'ja':
                return "❌ タイトルと内容を指定してください。\n例: タイトル: 会議メモ 内容: 今日の会議の議事録 カテゴリ: 仕事"
            else:
                return "❌ Please specify title and content.\nExample: title: Meeting Note content: Today's minutes category: Work"

        try:
            conn = self._get_conn()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO documents (title, content, category, language)
                VALUES (?, ?, ?, ?)
            ''', (
                params['title'],
                params['content'],
                params.get('category'),
                self.language
            ))

            doc_id = cursor.lastrowid

            if 'tags' in params:
                for tag_name in params['tags']:
                    cursor.execute('SELECT id FROM tags WHERE name = ?', (tag_name,))
                    tag_row = cursor.fetchone()
                    if tag_row:
                        tag_id = tag_row[0]
                        cursor.execute('UPDATE tags SET count = count + 1 WHERE id = ?', (tag_id,))
                    else:
                        cursor.execute('INSERT INTO tags (name) VALUES (?)', (tag_name,))
                        tag_id = cursor.lastrowid

                    cursor.execute('INSERT INTO document_tags (document_id, tag_id) VALUES (?, ?)',
                                 (doc_id, tag_id))

            conn.commit()
            conn.close()

            if self.language == 'ja':
                return f"✅ 書類を追加しました！ID: {doc_id}"
            else:
                return f"✅ Document added! ID: {doc_id}"

        except Exception as e:
            if self.language == 'ja':
                return f"❌ エラーが発生しました: {str(e)}"
            else:
                return f"❌ Error occurred: {str(e)}"

    def _handle_update(self, params: Dict[str, Any]) -> str:
        if 'id' not in params:
            if self.language == 'ja':
                return "❌ IDを指定してください。"
            else:
                return "❌ Please specify document ID."

        if not any(k in params for k in ['title', 'content', 'category']):
            if self.language == 'ja':
                return "❌ 更新するフィールドを指定してください。"
            else:
                return "❌ Please specify fields to update."

        try:
            conn = self._get_conn()
            cursor = conn.cursor()

            cursor.execute('SELECT id FROM documents WHERE id = ?', (params['id'],))
            if not cursor.fetchone():
                conn.close()
                if self.language == 'ja':
                    return f"❌ ID {params['id']} の書類が見つかりません。"
                else:
                    return f"❌ Document with ID {params['id']} not found."

            updates = []
            values = []
            if 'title' in params:
                updates.append('title = ?')
                values.append(params['title'])
            if 'content' in params:
                updates.append('content = ?')
                values.append(params['content'])
            if 'category' in params:
                updates.append('category = ?')
                values.append(params['category'])

            values.append(params['id'])
            values.append(datetime.now())

            cursor.execute(f'''
                UPDATE documents
                SET {', '.join(updates)}, updated_at = ?
                WHERE id = ?
            ''', values)

            conn.commit()
            conn.close()

            if self.language == 'ja':
                return f"✅ ID {params['id']} の書類を更新しました。"
            else:
                return f"✅ Document {params['id']} updated."

        except Exception as e:
            if self.language == 'ja':
                return f"❌ エラーが発生しました: {str(e)}"
            else:
                return f"❌ Error occurred: {str(e)}"

    def _handle_delete(self, params: Dict[str, Any]) -> str:
        if 'id' not in params:
            if self.language == 'ja':
                return "❌ IDを指定してください。"
            else:
                return "❌ Please specify document ID."

        try:
            conn = self._get_conn()
            cursor = conn.cursor()

            cursor.execute('DELETE FROM documents WHERE id = ?', (params['id'],))

            if cursor.rowcount == 0:
                conn.close()
                if self.language == 'ja':
                    return f"❌ ID {params['id']} の書類が見つかりません。"
                else:
                    return f"❌ Document with ID {params['id']} not found."

            conn.commit()
            conn.close()

            if self.language == 'ja':
                return f"✅ ID {params['id']} の書類を削除しました。"
            else:
                return f"✅ Document {params['id']} deleted."

        except Exception as e:
            if self.language == 'ja':
                return f"❌ エラーが発生しました: {str(e)}"
            else:
                return f"❌ Error occurred: {str(e)}"

    def _handle_search(self, params: Dict[str, Any]) -> str:
        try:
            conn = self._get_conn()
            cursor = conn.cursor()

            query = 'SELECT id, title, category, created_at FROM documents WHERE status = ?'
            values = ['active']

            if 'title' in params:
                query += ' AND title LIKE ?'
                values.append(f'%{params["title"]}%')
            elif 'content' in params:
                query += ' AND content LIKE ?'
                values.append(f'%{params["content"]}%')
            elif 'query' in params:
                query += ' AND (title LIKE ? OR content LIKE ?)'
                values.append(f'%{params["query"]}%')
                values.append(f'%{params["query"]}%')

            query += ' ORDER BY created_at DESC LIMIT 20'

            cursor.execute(query, values)
            results = cursor.fetchall()
            conn.close()

            if not results:
                if self.language == 'ja':
                    return "📄 書類が見つかりませんでした。"
                else:
                    return "📄 No documents found."

            output = []
            if self.language == 'ja':
                output.append("📄 **検索結果**:")
            else:
                output.append("📄 **Search Results**:")

            for row in results:
                output.append(f"  - ID {row[0]}: {row[1]} ({row[2] or 'No category'}) - {row[3][:10]}")

            return '\n'.join(output)

        except Exception as e:
            if self.language == 'ja':
                return f"❌ エラーが発生しました: {str(e)}"
            else:
                return f"❌ Error occurred: {str(e)}"

    def _handle_list(self, params: Dict[str, Any]) -> str:
        try:
            conn = self._get_conn()
            cursor = conn.cursor()

            query = 'SELECT id, title, category, created_at FROM documents WHERE status = ?'
            values = ['active']

            if 'category' in params:
                query += ' AND category = ?'
                values.append(params['category'])

            query += ' ORDER BY created_at DESC LIMIT 30'

            cursor.execute(query, values)
            results = cursor.fetchall()

            conn.close()

            if not results:
                if self.language == 'ja':
                    return "📄 書類がありません。"
                else:
                    return "📄 No documents."

            output = []
            if self.language == 'ja':
                output.append("📄 **書類一覧**:")
            else:
                output.append("📄 **Document List**:")

            for row in results:
                category = row[2] or 'N/A'
                output.append(f"  - ID {row[0]}: {row[1]} [{category}]")

            return '\n'.join(output)

        except Exception as e:
            if self.language == 'ja':
                return f"❌ エラーが発生しました: {str(e)}"
            else:
                return f"❌ Error occurred: {str(e)}"

    def _handle_stats(self, params: Dict[str, Any]) -> str:
        try:
            conn = self._get_conn()
            cursor = conn.cursor()

            cursor.execute('SELECT COUNT(*) FROM documents')
            total = cursor.fetchone()[0]

            cursor.execute('SELECT status, COUNT(*) FROM documents GROUP BY status')
            by_status = {row[0]: row[1] for row in cursor.fetchall()}

            cursor.execute('''
                SELECT category, COUNT(*)
                FROM documents
                WHERE category IS NOT NULL
                GROUP BY category
                ORDER BY COUNT(*) DESC
                LIMIT 10
            ''')
            by_category = cursor.fetchall()

            cursor.execute('SELECT COUNT(*) FROM tags')
            total_tags = cursor.fetchone()[0]

            conn.close()

            output = []
            if self.language == 'ja':
                output.append("📊 **書類統計**:")
                output.append(f"  - 総数: {total}")
                output.append(f"  - アクティブ: {by_status.get('active', 0)}")
                output.append(f"  - アーカイブ: {by_status.get('archived', 0)}")
                output.append(f"  - タグ数: {total_tags}")

                if by_category:
                    output.append("\n  **カテゴリ別 (トップ10)**:")
                    for cat, count in by_category:
                        output.append(f"    - {cat}: {count}")
            else:
                output.append("📊 **Document Statistics**:")
                output.append(f"  - Total: {total}")
                output.append(f"  - Active: {by_status.get('active', 0)}")
                output.append(f"  - Archived: {by_status.get('archived', 0)}")
                output.append(f"  - Tags: {total_tags}")

                if by_category:
                    output.append("\n  **By Category (Top 10)**:")
                    for cat, count in by_category:
                        output.append(f"    - {cat}: {count}")

            return '\n'.join(output)

        except Exception as e:
            if self.language == 'ja':
                return f"❌ エラーが発生しました: {str(e)}"
            else:
                return f"❌ Error occurred: {str(e)}"

    def _handle_category(self, params: Dict[str, Any]) -> str:
        try:
            conn = self._get_conn()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT name, description, color
                FROM categories
                ORDER BY name
            ''')
            categories = cursor.fetchall()
            conn.close()

            if not categories:
                if self.language == 'ja':
                    return "📂 カテゴリがありません。"
                else:
                    return "📂 No categories."

            output = []
            if self.language == 'ja':
                output.append("📂 **カテゴリ一覧**:")
            else:
                output.append("📂 **Categories**:")

            for cat in categories:
                output.append(f"  - {cat[0]}: {cat[1] or 'No description'}")

            return '\n'.join(output)

        except Exception as e:
            if self.language == 'ja':
                return f"❌ エラーが発生しました: {str(e)}"
            else:
                return f"❌ Error occurred: {str(e)}"

    def _handle_archive(self, params: Dict[str, Any]) -> str:
        if 'id' not in params:
            if self.language == 'ja':
                return "❌ IDを指定してください。"
            else:
                return "❌ Please specify document ID."

        try:
            conn = self._get_conn()
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE documents
                SET status = 'archived', updated_at = ?
                WHERE id = ?
            ''', (datetime.now(), params['id']))

            if cursor.rowcount == 0:
                conn.close()
                if self.language == 'ja':
                    return f"❌ ID {params['id']} の書類が見つかりません。"
                else:
                    return f"❌ Document with ID {params['id']} not found."

            conn.commit()
            conn.close()

            if self.language == 'ja':
                return f"✅ ID {params['id']} をアーカイブしました。"
            else:
                return f"✅ Document {params['id']} archived."

        except Exception as e:
            if self.language == 'ja':
                return f"❌ エラーが発生しました: {str(e)}"
            else:
                return f"❌ Error occurred: {str(e)}"

    def _handle_unknown(self, params: Dict[str, Any]) -> str:
        if self.language == 'ja':
            return """📄 **Document Agent - 書類管理**

コマンド:
- タイトル: [タイトル] 内容: [内容] カテゴリ: [カテゴリ] - 書類を追加
- 更新 ID: [ID] タイトル: [新しいタイトル] - 書類を更新
- 削除 ID: [ID] - 書類を削除
- 検索 [キーワード] - 書類を検索
- 一覧 - すべての書類を表示
- 統計 - 統計情報を表示
- カテゴリ - カテゴリ一覧
- アーカイブ ID: [ID] - 書類をアーカイブ

Example:
- タイトル: 会議メモ 内容: 今日の議事録 カテゴリ: 仕事"""
        else:
            return """📄 **Document Agent - Document Management**

Commands:
- title: [title] content: [content] category: [category] - Add document
- update ID: [id] title: [new title] - Update document
- delete ID: [id] - Delete document
- search [keyword] - Search documents
- list - Show all documents
- stats - Show statistics
- category - List categories
- archive ID: [id] - Archive document

Example:
- title: Meeting Note content: Today's minutes category: Work"""


def test_discord_bot():
    bot = DocumentDiscordBot()
    print("=== Test: Add Document ===")
    print(bot.handle_message("タイトル: 会議メモ 内容: 今日の会議の議事録 カテゴリ: 仕事"))
    print("\n=== Test: List Documents ===")
    print(bot.handle_message("一覧"))
    print("\n=== Test: Search ===")
    print(bot.handle_message("検索 会議"))
    print("\n=== Test: Stats ===")
    print(bot.handle_message("統計"))
    print("\n=== Test: Help ===")
    print(bot.handle_message("help"))


if __name__ == "__main__":
    test_discord_bot()
