#!/usr/bin/env python3
"""
SaaSアプリMVP：Discordボット版AIアシスタント
"""
import os
import sqlite3
import discord
from discord.ext import commands
from pathlib import Path

# 設定
TOKEN = os.getenv('DISCORD_BOT_TOKEN', '')
DB_PATH = Path(__file__).parent / "data" / "lifelog.db"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

def get_connection():
    return sqlite3.connect(DB_PATH)

def get_or_create_user(discord_id, username):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT id FROM users WHERE discord_id = ?', (discord_id,))
    user = cursor.fetchone()

    if user:
        user_id = user[0]
    else:
        cursor.execute('INSERT INTO users (discord_id, username) VALUES (?, ?)', (discord_id, username))
        user_id = cursor.lastrowid

    conn.commit()
    conn.close()
    return user_id

def add_user_task(user_id, title, description=None, priority=0):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO user_tasks (user_id, title, description, priority)
    VALUES (?, ?, ?, ?)
    ''', (user_id, title, description, priority))

    task_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return task_id

def get_user_tasks(user_id, status=None):
    conn = get_connection()
    cursor = conn.cursor()

    query = 'SELECT * FROM user_tasks WHERE user_id = ?'
    params = [user_id]

    if status:
        query += ' AND status = ?'
        params.append(status)

    query += ' ORDER BY priority DESC, created_at ASC'

    cursor.execute(query, params)
    tasks = cursor.fetchall()
    conn.close()
    return tasks

@bot.event
async def on_ready():
    print(f'✅ Bot ready: {bot.user.name}')

@bot.command()
async def task(ctx, action=None, *, args=None):
    """タスク管理: !task add <title> | !task list | !task complete <id>"""
    user_id = get_or_create_user(str(ctx.author.id), ctx.author.name)

    if action == 'add':
        if not args:
            await ctx.send("使い方: !task add <タイトル>")
            return

        task_id = add_user_task(user_id, args)
        await ctx.send(f"✨ タスク #{task_id} を追加しました")

    elif action == 'list':
        tasks = get_user_tasks(user_id)

        if not tasks:
            await ctx.send("📝 タスクはまだありません")
            return

        msg = "📋 **あなたのタスク**\n\n"
        for t in tasks:
            status_emoji = "✅" if t[3] == "completed" else "⏳"
            msg += f"{status_emoji} #{t[0]} {t[2]}\n"

        await ctx.send(msg)

    elif action == 'complete':
        if not args or not args.isdigit():
            await ctx.send("使い方: !task complete <タスクID>")
            return

        task_id = int(args)
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('''
        UPDATE user_tasks SET status = 'completed', completed_at = CURRENT_TIMESTAMP
        WHERE id = ? AND user_id = ?
        ''', (task_id, user_id))

        conn.commit()
        conn.close()

        await ctx.send(f"🎉 タスク #{task_id} を完了しました！")

    else:
        await ctx.send("使い方: !task add|list|complete")

@bot.command()
async def advice(ctx):
    """AIアドバイスを提供（現在はダミー）"""
    user_id = get_or_create_user(str(ctx.author.id), ctx.author.name)
    tasks = get_user_tasks(user_id, status='pending')

    if not tasks:
        await ctx.send("💫 まずはタスクを追加してね: !task add <タイトル>")
        return

    # TODO: AIでアドバイス生成
    advice_text = "タスクを優先度順に進めるのがおすすめです✨"

    await ctx.send(f"💡 **アドバイス**\n{advice_text}")

if __name__ == '__main__':
    if not TOKEN:
        print("❌ DISCORD_BOT_TOKENが設定されていません")
        exit(1)

    bot.run(TOKEN)
