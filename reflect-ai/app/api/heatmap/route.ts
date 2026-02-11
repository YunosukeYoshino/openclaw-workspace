import { NextRequest, NextResponse } from 'next/server';
import db from '@/lib/db';

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const userId = searchParams.get('userId');

  if (!userId) {
    return NextResponse.json({ error: 'userId is required' }, { status: 400 });
  }

  const entries = db.prepare(\`
    SELECT DATE(created_at) as date
    FROM entries
    WHERE user_id = ?
    ORDER BY date DESC
    LIMIT 30
  \`).all(userId);

  const heatmap: { date: string; count: number }[] = [];
  
  for (const entry of entries as any[]) {
    const existing = heatmap.find(h => h.date === entry.date);
    if (existing) {
      existing.count++;
    } else {
      heatmap.push({ date: entry.date, count: 1 });
    }
  }

  return NextResponse.json(heatmap);
}
