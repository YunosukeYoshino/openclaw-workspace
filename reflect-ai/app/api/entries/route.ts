import { NextRequest, NextResponse } from 'next/server';
import db from '@/lib/db';

export async function POST(request: NextRequest) {
  const body = await request.json();
  const { userId, type, title, content, mood, tags } = body;

  const stmt = db.prepare(`
    INSERT INTO entries (user_id, type, title, content, mood, tags)
    VALUES (?, ?, ?, ?, ?, ?)
  `);

  const result = stmt.run(userId, type, title, content, mood, tags);

  return NextResponse.json({ success: true, id: result.lastInsertRowid });
}

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const userId = searchParams.get('userId');
  const type = searchParams.get('type');

  let query = 'SELECT * FROM entries WHERE user_id = ?';
  const params = [userId];

  if (type) {
    query += ' AND type = ?';
    params.push(type);
  }

  query += ' ORDER BY created_at DESC LIMIT 50';

  const stmt = db.prepare(query);
  const entries = stmt.all(...params);

  return NextResponse.json(entries);
}
