#!/usr/bin/env python3
"""
tax-agent discord bot
Natural language processing for tax record management
Supports Japanese and English
"""

import re
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Import database module
from db import TaxDatabase


class MessageParser:
    """Natural language parser for tax-related commands"""

    # Keywords for actions (English/Japanese)
    ACTION_KEYWORDS = {
        'en': {
            'add': ['add', 'record', 'save', 'new', 'create'],
            'list': ['list', 'show', 'display', 'view', 'get'],
            'delete': ['delete', 'remove', 'del'],
            'update': ['update', 'edit', 'change', 'modify'],
            'search': ['search', 'find', 'lookup'],
            'summary': ['summary', 'total', 'sum', 'report'],
            'help': ['help', 'commands'],
            'set': ['set', 'config', 'configure', 'language', 'lang'],
        },
        'ja': {
            'add': ['追加', '記録', '保存', '新規', '登録'],
            'list': ['一覧', '表示', '見る', '確認'],
            'delete': ['削除', '消す'],
            'update': ['更新', '変更', '修正'],
            'search': ['検索', '探す'],
            'summary': ['集計', '合計', 'サマリー', 'レポート'],
            'help': ['ヘルプ', '使い方', 'コマンド'],
            'set': ['設定', '言語', 'セッティング'],
        }
    }

    # Category keywords
    CATEGORY_KEYWORDS = {
        'en': {
            'income': ['income', 'earning', 'salary', 'revenue', '収入'],
            'expense': ['expense', 'cost', 'spending', 'payment', '経費', '費用'],
            'deduction': ['deduction', 'tax deduction', '控除'],
            'tax_paid': ['tax', 'tax paid', '納税', '税金'],
            'other': ['other', 'misc', 'その他'],
        },
        'ja': {
            'income': ['所得', '収入', '給与', '報酬'],
            'expense': ['経費', '費用', '出費'],
            'deduction': ['控除', '免除'],
            'tax_paid': ['納税', '税金'],
            'other': ['その他'],
        }
    }

    # Amount patterns
    AMOUNT_PATTERN = re.compile(r'[¥$￥]?\s*([0-9,]+(?:\.[0-9]{0,2})?)')
    YEAR_PATTERN = re.compile(r'\b(20[0-9]{2})\b')

    def __init__(self, default_language: str = 'ja'):
        self.default_language = default_language

    def detect_language(self, text: str) -> str:
        """Detect language from text (simple heuristic)"""
        # Check for Japanese characters
        if re.search(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]', text):
            return 'ja'
        return 'en'

    def parse_amount(self, text: str) -> Optional[float]:
        """Extract amount from text"""
        matches = self.AMOUNT_PATTERN.findall(text)
        if matches:
            try:
                return float(matches[0].replace(',', ''))
            except ValueError:
                pass
        return None

    def parse_year(self, text: str) -> Optional[int]:
        """Extract year from text"""
        matches = self.YEAR_PATTERN.findall(text)
        if matches:
            try:
                return int(matches[0])
            except ValueError:
                pass
        return None

    def detect_category(self, text: str, language: str) -> Optional[str]:
        """Detect category from text"""
        keywords = self.CATEGORY_KEYWORDS[language]
        text_lower = text.lower()

        for category, words in keywords.items():
            for word in words:
                if word in text_lower:
                    return category
        return None

    def detect_action(self, text: str, language: str) -> Optional[str]:
        """Detect intended action from text"""
        keywords = self.ACTION_KEYWORDS[language]
        text_lower = text.lower()

        for action, words in keywords.items():
            for word in words:
                if text_lower.startswith(word) or f' {word} ' in text_lower:
                    return action
        return None

    def parse_add_command(self, text: str, language: str) -> Optional[Dict]:
        """Parse 'add record' command"""
        amount = self.parse_amount(text)
        if not amount:
            return None

        category = self.detect_category(text, language) or 'other'
        year = self.parse_year(text) or datetime.now().year

        # Extract description (everything after removing amount and year)
        desc = text
        for pattern in [self.AMOUNT_PATTERN, self.YEAR_PATTERN]:
            desc = re.sub(pattern.pattern, '', desc)
        # Remove action keywords and category keywords
        for word in self.ACTION_KEYWORDS[language]['add'] + self.ACTION_KEYWORDS[language].get('en', [])[:5]:
            desc = desc.replace(word, '')
        desc = desc.strip()

        # Remove currency symbols and clean up
        desc = re.sub(r'[¥$￥]', '', desc)
        desc = desc.strip()

        return {
            'action': 'add',
            'category': category,
            'amount': amount,
            'year': year,
            'description': desc if desc else None
        }

    def parse_list_command(self, text: str, language: str) -> Dict:
        """Parse 'list records' command"""
        year = self.parse_year(text)
        category = self.detect_category(text, language)

        return {
            'action': 'list',
            'year': year,
            'category': category
        }

    def parse_summary_command(self, text: str, language: str) -> Dict:
        """Parse 'summary' command"""
        year = self.parse_year(text) or datetime.now().year
        category = self.detect_category(text, language)

        return {
            'action': 'summary',
            'year': year,
            'category': category
        }

    def parse_search_command(self, text: str, language: str) -> Optional[Dict]:
        """Parse 'search' command"""
        # Extract search term
        for word in self.ACTION_KEYWORDS[language]['search'] + \
                   self.ACTION_KEYWORDS['en']['search']:
            text = text.replace(word, '', 1)

        keyword = text.strip()
        if not keyword:
            return None

        year = self.parse_year(text)

        return {
            'action': 'search',
            'keyword': keyword,
            'year': year
        }

    def parse_delete_command(self, text: str, language: str) -> Optional[Dict]:
        """Parse 'delete' command"""
        # Try to extract record ID
        match = re.search(r'\b(\d+)\b', text)
        if not match:
            return None

        return {
            'action': 'delete',
            'record_id': int(match.group(1))
        }

    def parse_set_command(self, text: str, language: str) -> Optional[Dict]:
        """Parse 'settings' command"""
        # Check for language setting
        if 'english' in text.lower() or '英語' in text or 'en' in text:
            return {'action': 'set', 'setting': 'language', 'value': 'en'}
        elif 'japanese' in text.lower() or '日本語' in text or 'ja' in text:
            return {'action': 'set', 'setting': 'language', 'value': 'ja'}

        return None

    def parse(self, text: str) -> Optional[Dict]:
        """Parse message and return structured command"""
        language = self.detect_language(text)
        action = self.detect_action(text, language)

        if not action:
            # Try to infer from content
            if self.parse_amount(text):
                action = 'add'
            else:
                return {'action': 'help'}

        if action == 'add':
            return self.parse_add_command(text, language)
        elif action == 'list':
            return self.parse_list_command(text, language)
        elif action == 'summary':
            return self.parse_summary_command(text, language)
        elif action == 'search':
            return self.parse_search_command(text, language)
        elif action == 'delete':
            return self.parse_delete_command(text, language)
        elif action == 'set':
            return self.parse_set_command(text, language)
        elif action == 'help':
            return {'action': 'help', 'language': language}

        return None


