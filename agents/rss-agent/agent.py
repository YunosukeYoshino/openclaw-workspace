"""
RSS Agent - Discord Bot
RSS feed management and article notifications
"""
import discord
from discord.ext import commands
import feedparser
from datetime import datetime
from typing import List, Optional
from db import RSSDB

class RSSAgent(commands.Cog):
    """RSS agent for feed management and notifications"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = RSSDB()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"RSS Agent ready as {self.bot.user}")

    @commands.command(name='rss', help='Manage RSS feeds | RSSフィードを管理')
    async def manage_rss(self, ctx, action: str = None, *, args: str = None):
        """Main RSS management command"""
        if not action:
            embed = discord.Embed(
                title="RSS Agent / RSSエージェント",
                description="Commands available / 利用可能なコマンド:\n"
                            "• `!rss add <name> <url>` - Add feed / フィード追加\n"
                            "• `rss list` - List feeds / フィード一覧\n"
                            "• `rss remove <id>` - Remove feed / フィード削除\n"
                            "• `rss check <id>` - Check for new articles / 新着記事チェック\n"
                            "• `rss articles [id]` - Show articles / 記事表示\n"
                            "• `rss unread` - Show unread articles / 未読記事\n"
                            "• `rss favorite <id>` - Mark as favorite / お気に入りに追加\n"
                            "• `rss stats` - Show statistics / 統計表示",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)
            return

        if action == 'add':
            await self._add_feed(ctx, args)
        elif action == 'list':
            await self._list_feeds(ctx)
        elif action == 'remove':
            await self._remove_feed(ctx, args)
        elif action == 'check':
            await self._check_feed(ctx, args)
        elif action == 'articles':
            await self._show_articles(ctx, args)
        elif action == 'unread':
            await self._show_unread(ctx)
        elif action == 'favorite':
            await self._mark_favorite(ctx, args)
        elif action == 'stats':
            await self._show_stats(ctx)
        else:
            await ctx.send(f"Unknown action: {action}\nUnknown action: {action}\nUse `!rss` for help / `!rss`でヘルプを表示")

    async def _add_feed(self, ctx, args: str):
        """Add a new RSS feed"""
        if not args:
            await ctx.send("Usage: `!rss add <name> <url>`\nUsage: `!rss add <name> <url>`")
            return

        parts = args.split(maxsplit=1)
        if len(parts) < 2:
            await ctx.send("Please provide both name and URL.\n名前とURLの両方を指定してください。")
            return

        name = parts[0]
        url = parts[1]

        # Validate URL by trying to fetch
        try:
            feed = feedparser.parse(url)
            if not feed.entries:
                await ctx.send("⚠️ Feed might be invalid or empty.\nフィードが無効か空の可能性があります。")

            feed_id = self.db.add_feed(name, url)

            if feed_id:
                # Auto-add initial articles
                added_count = 0
                for entry in feed.entries[:20]:
                    self.db.add_article(
                        feed_id=feed_id,
                        title=entry.get('title', 'No title'),
                        link=entry.get('link', ''),
                        description=entry.get('description', ''),
                        published_date=entry.get('published', '')
                    )
                    added_count += 1

                embed = discord.Embed(
                    title="✅ Feed Added / フィード追加完了",
                    description=f"Name: {name}\nURL: {url}\nInitial articles: {added_count}",
                    color=discord.Color.green()
                )
                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ Feed with this URL already exists.\nこのURLのフィードは既に存在します。")

        except Exception as e:
            await ctx.send(f"❌ Error adding feed: {str(e)}\nフィード追加エラー: {str(e)}")

    async def _list_feeds(self, ctx):
        """List all RSS feeds"""
        feeds = self.db.get_feeds()

        if not feeds:
            await ctx.send("No feeds found. Use `!rss add` to add one.\n"
                         "フィードがありません。`!rss add`で追加してください。")
            return

        embed = discord.Embed(
            title="RSS Feeds / RSSフィード",
            description=f"Total: {len(feeds)} feeds",
            color=discord.Color.blue()
        )

        for feed in feeds:
            stats = self.db.get_feed_stats(feed['id'])
            status = "✅ Active" if feed['is_active'] else "⏸️ Inactive"
            embed.add_field(
                name=f"#{feed['id']} - {feed['name']}",
                value=f"URL: {feed['url'][:50]}...\n"
                      f"Status: {status}\n"
                      f"Articles: {stats.get('total_articles', 0)} | "
                      f"Unread: {stats.get('unread_count', 0)}",
                inline=False
            )

        await ctx.send(embed=embed)

    async def _remove_feed(self, ctx, args: str):
        """Remove an RSS feed"""
        if not args:
            await ctx.send("Usage: `!rss remove <feed_id>`\nUsage: `!rss remove <feed_id>`")
            return

        try:
            feed_id = int(args)
            feed = self.db.get_feed(feed_id)

            if not feed:
                await ctx.send("❌ Feed not found.\nフィードが見つかりません。")
                return

            if self.db.delete_feed(feed_id):
                embed = discord.Embed(
                    title="✅ Feed Removed / フィード削除完了",
                    description=f"Removed: {feed['name']}",
                    color=discord.Color.green()
                )
                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ Failed to remove feed.\nフィード削除に失敗しました。")

        except ValueError:
            await ctx.send("❌ Invalid feed ID.\n無効なフィードIDです。")

    async def _check_feed(self, ctx, args: str):
        """Check for new articles in a feed"""
        if not args:
            await ctx.send("Usage: `!rss check <feed_id>`\nUsage: `!rss check <feed_id>`")
            return

        try:
            feed_id = int(args)
            feed = self.db.get_feed(feed_id)

            if not feed:
                await ctx.send("❌ Feed not found.\nフィードが見つかりません。")
                return

            # Fetch and parse feed
            feed_data = feedparser.parse(feed['url'])

            new_articles = []
            for entry in feed_data.entries[:20]:
                article_id = self.db.add_article(
                    feed_id=feed_id,
                    title=entry.get('title', 'No title'),
                    link=entry.get('link', ''),
                    description=entry.get('description', ''),
                    published_date=entry.get('published', ''),
                    author=entry.get('author', '')
                )

                if article_id:  # Article is new
                    new_articles.append(article_id)

            # Update last checked time
            self.db.update_feed_check_time(feed_id)

            if new_articles:
                embed = discord.Embed(
                    title=f"📰 New Articles / 新着記事 - {feed['name']}",
                    description=f"Found {len(new_articles)} new articles!",
                    color=discord.Color.green()
                )

                # Show first few new articles
                articles = self.db.get_articles(feed_id=feed_id, limit=len(new_articles))
                for article in articles[:5]:
                    embed.add_field(
                        name=article['title'][:100],
                        value=f"Published: {article['published_date'] or 'N/A'}\n"
                              f"[Link]({article['link']})",
                        inline=False
                    )

                await ctx.send(embed=embed)
            else:
                await ctx.send("✅ No new articles found.\n新着記事はありません。")

        except Exception as e:
            await ctx.send(f"❌ Error checking feed: {str(e)}\nフィードチェックエラー: {str(e)}")

    async def _show_articles(self, ctx, args: str = None):
        """Show articles from a specific feed or all feeds"""
        feed_id = None

        if args:
            try:
                feed_id = int(args)
                feed = self.db.get_feed(feed_id)
                if not feed:
                    await ctx.send("❌ Feed not found.\nフィードが見つかりません。")
                    return
            except ValueError:
                pass

        articles = self.db.get_articles(feed_id=feed_id, limit=20)

        if not articles:
            await ctx.send("No articles found.\n記事が見つかりません。")
            return

        feed_name = feed['name'] if feed_id else "All Feeds / 全フィード"

        embed = discord.Embed(
            title=f"📰 Articles / 記事 - {feed_name}",
            description=f"Showing {len(articles)} articles",
            color=discord.Color.blue()
        )

        for article in articles[:10]:
            status = ""
            if article['is_read']:
                status += "✓Read "
            if article['is_favorite']:
                status += "⭐Favorite"

            embed.add_field(
                name=f"{article['title'][:100]}",
                value=f"{status}\n"
                      f"Published: {article['published_date'] or 'N/A'}\n"
                      f"[Link]({article['link']})",
                inline=False
            )

        await ctx.send(embed=embed)

    async def _show_unread(self, ctx):
        """Show unread articles"""
        articles = self.db.get_unread_articles(limit=30)

        if not articles:
            await ctx.send("✅ No unread articles.\n未読記事はありません。")
            return

        embed = discord.Embed(
            title="📬 Unread Articles / 未読記事",
            description=f"Total: {len(articles)} unread",
            color=discord.Color.orange()
        )

        for article in articles[:10]:
            embed.add_field(
                name=f"📰 {article['title'][:100]}",
                value=f"Published: {article['published_date'] or 'N/A'}\n"
                      f"[Read](<http://placeholder>) | [Link]({article['link']})",
                inline=False
            )

        await ctx.send(embed=embed)

    async def _mark_favorite(self, ctx, args: str):
        """Mark an article as favorite"""
        if not args:
            await ctx.send("Usage: `!rss favorite <article_id>`\nUsage: `!rss favorite <article_id>`")
            return

        try:
            article_id = int(args)
            self.db.mark_article_favorite(article_id)
            await ctx.send("⭐ Article marked as favorite.\n記事をお気に入りに追加しました。")
        except ValueError:
            await ctx.send("❌ Invalid article ID.\n無効な記事IDです。")

    async def _show_stats(self, ctx):
        """Show RSS statistics"""
        feeds = self.db.get_feeds(is_active=True)
        stats = self.db.get_feed_stats()

        embed = discord.Embed(
            title="📊 RSS Statistics / RSS統計",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="Active Feeds / アクティブなフィード",
            value=str(len(feeds)),
            inline=True
        )

        embed.add_field(
            name="Total Articles / 総記事数",
            value=str(stats.get('total_articles', 0)),
            inline=True
        )

        embed.add_field(
            name="Unread / 未読",
            value=str(stats.get('unread_count', 0)),
            inline=True
        )

        embed.add_field(
            name="Favorites / お気に入り",
            value=str(stats.get('favorite_count', 0)),
            inline=True
        )

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(RSSAgent(bot))
