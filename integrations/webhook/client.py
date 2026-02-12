#!/usr/bin/env python3
"""
Webhook Integration
汎用的なWebhookシステムを実装して、外部サービスとの連携を行う

Usage:
    from integrations.webhook import WebhookManager

    manager = WebhookManager()
    manager.register_webhook("github", "https://example.com/webhook")
    manager.send_webhook("github", data={"event": "push"})
"""

import os
import json
import logging
from typing import List, Dict, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

# Webhook送信に必要なライブラリチェック
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Webhook:
    """Webhookデータクラス"""
    id: str
    name: str
    url: str
    method: str = "POST"
    headers: Dict[str, str] = None
    enabled: bool = True
    created_at: str = None

    def __post_init__(self):
        if self.headers is None:
            self.headers = {}
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class WebhookManager:
    """
    Webhook管理クラス

    環境変数:
        WEBHOOKS_DB_PATH: Webhookデータベースファイルのパス
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = Path(db_path or os.getenv('WEBHOOKS_DB_PATH', '/workspace/integrations/webhook/webhooks.json'))
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.webhooks: Dict[str, Webhook] = {}
        self.load_webhooks()

        logger.info("Webhookマネージャー初期化完了")

    def load_webhooks(self):
        """Webhookデータベースから読み込み"""
        if self.db_path.exists():
            with open(self.db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

                for webhook_data in data:
                    webhook = Webhook(**webhook_data)
                    self.webhooks[webhook.id] = webhook

            logger.info(f"Webhookを{len(self.webhooks)}件読み込みました")

    def save_webhooks(self):
        """Webhookデータベースに保存"""
        data = [webhook.to_dict() for webhook in self.webhooks.values()]

        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info("Webhookデータベースを保存しました")

    def register_webhook(
        self,
        webhook_id: str,
        name: str,
        url: str,
        method: str = "POST",
        headers: Optional[Dict[str, str]] = None,
        enabled: bool = True
    ) -> Webhook:
        """
        Webhookを登録

        Args:
            webhook_id: Webhook ID
            name: Webhook名
            url: Webhook URL
            method: HTTPメソッド
            headers: ヘッダー
            enabled: 有効フラグ

        Returns:
            登録されたWebhook
        """
        webhook = Webhook(
            id=webhook_id,
            name=name,
            url=url,
            method=method,
            headers=headers or {},
            enabled=enabled
        )

        self.webhooks[webhook_id] = webhook
        self.save_webhooks()

        logger.info(f"Webhookを登録: {name}")
        return webhook

    def unregister_webhook(self, webhook_id: str) -> bool:
        """
        Webhookを削除

        Args:
            webhook_id: Webhook ID

        Returns:
            成功したらTrue
        """
        if webhook_id in self.webhooks:
            name = self.webhooks[webhook_id].name
            del self.webhooks[webhook_id]
            self.save_webhooks()
            logger.info(f"Webhookを削除: {name}")
            return True
        return False

    def get_webhook(self, webhook_id: str) -> Optional[Webhook]:
        """
        Webhookを取得

        Args:
            webhook_id: Webhook ID

        Returns:
            Webhookオブジェクト
        """
        return self.webhooks.get(webhook_id)

    def list_webhooks(self, enabled_only: bool = False) -> List[Webhook]:
        """
        Webhook一覧を取得

        Args:
            enabled_only: 有効なWebhookのみ

        Returns:
            Webhookリスト
        """
        webhooks = list(self.webhooks.values())

        if enabled_only:
            webhooks = [w for w in webhooks if w.enabled]

        return webhooks

    def enable_webhook(self, webhook_id: str) -> bool:
        """
        Webhookを有効化

        Args:
            webhook_id: Webhook ID

        Returns:
            成功したらTrue
        """
        webhook = self.get_webhook(webhook_id)
        if webhook:
            webhook.enabled = True
            self.save_webhooks()
            logger.info(f"Webhookを有効化: {webhook.name}")
            return True
        return False

    def disable_webhook(self, webhook_id: str) -> bool:
        """
        Webhookを無効化

        Args:
            webhook_id: Webhook ID

        Returns:
            成功したらTrue
        """
        webhook = self.get_webhook(webhook_id)
        if webhook:
            webhook.enabled = False
            self.save_webhooks()
            logger.info(f"Webhookを無効化: {webhook.name}")
            return True
        return False

    def send_webhook(
        self,
        webhook_id: str,
        data: Dict[str, Any],
        timeout: int = 30
    ) -> Optional[Dict[str, Any]]:
        """
        Webhookを送信

        Args:
            webhook_id: Webhook ID
            data: 送信データ
            timeout: タイムアウト（秒）

        Returns:
            レスポンス（成功した場合）
        """
        webhook = self.get_webhook(webhook_id)

        if not webhook:
            logger.error(f"Webhookが見つかりません: {webhook_id}")
            return None

        if not webhook.enabled:
            logger.warning(f"Webhookが無効です: {webhook.name}")
            return None

        return self._send_request(
            url=webhook.url,
            method=webhook.method,
            data=data,
            headers=webhook.headers,
            timeout=timeout
        )

    def send_to_all(
        self,
        data: Dict[str, Any],
        timeout: int = 30
    ) -> List[Dict[str, Any]]:
        """
        全ての有効なWebhookに送信

        Args:
            data: 送信データ
            timeout: タイムアウト（秒）

        Returns:
            レスポンスリスト
        """
        results = []

        for webhook in self.list_webhooks(enabled_only=True):
            result = self._send_request(
                url=webhook.url,
                method=webhook.method,
                data=data,
                headers=webhook.headers,
                timeout=timeout
            )

            results.append({
                'webhook_id': webhook.id,
                'webhook_name': webhook.name,
                'result': result
            })

        return results

    def _send_request(
        self,
        url: str,
        method: str,
        data: Dict[str, Any],
        headers: Dict[str, str],
        timeout: int
    ) -> Dict[str, Any]:
        """
        HTTPリクエストを送信

        Args:
            url: URL
            method: HTTPメソッド
            data: 送信データ
            headers: ヘッダー
            timeout: タイムアウト（秒）

        Returns:
            レスポンス
        """
        if not REQUESTS_AVAILABLE:
            raise ImportError("requestsライブラリがインストールされていません")

        try:
            if method.upper() == 'GET':
                response = requests.get(url, params=data, headers=headers, timeout=timeout)
            else:
                response = requests.request(
                    method.upper(),
                    url,
                    json=data,
                    headers=headers,
                    timeout=timeout
                )

            result = {
                'status_code': response.status_code,
                'success': 200 <= response.status_code < 300,
                'data': response.json() if response.content else None
            }

            if result['success']:
                logger.info(f"Webhook送信成功: {url}")
            else:
                logger.warning(f"Webhook送信失敗: {url} - {response.status_code}")

            return result

        except requests.RequestException as e:
            logger.error(f"Webhook送信エラー: {url} - {e}")
            return {
                'status_code': None,
                'success': False,
                'error': str(e)
            }

    def send_raw_webhook(
        self,
        url: str,
        data: Dict[str, Any],
        method: str = "POST",
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        一時的なWebhookを送信（登録なし）

        Args:
            url: Webhook URL
            data: 送信データ
            method: HTTPメソッド
            headers: ヘッダー
            timeout: タイムアウト（秒）

        Returns:
            レスポンス
        """
        return self._send_request(
            url=url,
            method=method,
            data=data,
            headers=headers or {},
            timeout=timeout
        )


