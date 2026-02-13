#!/usr/bin/env python3
"""
えっちコンテンツ評価レビューエージェント - メインモジュール
Erotic Content Rating & Review Agent - Main Module

えっちな作品の評価・レビュー管理を行うエージェント
"""

import re
from db import EroticRatingAgentDB


class EroticRatingAgent:
    """えっちコンテンツ評価レビューエージェント"""

    def __init__(self):
        """初期化"""
        self.db = EroticRatingAgentDB()
        self.db.initialize()

    def parse_message(self, message: str) -> dict:
        """メッセージを解析 / Parse message"""
        message = message.strip()

        # レビュー追加 / Add review
        add_match = re.match(r'(?:レビュー|review|評価|rate)[:：]\s*(.+)', message, re.IGNORECASE)
        if add_match:
            return self._parse_add(add_match.group(1))

        # 更新 / Update
        update_match = re.match(r'(?:更新|update)[:：]\s*(\d+)\s*,\s*(.+)', message, re.IGNORECASE)
        if update_match:
            return self._parse_update(int(update_match.group(1)), update_match.group(2))

        # 削除 / Delete
        delete_match = re.match(r'(?:削除|delete|del)[:：]\s*(\d+)', message, re.IGNORECASE)
        if delete_match:
            return {'action': 'delete', 'review_id': int(delete_match.group(1))}

        # 検索 / Search
        search_match = re.match(r'(?:検索|search)[:：]\s*(.+)', message, re.IGNORECASE)
        if search_match:
            return {'action': 'search', 'keyword': search_match.group(1)}

        # 一覧 / List
        list_match = re.match(r'(?:レビュー|review|評価)(?:一覧|list)?', message, re.IGNORECASE)
        if list_match:
            return {'action': 'list'}

        # アーティスト別 / By artist
        artist_match = re.match(r'(?:アーティスト|artist)[:：]\s*(.+)', message, re.IGNORECASE)
        if artist_match:
            return {'action': 'list_artist', 'artist': artist_match.group(1)}

        # 高評価 / Top rated
        if message.strip().lower() in ['top', '高評価', '上位']:
            return {'action': 'top_rated'}

        # 低評価 / Low rated
        if message.strip().lower() in ['low', '低評価', '下位']:
            return {'action': 'low_rated'}

        # 統計 / Stats
        if message.strip() in ['統計', 'stats', '評価統計']:
            return {'action': 'stats'}

        # 平均評価 / Average rating
        avg_match = re.match(r'(?:平均|average|avg)[:：]?\s*(.+)?', message, re.IGNORECASE)
        if avg_match:
            return {'action': 'average', 'artist': avg_match.group(1)}

        return None

    def _parse_add(self, content: str) -> dict:
        """追加コマンド解析"""
        result = {'action': 'add', 'content_id': None, 'content_title': None,
                  'artist': None, 'rating': 5, 'review_text': None, 'tags': None}

        # コンテンツID
        id_match = re.search(r'(?:id|コンテンツID|content_id)[:：]\s*(\S+)', content, re.IGNORECASE)
        if id_match:
            result['content_id'] = id_match.group(1).strip()
            content = content.replace(id_match.group(0), '', 1).strip()

        # タイトル
        title_match = re.search(r'(?:タイトル|title)[:：]\s*([^,、]+)', content, re.IGNORECASE)
        if title_match:
            result['content_title'] = title_match.group(1).strip()
            content = content.replace(title_match.group(0), '', 1).strip()

        # アーティスト
        artist_match = re.search(r'(?:アーティスト|artist)[:：]\s*([^,、]+)', content, re.IGNORECASE)
        if artist_match:
            result['artist'] = artist_match.group(1).strip()
            content = content.replace(artist_match.group(0), '', 1).strip()

        # 評価
        rating_match = re.search(r'(?:評価|rating|rate)[:：]\s*(\d{1,2})', content, re.IGNORECASE)
        if rating_match:
            result['rating'] = int(rating_match.group(1))

        # レビュー本文
        review_match = re.search(r'(?:レビュー|review|本文|text)[:：]\s*(.+)', content, re.IGNORECASE)
        if review_match:
            result['review_text'] = review_match.group(1).strip()

        # タグ
        tag_match = re.search(r'(?:タグ|tag)[:：]\s*(.+)', content, re.IGNORECASE)
        if tag_match:
            tags_str = tag_match.group(1).strip()
            result['tags'] = ', '.join([t.strip() for t in re.split(r'[,、\s]+', tags_str) if t.strip()])

        return result

    def _parse_update(self, review_id: int, content: str) -> dict:
        """更新コマンド解析"""
        result = {'action': 'update', 'review_id': review_id, 'content_title': None,
                  'artist': None, 'rating': None, 'review_text': None, 'tags': None}

        # タイトル
        title_match = re.search(r'(?:タイトル|title)[:：]\s*([^,、]+)', content, re.IGNORECASE)
        if title_match:
            result['content_title'] = title_match.group(1).strip()

        # アーティスト
        artist_match = re.search(r'(?:アーティスト|artist)[:：]\s*([^,、]+)', content, re.IGNORECASE)
        if artist_match:
            result['artist'] = artist_match.group(1).strip()

        # 評価
        rating_match = re.search(r'(?:評価|rating|rate)[:：]\s*(\d{1,2})', content, re.IGNORECASE)
        if rating_match:
            result['rating'] = int(rating_match.group(1))

        # レビュー本文
        review_match = re.search(r'(?:レビュー|review|本文|text)[:：]\s*(.+)', content, re.IGNORECASE)
        if review_match:
            result['review_text'] = review_match.group(1).strip()

        # タグ
        tag_match = re.search(r'(?:タグ|tag)[:：]\s*(.+)', content, re.IGNORECASE)
        if tag_match:
            tags_str = tag_match.group(1).strip()
            result['tags'] = ', '.join([t.strip() for t in re.split(r'[,、\s]+', tags_str) if t.strip()])

        return result

    def handle_message(self, message: str) -> str:
        """メッセージを処理 / Handle message"""
        parsed = self.parse_message(message)

        if not parsed:
            return None

        action = parsed['action']

        if action == 'add':
            if not parsed['content_id']:
                return "❌ コンテンツIDを入力してください / Please enter a content ID"

            try:
                review_id = self.db.add_review(
                    content_id=parsed['content_id'],
                    content_title=parsed['content_title'] or "タイトルなし",
                    artist=parsed['artist'] or "",
                    rating=parsed['rating'],
                    review_text=parsed['review_text'] or "",
                    tags=parsed['tags'] or ""
                )

                response = f"✅ レビュー #{review_id} 追加完了 / Review added\n"
                response += f"タイトル / Title: {parsed['content_title'] or 'タイトルなし'}\n"
                response += f"評価 / Rating: {parsed['rating']}/10\n"
                if parsed['artist']:
                    response += f"アーティスト / Artist: {parsed['artist']}\n"
                if parsed['review_text']:
                    response += f"レビュー / Review: {parsed['review_text'][:100]}..."
                return response
            except ValueError as e:
                return f"❌ {str(e)}"

        elif action == 'update':
            try:
                success = self.db.update_review(
                    parsed['review_id'],
                    content_title=parsed['content_title'],
                    artist=parsed['artist'],
                    rating=parsed['rating'],
                    review_text=parsed['review_text'],
                    tags=parsed['tags']
                )

                if not success:
                    return f"❌ レビュー #{parsed['review_id']} が見つかりません / Review not found"

                response = f"✏️ レビュー #{parsed['review_id']} 更新完了 / Review updated\n"
                if parsed['content_title']:
                    response += f"タイトル / Title: {parsed['content_title']}\n"
                if parsed['rating']:
                    response += f"評価 / Rating: {parsed['rating']}/10"
                return response
            except ValueError as e:
                return f"❌ {str(e)}"

        elif action == 'delete':
            success = self.db.delete_review(parsed['review_id'])
            if success:
                return f"🗑️ レビュー #{parsed['review_id']} 削除完了 / Review deleted"
            return f"❌ レビュー #{parsed['review_id']} が見つかりません / Review not found"

        elif action == 'search':
            keyword = parsed['keyword']
            reviews = self.db.search_reviews(keyword)

            if not reviews:
                return f"🔍 「{keyword}」の検索結果: 見つかりませんでした / No results found for \"{keyword}\""

            response = f"🔍 「{keyword}」の検索結果 ({len(reviews)}件 / results):\n"
            for review in reviews:
                response += self._format_review(review)
            return response

        elif action == 'list':
            reviews = self.db.list_reviews()

            if not reviews:
                return "📋 レビューがありません / No reviews found"

            response = f"📋 レビュー一覧 ({len(reviews)}件 / reviews):\n"
            for review in reviews:
                response += self._format_review(review)
            return response

        elif action == 'list_artist':
            artist = parsed['artist']
            reviews = self.db.get_reviews_by_artist(artist)

            if not reviews:
                return f"🎨 アーティスト「{artist}」のレビュー: 見つかりませんでした / No reviews found for artist \"{artist}\""

            response = f"🎨 アーティスト「{artist}」のレビュー ({len(reviews)}件 / reviews):\n"
            for review in reviews:
                response += self._format_review(review)
            return response

        elif action == 'top_rated':
            reviews = self.db.get_top_rated(10)

            if not reviews:
                return "🏆 高評価作品がありません / No top rated reviews found"

            response = "🏆 高評価作品 Top 10:\n"
            for i, review in enumerate(reviews, 1):
                response += f"\n#{i} " + self._format_review(review, compact=True)
            return response

        elif action == 'low_rated':
            reviews = self.db.get_low_rated(10)

            if not reviews:
                return "⚠️ 低評価作品がありません / No low rated reviews found"

            response = "⚠️ 低評価作品:\n"
            for i, review in enumerate(reviews, 1):
                response += f"\n#{i} " + self._format_review(review, compact=True)
            return response

        elif action == 'stats':
            stats = self.db.get_stats()

            response = "📊 レビュー統計 / Review Stats:\n"
            response += f"全レビュー数 / Total: {stats['total_reviews']}件\n"
            response += f"平均評価 / Average: {stats['average_rating']}/10\n"
            response += f"トップアーティスト / Top artist: {stats['top_artist']}\n"

            if stats['rating_distribution']:
                response += "\n評価分布 / Rating distribution:\n"
                for rating, count in sorted(stats['rating_distribution'].items()):
                    bar = '█' * (count * 2)
                    response += f"  {rating}⭐: {count}件 {bar}\n"

            return response

        elif action == 'average':
            artist = parsed['artist']
            avg = self.db.get_average_rating(artist)
            if artist:
                return f"📈 アーティスト「{artist}」の平均評価: {avg:.1f}/10"
            return f"📈 全体の平均評価: {avg:.1f}/10"

        return None

    def _format_review(self, review: dict, compact: bool = False) -> str:
        """レビューをフォーマット"""
        if compact:
            rating = review['rating']
            return f"{review['content_title']} (★★★★★★★★★☆★"[:rating*2+10].replace('☆', '⭐')[:rating+10])[:20] + f" - {rating}/10\n"

        id, content_id, content_title, artist, rating, review_text, tags, created_at = \
            review['id'], review['content_id'], review['content_title'], \
            review['artist'], review['rating'], review['review_text'], \
            review['tags'], review['created_at']

        response = f"\n📝 [{id}] {content_title}\n"
        if artist:
            response += f"    🎨 {artist}\n"
        response += f"    ⭐ 評価: {rating}/10 {'⭐' * rating}\n"
        if review_text:
            response += f"    💬 {review_text[:100]}...\n"
        if tags:
            response += f"    🏷️ {tags}\n"
        response += f"    📅 {created_at[:10]}"

        return response


if __name__ == '__main__':
    agent = EroticRatingAgent()

    test_messages = [
        "レビュー: id:001, タイトル:素晴らしい作品, 評価:9, レビュー:最高です",
        "アーティスト: テスト",
        "top",
        "stats",
    ]

    for msg in test_messages:
        print(f"\n入力 / Input: {msg}")
        result = agent.handle_message(msg)
        if result:
            print(result)
