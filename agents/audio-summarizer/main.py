#!/usr/bin/env python3
"""
音声要約エージェント #1
- whisper.cppで音声認識
- ローカルLLM (Ollama) で要約
- Slackに配信
"""

import subprocess
import json
import requests
from pathlib import Path
from datetime import datetime

# 設定
WHISPER_CPP_PATH = Path("/home/node/.openclaw/workspace/agents/audio-summarizer/bin/whisper.cpp/main")
MODEL_PATH = Path("/home/node/.openclaw/workspace/agents/audio-summarizer/models/ggml-base.bin")
OLLAMA_URL = "http://localhost:11434/api/generate"
SLACK_WEBHOOK_URL = ""  # TODO: 設定

def transcribe_audio(audio_file):
    """音声→テキスト (whisper.cpp)"""
    cmd = [
        str(WHISPER_CPP_PATH),
        "-m", str(MODEL_PATH),
        "-f", str(audio_file),
        "-otxt"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

def summarize_text(text):
    """テキスト→要約 (Ollama)"""
    prompt = f"""以下のテキストを要約してください。出力形式:
【要約】
(簡潔な要約)

【キーポイント】
- ポイント1
- ポイント2
...

テキスト:
{text}"""

    payload = {
        "model": "llama2",  # TODO: モデル名
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(OLLAMA_URL, json=payload)
    return response.json().get("response", "")

def send_to_slack(summary):
    """Slackに送信"""
    if not SLACK_WEBHOOK_URL:
        print("⚠️ SLACK_WEBHOOK_URL未設定")
        return

    payload = {
        "text": f"🎤 音声要約 ({datetime.now().strftime('%Y-%m-%d %H:%M')})\n\n{summary}"
    }
    requests.post(SLACK_WEBHOOK_URL, json=payload)
    print("✅ Slack送信完了")

def main():
    audio_file = Path("audio.mp3")  # TODO: 入力ファイル

    print("🎤 音声認識中...")
    text = transcribe_audio(audio_file)
    print(f"📝 認識結果: {len(text)}文字")

    print("✨ 要約中...")
    summary = summarize_text(text)
    print(summary)

    print("📤 Slack送信中...")
    send_to_slack(summary)

if __name__ == "__main__":
    main()
