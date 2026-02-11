#!/usr/bin/env python3
"""
音声要約エージェント #1 (Python版Whisper)
- Whisper Python版で音声認識
- ローカルLLM (Ollama) で要約
- Slackに配信
"""

import whisper
import requests
import torch
from pathlib import Path
from datetime import datetime

# 設定
OLLAMA_URL = "http://localhost:11434/api/generate"
SLACK_WEBHOOK_URL = ""  # TODO: 設定
WHISPER_MODEL = "base"  # tiny, base, small, medium, large

def transcribe_audio(audio_file):
    """音声→テキスト (Whisper Python)"""
    print(f"📥 Whisperモデルロード中 ({WHISPER_MODEL})...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = whisper.load_model(WHISPER_MODEL, device=device)

    print(f"🎤 音声認識中 (device: {device})...")
    result = model.transcribe(str(audio_file))
    text = result["text"]

    print(f"📝 認識完了: {len(text)}文字")
    return text

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
    print("✨ 要約中...")
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

    if not audio_file.exists():
        print(f"⚠️ 音声ファイルが見つかりません: {audio_file}")
        return

    text = transcribe_audio(audio_file)
    summary = summarize_text(text)
    print("\n" + summary)
    send_to_slack(summary)

if __name__ == "__main__":
    main()
