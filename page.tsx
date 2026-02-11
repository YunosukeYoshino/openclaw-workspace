'use client';

import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const formSchema = z.object({
  userId: z.string().min(1, 'ユーザーIDを入力してください'),
  type: z.enum(['note', 'task', 'idea', 'goal']),
  content: z.string().min(1, '内容を入力してください'),
  mood: z.string().optional(),
});

interface StreakData {
  currentStreak: number;
  maxStreak: number;
  recordedToday: boolean;
  totalEntries: number;
}

interface HeatmapData {
  date: string;
  count: number;
}[]

export default function Home() {
  const [userId, setUserId] = useState('');
  const [type, setType] = useState('note');
  const [content, setContent] = useState('');
  const [mood, setMood] = useState('');
  const [advice, setAdvice] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [streakData, setStreakData] = useState<StreakData | null>(null);
  const [heatmapData, setHeatmapData] = useState<HeatmapData>([]);

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors: formErrors },
  } = useForm({
    resolver: zodResolver(formSchema),
    defaultValues: {
      type: 'note',
      content: '',
      mood: '',
    },
  });

  // びっくりデータをロード
  const loadStreakData = async () => {
    if (!userId) return;
    try {
      const res = await fetch(`/api/streak?userId=${userId}`);
      const data = await res.json();
      setStreakData(data);
    } catch (error) {
      console.error('ストーク取得エラー:', error);
    }
  };

  // ヒートマップをロード
  const loadHeatmap = async () => {
    if (!userId) return;
    try {
      const res = await fetch(`/api/heatmap?userId=${userId}`);
      const data = await res.json();
      setHeatmapData(data);
    } catch (error) {
      console.error('ヒートマップ取得エラー:', error);
    }
  };

  useEffect(() => {
    if (userId) {
      loadStreakData();
      loadHeatmap();
    }
  }, [userId]);

  const onSubmit = async (data: any) => {
    setErrors({});

    if (!data.userId) {
      setErrors({ userId: 'ユーザーIDを入力してください' });
      return;
    }

    if (!data.content) {
      setErrors({ content: '内容を入力してください' });
      return;
    }

    try {
      await fetch('/api/entries', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          userId: data.userId,
          type: data.type,
          title: null,
          content: data.content,
          mood: data.mood,
          tags: null,
        }),
      });

      setUserId(data.userId);
      setType(data.type);
      setContent('');
      setMood('');
      setErrors({});

      await loadAdvice(data.userId);
      await loadStreakData();
      await loadHeatmap();
    } catch (error) {
      console.error('エントリー登録エラー:', error);
      setErrors({ root: 'エントリーの登録に失敗しました。もう一度お試しください。' });
    }
  };

  const loadAdvice = async (uid: string) => {
    if (!uid) return;
    setLoading(true);
    try {
      const res = await fetch('/api/advice', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userId: uid, days: 7 }),
      });
      const data = await res.json();
      setAdvice(data.advice || []);
    } catch (error) {
      console.error('アドバイス生成エラー:', error);
    } finally {
      setLoading(false);
    }
  };

  const getLastRecordedTime = () => {
    if (heatmapData.length === 0) return null;
    const lastDate = new Date(heatmapData[heatmapData.length - 1].date);
    const now = new Date();
    const diffMs = now.getTime() - lastDate.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffHours < 1) return 'たった今';
    if (diffHours < 24) return `${diffHours}時間前`;
    if (diffDays === 1) return '昨日';
    return `${diffDays}日前`;
  };

  const getHeatmapColor = (count: number) => {
    if (count === 0) return 'bg-gray-100 text-gray-300';
    if (count === 1) return 'bg-pink-100 text-pink-500';
    if (count === 2) return 'bg-pink-200 text-pink-600';
    if (count >= 3) return 'bg-pink-300 text-pink-700';
    return 'bg-gray-100 text-gray-300';
  };

  const getStreakMessage = () => {
    if (!streakData) return '';
    if (streakData.currentStreak === 0) return 'さあ、今日から始めよう！';
    if (streakData.currentStreak === 1) return '1日連続記録中！';
    if (streakData.currentStreak >= 7) return '1週間連続記録すごい！';
    if (streakData.currentStreak >= 3) return '好調！';
    return `${streakData.currentStreak}日連続記録中！`;
  };

  return (
    <div className="min-h-dvh bg-gradient-to-br from-pink-50 via-purple-50 to-blue-50 flex items-start justify-center p-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center w-14 h-14 bg-white rounded-2xl mb-4 shadow-md">
            <span className="text-2xl">⊂</span>
          </div>
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            Reflect.ai
          </h1>
          <p className="text-gray-600 text-sm">
            あなたの成長をサポートするAIアドバイザー
          </p>
        </div>

        {/* Streak Counter */}
        {streakData && (
          <div className="bg-white rounded-2xl shadow-sm p-4 mb-4 border border-gray-100">
            <div className="text-center">
              <div className="text-4xl font-bold text-pink-500 mb-1">
                {streakData.currentStreak}
              </div>
              <div className="text-gray-600 text-sm mb-2">
                連続記録日数
              </div>
              <div className="text-xs text-gray-400">
                最高記録: {streakData.maxStreak}日
              </div>
              <div className="text-sm text-purple-600 mt-3 font-medium">
                {getStreakMessage()}
              </div>
            </div>
          </div>
        )}

        {/* Heatmap */}
        {heatmapData.length > 0 && (
          <div className="bg-white rounded-2xl shadow-sm p-4 mb-4 border border-gray-100">
            <div className="text-xs font-semibold text-gray-600 mb-3">
              過去7日間の活動
            </div>
            <div className="grid grid-cols-7 gap-1">
              {heatmapData.slice(0, 7).reverse().map((day, idx) => {
                const date = new Date(day.date);
                const dayName = ['日', '月', '火', '水', '木', '金', '土'][date.getDay()];
                return (
                  <div
                    key={day.date}
                    className={`text-center p-2 rounded-lg ${getHeatmapColor(day.count)}`}
                  >
                    <div className="text-xs mb-1">{dayName}</div>
                    <div className="text-lg font-bold">{day.count}</div>
                  </div>
                );
              })}
            </div>
            {streakData && !streakData.recordedToday && (
              <div className="mt-3 text-center">
                <p className="text-sm text-gray-500">
                  前回: {getLastRecordedTime()}
                </p>
              </div>
            )}
          </div>
        )}

        {/* Main Card */}
        <div className="bg-white rounded-3xl shadow-sm p-5 mb-4 border border-gray-100">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {/* User ID */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                ユーザーID <span className="text-rose-400 ml-1">*</span>
              </label>
              <input
                {...register('userId')}
                type="text"
                placeholder="任意の文字列"
                className={`w-full px-4 py-2.5 bg-gray-50 border rounded-2xl transition-colors duration-200 focus:outline-none focus:border-pink-300 focus:bg-white text-gray-900 placeholder:text-gray-400 text-sm ${
                  formErrors.userId ? 'border-rose-300 bg-rose-50' : 'border-gray-200'
                }`}
              />
              {formErrors.userId && (
                <p className="text-rose-400 text-xs mt-1.5">
                  {formErrors.userId.message}
                </p>
              )}
            </div>

            {/* Type Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                種類
              </label>
              <div className="grid grid-cols-4 gap-2">
                {[
                  { value: 'note', label: 'メモ' },
                  { value: 'task', label: 'タスク' },
                  { value: 'idea', label: 'アイデア' },
                  { value: 'goal', label: '目標' },
                ].map((item) => (
                  <label
                    key={item.value}
                    className={`cursor-pointer p-2 rounded-xl border text-center transition-all duration-200 ${
                      watch('type') === item.value
                        ? 'bg-pink-100 border-pink-300 text-pink-700'
                        : 'bg-gray-50 border-gray-200 hover:border-pink-200 hover:bg-pink-50 text-gray-600'
                    }`}
                  >
                    <input
                      {...register('type')}
                      type="radio"
                      value={item.value}
                      className="sr-only"
                    />
                    <div className="text-xs font-medium">{item.label}</div>
                  </label>
                ))}
              </div>
            </div>

            {/* Content */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                内容 <span className="text-rose-400 ml-1">*</span>
              </label>
              <textarea
                {...register('content')}
                className={`w-full px-4 py-2.5 bg-gray-50 border rounded-2xl transition-colors duration-200 focus:outline-none focus:border-pink-300 focus:bg-white text-gray-900 placeholder:text-gray-400 resize-none h-24 text-sm ${
                  formErrors.content ? 'border-rose-300 bg-rose-50' : 'border-gray-200'
                }`}
                placeholder="今日の振り返りや気づきを書いてください..."
              />
              {formErrors.content && (
                <p className="text-rose-400 text-xs mt-1.5">
                  {formErrors.content.message}
                </p>
              )}
            </div>

            {/* Mood */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                気分
              </label>
              <div className="flex gap-2">
                {[
                  { value: 'happy', emoji: '☺️' },
                  { value: 'neutral', emoji: '😐' },
                  { value: 'tired', emoji: '😴' },
                  { value: 'excited', emoji: '🎉' },
                  { value: 'calm', emoji: '😌' },
                ].map((item) => (
                  <button
                    key={item.value}
                    type="button"
                    onClick={() => setValue('mood', item.value)}
                    className={`p-2 text-xl rounded-xl border-2 transition-all duration-200 hover:scale-110 ${
                      watch('mood') === item.value
                        ? 'bg-pink-100 border-pink-300'
                        : 'bg-gray-50 border-gray-200 hover:border-pink-200 hover:bg-pink-50'
                    }`}
                  >
                    {item.emoji}
                  </button>
                ))}
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              className="w-full bg-gradient-to-r from-pink-400 to-purple-400 text-white py-3 rounded-2xl font-semibold text-sm shadow-sm hover:shadow-md hover:scale-[1.01] transition-all duration-200 flex items-center justify-center gap-2"
            >
              保存する
            </button>
          </form>
        </div>

        {/* Generate Advice Button */}
        {userId && (
          <button
            onClick={() => loadAdvice(userId)}
            disabled={loading}
            className={`w-full bg-white text-pink-600 py-3 rounded-2xl font-semibold text-sm shadow-sm hover:shadow-md hover:scale-[1.01] transition-all duration-200 flex items-center justify-center gap-2 border-2 border-pink-100 ${
              loading ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            {loading ? (
              <span className="inline-flex items-center gap-2">
                <span className="animate-spin">◌</span> 分析中...
              </span>
            ) : (
              <>アドバイスを生成</>
            )}
          </button>
        )}

        {/* Advice Cards */}
        {advice.length > 0 && (
          <div className="mt-6 space-y-3">
            <h2 className="text-lg font-bold text-gray-800 text-center mb-4">
              あなたへのアドバイス
            </h2>
            {advice.map((adv, idx) => (
              <div
                key={idx}
                className="bg-white rounded-3xl shadow-sm p-4 border border-gray-100"
              >
                <div className="inline-block px-2 py-1 bg-pink-100 text-pink-700 text-xs font-semibold rounded-full mb-2">
                  {adv.category}
                </div>
                <div className="text-gray-800 text-sm leading-relaxed">
                  {adv.action}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
