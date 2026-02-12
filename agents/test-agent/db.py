#!/usr/bin/env python3
"""
Test Agent - Database Management
Test cases and results management
"""

import sqlite3
from pathlib import Path
from datetime import datetime
import json

DB_PATH = Path(__file__).parent / "test.db"

def init_db():
    """Initialize database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Test suites table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS test_suites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        component TEXT,
        tags TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Test cases table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS test_cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        suite_id INTEGER,
        name TEXT NOT NULL,
        description TEXT,
        test_type TEXT DEFAULT 'functional' CHECK(test_type IN ('unit','integration','functional','e2e','performance','security')),
        priority TEXT DEFAULT 'medium' CHECK(priority IN ('low','medium','high','critical')),
        status TEXT DEFAULT 'active' CHECK(status IN ('active','deprecated','archived')),
        preconditions TEXT,
        steps TEXT,
        expected_result TEXT,
        tags TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (suite_id) REFERENCES test_suites(id)
    )
    ''')

    # Test runs table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS test_runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        environment TEXT NOT NULL,
        build_version TEXT,
        branch TEXT,
        commit_hash TEXT,
        triggered_by TEXT,
        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP,
        status TEXT DEFAULT 'running' CHECK(status IN ('running','completed','failed','aborted')),
        total_tests INTEGER DEFAULT 0,
        passed INTEGER DEFAULT 0,
        failed INTEGER DEFAULT 0,
        skipped INTEGER DEFAULT 0,
        FOREIGN KEY (environment) REFERENCES test_suites(id)
    )
    ''')

    # Test results table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS test_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id INTEGER NOT NULL,
        case_id INTEGER NOT NULL,
        status TEXT CHECK(status IN ('passed','failed','skipped','error')),
        duration_ms INTEGER,
        error_message TEXT,
        stack_trace TEXT,
        screenshots TEXT,
        logs TEXT,
        retry_count INTEGER DEFAULT 0,
        started_at TIMESTAMP,
        completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (run_id) REFERENCES test_runs(id),
        FOREIGN KEY (case_id) REFERENCES test_cases(id)
    )
    ''')

    # Test data table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS test_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id INTEGER NOT NULL,
        data_name TEXT NOT NULL,
        data_value TEXT NOT NULL,
        data_type TEXT DEFAULT 'input' CHECK(data_type IN ('input','expected','config','fixture')),
        FOREIGN KEY (case_id) REFERENCES test_cases(id)
    )
    ''')

    # Test coverage table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS test_coverage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id INTEGER NOT NULL,
        component TEXT,
        file_path TEXT,
        line_coverage INTEGER,
        branch_coverage INTEGER,
        function_coverage INTEGER,
        total_lines INTEGER,
        covered_lines INTEGER,
        total_branches INTEGER,
        covered_branches INTEGER,
        calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (run_id) REFERENCES test_runs(id)
    )
    ''')

    # Test issues table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS test_issues (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        result_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        severity TEXT DEFAULT 'medium' CHECK(severity IN ('low','medium','high','critical')),
        issue_type TEXT CHECK(issue_type IN ('flaky','slow','bug','performance','security','environment')),
        status TEXT DEFAULT 'open' CHECK(status IN ('open','investigating','fixed','wontfix','duplicate')),
        jira_id TEXT,
        fixed_in_version TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        resolved_at TIMESTAMP,
        FOREIGN KEY (result_id) REFERENCES test_results(id)
    )
    ''')

    # Indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_test_cases_suite ON test_cases(suite_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_test_cases_status ON test_cases(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_test_runs_status ON test_runs(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_test_results_run ON test_results(run_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_test_results_case ON test_results(case_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_test_coverage_run ON test_coverage(run_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_test_issues_result ON test_issues(result_id)')

    conn.commit()
    conn.close()
    print("✅ Database initialized")

def create_suite(name, description=None, component=None, tags=None):
    """Create a test suite"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    tags_json = json.dumps(tags) if tags else None
    cursor.execute('''
    INSERT INTO test_suites (name, description, component, tags)
    VALUES (?, ?, ?, ?)
    ''', (name, description, component, tags_json))

    conn.commit()
    suite_id = cursor.lastrowid
    conn.close()
    return suite_id

