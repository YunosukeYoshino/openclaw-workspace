#!/usr/bin/env python3
"""
Discord Notification Module for Instapaper Summary Agent
Discord Webhook経由で通知を送信
"""

import requests
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class DiscordClient:
    """Discord Webhook クライアント"""

    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url

    def send_message(self, content: str, username: Optional[str] = None,
                     avatar_url: Optional[str] = None, embeds: Optional[list] = None):
        """メッセージを送信"""
        if not self.webhook_url:
            logger.warning("Webhook URL not configured, skipping notification")
            return

        try:
            payload = {
                'content': content,
                'username': username or 'Instapaper Summarizer',
                'avatar_url': avatar_url or None,
            }

            if embeds:
                payload['embeds'] = embeds

            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )

            if response.status_code == 204:
                logger.info("Message sent successfully to Discord")
            else:
                logger.warning(f"Discord API returned status {response.status_code}: {response.text}")

        except requests.Timeout:
            logger.error("Timeout while sending message to Discord")
        except requests.RequestException as e:
            logger.error(f"Failed to send message to Discord: {e}")

    def send_embed(self, title: str, description: str, url: Optional[str] = None,
                   color: int = 0x5865F2):
        """Embed形式で送信"""
        embed = {
            'title': title,
            'description': description,
            'color': color,
        }

        if url:
            embed['url'] = url

        self.send_message('', embeds=[embed])
