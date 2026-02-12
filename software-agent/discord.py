#!/usr/bin/env python3
"""
Software Agent 77 - Discord Bot Module
Discord Botと自然言語解析によるメッセージ処理モジュール
日本語と英語に対応
"""

import os
import re
import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime

# Discordライブラリ
try:
    import discord
    from discord.ext import commands
except ImportError:
    print("discord.py がインストールされていません")
    print("pip install discord.py")
    exit(1)

# 自然言語処理ライブラリ
try:
    from openai import AsyncOpenAI
except ImportError:
    print("openai がインストールされていません")
    print("pip install openai")
    exit(1)

# データベースモジュール
from db import get_database


# 設定
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

if not DISCORD_TOKEN:
    print("エラー: DISCORD_TOKEN 環境変数が設定されていません")
    exit(1)

if not OPENAI_API_KEY:
    print("警告: OPENAI_API_KEY 環境変数が設定されていません")
    print("自然言語処理機能が制限されます")


class NLPProcessor:
    """自然言語処理クラス"""

    def __init__(self, api_key: str = None):
        self.client = AsyncOpenAI(api_key=api_key or OPENAI_API_KEY) if OPENAI_API_KEY else None

    async def detect_language(self, text: str) -> str:
        """テキストの言語を検出"""
        if not self.client:
            # 簡易的な言語検出
            japanese_chars = len(re.findall(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', text))
            if japanese_chars > len(text) * 0.3:
                return 'ja'
            return 'en'

        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a language detector. Respond with only 'ja' for Japanese, 'en' for English, or 'unknown'."},
                    {"role": "user", "content": text}
                ],
                max_tokens=10
            )
            lang = response.choices[0].message.content.strip().lower()
            return 'ja' if lang == 'ja' else 'en'
        except Exception as e:
            print(f"言語検出エラー: {e}")
            return 'en'

    async def analyze_intent(self, text: str, language: str = 'ja') -> Dict[str, Any]:
        """メッセージの意図を分析"""
        if not self.client:
            return {'intent': 'unknown', 'confidence': 0.5}

        system_prompt = {
            'ja': """あなたは自然言語解析アシスタントです。ユーザーのメッセージを分析し、以下の意図のいずれかを判定してください:

intentの候補:
- question: 質問
- task: タスクの追加・管理
- greeting: 挨拶
- casual: 世間話
- command: コマンド実行
- information: 情報提供の依頼

JSON形式で返してください: {"intent": "intent名", "confidence": 0.0-1.0, "entities": {}}""",
            'en': """You are a natural language processing assistant. Analyze the user's message and determine the intent:

intent candidates:
- question: asking a question
- task: task addition/management
- greeting: greeting
- casual: casual conversation
- command: command execution
- information: requesting information

Respond in JSON format: {"intent": "intent_name", "confidence": 0.0-1.0, "entities": {}}"""
        }

        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt[language]},
                    {"role": "user", "content": text}
                ],
                max_tokens=200,
                response_format={"type": "json_object"}
            )
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            print(f"意図分析エラー: {e}")
            return {'intent': 'unknown', 'confidence': 0.5, 'entities': {}}

    async def generate_response(self, message: str, context: Dict[str, Any],
                                language: str = 'ja') -> str:
        """メッセージに対する応答を生成"""
        if not self.client:
            return self._generate_simple_response(message, language, context)

        system_prompt = {
            'ja': """あなたは親切で役立つAIアシスタントです。ユーザーの質問や依頼に日本語で答えてください。
会話の文脈を考慮して、自然で丁寧な応答を生成してください。
タスク管理や知識検索などの機能も活用してください。""",
            'en': """You are a helpful and friendly AI assistant. Respond to the user's questions or requests in English.
Consider the conversation context and generate natural and polite responses.
Utilize features like task management and knowledge retrieval."""
        }

        # コンテキスト情報の構築
        context_str = ""
        if context.get('recent_messages'):
            context_str += "\nRecent messages:\n" + "\n".join(context['recent_messages'])
        if context.get('tasks'):
            tasks = [f"- {t['title']}" for t in context['tasks']]
            context_str += f"\nUser's tasks:\n" + "\n".join(tasks)
        if context.get('knowledge'):
            context_str += "\nRelevant knowledge:\n" + "\n".join(
                f"- {k['question']}: {k['answer']}" for k in context['knowledge']
            )

        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt[language]},
                    {"role": "user", "content": f"User message: {message}\n\nContext:{context_str}"}
                ],
                max_tokens=500
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"応答生成エラー: {e}")
            return self._generate_simple_response(message, language, context)

    def _generate_simple_response(self, message: str, language: str,
                                  context: Dict[str, Any]) -> str:
        """簡易応答生成（OpenAI APIなしの場合）"""
        responses = {
            'ja': {
                'question': "質問ありがとうございます。少し詳しく教えていただけますか？",
                'task': "タスクを記録しました。",
                'greeting': "こんにちは！何かお手伝いできることはありますか？",
                'casual': "なるほど、ですね。",
                'command': "コマンドを受け付けました。",
                'default': "メッセージを受け取りました。"
            },
            'en': {
                'question': "Thank you for your question. Could you provide more details?",
                'task': "Task has been recorded.",
                'greeting': "Hello! How can I help you today?",
                'casual': "I see.",
                'command': "Command received.",
                'default': "Message received."
            }
        }
        return responses[language].get('default', responses[language]['default'])