def get_suites(component=None, limit=50):
    """Get test suites"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if component:
        cursor.execute('SELECT * FROM test_suites WHERE component = ? ORDER BY created_at DESC LIMIT ?', (component, limit))
    else:
        cursor.execute('SELECT * FROM test_suites ORDER BY created_at DESC LIMIT ?', (limit,))

    suites = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return suites

def create_case(suite_id, name, description=None, test_type='functional', priority='medium',
                preconditions=None, steps=None, expected_result=None, tags=None):
    """Create a test case"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    tags_json = json.dumps(tags) if tags else None
    cursor.execute('''
    INSERT INTO test_cases (suite_id, name, description, test_type, priority, preconditions, steps, expected_result, tags)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (suite_id, name, description, test_type, priority, preconditions, steps, expected_result, tags_json))

    conn.commit()
    case_id = cursor.lastrowid
    conn.close()
    return case_id

def get_cases(suite_id=None, status=None, test_type=None, limit=100):
    """Get test cases"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = 'SELECT * FROM test_cases WHERE 1=1'
    params = []

    if suite_id:
        query += ' AND suite_id = ?'
        params.append(suite_id)
    if status:
        query += ' AND status = ?'
        params.append(status)
    if test_type:
        query += ' AND test_type = ?'
        params.append(test_type)

    query += ' ORDER BY created_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    cases = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return cases

def start_test_run(name, environment, build_version=None, branch=None, commit_hash=None, triggered_by=None):
    """Start a test run"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO test_runs (name, environment, build_version, branch, commit_hash, triggered_by)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, environment, build_version, branch, commit_hash, triggered_by))

    conn.commit()
    run_id = cursor.lastrowid
    conn.close()
    return run_id

def complete_test_run(run_id, status='completed'):
    """Complete a test run"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Update counts
    cursor.execute('''
    UPDATE test_runs
    SET status = ?,
        completed_at = CURRENT_TIMESTAMP,
        total_tests = (SELECT COUNT(*) FROM test_results WHERE run_id = ?),
        passed = (SELECT COUNT(*) FROM test_results WHERE run_id = ? AND status = 'passed'),
        failed = (SELECT COUNT(*) FROM test_results WHERE run_id = ? AND status IN ('failed', 'error')),
        skipped = (SELECT COUNT(*) FROM test_results WHERE run_id = ? AND status = 'skipped')
    WHERE id = ?
    ''', (status, run_id, run_id, run_id, run_id, run_id))

    conn.commit()
    conn.close()

def add_test_result(run_id, case_id, status, duration_ms=None, error_message=None,
                    stack_trace=None, screenshots=None, logs=None, retry_count=0):
    """Add a test result"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    screenshots_json = json.dumps(screenshots) if screenshots else None
    logs_json = json.dumps(logs) if logs else None

    cursor.execute('''
    INSERT INTO test_results (run_id, case_id, status, duration_ms, error_message, stack_trace, screenshots, logs, retry_count)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (run_id, case_id, status, duration_ms, error_message, stack_trace, screenshots_json, logs_json, retry_count))

    conn.commit()
    conn.close()

def get_test_results(run_id=None, case_id=None, status=None, limit=100):
    """Get test results"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = 'SELECT * FROM test_results WHERE 1=1'
    params = []

    if run_id:
        query += ' AND run_id = ?'
        params.append(run_id)
    if case_id:
        query += ' AND case_id = ?'
        params.append(case_id)
    if status:
        query += ' AND status = ?'
        params.append(status)

    query += ' ORDER BY completed_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results

def get_test_runs(status=None, limit=20):
    """Get test runs"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if status:
        cursor.execute('SELECT * FROM test_runs WHERE status = ? ORDER BY started_at DESC LIMIT ?', (status, limit))
    else:
        cursor.execute('SELECT * FROM test_runs ORDER BY started_at DESC LIMIT ?', (limit,))

    runs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return runs

