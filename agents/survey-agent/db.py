#!/usr/bin/env python3
"""
Survey Agent - Database Management
Create, distribute, and analyze surveys
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "survey.db"

def init_db():
    """Initialize database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Surveys table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS surveys (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        status TEXT DEFAULT 'draft' CHECK(status IN ('draft','active','closed')),
        created_by TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        starts_at TIMESTAMP,
        ends_at TIMESTAMP
    )
    ''')

    # Questions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        survey_id INTEGER NOT NULL,
        question_text TEXT NOT NULL,
        question_type TEXT NOT NULL CHECK(question_type IN ('text','multiple_choice','rating','yes_no','checkbox')),
        options TEXT,
        required BOOLEAN DEFAULT 0,
        order_num INTEGER DEFAULT 0,
        FOREIGN KEY (survey_id) REFERENCES surveys(id) ON DELETE CASCADE
    )
    ''')

    # Responses table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        survey_id INTEGER NOT NULL,
        respondent_id TEXT NOT NULL,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (survey_id) REFERENCES surveys(id) ON DELETE CASCADE
    )
    ''')

    # Answers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        response_id INTEGER NOT NULL,
        question_id INTEGER NOT NULL,
        answer TEXT,
        FOREIGN KEY (response_id) REFERENCES responses(id) ON DELETE CASCADE,
        FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
    )
    ''')

    # Indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_surveys_status ON surveys(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_questions_survey ON questions(survey_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_responses_survey ON responses(survey_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_answers_response ON answers(response_id)')

    conn.commit()
    conn.close()
    print("✅ Database initialized")

def create_survey(title, description, created_by, starts_at=None, ends_at=None):
    """Create a new survey"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO surveys (title, description, created_by, starts_at, ends_at)
    VALUES (?, ?, ?, ?, ?)
    ''', (title, description, created_by, starts_at, ends_at))

    survey_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return survey_id

def add_question(survey_id, question_text, question_type, options=None, required=False, order_num=0):
    """Add a question to a survey"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO questions (survey_id, question_text, question_type, options, required, order_num)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (survey_id, question_text, question_type, options, 1 if required else 0, order_num))

    question_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return question_id

def update_survey(survey_id, status=None, starts_at=None, ends_at=None):
    """Update survey details"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    updates = []
    params = []

    if status:
        updates.append("status = ?")
        params.append(status)

    if starts_at:
        updates.append("starts_at = ?")
        params.append(starts_at)

    if ends_at:
        updates.append("ends_at = ?")
        params.append(ends_at)

    if updates:
        params.append(survey_id)
        query = f"UPDATE surveys SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        conn.commit()

    conn.close()

def submit_response(survey_id, respondent_id, answers):
    """Submit a survey response"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create response
    cursor.execute('''
    INSERT INTO responses (survey_id, respondent_id)
    VALUES (?, ?)
    ''', (survey_id, respondent_id))

    response_id = cursor.lastrowid

    # Add answers
    for question_id, answer in answers:
        cursor.execute('''
        INSERT INTO answers (response_id, question_id, answer)
        VALUES (?, ?, ?)
        ''', (response_id, question_id, answer))

    conn.commit()
    conn.close()
    return response_id

def get_survey(survey_id):
    """Get survey with questions"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM surveys WHERE id = ?', (survey_id,))
    survey = cursor.fetchone()

    questions = []
    if survey:
        cursor.execute('''
        SELECT id, question_text, question_type, options, required, order_num
        FROM questions WHERE survey_id = ? ORDER BY order_num
        ''', (survey_id,))
        questions = cursor.fetchall()

    conn.close()
    return survey, questions

def list_surveys(status=None):
    """List surveys"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if status:
        cursor.execute('''
        SELECT id, title, status, created_at FROM surveys
        WHERE status = ? ORDER BY created_at DESC
        ''', (status,))
    else:
        cursor.execute('''
        SELECT id, title, status, created_at FROM surveys
        ORDER BY created_at DESC
        ''')

    surveys = cursor.fetchall()
    conn.close()
    return surveys

def get_responses(survey_id):
    """Get all responses for a survey"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT r.id, r.respondent_id, r.submitted_at
    FROM responses r WHERE r.survey_id = ?
    ORDER BY r.submitted_at DESC
    ''', (survey_id,))

    responses = cursor.fetchall()
    response_data = []

    for resp in responses:
        cursor.execute('''
        SELECT q.question_text, a.answer
        FROM answers a
        JOIN questions q ON a.question_id = q.id
        WHERE a.response_id = ?
        ''', (resp[0],))
        answers = cursor.fetchall()
        response_data.append((resp, answers))

    conn.close()
    return response_data

def analyze_survey(survey_id):
    """Analyze survey results"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Total responses
    cursor.execute('SELECT COUNT(*) FROM responses WHERE survey_id = ?', (survey_id,))
    total_responses = cursor.fetchone()[0]

    # Question analysis
    cursor.execute('''
    SELECT q.id, q.question_text, q.question_type, q.options
    FROM questions q WHERE q.survey_id = ?
    ''', (survey_id,))
    questions = cursor.fetchall()

    analysis = {
        'total_responses': total_responses,
        'questions': []
    }

    for q in questions:
        question_data = {
            'id': q[0],
            'question': q[1],
            'type': q[2],
            'stats': {}
        }

        if q[2] in ['multiple_choice', 'yes_no']:
            # Count responses by option
            cursor.execute('''
            SELECT a.answer, COUNT(*) as count
            FROM answers a
            WHERE a.question_id = ?
            GROUP BY a.answer
            ORDER BY count DESC
            ''', (q[0],))
            question_data['stats']['distribution'] = dict(cursor.fetchall())

        elif q[2] == 'rating':
            # Average rating
            cursor.execute('''
            SELECT AVG(CAST(a.answer AS INTEGER)), MIN(CAST(a.answer AS INTEGER)), MAX(CAST(a.answer AS INTEGER))
            FROM answers a WHERE a.question_id = ?
            ''', (q[0],))
            avg, min_r, max_r = cursor.fetchone()
            question_data['stats'] = {'average': avg, 'min': min_r, 'max': max_r}

        elif q[2] == 'text':
            # List all text answers
            cursor.execute('''
            SELECT a.answer FROM answers a WHERE a.question_id = ?
            ''', (q[0],))
            question_data['stats']['answers'] = [a[0] for a in cursor.fetchall()]

        analysis['questions'].append(question_data)

    conn.close()
    return analysis

if __name__ == '__main__':
    init_db()
