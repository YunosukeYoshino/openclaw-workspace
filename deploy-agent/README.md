# Deploy Agent

デプロイとロールバック管理のためのDiscordボット

A Discord bot for deployment and rollback management

## Features / 機能

### Core Features
- **環境管理 / Environment Management**: Create and manage deployment environments
- **デプロイ管理 / Deployment Management**: Track and manage deployments
- **デプロイステップ / Deployment Steps**: Monitor deployment step-by-step progress
- **ロールバック / Rollbacks**: Track and perform rollbacks
- **アーティファクト / Artifacts**: Track deployment artifacts (Docker images, files, etc.)
- **設定管理 / Configuration Management**: Manage deployment configurations
- **ヘルスチェック / Health Checks**: Monitor post-deployment health
- **通知 / Notifications**: Track deployment notifications
- **統計 / Statistics**: View deployment statistics and trends
- **自然言語インターフェース / Natural Language Interface**: Interact using natural language

## Installation / インストール

```bash
# Clone the repository
git clone <repository-url>
cd deploy-agent

# Install dependencies
pip install -r requirements.txt

# Set Discord bot token
export DISCORD_TOKEN='your-bot-token-here'

# Run the bot
python discord.py
```

## Database Schema / データベース構造

### Tables / テーブル

#### environments
デプロイ環境を保存 / Stores deployment environments

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key |
| name | TEXT | Unique environment name |
| type | TEXT | Type (development/staging/production/qa) |
| description | TEXT | Environment description |
| url | TEXT | Environment URL |
| branch | TEXT | Default git branch |
| config | TEXT | JSON configuration |
| created_at | TIMESTAMP | Creation time |
| updated_at | TIMESTAMP | Last update time |

#### deployments
デプロイを追跡 / Tracks deployments

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key |
| environment_id | INTEGER | Foreign key to environments |
| version | TEXT | Deployment version |
| build_number | TEXT | Build number |
| git_branch | TEXT | Git branch |
| git_commit | TEXT | Git commit hash |
| git_tag | TEXT | Git tag |
| status | TEXT | Status (pending/in_progress/success/failed/rolled_back) |
| triggered_by | TEXT | User who triggered |
| started_at | TIMESTAMP | Start time |
| completed_at | TIMESTAMP | Completion time |
| duration_seconds | INTEGER | Deployment duration |
| deployed_by | TEXT | User who completed |
| rollback_id | INTEGER | Foreign key to rollbacks |
| notes | TEXT | Deployment notes |
| metadata | TEXT | JSON metadata |

#### deployment_steps
デプロイステップを追跡 / Tracks deployment steps

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key |
| deployment_id | INTEGER | Foreign key to deployments |
| step_name | TEXT | Step name |
| step_type | TEXT | Type (build/test/deploy/verify/rollback) |
| status | TEXT | Status (pending/in_progress/success/failed/skipped) |
| started_at | TIMESTAMP | Start time |
| completed_at | TIMESTAMP | Completion time |
| duration_seconds | INTEGER | Step duration |
| output | TEXT | Step output |
| error_message | TEXT | Error message if failed |
| log_path | TEXT | Path to log file |
| order_index | INTEGER | Step execution order |

#### rollbacks
ロールバックを追跡 / Tracks rollbacks

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key |
| deployment_id | INTEGER | Foreign key to deployments |
| original_deployment_id | INTEGER | Original deployment being rolled back to |
| reason | TEXT | Rollback reason |
| triggered_by | TEXT | User who triggered |
| started_at | TIMESTAMP | Start time |
| completed_at | TIMESTAMP | Completion time |
| status | TEXT | Status (pending/in_progress/success/failed) |
| notes | TEXT | Rollback notes |

#### artifacts
デプロイアーティファクトを保存 / Stores deployment artifacts

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key |
| deployment_id | INTEGER | Foreign key to deployments |
| artifact_name | TEXT | Artifact name |
| artifact_type | TEXT | Type (docker_image/zip/tar/jar/war/other) |
| artifact_path | TEXT | Artifact file path |
| size_bytes | INTEGER | Artifact size in bytes |
| checksum | TEXT | Artifact checksum |
| storage_location | TEXT | Storage location |
| created_at | TIMESTAMP | Creation time |

#### configs
デプロイ設定を保存 / Stores deployment configurations

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key |
| deployment_id | INTEGER | Foreign key to deployments |
| config_key | TEXT | Configuration key |
| config_value | TEXT | Configuration value |
| config_type | TEXT | Type (env_var/secret/config_file/database) |
| is_sensitive | BOOLEAN | Whether value is sensitive |
| created_at | TIMESTAMP | Creation time |

#### health_checks
ヘルスチェックを追跡 / Tracks health checks

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key |
| deployment_id | INTEGER | Foreign key to deployments |
| check_name | TEXT | Check name |
| check_type | TEXT | Type (http/tcp/database/custom) |
| endpoint | TEXT | Endpoint to check |
| expected_status | INTEGER | Expected HTTP status |
| actual_status | INTEGER | Actual HTTP status |
| response_time_ms | INTEGER | Response time in ms |
| status | TEXT | Status (pending/pass/fail) |
| checked_at | TIMESTAMP | Check time |
| notes | TEXT | Additional notes |