def add_test_data(case_id, data_name, data_value, data_type='input'):
    """Add test data for a test case"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO test_data (case_id, data_name, data_value, data_type)
    VALUES (?, ?, ?, ?)
    ''', (case_id, data_name, data_value, data_type))

    conn.commit()
    conn.close()

def get_test_data(case_id):
    """Get test data for a test case"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM test_data WHERE case_id = ? ORDER BY id', (case_id,))
    data = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return data

def save_coverage(run_id, component, file_path, line_coverage, branch_coverage, function_coverage,
                  total_lines, covered_lines, total_branches, covered_branches):
    """Save test coverage data"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO test_coverage (run_id, component, file_path, line_coverage, branch_coverage,
                               function_coverage, total_lines, covered_lines, total_branches, covered_branches)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (run_id, component, file_path, line_coverage, branch_coverage, function_coverage,
          total_lines, covered_lines, total_branches, covered_branches))

    conn.commit()
    conn.close()

def get_coverage(run_id=None, component=None, limit=100):
    """Get test coverage"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if run_id:
        cursor.execute('SELECT * FROM test_coverage WHERE run_id = ? ORDER BY file_path LIMIT ?', (run_id, limit))
    elif component:
        cursor.execute('SELECT * FROM test_coverage WHERE component = ? ORDER BY run_id DESC LIMIT ?', (component, limit))
    else:
        cursor.execute('SELECT * FROM test_coverage ORDER BY run_id DESC LIMIT ?', (limit,))

    coverage = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return coverage

def create_test_issue(result_id, title, description=None, severity='medium', issue_type='bug', jira_id=None):
    """Create a test issue"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO test_issues (result_id, title, description, severity, issue_type, jira_id)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (result_id, title, description, severity, issue_type, jira_id))

    conn.commit()
    issue_id = cursor.lastrowid
    conn.close()
    return issue_id

def get_test_issues(status=None, severity=None, issue_type=None, limit=50):
    """Get test issues"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = 'SELECT * FROM test_issues WHERE 1=1'
    params = []

    if status:
        query += ' AND status = ?'
        params.append(status)
    if severity:
        query += ' AND severity = ?'
        params.append(severity)
    if issue_type:
        query += ' AND issue_type = ?'
        params.append(issue_type)

    query += ' ORDER BY created_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    issues = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return issues

def resolve_issue(issue_id, fixed_in_version=None):
    """Resolve a test issue"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE test_issues
    SET status = 'fixed', resolved_at = CURRENT_TIMESTAMP, fixed_in_version = ?
    WHERE id = ?
    ''', (fixed_in_version, issue_id))

    conn.commit()
    conn.close()

def get_test_summary(run_id=None):
    """Get test summary statistics"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if run_id:
        cursor.execute('''
        SELECT
            total_tests,
            passed,
            failed,
            skipped,
            ROUND(CAST(passed AS FLOAT) * 100 / NULLIF(total_tests, 0), 2) as pass_rate
        FROM test_runs
        WHERE id = ?
        ''', (run_id,))
    else:
        cursor.execute('''
        SELECT
            SUM(total_tests) as total_tests,
            SUM(passed) as passed,
            SUM(failed) as failed,
            SUM(skipped) as skipped,
            ROUND(CAST(SUM(passed) AS FLOAT) * 100 / NULLIF(SUM(total_tests), 0), 2) as pass_rate
        FROM test_runs
        WHERE status = 'completed'
        ''')

    summary = cursor.fetchone()
    conn.close()
    return dict(summary) if summary else None

if __name__ == '__main__':
    init_db()
