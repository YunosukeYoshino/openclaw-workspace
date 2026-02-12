# Test Agent

テストケースとテスト結果管理のためのDiscordボット

A Discord bot for test cases and results management

## Features / 機能

### Core Features
- **テストスイート管理 / Test Suite Management**: Create and manage test suites
- **テストケース管理 / Test Case Management**: Create and organize test cases
- **テスト実行 / Test Execution**: Track test runs and execution status
- **テスト結果 / Test Results**: View and analyze test results
- **カバレッジ / Coverage**: Track code coverage metrics
- **課題管理 / Issue Management**: Track test-related issues (flaky, slow, bugs)
- **統計 / Statistics**: View test summary statistics
- **自然言語インターフェース / Natural Language Interface**: Interact using natural language

## Installation / インストール

```bash
# Clone the repository
git clone <repository-url>
cd test-agent

# Install dependencies
pip install -r requirements.txt

# Set Discord bot token
export DISCORD_TOKEN='your-bot-token-here'

# Run the bot
python discord.py
```

## Database Schema / データベース構造

### Tables / テーブル

#### test_suites
テストスイートを保存 / Stores test suites

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key |
| name | TEXT | Unique suite name |
| description | TEXT | Suite description |
| component | TEXT | Component being tested |
| tags | TEXT | JSON tags |
| created_at | TIMESTAMP | Creation time |
| updated_at | TIMESTAMP | Last update time |

#### test_cases
テストケースを保存 / Stores test cases

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key |
| suite_id | INTEGER | Foreign key to test_suites |
| name | TEXT | Test case name |
| description | TEXT | Test description |
| test_type | TEXT | Type (unit/integration/functional/e2e/performance/security) |
| priority | TEXT | Priority (low/medium/high/critical) |
| status | TEXT | Status (active/deprecated/archived) |
| preconditions | TEXT | Test preconditions |
| steps | TEXT | Test steps |
| expected_result | TEXT | Expected result |
| tags | TEXT | JSON tags |
| created_at | TIMESTAMP | Creation time |
| updated_at | TIMESTAMP | Last update time |

#### test_runs
テスト実行を追跡 / Tracks test executions

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key |
| name | TEXT | Run name |
| environment | TEXT | Test environment |
| build_version | TEXT | Build version |
| branch | TEXT | Git branch |
| commit_hash | TEXT | Git commit hash |
| triggered_by | TEXT | Who triggered the run |
| started_at | TIMESTAMP | Start time |
| completed_at | TIMESTAMP | Completion time |
| status | TEXT | Status (running/completed/failed/aborted) |
| total_tests | INTEGER | Total test count |
| passed | INTEGER | Passed count |
| failed | INTEGER | Failed count |
| skipped | INTEGER | Skipped count |

#### test_results
テスト結果を保存 / Stores test results

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key |
| run_id | INTEGER | Foreign key to test_runs |
| case_id | INTEGER | Foreign key to test_cases |
| status | TEXT | Status (passed/failed/skipped/error) |
| duration_ms | INTEGER | Execution time in milliseconds |
| error_message | TEXT | Error message if failed |
| stack_trace | TEXT | Stack trace if failed |
| screenshots | TEXT | JSON of screenshot paths |
| logs | TEXT | JSON of log data |
| retry_count | INTEGER | Number of retries |
| started_at | TIMESTAMP | Start time |
| completed_at | TIMESTAMP | Completion time |

#### test_data
テストデータを保存 / Stores test data

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key |
| case_id | INTEGER | Foreign key to test_cases |
| data_name | TEXT | Data name |
| data_value | TEXT | Data value |
| data_type | TEXT | Type (input/expected/config/fixture) |

#### test_coverage
テストカバレッジを保存 / Stores coverage data

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key |
| run_id | INTEGER | Foreign key to test_runs |
| component | TEXT | Component name |
| file_path | TEXT | File path |
| line_coverage | INTEGER | Line coverage percentage |
| branch_coverage | INTEGER | Branch coverage percentage |
| function_coverage | INTEGER | Function coverage percentage |
| total_lines | INTEGER | Total lines |
| covered_lines | INTEGER | Covered lines |
| total_branches | INTEGER | Total branches |
| covered_branches | INTEGER | Covered branches |
| calculated_at | TIMESTAMP | Calculation time |

#### test_issues
テスト課題を追跡 / Tracks test issues

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key |
| result_id | INTEGER | Foreign key to test_results |
| title | TEXT | Issue title |
| description | TEXT | Issue description |
| severity | TEXT | Severity (low/medium/high/critical) |
| issue_type | TEXT | Type (flaky/slow/bug/performance/security/environment) |
| status | TEXT | Status (open/investigating/fixed/wontfix/duplicate) |
| jira_id | TEXT | JIRA ticket ID |
| fixed_in_version | TEXT | Fixed version |
| created_at | TIMESTAMP | Creation time |
| resolved_at | TIMESTAMP | Resolution time |