class SoftwareAgent77(commands.Bot):
    """Software Agent 77 Discord Bot"""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.messages = True
        intents.guilds = True
        intents.members = True

        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None
        )

        self.db = get_database()
        self.nlp = NLPProcessor()

    async def on_ready(self):
        """Bot起動時"""
        print(f'{self.user.name} が起動しました (ID: {self.user.id})')
        print('------')
        activity = discord.Activity(
            type=discord.ActivityType.listening,
            name="/help でヘルプを表示"
        )
        await self.change_presence(activity=activity)

    async def on_message(self, message: discord.Message):
        """メッセージ受信時の処理"""
        # Bot自身のメッセージは無視
        if message.author.bot:
            return

        # コマンド処理
        await self.process_commands(message)

        # 自然言語処理による応答
        await self.process_natural_language(message)

    async def process_natural_language(self, message: discord.Message):
        """自然言語処理によるメッセージ処理"""
        try:
            # ユーザー情報の登録・更新
            self.db.add_or_update_user(
                str(message.author.id),
                message.author.name,
                language='ja'  # デフォルトは日本語、後で検出で更新
            )

            # 言語検出
            language = await self.nlp.detect_language(message.content)
            print(f"検出された言語: {language}")

            # 意図分析
            intent_result = await self.nlp.analyze_intent(message.content, language)
            print(f"意図分析: {intent_result}")

            # メッセージをデータベースに保存
            self.db.save_message(
                str(message.author.id),
                str(message.channel.id),
                message.content,
                language=language,
                intent=intent_result.get('intent', 'unknown'),
                metadata=intent_result.get('entities', {})
            )

            # コンテキストの構築
            context = {
                'recent_messages': [],
                'tasks': [],
                'knowledge': []
            }

            # 最近のメッセージ履歴を取得
            recent = self.db.get_recent_messages(
                str(message.author.id),
                str(message.channel.id),
                limit=5
            )
            context['recent_messages'] = [
                f"{msg['content']}" for msg in recent[:3]
            ]

            # タスク処理
            if intent_result.get('intent') == 'task':
                # タスクとして保存
                self.db.add_task(
                    str(message.author.id),
                    message.content[:100],
                    description=message.content
                )

            # タスクリストを取得
            tasks = self.db.get_tasks(str(message.author.id), status='pending')
            context['tasks'] = tasks[:5]

            # 知識検索（質問の場合）
            if intent_result.get('intent') == 'question':
                knowledge = self.db.search_knowledge(message.content[:50], language)
                if knowledge:
                    context['knowledge'] = knowledge[:3]

            # 応答生成
            response = await self.nlp.generate_response(message.content, context, language)

            # 送信
            if response and response.strip():
                async with message.channel.typing():
                    await asyncio.sleep(1)  # 入力中の演出
                    await message.channel.send(response[:2000])  # Discordの制限

            # コンテキストを保存
            self.db.save_context(
                str(message.author.id),
                str(message.channel.id),
                context
            )

        except Exception as e:
            print(f"自然言語処理エラー: {e}")
            import traceback
            traceback.print_exc()

    @commands.command(name='help', aliases=['h'])
    async def help_command(self, ctx):
        """ヘルプコマンド"""
        user = self.db.get_user(str(ctx.author.id))
        language = user.get('language', 'ja') if user else 'ja'

        if language == 'ja':
            help_text = """
**Software Agent 77 - ヘルプ**

🤖 **自然言語処理**
- メッセージを送るだけで自動的に応答します
- 日本語と英語に対応しています

📋 **主な機能**
- タスク管理: 「明日のタスクを追加」など
- 質問応答: 知識ベースから回答を検索
- 会話履歴: 過去の会話を記憶

📊 **コマンド**
- `/stats` - 統計情報を表示
- `/tasks` - タスク一覧を表示
- `/lang [ja|en]` - 言語を切り替え
- `/reset` - 会話コンテキストをリセット

💡 **ヒント**
- 自然な文章で話しかけてください
- メンション(@)は不要です
"""
        else:
            help_text = """
**Software Agent 77 - Help**

🤖 **Natural Language Processing**
- Just send a message and I'll respond automatically
- Supports Japanese and English

📋 **Main Features**
- Task Management: "Add a task for tomorrow"
- Q&A: Search knowledge base for answers
- Conversation History: Remembers past conversations

📊 **Commands**
- `/stats` - Show statistics
- `/tasks` - Show task list
- `/lang [ja|en]` - Switch language
- `/reset` - Reset conversation context

💡 **Tips**
- Just chat naturally
- No need to mention me (@)
"""

        await ctx.send(help_text)

    @commands.command(name='stats', aliases=['s'])
    async def stats_command(self, ctx):
        """統計情報コマンド"""
        stats = self.db.get_stats()
        user = self.db.get_user(str(ctx.author.id))
        language = user.get('language', 'ja') if user else 'ja'

        if language == 'ja':
            stats_text = f"""📊 **統計情報**

👥 ユーザー数: {stats['total_users']}
💬 メッセージ数: {stats['total_messages']}
📚 知識数: {stats['total_knowledge']}
✅ 完了タスク: {stats['completed_tasks']}
⏳ 未完了タスク: {stats['pending_tasks']}
"""
        else:
            stats_text = f"""📊 **Statistics**

👥 Users: {stats['total_users']}
💬 Messages: {stats['total_messages']}
📚 Knowledge: {stats['total_knowledge']}
✅ Completed Tasks: {stats['completed_tasks']}
⏳ Pending Tasks: {stats['pending_tasks']}
"""

        await ctx.send(stats_text)

    @commands.command(name='tasks', aliases=['t'])
    async def tasks_command(self, ctx):
        """タスクリストコマンド"""
        tasks = self.db.get_tasks(str(ctx.author.id), status='pending')
        user = self.db.get_user(str(ctx.author.id))
        language = user.get('language', 'ja') if user else 'ja'

        if not tasks:
            if language == 'ja':
                await ctx.send("📋 未完了のタスクはありません")
            else:
                await ctx.send("📋 No pending tasks")
            return

        if language == 'ja':
            task_list = "📋 **未完了タスク**\n\n"
        else:
            task_list = "📋 **Pending Tasks**\n\n"

        for i, task in enumerate(tasks[:10], 1):
            task_list += f"{i}. {task['title']}\n"
            if task['description']:
                task_list += f"   {task['description'][:50]}...\n"
            task_list += "\n"

        await ctx.send(task_list[:2000])

    @commands.command(name='lang')
    async def lang_command(self, ctx, lang: str = None):
        """言語切り替えコマンド"""
        user = self.db.get_user(str(ctx.author.id))
        current_lang = user.get('language', 'ja') if user else 'ja'

        if lang not in ['ja', 'en']:
            if current_lang == 'ja':
                await ctx.send("使用方法: `/lang [ja|en]`\n現在の設定: 日本語")
            else:
                await ctx.send("Usage: `/lang [ja|en]`\nCurrent: English")
            return

        self.db.add_or_update_user(str(ctx.author.id), ctx.author.name, language=lang)

        if lang == 'ja':
            await ctx.send("言語を日本語に設定しました 🇯🇵")
        else:
            await ctx.send("Language set to English 🇬🇧")

    @commands.command(name='reset')
    async def reset_command(self, ctx):
        """コンテキストリセットコマンド"""
        # 現在のコンテキストを削除
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM contexts
            WHERE discord_id = ? AND channel_id = ?
        """, (str(ctx.author.id), str(ctx.channel.id)))
        conn.commit()
        conn.close()

        user = self.db.get_user(str(ctx.author.id))
        language = user.get('language', 'ja') if user else 'ja'

        if language == 'ja':
            await ctx.send("会話コンテキストをリセットしました 🔄")
        else:
            await ctx.send("Conversation context reset 🔄")


def main():
    """Botの起動"""
    bot = SoftwareAgent77()
    bot.run(DISCORD_TOKEN)


if __name__ == '__main__':
    main()
