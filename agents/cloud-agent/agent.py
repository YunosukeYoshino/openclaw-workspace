"""
Cloud Agent Discord Module

Natural language processing for cloud resource management commands in Japanese and English.
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

        Supported commands / サポートされるコマンド:
        - "service add <name> <provider> <type> [cost]" - Add service / サービス追加
        - "service list [provider] [status]" - List services / サービス一覧
        - "service update <id> <status>" - Update service status / サービスステータス更新
        - "storage add <name> <provider> <type> [size]" - Add storage / ストレージ追加
        - "storage list [provider]" - List storage / ストレージ一覧
        - "storage update <id> <size>" - Update storage usage / 使用量更新
        - "usage log <id> <metric> <value> [unit]" - Log usage / 使用ログ
        - "usage list <id>" - List usage logs / 使用ログ一覧
        - "stats" - Show cloud statistics / クラウド統計表示
        """
        content_lower = content.lower().strip()

        # Service commands / サービスコマンド
        if "service add" in content_lower or "add service" in content_lower:
            return self._add_service(content)
        elif "service list" in content_lower or "list service" in content_lower:
            return self._list_services(content_lower)
        elif "service update" in content_lower or "update service" in content_lower:
            return self._update_service(content)

        # Storage commands / ストレージコマンド
        elif "storage add" in content_lower or "add storage" in content_lower:
            return self._add_storage(content)
        elif "storage list" in content_lower or "list storage" in content_lower:
            return self._list_storage(content_lower)
        elif "storage update" in content_lower or "update storage" in content_lower:
            return self._update_storage(content)

        # Usage commands / 使用コマンド
        elif "usage log" in content_lower:
            return self._log_usage(content)
        elif "usage list" in content_lower:
            return self._list_usage(content)

        # Stats / 統計
        elif "stat" in content_lower or "統計" in content_lower:
            return self._show_stats()

        # Help / ヘルプ
        elif "help" in content_lower or "ヘルプ" in content_lower:
            return self._show_help()

        else:
            return self._show_help()

    def _add_service(self, content: str) -> str:
        """Parse and add a new cloud service / 新しいクラウドサービスを追加"""
        # Extract provider
        providers = ['aws', 'azure', 'gcp', 'digitalocean', 'heroku', 'vercel']
        provider = None
        for p in providers:
            if p.lower() in content.lower():
                provider = p
                break

        if not provider:
            return "❌ Please specify provider (aws/azure/gcp/digitalocean/heroku/vercel)\nプロバイダーを指定してください"

        # Extract service type
        service_types = ['compute', 'database', 'storage', 'network', 'monitoring', 'other']
        service_type = None
        for st in service_types:
            if st in content.lower():
                service_type = st
                break

        if not service_type:
            service_type = 'other'

        # Extract name (before provider and type)
        name_match = re.search(r'(?:service add)\s+"?([^"]+)"?', content, re.IGNORECASE)
        name = name_match.group(1).strip() if name_match else f"Service"

        # Extract cost
        cost_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:usd|\$)?$', content, re.IGNORECASE)
        cost = float(cost_match.group(1)) if cost_match else None

        service_id = self.db.add_service(
            name=name,
            provider=provider,
            service_type=service_type,
            cost_monthly=cost
        )

        cost_str = f"${cost}/month" if cost else "Not specified"
        return f"✅ Service registered / サービスを登録しました (ID: {service_id})\n" \
               f"   Name / 名前: {name}\n" \
               f"   Provider / プロバイダー: {provider}\n" \
               f"   Type / タイプ: {service_type}\n" \
               f"   Cost / コスト: {cost_str}"

    def _list_services(self, content: str) -> str:
        """List services with optional filters / サービス一覧を表示"""
        provider = None
        status = None

        providers = ['aws', 'azure', 'gcp', 'digitalocean', 'heroku', 'vercel']
        for p in providers:
            if p in content:
                provider = p
                break

        if "active" in content:
            status = "active"
        elif "inactive" in content:
            status = "inactive"

        services = self.db.get_services(provider=provider, status=status, limit=20)

        if not services:
            return "📭 No services found / サービスは見つかりませんでした"

        output = f"☁️ **Service List / サービス一覧** (Filter: {provider or 'All / 全て'}/{status or 'All / 全て'})\n\n"
        for s in services:
            status_emoji = '🟢' if s['status'] == 'active' else '⚪'
            cost_str = f"${s['cost_monthly']}" if s['cost_monthly'] else "N/A"

            output += f"**#{s['id']}** {status_emoji} {s['name']}\n"
            output += f"   Provider: {s['provider']} | Type: {s['service_type']} | Cost: {cost_str}/month\n"
            output += f"   Region: {s['region'] or 'N/A'} | Status: {s['status']}\n\n"

        return output

    def _update_service(self, content: str) -> str:
        """Update service status / サービスステータスを更新"""
        id_match = re.search(r'(\d+)', content)
        if not id_match:
            return "❌ Please specify service ID / サービスIDを指定してください (例: service update 123 inactive)"

        service_id = int(id_match.group(1))

        if "active" in content.lower():
            status = "active"
        elif "inactive" in content.lower():
            status = "inactive"
        elif "deprecated" in content.lower():
            status = "deprecated"
        else:
            return "❌ Please specify status / ステータスを指定してください (active/inactive/deprecated)"

        success = self.db.update_service_status(service_id, status)

        if success:
            return f"✅ Service #{service_id} status updated to {status} / サービス #{service_id} のステータスを {status} に更新しました"
        else:
            return f"❌ Service #{service_id} not found / サービス #{service_id} が見つかりません"

    def _add_storage(self, content: str) -> str:
        """Parse and add a new storage resource / 新しいストレージリソースを追加"""
        # Extract provider
        providers = ['aws', 'azure', 'gcp', 'digitalocean', 'heroku', 'vercel']
        provider = None
        for p in providers:
            if p.lower() in content.lower():
                provider = p
                break

        if not provider:
            return "❌ Please specify provider (aws/azure/gcp/digitalocean/heroku/vercel)\nプロバイダーを指定してください"

        # Extract storage type
        storage_types = ['s3', 'blob', 'file', 'database', 'backup']
        storage_type = None
        for st in storage_types:
            if st in content.lower():
                storage_type = st
                break

        if not storage_type:
            storage_type = 'storage'

        # Extract name
        name_match = re.search(r'(?:storage add)\s+"?([^"]+)"?', content, re.IGNORECASE)
        name = name_match.group(1).strip() if name_match else f"Storage"

        # Extract size
        size_match = re.search(r'(\d+)\s*(?:gb|g)?$', content, re.IGNORECASE)
        size = int(size_match.group(1)) if size_match else None

        storage_id = self.db.add_storage(
            name=name,
            provider=provider,
            type=storage_type,
            size_total_gb=size
        )

        size_str = f"{size} GB" if size else "Not specified"
        return f"✅ Storage registered / ストレージを登録しました (ID: {storage_id})\n" \
               f"   Name / 名前: {name}\n" \
               f"   Provider / プロバイダー: {provider}\n" \
               f"   Type / タイプ: {storage_type}\n" \
               f"   Size / 容量: {size_str}"

    def _list_storage(self, content: str) -> str:
        """List storage resources / ストレージ一覧を表示"""
        provider = None

        providers = ['aws', 'azure', 'gcp', 'digitalocean', 'heroku', 'vercel']
        for p in providers:
            if p in content:
                provider = p
                break

        storage = self.db.get_storage(provider=provider, limit=20)

        if not storage:
            return "📭 No storage found / ストレージは見つかりませんでした"

        output = f"💾 **Storage List / ストレージ一覧** (Filter: {provider or 'All / 全て'})\n\n"
        for s in storage:
            usage_pct = (s['size_used_gb'] / s['size_total_gb'] * 100) if s['size_total_gb'] else 0
            status_emoji = '🟢' if s['status'] == 'active' else '⚪'

            output += f"**#{s['id']}** {status_emoji} {s['name']}\n"
            output += f"   Provider: {s['provider']} | Type: {s['type']}\n"
            output += f"   Usage: {s['size_used_gb']} GB / {s['size_total_gb'] or 'N/A'} GB ({usage_pct:.1f}%)\n"
            output += f"   Region: {s['region'] or 'N/A'}\n\n"

        return output

    def _update_storage(self, content: str) -> str:
        """Update storage usage / ストレージ使用量を更新"""
        id_match = re.search(r'(\d+)', content)
        if not id_match:
            return "❌ Please specify storage ID / ストレージIDを指定してください (例: storage update 123 450)"

        storage_id = int(id_match.group(1))

        # Extract size
        size_match = re.search(r'(\d+)', content)
        if not size_match or len([m for m in re.finditer(r'(\d+)', content)]) < 2:
            return "❌ Please specify new size / 新しいサイズを指定してください (例: storage update 123 450)"

        sizes = [int(m.group(1)) for m in re.finditer(r'(\d+)', content)]
        size_used = sizes[1] if len(sizes) > 1 else None

        if size_used is None:
            return "❌ Please specify new size / 新しいサイズを指定してください"

        success = self.db.update_storage_usage(storage_id, size_used)

        if success:
            return f"✅ Storage #{storage_id} usage updated to {size_used} GB / ストレージ #{storage_id} の使用量を {size_used} GB に更新しました"
        else:
            return f"❌ Storage #{storage_id} not found / ストレージ #{storage_id} が見つかりません"

    def _log_usage(self, content: str) -> str:
        """Log resource usage / リソース使用量をログ"""
        id_match = re.search(r'usage log\s+(\d+)', content, re.IGNORECASE)
        if not id_match:
            return "❌ Please specify resource ID / リソースIDを指定してください (例: usage log 123 requests 100000)"

        resource_id = int(id_match.group(1))

        # Extract metric
        metric_match = re.search(rf'usage log\s+{resource_id}\s+(\w+)', content, re.IGNORECASE)
        metric = metric_match.group(1).lower() if metric_match else 'unknown'

        # Extract value
        value_match = re.search(rf'usage log\s+{resource_id}\s+{metric}\s+(\d+(?:\.\d+)?)', content, re.IGNORECASE)
        if not value_match:
            return "❌ Please specify metric value / メトリクス値を指定してください (例: usage log 123 requests 100000)"

        value = float(value_match.group(1))

        # Extract unit
        unit_match = re.search(rf'usage log\s+{resource_id}\s+{metric}\s+{value}\s*(\w+)', content, re.IGNORECASE)
        unit = unit_match.group(1) if unit_match else None

        log_id = self.db.add_usage_log(resource_id, metric, value, unit)

        unit_str = f" {unit}" if unit else ""
        return f"✅ Usage logged / 使用ログを記録しました (ID: {log_id})\n" \
               f"   Resource / リソース: #{resource_id}\n" \
               f"   Metric / メトリクス: {metric}\n" \
               f"   Value / 値: {value}{unit_str}"

    def _list_usage(self, content: str) -> str:
        """List usage logs / 使用ログ一覧を表示"""
        id_match = re.search(r'(\d+)', content)
        if not id_match:
            return "❌ Please specify resource ID / リソースIDを指定してください"

        resource_id = int(id_match.group(1))
        logs = self.db.get_usage_logs(resource_id, limit=20)

        if not logs:
            return "📭 No usage logs found / 使用ログは見つかりませんでした"

        output = f"📊 **Usage Logs / 使用ログ** (Resource: #{resource_id})\n\n"
        for log in logs:
            unit_str = f" {log['unit']}" if log['unit'] else ""
            output += f"   {log['timestamp']} | {log['metric']}: {log['value']}{unit_str}\n"

        return output

    def _show_stats(self) -> str:
        """Show cloud statistics / クラウド統計を表示"""
        stats = self.db.get_stats()

        output = "📊 **Cloud Statistics / クラウド統計**\n\n"

        # Active services by provider
        by_provider = stats.get('services_by_provider', {})
        output += f"☁️ **Active Services / アクティブサービス**: {sum(by_provider.values())}\n"
        for provider, count in by_provider.items():
            output += f"   {provider.upper()}: {count}\n"
        output += "\n"

        # Total monthly cost
        total_cost = stats.get('total_monthly_cost', 0)
        output += f"💰 **Total Monthly Cost / 月額コスト合計**: ${total_cost:.2f}\n\n"

        # Storage usage
        storage = stats.get('storage_summary', {})
        output += f"💾 **Storage Usage / ストレージ使用状況**\n"
        output += f"   Total / 合計: {storage.get('total_used', 0)} GB\n"
        output += f"   Capacity / 容量: {storage.get('total_capacity', 0)} GB\n"
        if storage.get('total_capacity', 0) > 0:
            pct = (storage.get('total_used', 0) / storage.get('total_capacity', 1)) * 100
            output += f"   Usage / 使用率: {pct:.1f}%\n"

        return output

    def _show_help(self) -> str:
        """Show help message / ヘルプメッセージを表示"""
        return """
☁️ **Cloud Agent Help / クラウドエージェント ヘルプ**

**Service Management / サービス管理**
- `service add <name> <provider> <type> [cost]` - Add service / サービス追加
- `service list [provider] [status]` - List services / サービス一覧
- `service update <id> <status>` - Update status / ステータス更新

**Storage Management / ストレージ管理**
- `storage add <name> <provider> <type> [size]` - Add storage / ストレージ追加
- `storage list [provider]` - List storage / ストレージ一覧
- `storage update <id> <size>` - Update usage / 使用量更新

**Usage Logging / 使用ログ**
- `usage log <id> <metric> <value> [unit]` - Log usage / 使用ログ
- `usage list <id>` - List logs / ログ一覧

**Statistics / 統計**
- `stats` - Show statistics / 統計を表示

**Providers / プロバイダー**: aws, azure, gcp, digitalocean, heroku, vercel
**Service Types / サービスタイプ**: compute, database, storage, network, monitoring, other
**Storage Types / ストレージタイプ**: s3, blob, file, database, backup
"""