## Usage / 使い方

### Natural Language Commands / 自然言語コマンド

```bash
# Test Suites / テストスイート
"スイート作成 \"Authentication Suite\" \"Tests for authentication module\""
"テストスイート作成 \"API Tests\""
"create suite \"User Management\""
"スイート一覧"
"test suites"
"list suites"

# Test Cases / テストケース
"ケース作成 \"Login Test\" - スイートID: 1"
"テストケース作成 \"User Registration\""
"create case \"API Error Handling\" - high priority"
"create unit test \"Calculate Discount\""
"テストケース"
"cases"
"list cases"

# Test Runs / テスト実行
"テスト実行 \"Smoke Test\""
"start test \"Regression Test\" staging"
"テスト開始 \"E2E Test\" - staging environment"
"テスト実行中"
"running tests"
"test results"
"results"

# Coverage / カバレッジ
"カバレッジ"
"coverage"
"test coverage"

# Issues / 課題
"テスト課題"
"test issues"
"issues"
"課題解決 ID: 123"
"resolve issue ID: 456"

# Summary / 概要
"テスト概要"
"test summary"
"summary"

# Help / ヘルプ
"ヘルプ"
"help"
"使い方"
```

### Python API Usage / Python API使用例

```python
from db import (
    create_suite, get_suites, create_case, get_cases,
    start_test_run, complete_test_run, add_test_result, get_test_results,
    add_test_data, get_test_data, save_coverage, get_coverage,
    create_test_issue, get_test_issues, resolve_issue, get_test_summary
)

# Create test suite / テストスイート作成
suite_id = create_suite(
    name='Authentication',
    description='Tests for authentication module',
    component='auth'
)

# Create test case / テストケース作成
case_id = create_case(
    suite_id=suite_id,
    name='Login with valid credentials',
    description='Test successful login',
    test_type='functional',
    priority='high',
    steps='1. Enter valid username\n2. Enter valid password\n3. Click login',
    expected_result='User is logged in and redirected to dashboard'
)

# Add test data / テストデータ追加
add_test_data(case_id, 'username', 'testuser@example.com', 'input')
add_test_data(case_id, 'password', 'SecurePass123', 'input')

# Start test run / テスト実行開始
run_id = start_test_run(
    name='Nightly Build Test',
    environment='staging',
    build_version='v1.2.3',
    branch='main'
)

# Add test result / テスト結果追加
add_test_result(
    run_id=run_id,
    case_id=case_id,
    status='passed',
    duration_ms=1250
)

# Complete test run / テスト実行完了
complete_test_run(run_id)

# Get test results / テスト結果取得
results = get_test_results(run_id=run_id)
failed_results = get_test_results(status='failed')

# Save coverage / カバレッジ保存
save_coverage(
    run_id=run_id,
    component='auth',
    file_path='src/auth/login.py',
    line_coverage=85,
    branch_coverage=75,
    function_coverage=90,
    total_lines=200,
    covered_lines=170,
    total_branches=40,
    covered_branches=30
)

# Create test issue / テスト課題作成
issue_id = create_test_issue(
    result_id=1,
    title='Flaky test: Login fails intermittently',
    description='Test fails randomly, likely due to network timing',
    severity='medium',
    issue_type='flaky'
)

# Get test summary / テスト概要取得
summary = get_test_summary(run_id=run_id)
print(f"Pass rate: {summary['pass_rate']}%")
```

## Test Types / テストタイプ

### Unit Tests / ユニットテスト
Individual component or function testing

### Integration Tests / 結合テスト
Testing interaction between components

### Functional Tests / 機能テスト
Testing specific functionality against requirements

### E2E Tests / E2Eテスト
End-to-end testing of user workflows

### Performance Tests / パフォーマンステスト
Testing system performance under load

### Security Tests / セキュリティテスト
Testing for security vulnerabilities

## Test Priority / テスト優先度

- **Low**: Optional features, edge cases
- **Medium**: Standard features
- **High**: Core features
- **Critical**: Business-critical features

## Issue Types / 課題タイプ

- **Flaky**: Tests that fail intermittently
- **Slow**: Tests that take too long
- **Bug**: Tests that reveal actual bugs
- **Performance**: Tests that reveal performance issues
- **Security**: Tests that reveal security vulnerabilities
- **Environment**: Issues caused by test environment

## Environment Variables / 環境変数

```bash
DISCORD_TOKEN=your-bot-token-here
```

## Project Structure / プロジェクト構造

```
test-agent/
├── db.py              # Database operations / データベース操作
├── discord.py         # Discord bot / Discordボット
├── requirements.txt   # Dependencies / 依存パッケージ
├── README.md          # This file / このファイル
└── test.db            # SQLite database (auto-created) / SQLiteデータベース（自動作成）
```

## Dependencies / 依存パッケージ

See `requirements.txt`

## License / ライセンス

MIT License