class TaxAgent:
    """Main agent for tax record management via Discord"""

    # Response templates
    RESPONSES = {
        'en': {
            'help': """📊 **Tax Agent Commands**

**Add Record:**
• "add 5000 expense office supplies"
• "record ¥10000 income freelance work 2024"

**List Records:**
• "list 2024"
• "show expense 2024"
• "list" (all years)

**Summary:**
• "summary 2024"
• "total expense 2024"

**Search:**
• "search office"
• "find freelance"

**Delete:**
• "delete 123" (where 123 is record ID)

**Settings:**
• "set language english"
• "言語設定 日本語"
""",
            'added': "✅ Added record: {category} ¥{amount} ({year}) - {description}",
            'deleted': "🗑️ Deleted record #{id}",
            'not_found': "❌ Record not found",
            'no_records': "📭 No records found",
            'summary_header': "📊 **Tax Summary {year}**",
            'list_header': "📋 **Records {year}**",
            'language_set': "🌐 Language set to {lang}",
            'error': "❌ Error: {error}"
        },
        'ja': {
            'help': """📊 **税金エージェント コマンド**

**記録追加:**
• "追加 5000 経費 オフィス用品"
• "記録 ¥10000 所得 フリーランス 2024"

**一覧表示:**
• "一覧 2024"
• "表示 経費 2024"
• "一覧" (全年度)

**集計:**
• "集計 2024"
• "合計 経費 2024"

**検索:**
• "検索 オフィス"
• "探す フリーランス"

**削除:**
• "削除 123" (123は記録ID)

**設定:**
• "言語設定 日本語"
• "set language english"
""",
            'added': "✅ 記録を追加しました: {category} ¥{amount} ({year}) - {description}",
            'deleted': "🗑️ 記録 #{id} を削除しました",
            'not_found': "❌ 記録が見つかりません",
            'no_records': "📭 記録がありません",
            'summary_header': "📊 **税金集計 {year}年**",
            'list_header': "📋 **記録一覧 {year}年**",
            'language_set': "🌐 言語を {lang} に設定しました",
            'error': "❌ エラー: {error}"
        }
    }

    def __init__(self, db_path: str = None):
        self.db = TaxDatabase(db_path)
        self.parser = MessageParser()

    def get_user_language(self, user_id: str) -> str:
        """Get user's preferred language"""
        settings = self.db.get_user_settings(user_id)
        return settings.get('language', 'ja')

    def get_response(self, key: str, language: str, **kwargs) -> str:
        """Get localized response template"""
        template = self.RESPONSES[language].get(key, key)
        return template.format(**kwargs)

    def format_amount(self, amount: float, language: str) -> str:
        """Format amount with appropriate currency"""
        return f"¥{amount:,.0f}"

    def format_record(self, record: Dict, language: str) -> str:
        """Format a single record for display"""
        category_name = self.db.get_category_name(record['category'], language)
        return (
            f"**#{record['id']}** {category_name} "
            f"{self.format_amount(record['amount'], language)}\n"
            f"└ {record['description'] or '-'} "
            f"({record['date_recorded']})"
        )

    def process_message(self, user_id: str, message: str) -> str:
        """Process incoming message and return response"""
        language = self.get_user_language(user_id)
        command = self.parser.parse(message)

        if not command:
            return self.get_response('help', language)

        action = command['action']

        try:
            if action == 'add':
                return self._handle_add(user_id, command, language)

            elif action == 'list':
                return self._handle_list(user_id, command, language)

            elif action == 'summary':
                return self._handle_summary(user_id, command, language)

            elif action == 'search':
                return self._handle_search(user_id, command, language)

            elif action == 'delete':
                return self._handle_delete(user_id, command, language)

            elif action == 'set':
                return self._handle_set(user_id, command, language)

            elif action == 'help':
                return self.get_response('help', command.get('language', language))

            else:
                return self.get_response('help', language)

        except Exception as e:
            return self.get_response('error', language, error=str(e))

    def _handle_add(self, user_id: str, command: Dict, language: str) -> str:
        """Handle add record command"""
        record_id = self.db.add_record(
            user_id=user_id,
            year=command['year'],
            category=command['category'],
            amount=command['amount'],
            description=command['description']
        )

        category_name = self.db.get_category_name(command['category'], language)
        return self.get_response(
            'added', language,
            category=category_name,
            amount=command['amount'],
            year=command['year'],
            description=command['description'] or '-'
        )

    def _handle_list(self, user_id: str, command: Dict, language: str) -> str:
        """Handle list records command"""
        year = command.get('year')
        records = self.db.get_user_records(user_id, year)

        if not records:
            return self.get_response('no_records', language)

        # Filter by category if specified
        if command.get('category'):
            records = [r for r in records if r['category'] == command['category']]

        header = self.get_response('list_header', language, year=year or 'All')
        lines = [header, '']
        lines.extend([self.format_record(r, language) for r in records[:20]])
        lines.append(f"\n*Showing {len(records[:20])} of {len(records)} records*")

        return '\n'.join(lines)

    def _handle_summary(self, user_id: str, command: Dict, language: str) -> str:
        """Handle summary command"""
        year = command['year']
        summary = self.db.get_summary(user_id, year)

        lines = [self.get_response('summary_header', language, year=year), '']
        categories = self.db.get_categories(language)

        for category_id, data in summary.items():
            cat_name = categories.get(category_id, category_id)
            total = self.format_amount(data['total'], language)
            lines.append(f"**{cat_name}**: {total} ({data['count']} records)")

        if not summary:
            lines.append("No data for this year")

        return '\n'.join(lines)

    def _handle_search(self, user_id: str, command: Dict, language: str) -> str:
        """Handle search command"""
        results = self.db.search_records(
            user_id,
            command['keyword'],
            command.get('year')
        )

        if not results:
            return self.get_response('no_records', language)

        lines = [f"🔍 **Search Results for '{command['keyword']}'**", '']
        lines.extend([self.format_record(r, language) for r in results[:10]])
        lines.append(f"\n*Showing {len(results[:10])} of {len(results)} results*")

        return '\n'.join(lines)

    def _handle_delete(self, user_id: str, command: Dict, language: str) -> str:
        """Handle delete command"""
        success = self.db.delete_record(command['record_id'], user_id)

        if success:
            return self.get_response('deleted', language, id=command['record_id'])
        else:
            return self.get_response('not_found', language)

    def _handle_set(self, user_id: str, command: Dict, language: str) -> str:
        """Handle settings command"""
        if command['setting'] == 'language':
            self.db.set_user_language(user_id, command['value'])
            lang_name = 'English' if command['value'] == 'en' else '日本語'
            return self.get_response('language_set', language, lang=lang_name)

        return self.get_response('error', language, error='Unknown setting')


# Discord bot integration (placeholder - requires discord.py library)
def create_discord_bot(db_path: str = None):
    """Create Discord bot instance"""
    import discord
    from discord.ext import commands

    agent = TaxAgent(db_path)
    bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())

    @bot.event
    async def on_ready():
        print(f'{bot.user} is ready!')

    @bot.event
    async def on_message(message):
        # Ignore bot messages
        if message.author.bot:
            return

        # Skip commands starting with prefix (let other handlers deal with them)
        if message.content.startswith(bot.command_prefix):
            await bot.process_commands(message)
            return

        # Process natural language messages
        response = agent.process_message(str(message.author.id), message.content)
        await message.channel.send(response)

    return bot


# Main entry point
if __name__ == '__main__':
    # Simple CLI for testing
    agent = TaxAgent()

    print("Tax Agent CLI (type 'exit' to quit)")
    test_user_id = "test_user_123"

    while True:
        try:
            message = input("> ")
            if message.lower() in ['exit', 'quit']:
                break

            response = agent.process_message(test_user_id, message)
            print(response)
            print()

        except KeyboardInterrupt:
            break

    agent.db.close()
