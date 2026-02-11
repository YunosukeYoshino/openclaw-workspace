import { NextRequest, NextResponse } from 'next/server';
import db from '@/lib/db';
import OpenAI from 'openai';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

export async function POST(request: NextRequest) {
  const body = await request.json();
  const { userId, days = 7 } = body;

  // 過去のエントリーを取得
  const stmt = db.prepare(`
    SELECT * FROM entries
    WHERE user_id = ? AND created_at >= datetime('now', ?)
    ORDER BY created_at DESC
  `);

  const entries = stmt.all(userId, `-${days} days`);

  if (entries.length === 0) {
    return NextResponse.json({ advice: null, message: '十分なエントリーがありません' });
  }

  // エントリーを分析してアドバイスを生成
  const entriesSummary = entries
    .map((e: any) => `${e.type}: ${e.content}${e.mood ? ` (気分: ${e.mood})` : ''}`)
    .join('\n');

  const completion = await openai.chat.completions.create({
    model: 'gpt-4o',
    messages: [
      {
        role: 'system',
        content: 'あなたは個人の成長をサポートするAIアドバイザーです。過去のライフログからパターンを分析し、具体的で実用的なアドバイスを提供してください。',
      },
      {
        role: 'user',
        content: `過去${days}日間のライフログ:\n${entriesSummary}\n\nこのユーザーに最適なアドバイスを3つ提供してください。それぞれ、カテゴリー（健康、生産性、メンタル、成長など）と、具体的なアクションを含めてください。`,
      },
    ],
    response_format: { type: 'json_object' },
  });

  const adviceContent = JSON.parse(completion.choices[0].message.content || '{}');

  // アドバイスをDBに保存
  const insertStmt = db.prepare(`
    INSERT INTO advice (user_id, content, category)
    VALUES (?, ?, ?)
  `);

  adviceContent.advice?.forEach((adv: any) => {
    insertStmt.run(userId, JSON.stringify(adv), adv.category || 'general');
  });

  return NextResponse.json({ advice: adviceContent.advice });
}
