# AI Agents Dashboard

AIエージェントを管理・監視するためのWebダッシュボード。

## 機能

- エージェント一覧の表示
- 各エージェントのステータス確認（稼働中/停止中/エラー）
- エージェントの詳細情報表示
- エージェントの起動/停止操作（準備中）
- 統計情報のリアルタイム表示

## インストール

```bash
cd /workspace/dashboard
pip install -r requirements.txt
```

## 実行

```bash
python3 api.py
```

またはuvicornを直接使用:

```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

## アクセス

ブラウザで以下のURLにアクセスしてください:

- ダッシュボード: http://localhost:8000
- APIドキュメント: http://localhost:8000/docs

## APIエンドポイント

| エンドポイント | 説明 |
|-------------|------|
| `GET /` | ダッシュボードトップページ |
| `GET /api/agents` | 全エージェントのリスト |
| `GET /api/agents/{name}` | 特定のエージェント情報 |
| `POST /api/agents/{name}/start` | エージェント起動 |
| `POST /api/agents/{name}/stop` | エージェント停止 |
| `GET /api/stats` | 統計情報 |

## ディレクトリ構造

```
dashboard/
├── api.py              # FastAPIアプリケーション
├── requirements.txt    # 依存パッケージ
├── static/
│   ├── css/
│   │   └── style.css  # スタイルシート
│   └── js/
│       └── app.js     # フロントエンドアプリ
└── templates/
    └── index.html     # HTMLテンプレート
```

## 今後の拡張

- [ ] エージェントの実際の起動/停止ロジック
- [ ] リアルタイムログ表示
- [ ] データ可視化（チャート、グラフ）
- [ ] エージェント間連携の視覚化
- [ ] ユーザー認証・認可
- [ ] 設定管理画面
- [ ] アラート・通知機能

---

Built with FastAPI, HTML, CSS, and JavaScript.
