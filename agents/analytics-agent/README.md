# Analytics Agent / 分析エージェント

A Discord bot agent for data analysis, report generation, and visualization creation.

## Features / 機能

- **Data Analysis / データ分析**: Process and analyze JSON data from various sources
- **Report Generation / レポート生成**: Create analytics reports automatically
- **Visualization / 可視化**: Support for multiple chart types (bar, line, pie, scatter)
- **Multi-language Support / 多言語対応**: English and Japanese

## Installation / インストール

```bash
pip install -r requirements.txt
```

## Usage / 使い方

### Commands / コマンド

#### `!analyze` - Analyze Data
```
!analyze {"key": "value"}
!analyze from user_input
```
Analyze JSON data or retrieve data from a specific source.

#### `!report` - Generate Reports
```
!report generate    # Generate a new report
!report list        # List all reports
```

#### `!visualize` - Create Visualizations
```
!visualize bar {"labels": ["A","B"], "values": [10,20]}
!visualize line {"x": [1,2,3], "y": [10,20,30]}
```

## Running the Bot / ボットの実行

```python
import discord
from discord.ext import commands
from agent import AnalyticsAgent

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
bot.add_cog(AnalyticsAgent(bot))

# Replace with your token
bot.run('YOUR_BOT_TOKEN')
```

## Database Schema / データベース構造

- `analytics_data`: Stores analyzed data
- `reports`: Generated reports
- `visualizations`: Saved visualization configurations

## Requirements / 要件

- Python 3.8+
- discord.py 2.0+

## License / ライセンス

MIT
