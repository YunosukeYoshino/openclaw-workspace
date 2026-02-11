"""
Assistant Agent - Discord Bot
General Q&A, multi-agent integration, and context management
"""
import discord
from discord.ext import commands
import re
from typing import Dict, List
from db import AssistantDB

class AssistantAgent(commands.Cog):
    """Assistant agent for general Q&A and multi-agent integration"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = AssistantDB()
        self.supported_languages = ['en', 'ja']

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Assistant Agent ready as {self.bot.user}")

        # Initialize agent commands
        self._initialize_agent_commands()

    @commands.Cog.listener()
    async def on_message(self, message):
        """Handle incoming messages for context"""
        if message.author.bot:
            return

        # Only process non-command messages
        if not message.content.startswith('!'):
            # Get or create conversation
            conv_id = self.db.get_or_create_conversation(
                user_id=str(message.author.id),
                channel_id=str(message.channel.id),
                language=self._detect_language(message.content)
            )

            # Save user message
            self.db.save_message(conv_id, 'user', message.content)

    def _detect_language(self, text: str) -> str:
        """Simple language detection"""
        # Check for Japanese characters
        if re.search(r'[\u3040-\u309F\u30A0-\u30FF]', text):
            return 'ja'
        return 'en'

    def _initialize_agent_commands(self):
        """Initialize commands for other agents"""
        # Analytics Agent commands
        self.db.add_agent_command('analytics', '!analyze', 'Analyze data | データを分析', 'en')
        self.db.add_agent_command('analytics', '!report', 'Generate reports | レポートを生成', 'en')
        self.db.add_agent_command('analytics', '!visualize', 'Create visualizations | 可視化を作成', 'en')

        # Monitoring Agent commands
        self.db.add_agent_command('monitoring', '!monitor', 'Monitor system | システムを監視', 'en')
        self.db.add_agent_command('monitoring', '!check', 'Check status | 状態をチェック', 'en')
        self.db.add_agent_command('monitoring', '!alert', 'Create alerts | アラートを作成', 'en')

        # Integration Agent commands
        self.db.add_agent_command('integration', '!service', 'Manage services | サービスを管理', 'en')
        self.db.add_agent_command('integration', '!sync', 'Manage data sync | データ同期を管理', 'en')
        self.db.add_agent_command('integration', '!webhook', 'Manage webhooks | Webhookを管理', 'en')

        # Automation Agent commands
        self.db.add_agent_command('automation', '!task', 'Manage tasks | タスクを管理', 'en')
        self.db.add_agent_command('automation', '!workflow', 'Manage workflows | ワークフローを管理', 'en')
        self.db.add_agent_command('automation', '!trigger', 'Manage triggers | トリガーを管理', 'en')
        self.db.add_agent_command('automation', '!run', 'Execute automation | 自動化を実行', 'en')

        # Knowledge base entries
        self.db.add_knowledge('general', 'what can you do', 'I can help you with data analysis, monitoring, integration, automation, and general questions. / データ分析、監視、統合、自動化、一般的な質問をサポートします。', 'en')
        self.db.add_knowledge('general', 'how to analyze data', 'Use !analyze <json_data> or !analyze from <source>. / !analyze <json_data> または !analyze from <source> を使用してください。', 'en')

    @commands.command(name='ask', help='Ask a question | 質問する')
    async def ask_question(self, ctx, *, question: str = None):
        """Ask the assistant a question"""
        if not question:
            await ctx.send("Please ask a question. / 質問を入力してください。")
            return

        # Detect language
        language = self._detect_language(question)

        # Get or create conversation
        conv_id = self.db.get_or_create_conversation(
            user_id=str(ctx.author.id),
            channel_id=str(ctx.channel.id),
            language=language
        )

        # Save user message
        self.db.save_message(conv_id, 'user', question)

        # Search knowledge base
        kb_results = self.db.search_knowledge(question, language=language, limit=3)

        # Generate response
        if kb_results:
            # Found in knowledge base
            response = kb_results[0]['answer']
        else:
            # General response
            if language == 'ja':
                response = f"質問ありがとうございます: 「{question}」\n"
                response += "利用可能なエージェント:\n"
                response += "• Analytics - データ分析とレポート\n"
                response += "• Monitoring - システム監視\n"
                response += "• Integration - サービス統合\n"
                response += "• Automation - タスク自動化\n"
                response += "\n`!help` で全コマンドを確認できます。"
            else:
                response = f"Thank you for your question: \"{question}\"\n"
                response += "Available agents:\n"
                response += "• Analytics - Data analysis and reports\n"
                response += "• Monitoring - System monitoring\n"
                response += "• Integration - Service integration\n"
                response += "• Automation - Task automation\n"
                response += "\nUse `!help` to see all commands."

        # Save assistant response
        self.db.save_message(conv_id, 'assistant', response)

        embed = discord.Embed(
            title="Assistant Response / アシスタントの応答",
            description=response,
            color=discord.Color.green()
        )

        await ctx.send(embed=embed)

    @commands.command(name='agents', help='List available agents | 利用可能なエージェント一覧')
    async def list_agents(self, ctx):
        """List all available agents and their commands"""
        commands = self.db.get_agent_commands()

        if not commands:
            await ctx.send("No agents configured.\nエージェントが設定されていません。")
            return

        # Group by agent
        agents = {}
        for cmd in commands:
            agent = cmd['agent_name']
            if agent not in agents:
                agents[agent] = []
            agents[agent].append(cmd)

        embed = discord.Embed(
            title="Available Agents / 利用可能なエージェント",
            description=f"Total: {len(agents)} agents",
            color=discord.Color.blue()
        )

        for agent_name, agent_commands in agents.items():
            cmd_list = "\n".join([
                f"• {cmd['command']} - {cmd['description']}"
                for cmd in agent_commands
            ])
            embed.add_field(
                name=agent_name.capitalize(),
                value=cmd_list,
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name='context', help='Manage conversation context | 会話コンテキストを管理')
    async def manage_context(self, ctx, action: str = None, *, args: str = None):
        """Manage conversation context"""
        # Get conversation
        conv_id = self.db.get_or_create_conversation(
            user_id=str(ctx.author.id),
            channel_id=str(ctx.channel.id)
        )

        if not action:
            context = self.db.get_context(conv_id)

            if context:
                embed = discord.Embed(
                    title="Conversation Context / 会話コンテキスト",
                    description=f"Total keys: {len(context)}",
                    color=discord.Color.purple()
                )

                for key, value in context.items():
                    embed.add_field(name=key, value=str(value)[:1024], inline=False)

                await ctx.send(embed=embed)
            else:
                await ctx.send("No context set. Use `!context set <key> <value>`\n"
                             "コンテキストが設定されていません。`!context set <キー> <値>` を使用してください。")
            return

        if action == 'set':
            if not args:
                await ctx.send("Usage: `!context set <key> <value>`\n"
                             "使い方: `!context set <キー> <値>`")
                return

            parts = args.split(maxsplit=1)
            if len(parts) < 2:
                await ctx.send("❌ Key and value are required.\nキーと値が必要です。")
                return

            key = parts[0]
            value = parts[1]

            self.db.set_context(conv_id, key, value)
            await ctx.send(f"✅ Context set: {key} = {value}")

        elif action == 'get':
            if not args:
                await ctx.send("Usage: `!context get <key>`\n"
                             "使い方: `!context get <キー>`")
                return

            context = self.db.get_context(conv_id)
            value = context.get(args)

            if value is not None:
                await ctx.send(f"{args}: {value}")
            else:
                await ctx.send(f"❌ Context key '{args}' not found.\n"
                             f"コンテキストキー '{args}' が見つかりません。")

        elif action == 'clear':
            # Clear specific key or all context
            if args:
                # Clear specific key (implementation would need delete method)
                await ctx.send(f"ℹ️ Clearing context keys requires implementation.\n"
                             f"コンテキストキーのクリアは実装が必要です。")
            else:
                # Clear all context
                await ctx.send("ℹ️ Clearing all context requires implementation.\n"
                             "すべてのコンテキストのクリアは実装が必要です。")

    @commands.command(name='history', help='View conversation history | 会話履歴を表示')
    async def view_history(self, ctx, limit: int = 10):
        """View conversation history"""
        conv_id = self.db.get_or_create_conversation(
            user_id=str(ctx.author.id),
            channel_id=str(ctx.channel.id)
        )

        messages = self.db.get_conversation_messages(conv_id, limit=limit)

        if not messages:
            await ctx.send("No conversation history.\n会話履歴がありません。")
            return

        embed = discord.Embed(
            title="Conversation History / 会話履歴",
            description=f"Total messages: {len(messages)}",
            color=discord.Color.blue()
        )

        for msg in messages[:10]:
            role_emoji = "👤" if msg['role'] == 'user' else "🤖"
            embed.add_field(
                name=f"{role_emoji} {msg['role'].title()}",
                value=f"{msg['content'][:200]}...\n{msg['timestamp']}",
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name='kb', help='Knowledge base management | 知識ベースを管理')
    async def manage_knowledge(self, ctx, action: str = None, *, args: str = None):
        """Manage knowledge base"""
        if not action:
            await ctx.send("Usage: `!kb <search|add>`\n"
                         "使い方: `!kb <search|add>`")
            return

        if action == 'search':
            if not args:
                await ctx.send("Usage: `!kb search <query>`\n"
                             "使い方: `!kb search <検索クエリ>`")
                return

            results = self.db.search_knowledge(args, language='en', limit=5)

            if results:
                embed = discord.Embed(
                    title=f"Knowledge Base Results / 知識ベース検索結果",
                    description=f"Query: {args} | Found: {len(results)}",
                    color=discord.Color.blue()
                )

                for result in results:
                    embed.add_field(
                        name=f"Q: {result['question']}",
                        value=f"A: {result['answer'][:300]}...",
                        inline=False
                    )

                await ctx.send(embed=embed)
            else:
                await ctx.send("No results found.\n結果が見つかりませんでした。")

        elif action == 'add':
            await ctx.send("ℹ️ Adding to knowledge base requires admin permissions.\n"
                         "知識ベースへの追加には管理者権限が必要です。")

    @commands.command(name='help', help='Show help / ヘルプを表示')
    async def show_help(self, ctx):
        """Show help for assistant commands"""
        embed = discord.Embed(
            title="Assistant Agent Help / アシスタントエージェントヘルプ",
            description="Commands available / 利用可能なコマンド:",
            color=discord.Color.green()
        )

        embed.add_field(name="!ask <question>", value="Ask a question / 質問する", inline=False)
        embed.add_field(name="!agents", value="List all agents / 全エージェント一覧", inline=False)
        embed.add_field(name="!context [set|get]", value="Manage context / コンテキスト管理", inline=False)
        embed.add_field(name="!history [limit]", value="View conversation history / 会話履歴を表示", inline=False)
        embed.add_field(name="!kb search <query>", value="Search knowledge base / 知識ベース検索", inline=False)
        embed.add_field(name="!stats", value="Show statistics / 統計を表示", inline=False)

        await ctx.send(embed=embed)

    @commands.command(name='stats', help='Show statistics | 統計を表示')
    async def show_statistics(self, ctx):
        """Display assistant statistics"""
        stats = self.db.get_conversation_stats()

        embed = discord.Embed(
            title="Assistant Statistics / アシスタント統計",
            color=discord.Color.blue()
        )

        embed.add_field(name="Conversations / 会話数", value=str(stats['conversations']), inline=True)
        embed.add_field(name="Messages / メッセージ数", value=str(stats['messages']), inline=True)
        embed.add_field(name="Agent Commands / エージェントコマンド", value=str(stats['agent_commands']), inline=True)
        embed.add_field(name="Knowledge Entries / 知識ベースエントリー", value=str(stats['knowledge_entries']), inline=True)

        await ctx.send(embed=embed)

def setup(bot: commands.Bot):
    """Setup function for discord.py"""
    bot.add_cog(AssistantAgent(bot))
