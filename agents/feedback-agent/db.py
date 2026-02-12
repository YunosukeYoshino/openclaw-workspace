#!/usr/bin/env python3
"""
Feedback Agent - Database Management
Collect, analyze, and generate reports from user feedback
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "feedback.db"

def init_db():
    """Initialize database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Feedback table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        type TEXT NOT NULL CHECK(type IN ('bug','feature','improvement','compliment','complaint','other')),
        category TEXT,
        title TEXT NOT NULL,
        description TEXT,
        rating INTEGER CHECK(rating >= 1 AND rating <= 5),
        sentiment TEXT CHECK(sentiment IN ('positive','neutral','negative')),
        status TEXT DEFAULT 'new' CHECK(status IN ('new','reviewed','in_progress','resolved','dismissed')),
        tags TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        resolved_at TIMESTAMP
    )
    ''')

    # Feedback comments table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS feedback_comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        feedback_id INTEGER NOT NULL,
        commenter TEXT NOT NULL,
        comment TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (feedback_id) REFERENCES feedback(id) ON DELETE CASCADE
    )
    ''')

    # Analysis results table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS analysis_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_type TEXT NOT NULL,
        period_start DATE NOT NULL,
        period_end DATE NOT NULL,
        total_feedback INTEGER DEFAULT 0,
        sentiment_distribution TEXT,
        type_distribution TEXT,
        top_issues TEXT,
        top_compliments TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_feedback_type ON feedback(type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_feedback_status ON feedback(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_feedback_user ON feedback(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_feedback_date ON feedback(created_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_feedback_sentiment ON feedback(sentiment)')

    conn.commit()
    conn.close()
    print("✅ Database initialized")

def add_feedback(user_id, type, title, description=None, rating=None, sentiment=None, category=None, tags=None):
    """Add new feedback"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO feedback (user_id, type, title, description, rating, sentiment, category, tags)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, type, title, description, rating, sentiment, category, tags))

    feedback_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return feedback_id

def update_feedback(feedback_id, status=None, sentiment=None):
    """Update feedback status or sentiment"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    updates = []
    params = []

    if status:
        updates.append("status = ?")
        params.append(status)
        if status == 'resolved':
            updates.append("resolved_at = ?")
            params.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    if sentiment:
        updates.append("sentiment = ?")
        params.append(sentiment)

    if updates:
        updates.append("updated_at = ?")
        params.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        params.append(feedback_id)

        query = f"UPDATE feedback SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        conn.commit()

    conn.close()

def add_comment(feedback_id, commenter, comment):
    """Add comment to feedback"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO feedback_comments (feedback_id, commenter, comment)
    VALUES (?, ?, ?)
    ''', (feedback_id, commenter, comment))

    comment_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return comment_id

def get_feedback(feedback_id):
    """Get feedback details with comments"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM feedback WHERE id = ?', (feedback_id,))
    feedback = cursor.fetchone()

    comments = []
    if feedback:
        cursor.execute('''
        SELECT commenter, comment, created_at FROM feedback_comments
        WHERE feedback_id = ? ORDER BY created_at
        ''', (feedback_id,))
        comments = cursor.fetchall()

    conn.close()
    return feedback, comments

def list_feedback(status=None, type=None, sentiment=None, user_id=None, limit=10):
    """List feedback with filters"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = 'SELECT id, user_id, type, title, status, sentiment, rating, created_at FROM feedback WHERE 1=1'
    params = []

    if status:
        query += ' AND status = ?'
        params.append(status)

    if type:
        query += ' AND type = ?'
        params.append(type)

    if sentiment:
        query += ' AND sentiment = ?'
        params.append(sentiment)

    if user_id:
        query += ' AND user_id = ?'
        params.append(user_id)

    query += ' ORDER BY created_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    feedback_list = cursor.fetchall()
    conn.close()
    return feedback_list

def analyze_feedback(period_days=30):
    """Analyze feedback and generate insights"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    start_date = (datetime.now() - timedelta(days=period_days)).strftime("%Y-%m-%d")

    # Total feedback
    cursor.execute('SELECT COUNT(*) FROM feedback WHERE created_at >= ?', (start_date,))
    total = cursor.fetchone()[0]

    # Sentiment distribution
    cursor.execute('''
    SELECT sentiment, COUNT(*) FROM feedback
    WHERE created_at >= ? AND sentiment IS NOT NULL
    GROUP BY sentiment
    ''', (start_date,))
    sentiment_dist = dict(cursor.fetchall())

    # Type distribution
    cursor.execute('''
    SELECT type, COUNT(*) FROM feedback
    WHERE created_at >= ? GROUP BY type
    ''', (start_date,))
    type_dist = dict(cursor.fetchall())

    # Top issues (negative sentiment)
    cursor.execute('''
    SELECT title, COUNT(*) as count FROM feedback
    WHERE created_at >= ? AND sentiment = 'negative'
    GROUP BY title ORDER BY count DESC LIMIT 5
    ''', (start_date,))
    top_issues = cursor.fetchall()

    # Top compliments (positive sentiment)
    cursor.execute('''
    SELECT title, COUNT(*) as count FROM feedback
    WHERE created_at >= ? AND sentiment = 'positive'
    GROUP BY title ORDER BY count DESC LIMIT 5
    ''', (start_date,))
    top_compliments = cursor.fetchall()

    conn.close()

    return {
        'total': total,
        'sentiment_distribution': sentiment_dist,
        'type_distribution': type_dist,
        'top_issues': top_issues,
        'top_compliments': top_compliments
    }

def generate_report(period_days=30):
    """Generate and save analysis report"""
    from datetime import timedelta

    analysis = analyze_feedback(period_days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=period_days)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    import json
    cursor.execute('''
    INSERT INTO analysis_results (report_type, period_start, period_end, total_feedback,
                                   sentiment_distribution, type_distribution, top_issues, top_compliments)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        'summary',
        start_date.strftime("%Y-%m-%d"),
        end_date.strftime("%Y-%m-%d"),
        analysis['total'],
        json.dumps(analysis['sentiment_distribution']),
        json.dumps(analysis['type_distribution']),
        json.dumps(analysis['top_issues']),
        json.dumps(analysis['top_compliments'])
    ))

    report_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return report_id, analysis

if __name__ == '__main__':
    init_db()
