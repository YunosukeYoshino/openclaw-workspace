"""
Automation Agent - Discord Bot
Task automation, workflow creation, and trigger management
"""
import discord
from discord.ext import commands
import json
from datetime import datetime
from typing import Dict, List
from db import AutomationDB

class AutomationAgent(commands.Cog):
    """Automation agent for task automation and workflows"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = AutomationDB()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Automation Agent ready as {self.bot.user}")

    @commands.command(name='task', help='Manage tasks | タスクを管理')
    async def manage_tasks(self, ctx, action: str = None, *, args: str = None):
        """Task management commands"""
        if not action:
            embed = discord.Embed(
                title="Automation Agent / 自動化エージェント",
                description="Commands available / 利用可能なコマンド:\n"
                            "• `!task create <name> <type> <config>` - Create task / タスク作成\n"
                            "• `!task list` - List tasks / タスク一覧\n"
                            "• `!task info <id>` - Task details / タスク詳細\n"
                            "• `!task enable <id>` - Enable task / タスク有効化\n"
                            "• `!task disable <id>` - Disable task / タスク無効化\n\n"
                            "• `!workflow create <name> <steps_json>` - Create workflow / ワークフロー作成\n"
                            "• `!workflow list` - List workflows / ワークフロー一覧\n"
                            "• `!trigger create <name> <type> <config> <target_id>` - Create trigger / トリガー作成\n"
                            "• `!trigger list` - List triggers / トリガー一覧\n"
                            "• `!run <task_id|workflow_id>` - Execute / 実行",
                color=discord.Color.gold()
            )
            await ctx.send(embed=embed)
            return

        if action == 'create':
            if not args:
                await ctx.send("Usage: `!task create <name> <type> <config_json>`\n"
                             "使い方: `!task create <名前> <タイプ> <設定JSON>`")
                return

            parts = args.split(maxsplit=2)
            if len(parts) < 3:
                await ctx.send("❌ Task name, type, and config are required.\n"
                             "タスク名、タイプ、設定が必要です。")
                return

            name = parts[0]
            task_type = parts[1]

            try:
                config = json.loads(parts[2])
            except json.JSONDecodeError:
                await ctx.send("❌ Invalid JSON config.\n設定JSONが正しくありません。")
                return

            task_id = self.db.create_task(name, task_type, config)

            embed = discord.Embed(
                title="Task Created / タスク作成完了",
                color=discord.Color.green()
            )
            embed.add_field(name="Task ID", value=str(task_id), inline=True)
            embed.add_field(name="Name", value=name, inline=True)
            embed.add_field(name="Type", value=task_type, inline=True)

            await ctx.send(embed=embed)

        elif action == 'list':
            tasks = self.db.get_tasks(enabled_only=True)

            if tasks:
                embed = discord.Embed(
                    title="Active Tasks / アクティブなタスク",
                    description=f"Total: {len(tasks)} tasks",
                    color=discord.Color.gold()
                )

                for task in tasks:
                    status = "✅" if task['enabled'] else "❌"
                    embed.add_field(
                        name=f"{status} {task['name']} (ID: {task['id']})",
                        value=f"Type: {task['task_type']} | Created: {task['created_at']}",
                        inline=False
                    )

                await ctx.send(embed=embed)
            else:
                await ctx.send("No active tasks. Use `!task create` to create one.\n"
                             "アクティブなタスクがありません。`!task create`で作成してください。")

        elif action == 'info':
            if not args or not args.isdigit():
                await ctx.send("Usage: `!task info <id>`\n"
                             "使い方: `!task info <ID>`")
                return

            task = self.db.get_task(int(args))

            if task:
                config = json.loads(task['config_json'])

                embed = discord.Embed(
                    title=f"Task: {task['name']}",
                    color=discord.Color.gold()
                )

                embed.add_field(name="Task ID", value=str(task['id']), inline=True)
                embed.add_field(name="Type", value=task['task_type'], inline=True)
                embed.add_field(name="Status", value="Enabled" if task['enabled'] else "Disabled", inline=True)
                embed.add_field(name="Description", value=task['description'] or "N/A", inline=False)
                embed.add_field(name="Configuration", value=f"```json\n{json.dumps(config, indent=2)[:500]}```", inline=False)

                # Show recent executions
                executions = self.db.get_executions(task_id=task['id'], limit=5)
                if executions:
                    exec_text = "\n".join([
                        f"• ID {e['id']}: {e['status']} at {e['started_at']}"
                        for e in executions
                    ])
                    embed.add_field(name="Recent Executions", value=exec_text, inline=False)

                await ctx.send(embed=embed)
            else:
                await ctx.send(f"❌ Task {args} not found.\nタスク {args} が見つかりません。")

        elif action == 'enable':
            if not args or not args.isdigit():
                await ctx.send("Usage: `!task enable <id>`\n"
                             "使い方: `!task enable <ID>`")
                return

            self.db.update_task(int(args), enabled=True)
            await ctx.send(f"✅ Task {args} enabled.\nタスク {args} を有効にしました。")

        elif action == 'disable':
            if not args or not args.isdigit():
                await ctx.send("Usage: `!task disable <id>`\n"
                             "使い方: `!task disable <ID>`")
                return

            self.db.update_task(int(args), enabled=False)
            await ctx.send(f"✅ Task {args} disabled.\nタスク {args} を無効にしました。")

        else:
            await ctx.send("Unknown action. Use `!task` to see available commands.\n"
                         "不明なアクションです。`!task`でコマンドを確認してください。")

    @commands.command(name='workflow', help='Manage workflows | ワークフローを管理')
    async def manage_workflows(self, ctx, action: str = None, *, args: str = None):
        """Workflow management commands"""
        if not action:
            await ctx.send("Usage: `!workflow <create|list>`\n"
                         "使い方: `!workflow <create|list>`")
            return

        if action == 'create':
            if not args:
                await ctx.send("Usage: `!workflow create <name> <steps_json>`\n"
                             "使い方: `!workflow create <名前> <手順JSON>`")
                return

            parts = args.split(maxsplit=1)
            if len(parts) < 2:
                await ctx.send("❌ Workflow name and steps are required.\n"
                             "ワークフロー名と手順が必要です。")
                return

            name = parts[0]

            try:
                steps = json.loads(parts[1])
            except json.JSONDecodeError:
                await ctx.send("❌ Invalid JSON steps.\n手順JSONが正しくありません。")
                return

            workflow_id = self.db.create_workflow(name, steps)

            embed = discord.Embed(
                title="Workflow Created / ワークフロー作成完了",
                color=discord.Color.green()
            )
            embed.add_field(name="Workflow ID", value=str(workflow_id), inline=True)
            embed.add_field(name="Name", value=name, inline=True)
            embed.add_field(name="Steps", value=str(len(steps)), inline=True)

            await ctx.send(embed=embed)

        elif action == 'list':
            workflows = self.db.get_workflows(enabled_only=True)

            if workflows:
                embed = discord.Embed(
                    title="Active Workflows / アクティブなワークフロー",
                    description=f"Total: {len(workflows)} workflows",
                    color=discord.Color.orange()
                )

                for workflow in workflows:
                    steps = json.loads(workflow['steps_json'])
                    status = "✅" if workflow['enabled'] else "❌"
                    embed.add_field(
                        name=f"{status} {workflow['name']} (ID: {workflow['id']})",
                        value=f"Steps: {len(steps)} | Created: {workflow['created_at']}",
                        inline=False
                    )

                await ctx.send(embed=embed)
            else:
                await ctx.send("No active workflows. Use `!workflow create` to create one.\n"
                             "アクティブなワークフローがありません。`!workflow create`で作成してください。")

    @commands.command(name='trigger', help='Manage triggers | トリガーを管理')
    async def manage_triggers(self, ctx, action: str = None, *, args: str = None):
        """Trigger management commands"""
        if not action:
            await ctx.send("Usage: `!trigger <create|list>`\n"
                         "使い方: `!trigger <create|list>`")
            return

        if action == 'create':
            if not args:
                await ctx.send("Usage: `!trigger create <name> <type> <config_json> <target_id>`\n"
                             "使い方: `!trigger create <名前> <タイプ> <設定JSON> <ターゲットID>`")
                return

            parts = args.rsplit(maxsplit=1)
            if len(parts) < 2:
                await ctx.send("❌ All parameters are required.\n全てのパラメータが必要です。")
                return

            config_part = parts[0]
            try:
                target_id = int(parts[1])
            except ValueError:
                await ctx.send("❌ Target ID must be a number.\nターゲットIDは数値である必要があります。")
                return

            config_parts = config_part.split(maxsplit=2)
            if len(config_parts) < 3:
                await ctx.send("❌ Trigger name, type, and config are required.\n"
                             "トリガー名、タイプ、設定が必要です。")
                return

            name = config_parts[0]
            trigger_type = config_parts[1]

            try:
                config = json.loads(config_parts[2])
            except json.JSONDecodeError:
                await ctx.send("❌ Invalid JSON config.\n設定JSONが正しくありません。")
                return

            trigger_id = self.db.create_trigger(name, trigger_type, config, target_task_id=target_id)

            embed = discord.Embed(
                title="Trigger Created / トリガー作成完了",
                color=discord.Color.green()
            )
            embed.add_field(name="Trigger ID", value=str(trigger_id), inline=True)
            embed.add_field(name="Name", value=name, inline=True)
            embed.add_field(name="Type", value=trigger_type, inline=True)
            embed.add_field(name="Target", value=f"Task {target_id}", inline=True)

            await ctx.send(embed=embed)

        elif action == 'list':
            triggers = self.db.get_triggers(enabled_only=True)

            if triggers:
                embed = discord.Embed(
                    title="Active Triggers / アクティブなトリガー",
                    description=f"Total: {len(triggers)} triggers",
                    color=discord.Color.red()
                )

                for trigger in triggers:
                    target = f"Task {trigger['target_task_id']}" if trigger['target_task_id'] else f"Workflow {trigger['target_workflow_id']}"
                    status = "✅" if trigger['enabled'] else "❌"
                    embed.add_field(
                        name=f"{status} {trigger['name']} (ID: {trigger['id']})",
                        value=f"Type: {trigger['trigger_type']} | Target: {target}",
                        inline=False
                    )

                await ctx.send(embed=embed)
            else:
                await ctx.send("No active triggers. Use `!trigger create` to create one.\n"
                             "アクティブなトリガーがありません。`!trigger create`で作成してください。")

    @commands.command(name='run', help='Execute task or workflow | タスクまたはワークフローを実行')
    async def run_automation(self, ctx, target_type: str = None, target_id: int = None):
        """Execute a task or workflow"""
        if not target_type or not target_id:
            await ctx.send("Usage: `!run <task|workflow> <id>`\n"
                         "使い方: `!run <task|workflow> <ID>`")
            return

        if target_type == 'task':
            task = self.db.get_task(target_id)
            if not task:
                await ctx.send(f"❌ Task {target_id} not found.\nタスク {target_id} が見つかりません。")
                return

            # Start execution
            exec_id = self.db.log_execution(task_id=target_id, status='running')

            embed = discord.Embed(
                title=f"Executing Task: {task['name']}",
                color=discord.Color.blue()
            )
            embed.add_field(name="Task ID", value=str(target_id), inline=True)
            embed.add_field(name="Execution ID", value=str(exec_id), inline=True)

            await ctx.send(embed=embed)

            # Simulate execution (in real implementation, execute the task)
            result = {"status": "success", "output": "Task completed successfully"}
            self.db.update_execution(exec_id, status='completed', result=result)

            result_embed = discord.Embed(
                title="Execution Complete / 実行完了",
                description=f"Task {target_id} completed successfully.",
                color=discord.Color.green()
            )
            await ctx.send(embed=result_embed)

        elif target_type == 'workflow':
            workflow = self.db.get_workflow(target_id)
            if not workflow:
                await ctx.send(f"❌ Workflow {target_id} not found.\n"
                             f"ワークフロー {target_id} が見つかりません。")
                return

            # Start execution
            exec_id = self.db.log_execution(workflow_id=target_id, status='running')

            steps = json.loads(workflow['steps_json'])

            embed = discord.Embed(
                title=f"Executing Workflow: {workflow['name']}",
                color=discord.Color.blue()
            )
            embed.add_field(name="Workflow ID", value=str(target_id), inline=True)
            embed.add_field(name="Execution ID", value=str(exec_id), inline=True)
            embed.add_field(name="Total Steps", value=str(len(steps)), inline=True)

            await ctx.send(embed=embed)

            # Simulate execution
            result = {"status": "success", "steps_completed": len(steps)}
            self.db.update_execution(exec_id, status='completed', result=result)

            result_embed = discord.Embed(
                title="Workflow Execution Complete / ワークフロー実行完了",
                description=f"Workflow {target_id} completed {len(steps)} steps successfully.",
                color=discord.Color.green()
            )
            await ctx.send(embed=result_embed)

        else:
            await ctx.send("Invalid type. Use `task` or `workflow`.\n"
                         "無効なタイプです。`task` または `workflow` を使用してください。")

    @commands.command(name='stats', help='Show automation statistics | 統計を表示')
    async def show_statistics(self, ctx):
        """Display automation statistics"""
        stats = self.db.get_statistics()

        embed = discord.Embed(
            title="Automation Statistics / 自動化統計",
            color=discord.Color.blue()
        )

        embed.add_field(name="Total Tasks / 総タスク数", value=str(stats['tasks']['total']), inline=True)
        embed.add_field(name="Enabled Tasks / 有効タスク", value=str(stats['tasks']['enabled']), inline=True)
        embed.add_field(name="Workflows / ワークフロー", value=str(stats['workflows']), inline=True)
        embed.add_field(name="Triggers / トリガー", value=str(stats['triggers']), inline=True)

        if stats['executions']:
            exec_text = "\n".join([
                f"• {status}: {count}"
                for status, count in stats['executions'].items()
            ])
            embed.add_field(name="Executions / 実行回数", value=exec_text, inline=False)

        await ctx.send(embed=embed)

def setup(bot: commands.Bot):
    """Setup function for discord.py"""
    bot.add_cog(AutomationAgent(bot))
