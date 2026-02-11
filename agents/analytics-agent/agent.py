"""
Analytics Agent - Discord Bot
Data analysis, report generation, and visualization
"""
import discord
from discord.ext import commands
import json
import re
from datetime import datetime
from typing import Dict, List
from db import AnalyticsDB

class AnalyticsAgent(commands.Cog):
    """Analytics agent for data analysis and reporting"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = AnalyticsDB()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Analytics Agent ready as {self.bot.user}")

    @commands.command(name='analyze', help='Analyze data | データを分析')
    async def analyze_data(self, ctx, *, args: str = None):
        """
        Analyze data from various sources
        Usage: !analyze <json_data> or !analyze from <source>
        """
        if not args:
            embed = discord.Embed(
                title="Analytics Agent / 分析エージェント",
                description="Commands available / 利用可能なコマンド:\n"
                            "• `!analyze <json_data>` - Analyze JSON data / JSONデータを分析\n"
                            "• `!analyze from <source>` - Get data from source / ソースからデータを取得\n"
                            "• `!report generate` - Generate report / レポートを生成\n"
                            "• `!visualize <chart_type>` - Create visualization / 可視化を作成",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)
            return

        # Try to parse as JSON data
        if not args.startswith('from '):
            try:
                data = json.loads(args)

                # Store and analyze
                data_id = self.db.store_data(
                    source="user_input",
                    data_type="manual",
                    data=data
                )

                # Basic analysis
                analysis = self._perform_basic_analysis(data)

                embed = discord.Embed(
                    title="Analysis Complete / 分析完了",
                    description=f"Data ID: {data_id}",
                    color=discord.Color.green()
                )

                for key, value in analysis.items():
                    embed.add_field(name=key, value=str(value)[:1024], inline=False)

                await ctx.send(embed=embed)

            except json.JSONDecodeError:
                await ctx.send("❌ Invalid JSON format. Please provide valid JSON data.\n"
                             "JSON形式が正しくありません。有効なJSONを入力してください。")

        else:
            # Get data from source
            source = args[5:]
            data = self.db.get_data(source=source, limit=10)

            if data:
                embed = discord.Embed(
                    title=f"Data from {source} / {source}からのデータ",
                    description=f"Found {len(data)} records / {len(data)}件見つかりました",
                    color=discord.Color.blue()
                )

                for record in data[:5]:
                    embed.add_field(
                        name=f"ID: {record['id']}",
                        value=f"Type: {record['data_type']} | Time: {record['timestamp']}",
                        inline=False
                    )

                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ No data found for this source.\nこのソースのデータが見つかりません。")

    @commands.command(name='report', help='Generate reports | レポートを生成')
    async def manage_reports(self, ctx, action: str = None, *, args: str = None):
        """Manage analytics reports"""
        if action == 'generate':
            # Generate a report from recent data
            data = self.db.get_data(limit=50)

            if not data:
                await ctx.send("❌ No data available for report generation.\n"
                             "レポート生成に使用できるデータがありません。")
                return

            report_content = self._generate_report_content(data)
            report_id = self.db.create_report(
                title=f"Analytics Report {datetime.now().strftime('%Y%m%d')}",
                content=json.dumps(report_content),
                description="Auto-generated analytics report"
            )

            embed = discord.Embed(
                title="Report Generated / レポート生成完了",
                description=f"Report ID: {report_id}\nTotal records analyzed: {len(data)}",
                color=discord.Color.green()
            )

            await ctx.send(embed=embed)

        elif action == 'list':
            reports = self.db.get_reports()

            if reports:
                embed = discord.Embed(
                    title="Available Reports / 利用可能なレポート",
                    description=f"Total: {len(reports)} reports",
                    color=discord.Color.blue()
                )

                for report in reports[:5]:
                    embed.add_field(
                        name=f"{report['title']} (ID: {report['id']})",
                        value=f"Status: {report['status']} | Created: {report['created_at']}",
                        inline=False
                    )

                await ctx.send(embed=embed)
            else:
                await ctx.send("No reports found. Use `!report generate` to create one.\n"
                             "レポートがありません。`!report generate`で作成できます。")

        else:
            await ctx.send("Usage: `!report <generate|list>`\n"
                         "使い方: `!report <generate|list>`")

    @commands.command(name='visualize', help='Create visualizations | 可視化を作成')
    async def create_visualization(self, ctx, chart_type: str = None, *, data_json: str = None):
        """Create data visualizations"""
        if not chart_type:
            embed = discord.Embed(
                title="Visualization Types / 可視化タイプ",
                description="Supported chart types:\n"
                            "• `bar` - Bar chart / 棒グラフ\n"
                            "• `line` - Line chart / 折れ線グラフ\n"
                            "• `pie` - Pie chart / 円グラフ\n"
                            "• `scatter` - Scatter plot / 散布図\n\n"
                            "Usage: `!visualize <type> <json_data>`",
                color=discord.Color.purple()
            )
            await ctx.send(embed=embed)
            return

        if not data_json:
            await ctx.send("❌ Please provide JSON data for visualization.\n"
                         "可視化用のJSONデータを入力してください。")
            return

        try:
            data = json.loads(data_json)
            viz_id = self.db.save_visualization(
                title=f"{chart_type.title()} Chart {datetime.now().strftime('%Y%m%d')}",
                chart_type=chart_type,
                data=data,
                config={"style": "default"}
            )

            embed = discord.Embed(
                title="Visualization Created / 可視化作成完了",
                description=f"Visualization ID: {viz_id}\nType: {chart_type}",
                color=discord.Color.purple()
            )

            embed.add_field(
                name="Data Preview / データプレビュー",
                value=f"```json\n{json.dumps(data, indent=2)[:500]}\n```",
                inline=False
            )

            await ctx.send(embed=embed)

        except json.JSONDecodeError:
            await ctx.send("❌ Invalid JSON format.\nJSON形式が正しくありません。")

    def _perform_basic_analysis(self, data: Dict) -> Dict:
        """Perform basic data analysis"""
        results = {}

        if isinstance(data, dict):
            results["Field Count / フィールド数"] = len(data)
            results["Keys / キー"] = ", ".join(list(data.keys())[:10])

        elif isinstance(data, list):
            results["Record Count / レコード数"] = len(data)
            if data and isinstance(data[0], dict):
                results["Fields / フィールド"] = ", ".join(list(data[0].keys())[:10])

        return results

    def _generate_report_content(self, data: List[Dict]) -> Dict:
        """Generate report content from data"""
        sources = {}
        types = {}

        for record in data:
            source = record['source']
            dtype = record['data_type']
            sources[source] = sources.get(source, 0) + 1
            types[dtype] = types.get(dtype, 0) + 1

        return {
            "summary": {
                "total_records": len(data),
                "sources": sources,
                "data_types": types,
                "generated_at": datetime.now().isoformat()
            },
            "records": data[:20]  # Include first 20 records
        }

def setup(bot: commands.Bot):
    """Setup function for discord.py"""
    bot.add_cog(AnalyticsAgent(bot))