# CLIツールとして使用する場合
def main():
    import argparse

    parser = argparse.ArgumentParser(description="Webhook Manager")
    parser.add_argument('--list', action='store_true', help='Webhook一覧を表示')
    parser.add_argument('--register', type=str, nargs=3, metavar=('ID', 'NAME', 'URL'), help='Webhookを登録')
    parser.add_argument('--unregister', type=str, help='Webhookを削除')
    parser.add_argument('--enable', type=str, help='Webhookを有効化')
    parser.add_argument('--disable', type=str, help='Webhookを無効化')
    parser.add_argument('--send', type=str, help='Webhook IDを指定して送信')
    parser.add_argument('--data', type=str, help='送信データ（JSON）')
    parser.add_argument('--send-all', action='store_true', help='全ての有効なWebhookに送信')
    parser.add_argument('--raw', type=str, help='生のURLに送信')

    args = parser.parse_args()

    try:
        manager = WebhookManager()

        if args.list:
            webhooks = manager.list_webhooks()
            print(f"\n🪝 Webhook一覧 ({len(webhooks)}件):")
            for webhook in webhooks:
                status = "✅" if webhook.enabled else "❌"
                print(f"  {status} {webhook.name} ({webhook.id})")
                print(f"     URL: {webhook.url}")
                print(f"     Method: {webhook.method}")

        elif args.register:
            webhook_id, name, url = args.register
            manager.register_webhook(
                webhook_id=webhook_id,
                name=name,
                url=url
            )
            print(f"✅ Webhookを登録しました: {name}")

        elif args.unregister:
            if manager.unregister_webhook(args.unregister):
                print(f"✅ Webhookを削除しました: {args.unregister}")
            else:
                print(f"❌ Webhookが見つかりません: {args.unregister}")

        elif args.enable:
            if manager.enable_webhook(args.enable):
                print(f"✅ Webhookを有効化しました: {args.enable}")
            else:
                print(f"❌ Webhookが見つかりません: {args.enable}")

        elif args.disable:
            if manager.disable_webhook(args.disable):
                print(f"✅ Webhookを無効化しました: {args.disable}")
            else:
                print(f"❌ Webhookが見つかりません: {args.disable}")

        elif args.send:
            if not args.data:
                print("エラー: --data が必要です")
                return

            data = json.loads(args.data)
            result = manager.send_webhook(args.send, data)

            if result:
                print(f"✅ Webhookを送信しました")
                print(json.dumps(result, indent=2))
            else:
                print(f"❌ Webhook送信に失敗しました")

        elif args.send_all:
            if not args.data:
                print("エラー: --data が必要です")
                return

            data = json.loads(args.data)
            results = manager.send_to_all(data)

            print(f"\n📤 {len(results)}個のWebhookに送信しました:")
            for result in results:
                webhook_name = result['webhook_name']
                success = result['result'].get('success')
                status = "✅" if success else "❌"
                print(f"  {status} {webhook_name}")

        elif args.raw:
            if not args.data:
                print("エラー: --data が必要です")
                return

            data = json.loads(args.data)
            result = manager.send_raw_webhook(args.raw, data)

            print(f"✅ Webhookを送信しました")
            print(json.dumps(result, indent=2))

        else:
            print("オプションを指定してください。--help でヘルプを表示します。")

    except Exception as e:
        logger.error(f"エラー: {e}")
        print(f"❌ エラー: {e}")


if __name__ == "__main__":
    main()
