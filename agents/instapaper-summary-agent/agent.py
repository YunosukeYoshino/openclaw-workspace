#!/usr/bin/env python3
"""
Instapaper Summary Agent
Instapaper RSSから記事を取得して要約し、Discordに通知するエージェント
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import feedparser
import requests
from bs4 import BeautifulSoup

from db import Database
from discord import DiscordClient

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ArticleSummarizer:
    """記事の要約を行うクラス"""

    def __init__(self):
        pass

    def fetch_article_content(self, url: str) -> Optional[str]:
        """記事の本文を取得する"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # 不要な要素を削除
            for tag in soup(['script', 'style', 'nav', 'footer', 'aside', 'header']):
                tag.decompose()

            # メインコンテンツを抽出（シンプルな実装）
            content = ''
            for tag in soup.find_all(['p', 'h1', 'h2', 'h3']):
                text = tag.get_text(strip=True)
                if text and len(text) > 50:
                    content += text + '\n'

            return content[:3000]  # 3000文字に制限

        except Exception as e:
            logger.error(f"Failed to fetch article content from {url}: {e}")
            return None

    def summarize_article(self, title: str, url: str, content: str) -> str:
        """記事を要約する"""
        if not content:
            return f"{title}\n\n要約を取得できませんでした"

        # 簡易的な要約（最初の数段落を抽出）
        lines = content.split('\n')
        summary_lines = []
        char_count = 0

        for line in lines:
            if char_count + len(line) > 800:
                break
            if line.strip():
                summary_lines.append(line)
                char_count += len(line)

        summary = '\n'.join(summary_lines)
        return f"{title}\n\n{summary}\n...\n\n元記事: {url}"


class InstapaperAgent:
    """Instapaper RSSエージェント"""

    def __init__(self):
        self.rss_url = os.getenv('INSTAPAPER_RSS_URL', '')
        self.discord_webhook_url = os.getenv('DISCORD_WEBHOOK_URL', '')
        self.db = Database()
        self.discord = DiscordClient(self.discord_webhook_url)
        self.summarizer = ArticleSummarizer()

        if not self.rss_url:
            raise ValueError("INSTAPAPER_RSS_URL environment variable is required")

    def fetch_rss_items(self) -> List[Dict]:
        """RSSフィードからアイテムを取得"""
        try:
            feed = feedparser.parse(self.rss_url)
            items = []

            for entry in feed.entries:
                item = {
                    'title': entry.get('title', ''),
                    'url': entry.get('link', entry.get('guid', '')),
                    'description': entry.get('description', ''),
                    'pub_date': entry.get('published', '')
                }
                items.append(item)

            logger.info(f"Fetched {len(items)} items from RSS")
            return items

        except Exception as e:
            logger.error(f"Failed to fetch RSS feed: {e}")
            return []

    def is_duplicate(self, url: str) -> bool:
        """URLが重複しているかチェック"""
        return self.db.url_exists(url)

    def process_article(self, article: Dict) -> Optional[str]:
        """記事を処理して要約を生成"""
        url = article['url']

        # 重複チェック
        if self.is_duplicate(url):
            logger.info(f"Skipping duplicate article: {url}")
            return None

        # 記事コンテンツを取得
        content = self.summarizer.fetch_article_content(url)

        # 要約を生成
        summary = self.summarizer.summarize_article(
            article['title'],
            url,
            content or article['description']
        )

        # URLを保存（重複防止用）
        self.db.save_url(url, article['title'])

        return summary

    def send_discord_notification(self, summary: str, index: int, total: int):
        """Discordに通知を送信"""
        if not self.discord_webhook_url:
            logger.warning("Discord webhook URL not configured")
            return

        header = f"📰 Instapaper 記事通知 ({index}/{total})"
        footer = f"\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        message = f"{header}\n\n{summary}{footer}"

        self.discord.send_message(message)

    def run(self):
        """エージェントを実行"""
        logger.info("Starting Instapaper Summary Agent")

        # RSSからアイテムを取得
        items = self.fetch_rss_items()

        if not items:
            logger.info("No articles found in RSS feed")
            return

        # 古いキャッシュをクリーンアップ（30日以上前）
        self.db.cleanup_old_entries(days=30)

        # 記事を処理
        new_articles = 0
        for i, article in enumerate(items, 1):
            summary = self.process_article(article)
            if summary:
                new_articles += 1
                self.send_discord_notification(summary, i, len(items))

        logger.info(f"Processed {new_articles} new articles")


def main():
    """メイン関数"""
    try:
        agent = InstapaperAgent()
        agent.run()
    except Exception as e:
        logger.error(f"Agent failed: {e}")
        raise


if __name__ == '__main__':
    main()
