"""
API Agent Discord Module
Natural language processing for API key management and request logging
"""

import re
from typing import Optional, Dict, List
from db import APIDB


class APIDiscord:
    """Discord interface for API agent with NLP"""

    def __init__(self, db_path: str = "api.db"):
        self.db = APIDB(db_path)

    def process_message(self, message: str) -> str:
        """Process user message and return response"""
        message = message.strip()
        intent, entities = self._parse_intent(message)

        if intent == "add_key":
            return self._handle_add_key(entities)
        elif intent == "list_keys":
            return self._handle_list_keys(entities)
        elif intent == "get_key":
            return self._handle_get_key(entities)
        elif intent == "update_key":
            return self._handle_update_key(entities)
        elif intent == "delete_key":
            return self._handle_delete_key(entities)
        elif intent == "toggle_key":
            return self._handle_toggle_key(entities)
        elif intent == "log_request":
            return self._handle_log_request(entities)
        elif intent == "list_requests":
            return self._handle_list_requests(entities)
        elif intent == "get_stats":
            return self._handle_get_stats(entities)
        elif intent == "add_template":
            return self._handle_add_template(entities)
        elif intent == "list_templates":
            return self._handle_list_templates(entities)
        elif intent == "show_logs":
            return self._handle_show_logs(entities)
        elif intent == "help":
            return self._handle_help()
        else:
            return self._handle_unknown(message)

    def _parse_intent(self, message: str) -> tuple:
        """Parse intent and entities from message"""
        entities = {}
        lower_msg = message.lower()

        # Add API key
        if re.search(r'(api.*key.*add|add.*api.*key|apiキー追加|apiキーを登録|apiキーを追加|register.*api.*key)', lower_msg):
            entities['name'] = self._extract_name(message)
            entities['service'] = self._extract_service(message)
            entities['key_value'] = self._extract_key_value(message)
            entities['key_type'] = self._extract_key_type(message)
            entities['base_url'] = self._extract_url(message)
            entities['description'] = self._extract_description(message)
            return "add_key", entities

        # List API keys
        if re.search(r'(api.*key.*list|list.*api.*key|apiキー一覧|apiキー表示|show.*api.*key)', lower_msg):
            entities['service'] = self._extract_service(message)
            entities['is_active'] = self._extract_active_status(message)
            return "list_keys", entities

        # Get API key
        if re.search(r'(api.*key.*get|get.*api.*key|apiキー取得|apiキーを見る|show.*key|retrieve.*key)', lower_msg):
            entities['key_id'] = self._extract_id(message)
            entities['name'] = self._extract_name(message)
            return "get_key", entities

        # Update API key
        if re.search(r'(api.*key.*update|update.*api.*key|apiキー更新|apiキーを変更|edit.*key|change.*key)', lower_msg):
            entities['key_id'] = self._extract_id(message)
            entities['key_value'] = self._extract_key_value(message)
            entities['base_url'] = self._extract_url(message)
            entities['description'] = self._extract_description(message)
            return "update_key", entities

        # Delete API key
        if re.search(r'(api.*key.*delete|delete.*api.*key|apiキー削除|apiキーを削除|remove.*key)', lower_msg):
            entities['key_id'] = self._extract_id(message)
            return "delete_key", entities

        # Toggle key active
        if re.search(r'(api.*key.*toggle|toggle.*api.*key|apiキー有効|apiキー無効|activate|deactivate)', lower_msg):
            entities['key_id'] = self._extract_id(message)
            return "toggle_key", entities

        # Log request
        if re.search(r'(request.*log|log.*request|リクエスト記録|リクエストログ|api.*request)', lower_msg):
            entities['service'] = self._extract_service(message)
            entities['method'] = self._extract_method(message)
            entities['endpoint'] = self._extract_endpoint(message)
            entities['response_status'] = self._extract_status_code(message)
            entities['success'] = not re.search(r'(失敗|エラー|error|failed)', lower_msg)
            return "log_request", entities

        # List requests
        if re.search(r'(request.*list|list.*request|リクエスト一覧|リクエスト表示|show.*request)', lower_msg):
            entities['service'] = self._extract_service(message)
            return "list_requests", entities

        # Get stats
        if re.search(r'(stats|statistics|統計|サマリー|summary)', lower_msg):
            entities['service'] = self._extract_service(message)
            return "get_stats", entities

        # Add template
        if re.search(r'(template.*add|add.*template|テンプレート追加|テンプレートを作成|create.*template)', lower_msg):
            entities['name'] = self._extract_name(message)
            entities['service'] = self._extract_service(message)
            entities['method'] = self._extract_method(message)
            entities['endpoint'] = self._extract_endpoint(message)
            entities['description'] = self._extract_description(message)
            return "add_template", entities

        # List templates
        if re.search(r'(template.*list|list.*template|テンプレート一覧|テンプレート表示|show.*template)', lower_msg):
            entities['service'] = self._extract_service(message)
            return "list_templates", entities

        # Show logs
        if re.search(r'(log.*show|show.*log|ログ表示|ログ一覧|view.*log)', lower_msg):
            entities['log_type'] = self._extract_log_type(message)
            entities['severity'] = self._extract_severity(message)
            return "show_logs", entities

        # Help
        if re.search(r'(ヘルプ|help|使い方)', lower_msg):
            return "help", entities

        return "unknown", entities

    def _extract_name(self, message: str) -> Optional[str]:
        """Extract name from message"""
        patterns = [
            r'名前[:\s]+([^\s,]+)',
            r'name[:\s]+([^\s,]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _extract_service(self, message: str) -> Optional[str]:
        """Extract service name from message"""
        patterns = [
            r'サービス[:\s]+([^\s,]+)',
            r'service[:\s]+([^\s,]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _extract_key_value(self, message: str) -> Optional[str]:
        """Extract API key value"""
        patterns = [
            r'キー[:\s]+([^\s]+)',
            r'key[:\s]+([^\s]+)',
            r'key[:\s]*=[:\s]*([^\s]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _extract_key_type(self, message: str) -> str:
        """Extract key type"""
        type_map = {
            'api_key': 'api_key',
            'bearer': 'bearer',
            'basic': 'basic',
            'oauth': 'oauth',
        }
        lower_msg = message.lower()
        for key in type_map:
            if key in lower_msg:
                return type_map[key]
        return 'api_key'

    def _extract_url(self, message: str) -> Optional[str]:
        """Extract URL"""
        patterns = [
            r'url[:\s]+([^\s]+)',
            r'base_url[:\s]+([^\s]+)',
            r'https?://[^\s]+',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _extract_description(self, message: str) -> Optional[str]:
        """Extract description"""
        patterns = [
            r'説明[:\s]+(.+?)(?:\n|$)',
            r'description[:\s]+(.+?)(?:\n|$)',
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
            r'id[:\s]*(\d+)',
            r'#(\d+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return int(match.group(1))
        return None

    def _extract_active_status(self, message: str) -> Optional[bool]:
        """Extract active status filter"""
        if re.search(r'(有効|active|enabled)', message.lower()):
            return True
        if re.search(r'(無効|inactive|disabled)', message.lower()):
            return False
        return None

    def _extract_method(self, message: str) -> str:
        """Extract HTTP method"""
        methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
        upper_msg = message.upper()
        for method in methods:
            if method in upper_msg:
                return method
        return 'GET'

    def _extract_endpoint(self, message: str) -> Optional[str]:
        """Extract endpoint path"""
        patterns = [
            r'/[^\s]+',
            r'endpoint[:\s]+([^\s]+)',
            r'path[:\s]+([^\s]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return '/'

    def _extract_status_code(self, message: str) -> Optional[int]:
        """Extract HTTP status code"""
        match = re.search(r'(\d{3})', message)
        return int(match.group(1)) if match else None

    def _extract_log_type(self, message: str) -> Optional[str]:
        """Extract log type"""
        patterns = [
            r'タイプ[:\s]+([^\s,]+)',
            r'type[:\s]+([^\s,]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _extract_severity(self, message: str) -> Optional[str]:
        """Extract severity level"""
        severity_map = {
            'info': 'info',
            'warning': 'warning',
            'error': 'error',
            'debug': 'debug',
            'critical': 'critical',
        }
        lower_msg = message.lower()
        for key in severity_map:
            if key in lower_msg:
                return severity_map[key]
        return None

    # Handlers

    def _handle_add_key(self, entities: Dict) -> str:
        """Handle adding API key"""
        name = entities.get('name')
        service = entities.get('service')

        if not name or not service:
            return "名前とサービスを指定してください。例: APIキー追加 名前:GitHub サービス:github.com"

        key_id = self.db.add_api_key(
            name=name,
            service=service,
            key_value=entities.get('key_value') or 'placeholder_key',
            key_type=entities.get('key_type', 'api_key'),
            base_url=entities.get('base_url'),
            description=entities.get('description')
        )

        return f"✅ APIキーを追加しました (ID: {key_id})\n名前: {name}\nサービス: {service}"

    def _handle_list_keys(self, entities: Dict) -> str:
        """Handle listing API keys"""
        keys = self.db.get_api_keys(
            service=entities.get('service'),
            is_active=entities.get('is_active')
        )

        if not keys:
            return "APIキーが見つかりません"

        response = f"🔑 **APIキー一覧** ({len(keys)}件):\n\n"
        for k in keys:
            status = "🟢 有効" if k['is_active'] == 1 else "🔴 無効"
            response += f"#{k['id']} {k['name']} ({k['service']}) - {status}\n"

        return response

    def _handle_get_key(self, entities: Dict) -> str:
        """Handle getting API key"""
        key_id = entities.get('key_id')

        if not key_id:
            return "キーIDを指定してください。"

        key = self.db.get_api_key(key_id)
        if not key:
            return f"キーID {key_id} が見つかりません"

        response = f"🔑 **APIキー詳細**\n\n"
        response += f"ID: {key['id']}\n"
        response += f"名前: {key['name']}\n"
        response += f"サービス: {key['service']}\n"
        response += f"タイプ: {key['key_type']}\n"
        if key['base_url']:
            response += f"URL: {key['base_url']}\n"
        if key['description']:
            response += f"説明: {key['description']}\n"
        response += f"キー値: `||{key['key_value']}||`\n"
        response += f"状態: {'有効' if key['is_active'] == 1 else '無効'}"

        return response

    def _handle_update_key(self, entities: Dict) -> str:
        """Handle updating API key"""
        key_id = entities.get('key_id')

        if not key_id:
            return "キーIDを指定してください。"

        success = self.db.update_api_key(
            key_id=key_id,
            key_value=entities.get('key_value'),
            base_url=entities.get('base_url'),
            description=entities.get('description')
        )

        if success:
            return f"✅ APIキー {key_id} を更新しました"
        else:
            return "更新に失敗しました"

    def _handle_delete_key(self, entities: Dict) -> str:
        """Handle deleting API key"""
        key_id = entities.get('key_id')

        if not key_id:
            return "キーIDを指定してください。"

        self.db.delete_api_key(key_id)
        return f"🗑️ APIキー {key_id} を削除しました"

    def _handle_toggle_key(self, entities: Dict) -> str:
        """Handle toggling API key active status"""
        key_id = entities.get('key_id')

        if not key_id:
            return "キーIDを指定してください。"

        is_active = self.db.toggle_key_active(key_id)
        status = "有効" if is_active else "無効"
        return f"🔘 APIキー {key_id} を「{status}」にしました"

    def _handle_log_request(self, entities: Dict) -> str:
        """Handle logging API request"""
        service = entities.get('service') or "unknown"
        method = entities.get('method', 'GET')
        endpoint = entities.get('endpoint', '/')

        request_id = self.db.log_request(
            service=service,
            method=method,
            endpoint=endpoint,
            response_status=entities.get('response_status'),
            success=entities.get('success', True)
        )

        return f"📝 リクエストを記録しました (ID: {request_id})\n{method} {service}{endpoint}"

    def _handle_list_requests(self, entities: Dict) -> str:
        """Handle listing API requests"""
        requests = self.db.get_requests(service=entities.get('service'), limit=20)

        if not requests:
            return "リクエスト履歴が見つかりません"

        response = f"📊 **リクエスト履歴** ({len(requests)}件):\n\n"
        for r in requests:
            status_icon = "✅" if r['success'] == 1 else "❌"
            response += f"{status_icon} {r['method']} {r['service']}{r['endpoint']} - {r['response_status'] or 'N/A'} ({r['timestamp']})\n"

        return response

    def _handle_get_stats(self, entities: Dict) -> str:
        """Handle getting statistics"""
        stats = self.db.get_request_stats(service=entities.get('service'))

        if not stats:
            return "統計データが見つかりません"

        total = stats.get('total_requests', 0)
        success = stats.get('success_count', 0)
        failure = stats.get('failure_count', 0)
        avg_dur = stats.get('avg_duration')

        response = f"📈 **統計情報**\n\n"
        response += f"総リクエスト: {total}件\n"
        response += f"成功: {success}件\n"
        response += f"失敗: {failure}件\n"
        if avg_dur:
            response += f"平均応答時間: {avg_dur:.0f}ms\n"
        response += f"成功率: {(success/total*100):.1f}%" if total > 0 else "成功率: N/A"

        return response

    def _handle_add_template(self, entities: Dict) -> str:
        """Handle adding API template"""
        name = entities.get('name')
        service = entities.get('service')

        if not name or not service:
            return "名前とサービスを指定してください。"

        template_id = self.db.add_template(
            name=name,
            service=service,
            method=entities.get('method', 'GET'),
            endpoint=entities.get('endpoint', '/'),
            description=entities.get('description')
        )

        return f"📋 テンプレートを追加しました (ID: {template_id})\n名前: {name}\nサービス: {service}"

    def _handle_list_templates(self, entities: Dict) -> str:
        """Handle listing templates"""
        templates = self.db.get_templates(service=entities.get('service'))

        if not templates:
            return "テンプレートが見つかりません"

        response = f"📋 **テンプレート一覧** ({len(templates)}件):\n\n"
        for t in templates:
            response += f"#{t['id']} {t['name']} - {t['method']} {t['service']}{t['endpoint']}\n"

        return response

    def _handle_show_logs(self, entities: Dict) -> str:
        """Handle showing logs"""
        logs = self.db.get_logs(
            log_type=entities.get('log_type'),
            severity=entities.get('severity'),
            limit=20
        )

        if not logs:
            return "ログが見つかりません"

        response = f"📜 **ログ** ({len(logs)}件):\n\n"
        severity_icons = {'info': 'ℹ️', 'warning': '⚠️', 'error': '❌', 'debug': '🔍', 'critical': '💀'}
        for log in logs:
            icon = severity_icons.get(log['severity'], '📝')
            response += f"{icon} [{log['log_type']}] {log['message']} ({log['timestamp']})\n"

        return response

    def _handle_help(self) -> str:
        """Handle help command"""
        return """
🔑 **API Agent ヘルプ**

**APIキー管理:**
• APIキー追加 名前:GitHub サービス:github.com キー:sk_12345
• APIキー一覧
• APIキーを見る ID:1
• APIキーを更新 ID:1 キー:new_key
• APIキーを削除 ID:1

**リクエスト管理:**
• リクエストを記録 サービス:github.com GET /user
• リクエスト一覧
• 統計を表示

**テンプレート:**
• テンプレート追加 名前:User Request サービス:github.com GET /user
• テンプレート一覧

**ログ:**
• ログ表示
• エラーログを表示

**English support:**
• Add API key name: GitHub service: github.com
• List API keys
• Show API key ID:1
• Log request service: github.com GET /user
• Show request history
• Show statistics
"""

    def _handle_unknown(self, message: str) -> str:
        """Handle unknown command"""
        return "すみません、コマンドを理解できませんでした。「ヘルプ」と入力すると使い方を表示します"


# Test examples
if __name__ == '__main__':
    agent = APIDiscord(":memory:")

    # Test adding API key
    print("--- Add API Key ---")
    print(agent.process_message("APIキー追加 名前:GitHub サービス:github.com"))

    # Test listing keys
    print("\n--- List Keys ---")
    print(agent.process_message("APIキー一覧"))

    # Test logging request
    print("\n--- Log Request ---")
    print(agent.process_message("リクエストを記録 サービス:github.com GET /user"))

    # Test getting stats
    print("\n--- Get Stats ---")
    print(agent.process_message("統計を表示"))

    # Test help
    print("\n--- Help ---")
    print(agent.process_message("ヘルプ"))
