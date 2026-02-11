#!/usr/bin/env python3
"""
音声要約エージェント #1
"""

import whisper
from pathlib import Path

# 音声ファイル
AUDIO_FILE = Path("/workspace/media/inbound/fe6d6411-dda0-46e2-8e3c-ad8c4f75a004.ogg")

# Whisperモデル
MODEL_NAME = "base"  # tiny, base, small, medium, large

def main():
    if not AUDIO_FILE.exists():
        print(f"⚠️ 音声ファイルが見つかりません: {AUDIO_FILE}")
        return

    print(f"🎤 音声ファイル: {AUDIO_FILE}")
    print(f"📥 Whisperモデルロード中 ({MODEL_NAME})...")

    # モデルロード (CPU)
    model = whisper.load_model(MODEL_NAME, device="cpu")

    print(f"🎤 音声認識中...")
    result = model.transcribe(str(AUDIO_FILE), language="ja")
    text = result["text"]

    print("\n" + "="*50)
    print("📝 音声認識結果:")
    print("="*50)
    print(text)
    print("="*50)

    # 統計
    duration = result.get("segments", [])
    total_duration = sum(s["end"] for s in duration)
    print(f"\n📊 統計:")
    print(f"  音声長: {total_duration:.2f}秒")
    print(f"  文字数: {len(text)}文字")

if __name__ == "__main__":
    main()
