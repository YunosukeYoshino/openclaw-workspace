#!/bin/bash
# 音声要約エージェント セットアップ (Python版Whisper)

echo "🎤 音声要約エージェント セットアップ (Python版)"
echo "============================================"

# Python依存関係
echo "📦 Pythonパッケージインストール中..."
pip install openai-whisper requests torch

echo "✅ Whisperインストール完了"

# Ollama確認
echo ""
echo "🔍 Ollamaがインストールされているか確認..."
if command -v ollama &> /dev/null; then
    echo "✅ Ollamaが見つかりました"
    ollama list
else
    echo "⚠️ Ollamaが見つかりません"
    echo "インストール: curl -fsSL https://ollama.ai/install.sh | sh"
fi

echo ""
echo "🎉 セットアップ完了！"
echo ""
echo "次のステップ:"
echo "1. Slack Webhook URLを取得して main_python.py に設定"
echo "2. 音声ファイルを用意"
echo "3. python3 main_python.py を実行"
