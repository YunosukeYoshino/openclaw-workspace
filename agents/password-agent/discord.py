#!/usr/bin/env python3
"""
パスワード管理エージェント - Discord Interface
Natural language processing for password management
"""

import re
from typing import Optional, Dict, List, Tuple

try:
    from db import init_db, generate_password, add_password, get_password, list_passwords, search_passwords, update_password, delete_password, get_categories, get_tags, get_stats, check_password_strength
    _import_success = True
except ImportError as e:
    _import_success = False
    print(f"Warning: Could not import db module: {e}")


class PasswordDiscord:
    """Discord interface for password agent with NLP"""

    def __init__(self, master_password: str = "default_password"):
        """Initialize with master password"""
        if _import_success:
            init_db(master_password)

    def process_message(self, message: str) -> str:
        """Process user message and return response"""
        message = message.strip()
        intent, entities = self._parse_intent(message)

        if intent == "generate_password":
            return self._handle_generate_password(entities)
        elif intent == "add_password":
            return self._handle_add_password(entities)
        elif intent == "get_password":
            return self._handle_get_password(entities)
        elif intent == "list_passwords":
            return self._handle_list_passwords(entities)
        elif intent == "search_passwords":
            return self._handle_search_passwords(entities)
        elif intent == "update_password":
            return self._handle_update_password(entities)
        elif intent == "delete_password":
            return self._handle_delete_password(entities)
        elif intent == "check_strength":
            return self._handle_check_strength(entities)
        elif intent == "show_stats":
            return self._handle_show_stats(entities)
        elif intent == "show_categories":
            return self._handle_show_categories(entities)
        elif intent == "help":
            return self._handle_help()
        else:
            return self._handle_unknown(message)

    def _parse_intent(self, message: str) -> Tuple[str, Dict]:
        """Parse intent and entities from message"""
        entities = {}
        lower_msg = message.lower()

        # Generate password
        if re.search(r'(パスワード生成|generate.*password|create.*password|new.*password|make.*password)', lower_msg):
            entities['length'] = self._extract_length(message)
            entities['uppercase'] = self._extract_flag(message, ['大文字', 'uppercase', 'upper'])
            entities['lowercase'] = self._extract_flag(message, ['小文字', 'lowercase', 'lower'])
            entities['digits'] = self._extract_flag(message, ['数字', 'digits', 'numbers'])
            entities['symbols'] = self._extract_flag(message, ['記号', 'symbols', 'special'])
            return "generate_password", entities

        # Add password
        if re.search(r'(パスワードを保存|パスワードを追加|保存|add.*password|save.*password|store.*password)', lower_msg):
            entities['site_name'] = self._extract_site_name(message)
            entities['username'] = self._extract_username(message)
            entities['password'] = self._extract_password(message)
            entities['site_url'] = self._extract_url(message)
            entities['category'] = self._extract_category(message)
            return "add_password", entities

        # Get password
        if re.search(r'(パスワードを取得|パスワードを表示|get.*password|show.*password|retrieve.*password|what.*password)', lower_msg):
            entities['password_id'] = self._extract_id(message)
            entities['site_name'] = self._extract_site_name(message)
            return "get_password", entities

        # List passwords
        if re.search(r'(パスワード一覧|全パスワード|list.*password|show.*all.*password|my.*passwords|all.*passwords)', lower_msg):
            entities['category'] = self._extract_category(message)
            return "list_passwords", entities

        # Search passwords
        if re.search(r'(パスワード検索|search.*password|find.*password)', lower_msg):
            entities['keyword'] = self._extract_keyword(message)
            return "search_passwords", entities

        # Update password
        if re.search(r'(パスワードを更新|update.*password|change.*password|edit.*password)', lower_msg):
            entities['password_id'] = self._extract_id(message)
            entities['site_name'] = self._extract_site_name(message)
            entities['username'] = self._extract_username(message)
            entities['password'] = self._extract_password(message)
            return "update_password", entities

        # Delete password
        if re.search(r'(パスワードを削除|delete.*password|remove.*password)', lower_msg):
            entities['password_id'] = self._extract_id(message)
            return "delete_password", entities

        # Check password strength
        if re.search(r'(パスワード強度|strength|check.*password|how.*strong)', lower_msg):
            entities['password'] = self._extract_password(message)
            return "check_strength", entities

        # Show stats
        if re.search(r'(統計|stats|statistics|summary)', lower_msg):
            return "show_stats", entities

        # Show categories
        if re.search(r'(カテゴリ|categories|folders)', lower_msg):
            return "show_categories", entities

        # Help
        if re.search(r'(ヘルプ|help|使い方)', lower_msg):
            return "help", entities

        return "unknown", entities

    def _extract_length(self, message: str) -> Optional[int]:
        """Extract password length"""
        patterns = [
            r'(\d+)\s*文字',
            r'length[:\s]+(\d+)',
            r'(\d+)\s*chars?',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return int(match.group(1))
        return 16  # Default

    def _extract_flag(self, message: str, keywords: List[str]) -> bool:
        """Extract boolean flag from keywords"""
        lower_msg = message.lower()
        for kw in keywords:
            if kw.lower() in lower_msg:
                return True
        return None  # Use default

    def _extract_site_name(self, message: str) -> Optional[str]:
        """Extract site name from message"""
        patterns = [
            r'サイト[:\s]+([^\s,]+)',
            r'site[:\s]+([^\s,]+)',
            r'([a-z0-9-]+\.[a-z]{2,})',  # Domain pattern
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _extract_username(self, message: str) -> Optional[str]:
        """Extract username from message"""
        patterns = [
            r'ユーザー名[:\s]+([^\s,]+)',
            r'username[:\s]+([^\s,]+)',
            r'user[:\s]+([^\s,]+)',
            r'アカウント[:\s]+([^\s,]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _extract_password(self, message: str) -> Optional[str]:
        """Extract password from message"""
        patterns = [
            r'パスワード[:\s]+([^\s]+)',
            r'password[:\s]+([^\s]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _extract_url(self, message: str) -> Optional[str]:
        """Extract URL from message"""
        patterns = [
            r'url[:\s]+([^\s]+)',
            r'https?://[^\s]+',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _extract_category(self, message: str) -> Optional[str]:
        """Extract category from message"""
        patterns = [
            r'カテゴリ[:\s]+([^\s,]+)',
            r'category[:\s]+([^\s,]+)',
            r'folder[:\s]+([^\s,]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _extract_id(self, message: str) -> Optional[int]:
        """Extract ID from message"""
        patterns = [
            r'ID[:\s]*(\d+)',
            r'no\.?\s*(\d+)',
            r'#(\d+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return int(match.group(1))
        return None

    def _extract_keyword(self, message: str) -> Optional[str]:
        """Extract search keyword"""
        # Remove command keywords
        cleaned = re.sub(r'(パスワード検索|search|find|for|keyword)', '', message, flags=re.IGNORECASE)
        return cleaned.strip() or None

    def _handle_generate_password(self, entities: Dict) -> str:
        """Handle password generation"""
        length = entities.get('length', 16)

        # Use flags or defaults
        uppercase = entities.get('uppercase') if entities.get('uppercase') is not None else True
        lowercase = entities.get('lowercase') if entities.get('lowercase') is not None else True
        digits = entities.get('digits') if entities.get('digits') is not None else True
        symbols = entities.get('symbols') if entities.get('symbols') is not None else True

        password = generate_password(length, uppercase, lowercase, digits, symbols)
        strength = check_password_strength(password)

        return f"🔐 **生成されたパスワード** (長さ: {length}):\n`{password}`\n\n強度: {strength['level']}" + \
               (f"\nアドバイス: {', '.join(strength['feedback'])}" if strength['feedback'] else "")

    def _handle_add_password(self, entities: Dict) -> str:
        """Handle adding password"""
        site_name = entities.get('site_name')
        username = entities.get('username')

        if not site_name:
            return "サイト名を指定してください。例: Gmailのパスワードを保存 ユーザー名:example@gmail.com"

        password = entities.get('password')
        if not password:
            # Auto-generate if not provided
            password = generate_password(16)
            auto_generated = True
        else:
            auto_generated = False

        password_id = add_password(
            site_name=site_name,
            username=username,
            password=password,
            site_url=entities.get('site_url'),
            category=entities.get('category')
        )

        if auto_generated:
            return f"✅ パスワードを保存しました (ID: {password_id})\nサイト: {site_name}\n生成されたパスワード: `{password}`"
        else:
            return f"✅ パスワードを保存しました (ID: {password_id})\nサイト: {site_name}\nユーザー名: {username or 'なし'}"

    def _handle_get_password(self, entities: Dict) -> str:
        """Handle getting password"""
        password_id = entities.get('password_id')
        site_name = entities.get('site_name')

        if password_id:
            result = get_password(password_id)
        elif site_name:
            # Search by site name
            passwords = search_passwords(site_name)
            if not passwords:
                return f"{site_name} に一致するパスワードが見つかりません"
            # Use first match's ID
            result = get_password(passwords[0][0])
        else:
            return "パスワードIDまたはサイト名を指定してください"

        if not result:
            return "パスワードが見つかりません"

        id, site, url, username, password, last_used = result

        response = f"🔓 **{site}**\n"
        response += f"ID: {id}\n"
        if username:
            response += f"ユーザー名: `{username}`\n"
        if url:
            response += f"URL: {url}\n"
        response += f"パスワード: ||`{password}`||\n"
        if last_used:
            response += f"最終使用: {last_used}"

        return response

    def _handle_list_passwords(self, entities: Dict) -> str:
        """Handle listing passwords"""
        category = entities.get('category')
        passwords = list_passwords(limit=50, category=category)

        if not passwords:
            return "保存されているパスワードはありません"

        response = f"📋 **パスワード一覧** ({len(passwords)}件):\n\n"
        for p in passwords:
            id, site, url, username, cat, created, updated = p
            category_text = f" [{cat}]" if cat else ""
            response += f"#{id} {site}{category_text} - {username or 'ユーザー名なし'}\n"

        return response

    def _handle_search_passwords(self, entities: Dict) -> str:
        """Handle searching passwords"""
        keyword = entities.get('keyword')

        if not keyword:
            return "検索キーワードを指定してください。"

        passwords = search_passwords(keyword)

        if not passwords:
            return f"{keyword} に一致するパスワードが見つかりません"

        response = f"🔍 **検索結果** ({len(passwords)}件):\n\n"
        for p in passwords:
            id, site, url, username, cat, created, updated = p
            category_text = f" [{cat}]" if cat else ""
            response += f"#{id} {site}{category_text} - {username or 'ユーザー名なし'}\n"

        return response

    def _handle_update_password(self, entities: Dict) -> str:
        """Handle updating password"""
        password_id = entities.get('password_id')

        if not password_id:
            return "パスワードIDを指定してください。"

        # Get current to update
        update_password(
            password_id=password_id,
            site_name=entities.get('site_name'),
            username=entities.get('username'),
            password=entities.get('password'),
            site_url=entities.get('site_url'),
            category=entities.get('category')
        )

        return f"✅ パスワード {password_id} を更新しました"

    def _handle_delete_password(self, entities: Dict) -> str:
        """Handle deleting password"""
        password_id = entities.get('password_id')

        if not password_id:
            return "パスワードIDを指定してください。"

        delete_password(password_id)
        return f"🗑️ パスワード {password_id} を削除しました"

    def _handle_check_strength(self, entities: Dict) -> str:
        """Handle checking password strength"""
        password = entities.get('password')

        if not password:
            return "パスワードを指定してください。"

        result = check_password_strength(password)

        response = f"🔍 **パスワード強度チェック**\n\n"
        response += f"強度: {result['level']}\n"
        response += f"スコア: {result['score']}/6\n"

        if result['feedback']:
            response += "\nアドバイス:\n"
            for advice in result['feedback']:
                response += f"  • {advice}\n"

        return response

    def _handle_show_stats(self, entities: Dict) -> str:
        """Handle showing statistics"""
        stats = get_stats()

        response = f"📊 **統計情報**\n\n"
        response += f"総パスワード数: {stats['total_passwords']}\n\n"

        if stats['by_category']:
            response += "**カテゴリ別**:\n"
            for cat, count in stats['by_category'].items():
                response += f"  • {cat}: {count}\n"

        if stats['by_tag']:
            response += "\n**タグ別**:\n"
            for tag, count in stats['by_tag'].items():
                response += f"  • #{tag}: {count}\n"

        response += f"\n最近7日間の追加: {stats['recent_additions']}件"

        return response

    def _handle_show_categories(self, entities: Dict) -> str:
        """Handle showing categories"""
        categories = get_categories()

        response = f"📁 **カテゴリ一覧** ({len(categories)}件):\n\n"
        for c in categories:
            id, name, color, created = c
            response += f"• {name}\n"

        return response

    def _handle_help(self) -> str:
        """Handle help command"""
        return """
🔐 **Password Agent ヘルプ**

**パスワード生成:**
• 16文字のパスワードを生成
• Generate password length 20 with symbols

**パスワード保存:**
• Gmailのパスワードを保存 ユーザー名:example@gmail.com パスワード:secure123
• Save password for github.com username: myuser

**パスワード表示:**
• Gmailのパスワードを表示
• Show password ID:5

**一覧・検索:**
• パスワード一覧を表示
• Workカテゴリのパスワード
• 検索: github

**更新・削除:**
• パスワード5を更新 ユーザー名:newuser
• パスワード5を削除

**強度チェック:**
• パスワード強度チェック パスワード:MyP@ssw0rd

**統計:**
• 統計を表示
• カテゴリ一覧

**English support:**
• Generate password
• Add password for gmail.com
• Show all passwords
• Search for github
• Check password strength: MyP@ssw0rd
"""

    def _handle_unknown(self, message: str) -> str:
        """Handle unknown command"""
        return "すみません、コマンドを理解できませんでした。「ヘルプ」と入力すると使い方を表示します"


# Test examples
if __name__ == '__main__':
    agent = PasswordDiscord("test_master_password")

    # Test password generation
    print("--- Password Generation ---")
    print(agent.process_message("16文字のパスワードを生成"))
    print(agent.process_message("Generate password length 20 with symbols"))

    # Test adding password
    print("\n--- Add Password ---")
    print(agent.process_message("Gmailのパスワードを保存 ユーザー名:test@example.com"))

    # Test listing passwords
    print("\n--- List Passwords ---")
    print(agent.process_message("パスワード一覧を表示"))

    # Test strength check
    print("\n--- Strength Check ---")
    print(agent.process_message("パスワード強度チェック パスワード:MyP@ssw0rd"))

    # Test help
    print("\n--- Help ---")
    print(agent.process_message("ヘルプ"))
