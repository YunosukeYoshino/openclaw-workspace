import { NextRequest, NextResponse } from 'next/server';
import db from '@/lib/db';

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const userId = searchParams.get('userId');

  if (!userId) {
    return NextResponse.json({ error: 'userId is required' }, { status: 400 });
  }

  const entries = db.prepare(\`
    SELECT DATE(created_at) as date, COUNT(*) as count
    FROM entries
    WHERE user_id = ?
    GROUP BY DATE(created_at)
    ORDER BY date DESC
  \`).all(userId);

  let maxStreak = 0;
  let currentStreak = 0;

  const sortedDates = entries.map((e: any) => e.date).sort();
  let previousDate: string | null = null;

  for (const entry of entries) {
    const date = entry.date;
    if (!previousDate) {
      currentStreak = 1;
    } else {
      const prev = new Date(previousDate);
      const curr = new Date(date);
      const diffDays = Math.floor((curr.getTime() - prev.getTime()) / (1000 * 60 * 60 * 24));
      
      if (diffDays === 1) {
        currentStreak++;
      } else if (diffDays > 1) {
        currentStreak = 1;
      }
    }
    
    if (currentStreak > maxStreak) {
      maxStreak = currentStreak;
    }
    
    previousDate = date;
  }

  const today = new Date().toISOString().split('T')[0];
  const todayEntry = db.prepare(\`
    SELECT COUNT(*) as count
    FROM entries
    WHERE user_id = ? AND DATE(created_at) = ?
  \`).get(userId, today);

  const recordedToday = (todayEntry as any).count > 0;

  return NextResponse.json({
    currentStreak: currentStreak,
    maxStreak: maxStreak,
    recordedToday,
    totalEntries: entries.length,
  });
}
