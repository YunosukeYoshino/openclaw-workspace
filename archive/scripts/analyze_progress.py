#!/usr/bin/env python3
"""
エージェント開発の進捗を分析して、次に開発すべきエージェントを特定する
"""

import json

# 既存のエージェントをリストアップ（事前に取得済み）
existing_agents = """achievement-agent
analytics-agent
anniversary-agent
api-agent
asset-agent
assistant-agent
audio-agent
audio-summarizer
automation-agent
backup-agent
birthday-agent
book-agent
bookmark-agent
brainstorm-agent
budget-agent
budget-expense-agent
calendar-agent
calendar-event-agent
checklist-agent
clipboard-agent
code-agent
communication-agent
contact-agent
cooking-agent
crypto-agent
debt-agent
diet-agent
document-agent
dream-agent
email-agent
event-agent
feedback-agent
file-agent
finance-agent
finance-summary-agent
fitness-agent
game-agent
goal-agent
gratitude-agent
habit-agent
habit-tracker-agent
health-agent
holiday-agent
hydration-agent
image-agent
integration-agent
inventory-agent
investment-agent
journal-agent
language-agent
learning-agent
location-agent
meal-plan-agent
medication-agent
meditation-agent
memo-agent
monitoring-agent
mood-agent
movie-agent
music-agent
news-agent
newsfeed-agent
note-taking-agent
notification-agent
password-agent
pet-agent
plants-agent
podcast-agent
project-agent
quote-agent
reading-agent
recipe-agent
reminder-agent
routine-agent
rss-agent
savings-agent
schedule-agent
search-agent
shift-agent
shopping-agent
skills-agent
sleep-agent
social-agent
study-agent
subscription-agent
support-agent
survey-agent
task-list-agent
team-agent
ticket-agent
timer-agent
todo-agent
translate-agent
travel-agent
video-agent
voice-agent
watchlist-agent
weather-agent
weather-log-agent
wishlist-agent
workout-agent
workout-plan-agent""".splitlines()

existing = set(existing_agents)

