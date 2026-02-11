#!/bin/bash
# 音声要約エージェント セットアップスクリプト

echo "🎤 音声要約エージェント セットアップ"
echo "=================================="

# ディレクトリ
BIN_DIR="/home/node/.openclaw/workspace/agents/audio-summarizer/bin"
MODELS_DIR="/home/node/.openclaw/workspace/agents/audio-summarizer/models"

# whisper.cpp クローンとビルド
if [ ! -d "$BIN_DIR/whisper.cpp" ]; then
    echo "📥 whisper.cppをダウンロード中..."
    git clone https://github.com/ggerganov/whisper.cpp.git "$BIN_DIR/whisper.cpp"
fi

echo "🔨 whisper.cppをビルド中..."
cd "$BIN_DIR/whisper.cpp"
make
echo "✅ whisper.cppビルド完了"

# モデルダウンロード (baseモデル - 軽量)
if [ ! -f "$MODELS_DIR/ggml-base.bin" ]; then
    echo "📥 Whisperモデルをダウンロード中..."
    mkdir -p "$MODELS_DIR"
    ./download_model.sh base
    mv ggml-base.bin "$MODELS_DIR/"
fi

echo "✅ モデルダウンロード完了"

# Ollama確認
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
echo "1. Slack Webhook URLを取得して main.py に設定"
echo "2. 音声ファイルを用意"
echo "3. python3 main.py を実行"
