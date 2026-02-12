#!/usr/bin/env python3
"""
Audio Summarizer Agent - 音声要約エージェント
Audio Summarizer Agent - Summarize audio files and send to Slack
"""

import discord
from discord.ext import commands
from db import AudioSummarizerDB

class AudioSummarizerAgent(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        self.db = AudioSummarizerDB()

    async def setup_hook(self):
        await self.add_command(self.add_summary)
        await self.add_command(self.list_summaries)
        await self.add_command(self.show_summary)
        await self.add_command(self.delete_summary)

    @commands.command(name='add-summary')
    async def add_summary(self, ctx, *, args: str):
        """要約を追加 / Add a summary"""
        try:
            parts = args.split('|', 3)
            if len(parts) < 3:
                await ctx.send("使い方: !add-summary 音声ファイル|転記|要約|キーポイント\nUsage: !add-summary audio_file|transcription|summary|key_points")
                return

            audio_file = parts[0].strip()
            transcription = parts[1].strip()
            summary = parts[2].strip()
            key_points = parts[3].strip() if len(parts) > 3 else ""

            summary_id = self.db.add_summary(audio_file, transcription, summary, key_points)

            await ctx.send(f"✅ 要約を追加しました！ (ID: {summary_id})\nSummary added! (ID: {summary_id})")
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='list-summaries')
    async def list_summaries(self, ctx, limit: int = 10):
        """要約を一覧表示 / List summaries"""
        try:
            summaries = self.db.get_all_summaries()[:limit]

            if not summaries:
                await ctx.send("要約が見つかりませんでした。\nNo summaries found.")
                return

            response = "📝 要約リスト / Summary List\n\n"
            for s in summaries:
                response += f"🎤 **{s['audio_file']}** (ID: {s['id']})\n"
                response += f"   {s['summary'][:50]}...\n"
                response += f"   作成: {s['created_at']}\n\n"

            await ctx.send(response[:2000])
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='show-summary')
    async def show_summary(self, ctx, summary_id: int):
        """要約の詳細を表示 / Show summary details"""
        try:
            summary = self.db.get_summary(summary_id)

            if not summary:
                await ctx.send(f"要約が見つかりません (ID: {summary_id})\nSummary not found (ID: {summary_id})")
                return

            response = f"🎤 **{summary['audio_file']}** (ID: {summary['id']})\n\n"
            if summary['transcription']:
                response += f"転記 / Transcription:\n{summary['transcription'][:500]}...\n\n"
            response += f"要約 / Summary:\n{summary['summary']}\n\n"
            if summary['key_points']:
                response += f"キーポイント / Key Points:\n{summary['key_points']}\n\n"
            response += f"作成日 / Created: {summary['created_at']}"

            await ctx.send(response[:2000])
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='delete-summary')
    async def delete_summary(self, ctx, summary_id: int):
        """要約を削除 / Delete a summary"""
        try:
            self.db.delete_summary(summary_id)
            await ctx.send(f"🗑️ 要約を削除しました (ID: {summary_id})\nSummary deleted (ID: {summary_id})")
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

if __name__ == '__main__':
    bot = AudioSummarizerAgent()
    import os
    token = os.getenv('DISCORD_BOT_TOKEN')
    bot.run(token)