# dev_progress.jsonのpendingリスト
dev_progress_pending = [
    [41, "reading-agent", "読書記録", "books, progress, notes"],
    [42, "sleep-agent", "睡眠記録", "sleep time, quality, dreams"],
    [43, "meditation-agent", "瞑想記録", "duration, technique, notes"],
    [44, "gratitude-agent", "感謝日記", "things to be grateful for"],
    [45, "achievement-agent", "実績・達成記録", "goals, achievements, milestones"],
    [46, "language-agent", "言語学習", "vocabulary, grammar, practice"],
    [47, "workout-agent", "ワークアウト記録", "exercises, sets, reps"],
    [48, "diet-agent", "食事記録", "meals, calories, nutrition"],
    [49, "medication-agent", "薬服用記録", "medications, dosage, schedule"],
    [50, "hydration-agent", "水分摂取記録", "water intake, goals"],
    [51, "habit-tracker-agent", "習慣トラッカー", "daily habits, streaks"],
    [52, "budget-expense-agent", "予算・支出管理", "budget categories, expenses"],
    [53, "investment-agent", "投資管理", "stocks, bonds, portfolio"],
    [54, "savings-agent", "貯金管理", "goals, deposits, withdrawals"],
    [55, "debt-agent", "借金管理", "debts, payments, interest"],
    [56, "subscription-agent", "サブスクリプション管理", "services, billing dates"],
    [57, "event-agent", "イベント管理", "events, invitations, rsvps"],
    [58, "birthday-agent", "誕生日管理", "birthdays, gifts, reminders"],
    [59, "anniversary-agent", "記念日管理", "anniversaries, celebrations"],
    [60, "holiday-agent", "休暇管理", "holidays, plans, bookings"],
    [61, "weather-log-agent", "天気ログ", "daily weather conditions"],
    [62, "energy-agent", "エネルギーレベル記録", "daily energy tracking"],
    [63, "stress-agent", "ストレスレベル記録", "stress tracking, management"],
    [64, "mood-tracker-agent", "気分トラッカー", "mood patterns, triggers"],
    [65, "social-agent", "社交記録", "meetings, connections, networking"],
    [66, "gift-agent", "ギフト記録", "gifts given/received, ideas"],
    [67, "clothing-agent", "服飾管理", "wardrobe, shopping, outfits"],
    [68, "household-agent", "家事管理", "chores, maintenance, repairs"],
    [69, "garden-agent", "園芸記録", "plants, garden activities"],
    [70, "car-agent", "車管理", "maintenance, fuel, repairs"],
    [71, "insurance-agent", "保険管理", "policies, claims, renewals"],
    [72, "tax-agent", "税金管理", "documents, deductions, filings"],
    [73, "document-agent", "書類管理", "documents, categorization, retrieval"],
    [74, "password-agent", "パスワード管理", "secure password storage"],
    [76, "device-agent", "デバイス管理", "devices, warranties, support"],
    [77, "software-agent", "ソフトウェア管理", "licenses, updates, installs"],
    [78, "network-agent", "ネットワーク管理", "WiFi, passwords, settings"],
    [79, "security-agent", "セキュリティ管理", "threats, incidents, measures"],
    [80, "cloud-agent", "クラウド管理", "cloud services, storage, usage"],
    [81, "email-agent", "メール管理", "email organization, responses"],
    [82, "phone-agent", "通話記録管理", "calls, voicemail, contacts"],
    [83, "message-agent", "メッセージ管理", "text messages, communication logs"],
    [85, "calendar-integration-agent", "カレンダー連携", "sync calendars, events"],
    [86, "api-agent", "API連携", "API keys, endpoints, integrations"],
    [87, "webhook-agent", "Webhook管理", "webhook URLs, events, logs"],
    [88, "automation-agent", "自動化管理", "automated tasks, workflows"],
    [89, "integration-agent", "統合管理", "service integrations"],
    [90, "report-agent", "レポート管理", "reports, analytics, exports"],
    [91, "log-agent", "ログ管理", "system logs, monitoring"],
    [92, "debug-agent", "デバッグ管理", "debug sessions, issues"],
    [93, "test-agent", "テスト管理", "test cases, results"],
    [94, "deploy-agent", "デプロイ管理", "deployments, rollbacks"],
    [95, "monitor-agent", "モニタリング管理", "metrics, alerts"],
    [96, "performance-agent", "パフォーマンス管理", "optimization, benchmarks"],
    [97, "scale-agent", "スケール管理", "scaling, capacity planning"],
    [98, "backup-schedule-agent", "バックアップスケジュール", "scheduled backups"],
    [99, "cleanup-agent", "クリーンアップ管理", "scheduled cleanups"],
    [100, "archive-agent", "アーカイブ管理", "archiving, retention"],
]

# 分析
completed_in_pending = []
missing_agents = []

for idx, name, desc, tags in dev_progress_pending:
    if name in existing:
        completed_in_pending.append((idx, name, desc))
    else:
        missing_agents.append((idx, name, desc, tags))

# 結果表示
print("=" * 60)
print("📊 エージェント開発進捗分析")
print("=" * 60)

print(f"\n📁 既存のエージェント数: {len(existing)}")
print(f"✅ dev_progress.jsonのcompleted: 5")
print(f"⏳ dev_progress.jsonのpending: {len(dev_progress_pending)}")

print(f"\n🔄 pendingリストにあるが既に存在するエージェント ({len(completed_in_pending)}個):")
for idx, name, desc in completed_in_pending:
    print(f"  {idx}: {name} - {desc}")

print(f"\n❌ まだ開発されていないエージェント ({len(missing_agents)}個):")
for idx, name, desc, tags in missing_agents:
    print(f"  {idx}: {name} - {desc}")

print(f"\n📝 次に開発すべきエージェント (最初の5個):")
for idx, name, desc, tags in missing_agents[:5]:
    print(f"  {idx}: {name} - {desc} [{tags}]")

print("=" * 60)