#### notifications
通知を追跡 / Tracks notifications

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key |
| deployment_id | INTEGER | Foreign key to deployments |
| notification_type | TEXT | Type (slack/email/discord/webhook) |
| recipient | TEXT | Notification recipient |
| message | TEXT | Notification message |
| sent_at | TIMESTAMP | Sent time |
| status | TEXT | Status (pending/sent/failed) |

## Usage / 使い方

### Natural Language Commands / 自然言語コマンド

```bash
# Environments / 環境
"環境作成 \"Staging\" staging"
"create environment \"Production\" production"
"環境一覧"
"environments"
"list environments"

# Deployments / デプロイ
"デプロイ \"v1.2.3\" staging"
"deploy \"v1.2.4\" production"
"デプロイ開始 \"v2.0.0\""
"start deployment \"v1.0.0\""
"デプロイ中"
"deploying"
"active deployments"
"デプロイ履歴"
"deployment history"
"deploy history"
"デプロイ完了 ID: 123 success"
"deployment complete ID: 456 failed"

# Rollbacks / ロールバック
"ロールバック ID: 123"
"rollback ID: 456"
"ロールバック履歴"
"rollback history"

# Details / 詳細
"アーティファクト"
"artifacts"
"設定"
"configs"
"configuration"
"ヘルスチェック"
"health checks"

# Statistics / 統計
"デプロイ統計"
"deploy stats"
"deployment statistics"

# Help / ヘルプ
"ヘルプ"
"help"
"使い方"
```

### Python API Usage / Python API使用例

```python
from db import (
    create_environment, get_environments,
    start_deployment, complete_deployment, get_deployments,
    add_deployment_step, update_deployment_step, get_deployment_steps,
    start_rollback, complete_rollback, get_rollbacks,
    add_artifact, get_artifacts, add_config, get_configs,
    add_health_check, update_health_check, get_health_checks,
    add_notification, get_notifications, get_deployment_stats
)

# Create environment / 環境作成
env_id = create_environment(
    name='Staging',
    env_type='staging',
    description='Staging environment',
    url='https://staging.example.com',
    branch='develop'
)

# Start deployment / デプロイ開始
deployment_id = start_deployment(
    environment_id=env_id,
    version='v1.2.3',
    triggered_by='admin',
    build_number='build-123',
    git_branch='main',
    git_commit='abc123def',
    git_tag='v1.2.3'
)

# Add deployment steps / デプロイステップ追加
step1 = add_deployment_step(deployment_id, 'Build Docker Image', 'build', 1)
step2 = add_deployment_step(deployment_id, 'Run Tests', 'test', 2)
step3 = add_deployment_step(deployment_id, 'Deploy to Kubernetes', 'deploy', 3)
step4 = add_deployment_step(deployment_id, 'Health Check', 'verify', 4)

# Update step status / ステップステータス更新
update_deployment_step(step1, 'success', output='Build completed successfully')
update_deployment_step(step2, 'success', output='All tests passed')

# Add artifact / アーティファクト追加
add_artifact(
    deployment_id=deployment_id,
    artifact_name='app-image:v1.2.3',
    artifact_type='docker_image',
    size_bytes=150000000,
    checksum='sha256:abc123',
    storage_location='registry.example.com/app:v1.2.3'
)

# Add config / 設定追加
add_config(deployment_id, 'DATABASE_URL', 'postgres://...', 'env_var', is_sensitive=True)
add_config(deployment_id, 'API_KEY', 'secret-key', 'secret', is_sensitive=True)
add_config(deployment_id, 'LOG_LEVEL', 'info', 'env_var')

# Complete deployment / デプロイ完了
complete_deployment(deployment_id, 'success', deployed_by='admin')

# Add health check / ヘルスチェック追加
check_id = add_health_check(
    deployment_id=deployment_id,
    check_name='API Health',
    check_type='http',
    endpoint='https://staging.example.com/health',
    expected_status=200
)

# Update health check / ヘルスチェック更新
update_health_check(check_id, 200, 150, 'pass')

# Rollback / ロールバック
rollback_id = start_rollback(
    deployment_id=deployment_id,
    original_deployment_id=previous_deployment_id,
    triggered_by='admin',
    reason='Critical bug detected'
)

# Get deployment stats / デプロイ統計取得
stats = get_deployment_stats(days=30)
print(f"Success rate: {stats['successful'] / stats['total'] * 100:.1f}%")
```

## Deployment Status / デプロイステータス

### pending
Deployment is queued and waiting to start

### in_progress
Deployment is currently running

### success
Deployment completed successfully

### failed
Deployment failed

### rolled_back
Deployment was rolled back

## Step Types / ステップタイプ

- **Build**: Build artifacts (Docker images, compiled code, etc.)
- **Test**: Run tests (unit, integration, e2e)
- **Deploy**: Deploy to target environment
- **Verify**: Verify deployment (health checks, smoke tests)
- **Rollback**: Rollback deployment

## Environment Variables / 環境変数

```bash
DISCORD_TOKEN=your-bot-token-here
```

## Project Structure / プロジェクト構造

```
deploy-agent/
├── db.py              # Database operations / データベース操作
├── discord.py         # Discord bot / Discordボット
├── requirements.txt   # Dependencies / 依存パッケージ
├── README.md          # This file / このファイル
└── deploy.db          # SQLite database (auto-created) / SQLiteデータベース（自動作成）
```

## Dependencies / 依存パッケージ

See `requirements.txt`

## License / ライセンス

MIT License
