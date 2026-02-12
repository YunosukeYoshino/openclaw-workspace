"""
Cloud Agent Discord Module

Natural language processing for cloud management commands.
"""

import re
from typing import Dict, Optional, List
from .db import CloudDB

class CloudDiscordHandler:
    """Handle Discord messages for Cloud Agent"""

    def __init__(self, db: CloudDB):
        self.db = db

    def process_message(self, content: str) -> str:
        """
        Process a Discord message and execute appropriate action.

        Supported commands:
        - "service add <name> <provider> <type>" - Add service
        - "service list [provider] [status]" - List services
        - "service update <id> <status>" - Update service status
        - "storage add <name> <provider> <type> [size]" - Add storage
        - "storage list [provider]" - List storage
        - "storage update <id> <size_gb>" - Update storage usage
        - "usage log <resource_id> <metric> <value>" - Log usage
        - "stats" - Show cloud statistics
        """
        content_lower = content.lower().strip()

        # Service commands
        if "service add" in content_lower:
            return self._add_service(content)
        elif "service list" in content_lower or "list service" in content_lower:
            return self._list_services(content_lower)
        elif "service update" in content_lower:
            return self._update_service(content)

        # Storage commands
        elif "storage add" in content_lower:
            return self._add_storage(content)
        elif "storage list" in content_lower or "list storage" in content_lower:
            return self._list_storage(content_lower)
        elif "storage update" in content_lower:
            return self._update_storage(content)

        # Usage commands
        elif "usage log" in content_lower or "log usage" in content_lower:
            return self._log_usage(content)
        elif "usage list" in content_lower:
            return self._list_usage_logs(content)

        # Stats
        elif "stat" in content_lower:
            return self._show_stats()

        # Help
        elif "help" in content_lower:
            return self._show_help()

        else:
            return self._show_help()

    def _add_service(self, content: str) -> str:
        """Parse and add a new cloud service"""
        # Extract provider
        provider = None
        for prov in ['aws', 'azure', 'gcp', 'google cloud', 'digitalocean', 'heroku', 'vercel']:
            if prov.lower() in content.lower():
                provider = prov
                break

        if not provider:
            return "❌ プロバイダーを指定してください (aws/azure/gcp/digitalocean/heroku/vercel)"

        # Extract type
        type_match = re.search(rf'{provider}\s+(\w+)', content, re.IGNORECASE)
        service_type = type_match.group(1).lower() if type_match else 'unknown'

        # Extract name (before provider)
        name_match = re.search(r'(?:service add)\s+(.+?)\s+{}'.format(re.escape(provider)), content, re.IGNORECASE)
        name = name_match.group(1).strip() if name_match else f"{provider} service"

        # Extract cost if present
        cost_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:dollars?|usd|\$)', content, re.IGNORECASE)
        cost = float(cost_match.group(1)) if cost_match else 0

        service_id = self.db.add_service(
            name=name,
            provider=provider.lower(),
            service_type=service_type,
            cost_monthly=cost
        )

        return f"✅ サービスを登録しました (ID: {service_id})\n" \
               f"   名称: {name}\n" \
               f"   プロバイダー: {provider}\n" \
               f"   タイプ: {service_type}\n" \
               f"   月額コスト: ${cost}"

    def _list_services(self, content: str) -> str:
        """List cloud services with optional filters"""
        provider = None
        status = None

        # Check for provider
        for prov in ['aws', 'azure', 'gcp', 'google cloud']:
            if prov in content.lower():
                provider = prov
                break

        if "active" in content:
            status = "active"
        elif "inactive" in content:
            status = "inactive"

        services = self.db.get_services(provider=provider, status=status)

        if not services:
            return "📭 サービスは見つかりませんでした"

        output = f"☁️ **クラウドサービス一覧** (フィルター: {provider or '全て'}/{status or '全て'})\n\n"
        provider_emojis = {
            'aws': '🟠',
            'azure': '🔵',
            'gcp': '🟢',
            'google cloud': '🟢',
            'digitalocean': '🔷',
            'heroku': '🟣',
            'vercel': '⬛'
        }

        total_cost = 0
        for s in services:
            emoji = provider_emojis.get(s['provider'], '☁️')
            status_emoji = '🟢' if s['status'] == 'active' else '🔴'

            output += f"{emoji} **#{s['id']}** {status_emoji} {s['name']}\n"
            output += f"   プロバイダー: {s['provider']} | タイプ: {s['service_type']}\n"
            output += f"   ステータス: {s['status']} | 月額: ${s['cost_monthly']}\n"
            if s['region']:
                output += f"   リージョン: {s['region']}\n"
            output += "\n"

            if s['status'] == 'active':
                total_cost += s['cost_monthly']

        output += f"💰 **アクティブサービス合計コスト**: ${total_cost}/月"

        return output

    def _update_service(self, content: str) -> str:
        """Update service status or cost"""
        id_match = re.search(r'(\d+)', content)
        if not id_match:
            return "❌ サービスIDを指定してください (例: service update 123 inactive)"

        service_id = int(id_match.group(1))

        # Check if it's a status update or cost update
        if "active" in content.lower() or "inactive" in content.lower():
            status = "active" if "active" in content.lower() else "inactive"
            success = self.db.update_service_status(service_id, status)
            if success:
                return f"✅ サービス #{service_id} のステータスを {status} に更新しました"
            else:
                return f"❌ サービス #{service_id} が見つかりません"

        elif "$" in content or "cost" in content.lower():
            cost_match = re.search(r'(\d+(?:\.\d+)?)', content)
            if cost_match:
                cost = float(cost_match.group(1))
                success = self.db.update_service_cost(service_id, cost)
                if success:
                    return f"✅ サービス #{service_id} の月額コストを ${cost} に更新しました"
                else:
                    return f"❌ サービス #{service_id} が見つかりません"

        return "❌ ステータス (active/inactive) またはコストを指定してください"

    def _add_storage(self, content: str) -> str:
        """Parse and add a new storage resource"""
        # Extract provider
        provider = None
        for prov in ['aws', 'azure', 'gcp', 'google cloud']:
            if prov.lower() in content.lower():
                provider = prov
                break

        if not provider:
            return "❌ プロバイダーを指定してください (aws/azure/gcp)"

        # Extract type
        type_match = re.search(rf'{provider}\s+(\w+)', content, re.IGNORECASE)
        storage_type = type_match.group(1).lower() if type_match else 's3'

        # Extract name
        name_match = re.search(r'(?:storage add)\s+(.+?)\s+{}'.format(re.escape(provider)), content, re.IGNORECASE)
        name = name_match.group(1).strip() if name_match else f"{provider} storage"

        # Extract sizes
        total_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:gb|gigabyte)', content, re.IGNORECASE)
        size_total = float(total_match.group(1)) if total_match else 0

        storage_id = self.db.add_storage(
            name=name,
            provider=provider.lower(),
            storage_type=storage_type,
            size_total_gb=size_total
        )

        return f"✅ ストレージを登録しました (ID: {storage_id})\n" \
               f"   名称: {name}\n" \
               f"   プロバイダー: {provider}\n" \
               f"   タイプ: {storage_type}\n" \
               f"   容量: {size_total} GB"

    def _list_storage(self, content: str) -> str:
        """List storage resources with optional filters"""
        provider = None

        for prov in ['aws', 'azure', 'gcp']:
            if prov in content.lower():
                provider = prov
                break

        storage = self.db.get_storage(provider=provider)

        if not storage:
            return "📭 ストレージは見つかりませんでした"

        output = f"💾 **ストレージ一覧** (フィルター: {provider or '全て'})\n\n"
        provider_emojis = {
            'aws': '🟠',
            'azure': '🔵',
            'gcp': '🟢'
        }
        type_emojis = {
            's3': '🗃️',
            'blob': '📦',
            'file': '📁',
            'database': '🗄️',
            'backup': '💿'
        }

        total_used = 0
        total_capacity = 0

        for s in storage:
            prov_emoji = provider_emojis.get(s['provider'], '☁️')
            type_emoji = type_emojis.get(s['type'], '💾')
            status_emoji = '🟢' if s['status'] == 'active' else '🔴'

            utilization = round((s['size_used_gb'] / s['size_total_gb'] * 100), 1) if s['size_total_gb'] > 0 else 0

            output += f"{prov_emoji} **#{s['id']}** {status_emoji} {s['name']}\n"
            output += f"   プロバイダー: {s['provider']} | {type_emoji} タイプ: {s['type']}\n"
            output += f"   使用量: {s['size_used_gb']} GB / {s['size_total_gb']} GB ({utilization}%)\n"
            if s['region']:
                output += f"   リージョン: {s['region']}\n"
            output += "\n"

            if s['status'] == 'active':
                total_used += s['size_used_gb']
                total_capacity += s['size_total_gb']

        total_util = round((total_used / total_capacity * 100), 1) if total_capacity > 0 else 0
        output += f"📊 **合計**: {total_used} GB / {total_capacity} GB ({total_util}%)"

        return output

    def _update_storage(self, content: str) -> str:
        """Update storage usage"""
        id_match = re.search(r'(\d+)', content)
        if not id_match:
            return "❌ ストレージIDを指定してください (例: storage update 123 50)"

        storage_id = int(id_match.group(1))

        size_match = re.search(r'(\d+(?:\.\d+)?)', content)
        if not size_match:
            return "❌ 使用量を指定してください (例: storage update 123 50)"

        size_used = float(size_match.group(1))
        success = self.db.update_storage_usage(storage_id, size_used)

        if success:
            return f"✅ ストレージ #{storage_id} の使用量を {size_used} GB に更新しました"
        else:
            return f"❌ ストレージ #{storage_id} が見つかりません"

    def _log_usage(self, content: str) -> str:
        """Log usage metrics"""
        id_match = re.search(r'(\d+)', content)
        if not id_match:
            return "❌ リソースIDを指定してください (例: usage log 123 requests 1000)"

        resource_id = int(id_match.group(1))

        # Extract metric and value
        metric_match = re.search(r'(?:usage log)\s+\d+\s+(\w+)\s+(\d+(?:\.\d+)?)', content, re.IGNORECASE)
        if not metric_match:
            return "❌ メトリクスと値を指定してください (例: usage log 123 requests 1000)"

        metric = metric_match.group(1)
        value = float(metric_match.group(2))

        # Determine resource type (default to service)
        resource_type = 'storage' if "storage" in content.lower() else 'service'

        log_id = self.db.log_usage(
            resource_id=resource_id,
            resource_type=resource_type,
            metric=metric,
            value=value
        )

        return f"✅ 使用ログを記録しました (ID: {log_id})\n" \
               f"   リソース: #{resource_id} ({resource_type})\n" \
               f"   メトリクス: {metric} = {value}"

    def _list_usage_logs(self, content: str) -> str:
        """List usage logs"""
        id_match = re.search(r'(\d+)', content)
        resource_id = int(id_match.group(1)) if id_match else None

        logs = self.db.get_usage_logs(resource_id=resource_id, limit=10)

        if not logs:
            return "📭 使用ログは見つかりませんでした"

        output = f"📊 **使用ログ** (リソース: {resource_id or '全て'})\n\n"
        for log in logs:
            output += f"📝 #{log['id']}\n"
            output += f"   リソース: #{log['resource_id']} ({log['resource_type']})\n"
            output += f"   メトリクス: {log['metric']} = {log['value']} {log['unit'] or ''}\n"
            output += f"   時刻: {log['timestamp']}\n"
            if log['notes']:
                output += f"   備考: {log['notes']}\n"
            output += "\n"

        return output

    def _show_stats(self) -> str:
        """Show cloud statistics"""
        stats = self.db.get_stats()

        output = "📊 **クラウド統計**\n\n"

        # Services by provider
        output += "☁️ **サービス (プロバイダー別)**\n"
        services_by_provider = stats.get('services_by_provider', {})
        for provider, count in services_by_provider.items():
            emoji = {'aws': '🟠', 'azure': '🔵', 'gcp': '🟢'}.get(provider, '☁️')
            output += f"   {emoji} {provider}: {count}\n"
        output += "\n"

        # Cost
        total_cost = stats.get('total_monthly_cost', 0)
        output += f"💰 **月額コスト**: ${total_cost}\n\n"

        # Storage
        output += "💾 **ストレージ**\n"
        storage_by_provider = stats.get('storage_by_provider', {})
        for provider, count in storage_by_provider.items():
            emoji = {'aws': '🟠', 'azure': '🔵', 'gcp': '🟢'}.get(provider, '☁️')
            output += f"   {emoji} {provider}: {count}\n"

        used_gb = stats.get('storage_used_gb', 0)
        total_gb = stats.get('storage_total_gb', 0)
        utilization = stats.get('storage_utilization', 0)

        output += f"\n   使用量: {used_gb} GB / {total_gb} GB ({utilization}%)\n"

        # Alerts
        if utilization > 80:
            output += f"\n⚠️ **警告**: ストレージ使用率が {utilization}% です！\n"
        if total_cost > 1000:
            output += f"\n💸 **注意**: 月額コストが ${total_cost} です\n"

        return output

    def _show_help(self) -> str:
        """Show help message"""
        return """
☁️ **Cloud Agent ヘルプ**

**サービス管理**
- `service add <名称> <プロバイダー> <タイプ> [コスト]` - サービス追加
- `service list [プロバイダー] [status]` - サービス一覧
- `service update <ID> <status>` - ステータス更新

**ストレージ管理**
- `storage add <名称> <プロバイダー> <タイプ> [容量GB]` - ストレージ追加
- `storage list [プロバイダー]` - ストレージ一覧
- `storage update <ID> <使用量GB>` - 使用量更新

**使用ログ**
- `usage log <ID> <メトリクス> <値>` - 使用量を記録
- `usage list [ID]` - 使用ログ一覧

**統計**
- `stats` - クラウド統計を表示

**プロバイダー**: aws, azure, gcp, digitalocean, heroku, vercel
**タイプ**: compute, database, storage, network, monitoring, etc.
"""
