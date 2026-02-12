# Monitoring Agent / 監視エージェント

A Discord bot agent for system monitoring, error detection, and performance tracking.

## Features / 機能

- **Metric Recording / メトリック記録**: Track custom metrics with values and units
- **Alert Management / アラート管理**: Create, view, and resolve alerts with severity levels
- **Performance Tracking / パフォーマンス追跡**: Monitor service response times and status
- **Threshold Monitoring / 閾値監視**: Set warning and critical thresholds for metrics
- **System Status Check / システム状態チェック**: Quick overview of system health

## Installation / インストール

```bash
pip install -r requirements.txt
```

## Usage / 使い方

### Commands / コマンド

#### `!monitor` - Monitoring Commands
```
!monitor metric cpu_usage 75 %        # Record a metric
!monitor metric memory 2.4 GB         # Record metric with unit
!monitor alerts                      # View all alerts
!monitor resolve 5                   # Resolve alert ID 5
!monitor performance                 # View performance logs
!monitor threshold cpu_usage 80 95    # Set warning/critical thresholds
```

#### `!check` - System Status
```
!check
```
Display current system status including active alerts and metrics.

#### `!alert` - Create Manual Alert
```
!alert warning service_down "API service is not responding"
!alert critical disk_full "Disk usage at 95%"
```

## Alert Severities / アラート重大度

- `info` - Informational messages
- `warning` - Warning conditions
- `error` - Error conditions
- `critical` - Critical issues requiring immediate attention

## Running the Bot / ボットの実行

```python
import discord
from discord.ext import commands
from agent import MonitoringAgent

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
bot.add_cog(MonitoringAgent(bot))

# Replace with your token
bot.run('YOUR_BOT_TOKEN')
```

## Database Schema / データベース構造

- `metrics`: Stores recorded metrics
- `alerts`: System alerts with severity and resolution status
- `performance_logs`: Service performance data
- `thresholds`: Metric threshold configurations

## Requirements / 要件

- Python 3.8+
- discord.py 2.0+

## License / ライセンス

MIT
