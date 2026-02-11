# 音声要約エージェント #1

AIエージェント100個の1つ目！

## 概要

音声ファイルを渡すと、要約とキーポイントをSlackに送ってくれます。

## アーキテクチャ

```
🎤 音声ファイル
    ↓
📝 whisper.cpp (音声→テキスト)
    ↓
✨ Ollama (要約 + キーポイント)
    ↓
📤 Slack Webhook
```

## セットアップ

### 1. whisper.cppセットアップ

```bash
cd /home/node/.openclaw/workspace/agents/audio-summarizer
chmod +x setup.sh
./setup.sh
```

### 2. Ollamaセットアップ

```bash
# Ollamaインストール
curl -fsSL https://ollama.ai/install.sh | sh

# モデル起動
ollama serve &

# モデルプル (軽量モデル)
ollama pull llama2
# または
ollama pull mistral
```

### 3. Slack Webhook取得

1. Slackの [Incoming Webhook](https://api.slack.com/messaging/webhooks) に行く
2. 新しいWebhookを作成
3. URLをコピーして `main.py` の `SLACK_WEBHOOK_URL` に設定

### 4. Python依存関係

```bash
pip install requests
```

## 使い方

```bash
# 音声ファイルを配置
mv your_audio.mp3 /home/node/.openclaw/workspace/agents/audio-summarizer/audio.mp3

# 実行
python3 main.py
```

## 出力例

Slackにこんな感じで送られる:

```
🎤 音声要約 (2026-02-07 16:30)

【要約】
会議でQ2のプロダクトロードマップについて議論。3つの新機能を決定。

【キーポイント】
- 新機能A: AI要約機能を追加
- 新機能B: モバイルアプリのUI改善
- 新機能C: パフォーマンス最適化
- 次回会議: 来週月曜日
```

## 技術スタック

- **音声認識**: whisper.cpp (ローカル、高速)
- **要約**: Ollama (ローカルLLM)
- **配信**: Slack Incoming Webhooks

## 達成状況

- [x] 仕設計完了
- [x] プロトタイプ作成
- [ ] セットアップ完了
- [ ] 最初の要約成功
- [ ] 本番稼働

## 次のステップ

1. セットアップ実行
2. テスト音声で動作確認
3. Slackで要約受け取り確認
