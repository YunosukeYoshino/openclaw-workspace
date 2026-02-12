#!/usr/bin/env python3
"""
Notion API Client
Notion APIを統合して、データベース・ページの同期を行う

Usage:
    from integrations.notion import NotionClient

    client = NotionClient(api_key="your_api_key")
    pages = client.list_pages()
    client.create_page(parent_id="database_id", title="New Page")
"""

import os
import json
import logging
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime

# Notion APIクライアントが利用可能かチェック
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class NotionPage:
    """Notionページデータクラス"""
    id: str
    title: str
    url: str
    icon: Optional[str] = None
    cover: Optional[str] = None
    created_time: Optional[str] = None
    last_edited_time: Optional[str] = None


@dataclass
class NotionDatabase:
    """Notionデータベースデータクラス"""
    id: str
    title: str
    url: str
    description: Optional[str] = None


class NotionClient:
    """
    Notion APIクライアント

    環境変数:
        NOTION_API_KEY: Notion APIキー
        NOTION_VERSION: APIバージョン（デフォルト: '2022-06-28'）
    """

    BASE_URL = "https://api.notion.com/v1"

    def __init__(
        self,
        api_key: Optional[str] = None,
        version: str = "2022-06-28"
    ):
        if not REQUESTS_AVAILABLE:
            logger.warning("requestsライブラリがインストールされていません")
            logger.warning("インストール: pip install requests")
            raise ImportError("requestsライブラリがインストールされていません")

        self.api_key = api_key or os.getenv('NOTION_API_KEY')
        self.version = version

        if not self.api_key:
            raise ValueError(
                "Notion APIキーが必要です。\n"
                "環境変数 NOTION_API_KEY またはコンストラクタで設定してください。\n"
                "https://www.notion.so/my-integrations でAPIキーを取得できます。"
            )

        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Notion-Version': self.version,
            'Content-Type': 'application/json'
        }

        logger.info("Notion APIクライアント初期化完了")

    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Notion APIにリクエストを送信

        Args:
            method: HTTPメソッド (GET, POST, PATCH, DELETE)
            endpoint: APIエンドポイント
            data: リクエストボディ

        Returns:
            レスポンスJSON
        """
        url = f"{self.BASE_URL}{endpoint}"
        response = requests.request(
            method,
            url,
            headers=self.headers,
            json=data
        )

        response.raise_for_status()
        return response.json()

    def search(
        self,
        query: Optional[str] = None,
        filter_obj: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Notion内を検索

        Args:
            query: 検索キーワード
            filter_obj: フィルターオブジェクト

        Returns:
            検索結果
        """
        data = {}

        if query:
            data['query'] = query

        if filter_obj:
            data['filter'] = filter_obj

        result = self._request('POST', '/search', data)
        logger.info(f"検索結果: {len(result.get('results', []))}件")
        return result

    def list_pages(self) -> List[Dict[str, Any]]:
        """
        ページ一覧を取得

        Returns:
            ページリスト
        """
        result = self.search(filter_obj={'value': 'page', 'property': 'object'})
        pages = result.get('results', [])
        logger.info(f"ページを{len(pages)}件取得しました")
        return pages

    def list_databases(self) -> List[Dict[str, Any]]:
        """
        データベース一覧を取得

        Returns:
            データベースリスト
        """
        result = self.search(filter_obj={'value': 'database', 'property': 'object'})
        databases = result.get('results', [])
        logger.info(f"データベースを{len(databases)}件取得しました")
        return databases

    def get_page(self, page_id: str) -> Dict[str, Any]:
        """
        ページを取得

        Args:
            page_id: ページID

        Returns:
            ページ情報
        """
        page = self._request('GET', f'/pages/{page_id}')
        logger.info(f"ページを取得: {page_id}")
        return page

    def get_database(self, database_id: str) -> Dict[str, Any]:
        """
        データベースを取得

        Args:
            database_id: データベースID

        Returns:
            データベース情報
        """
        database = self._request('GET', f'/databases/{database_id}')
        logger.info(f"データベースを取得: {database_id}")
        return database

    def create_page(
        self,
        parent_id: str,
        title: str,
        properties: Optional[Dict] = None,
        content: Optional[str] = None,
        parent_type: str = "database"
    ) -> Dict[str, Any]:
        """
        新しいページを作成

        Args:
            parent_id: 親のID（データベースIDまたはページID）
            title: ページタイトル
            properties: プロパティ（データベースの場合）
            content: ページ本文（Markdown風）
            parent_type: 親のタイプ（"database" または "page"）

        Returns:
            作成されたページ情報
        """
        data = {
            'parent': {f'{parent_type}_id': parent_id}
        }

        # プロパティまたはタイトルを設定
        if properties:
            data['properties'] = properties
        else:
            data['properties'] = {
                'title': {
                    'title': [{'text': {'content': title}}]
                }
            }

        # 本文を設定
        if content:
            data['children'] = [
                {
                    'object': 'block',
                    'type': 'paragraph',
                    'paragraph': {
                        'text': [{'text': {'content': content}}]
                    }
                }
            ]

        page = self._request('POST', '/pages', data)
        logger.info(f"ページを作成: {title}")
        return page

    def update_page(
        self,
        page_id: str,
        properties: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        ページを更新

        Args:
            page_id: ページID
            properties: 更新するプロパティ

        Returns:
            更新されたページ情報
        """
        page = self._request('PATCH', f'/pages/{page_id}', properties)
        logger.info(f"ページを更新: {page_id}")
        return page

    def delete_page(self, page_id: str) -> bool:
        """
        ページを削除（アーカイブ）

        Args:
            page_id: ページID

        Returns:
            成功したらTrue
        """
        self._request('PATCH', f'/pages/{page_id}', {'archived': True})
        logger.info(f"ページをアーカイブ: {page_id}")
        return True

    def add_blocks(
        self,
        block_id: str,
        blocks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        ブロックを追加

        Args:
            block_id: ブロックID
            blocks: 追加するブロックリスト

        Returns:
            追加されたブロック情報
        """
        data = {'children': blocks}
        result = self._request('PATCH', f'/blocks/{block_id}/children', data)
        logger.info(f"ブロックを追加: {len(blocks)}個")
        return result

    def query_database(
        self,
        database_id: str,
        filter_obj: Optional[Dict] = None,
        sorts: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        データベースをクエリ

        Args:
            database_id: データベースID
            filter_obj: フィルターオブジェクト
            sorts: ソート条件

        Returns:
            クエリ結果
        """
        data = {}

        if filter_obj:
            data['filter'] = filter_obj

        if sorts:
            data['sorts'] = sorts

        result = self._request('POST', f'/databases/{database_id}/query', data)
        logger.info(f"クエリ結果: {len(result.get('results', []))}件")
        return result


# CLIツールとして使用する場合
def main():
    import argparse

    parser = argparse.ArgumentParser(description="Notion API Client")
    parser.add_argument('--list-pages', action='store_true', help='ページ一覧を表示')
    parser.add_argument('--list-databases', action='store_true', help='データベース一覧を表示')
    parser.add_argument('--search', type=str, help='検索キーワード')
    parser.add_argument('--get-page', type=str, help='ページIDを指定して取得')
    parser.add_argument('--create-page', type=str, help='新しいページを作成')
    parser.add_argument('--parent', type=str, help='親ID')
    parser.add_argument('--content', type=str, help='ページ本文')

    args = parser.parse_args()

    try:
        client = NotionClient()

        if args.list_pages:
            pages = client.list_pages()
            print(f"\n📄 ページ一覧 ({len(pages)}件):")
            for page in pages:
                title = page.get('properties', {}).get('title', {})
                title_text = title.get('title', [{}])[0].get('text', {}).get('content', 'No title')
                print(f"  - {title_text}")
                print(f"    ID: {page['id']}")

        elif args.list_databases:
            databases = client.list_databases()
            print(f"\n📊 データベース一覧 ({len(databases)}件):")
            for db in databases:
                title = db.get('title', [{}])[0].get('text', {}).get('content', 'No title')
                print(f"  - {title}")
                print(f"    ID: {db['id']}")

        elif args.search:
            result = client.search(query=args.search)
            items = result.get('results', [])
            print(f"\n🔍 検索結果: '{args.search}' ({len(items)}件):")
            for item in items:
                obj_type = item.get('object')
                if obj_type == 'page':
                    title = item.get('properties', {}).get('title', {})
                    title_text = title.get('title', [{}])[0].get('text', {}).get('content', 'No title')
                    print(f"  [Page] {title_text}")
                elif obj_type == 'database':
                    title = item.get('title', [{}])[0].get('text', {}).get('content', 'No title')
                    print(f"  [Database] {title}")

        elif args.get_page:
            page = client.get_page(args.get_page)
            print(f"\n📄 ページ情報:")
            print(json.dumps(page, indent=2, ensure_ascii=False))

        elif args.create_page:
            if not args.parent:
                print("エラー: --parent が必要です")
                return

            client.create_page(
                parent_id=args.parent,
                title=args.create_page,
                content=args.content
            )
            print(f"✅ ページを作成しました: {args.create_page}")

        else:
            print("オプションを指定してください。--help でヘルプを表示します。")

    except Exception as e:
        logger.error(f"エラー: {e}")
        print(f"❌ エラー: {e}")


if __name__ == "__main__":
    main()
