# モニタリング・運用ガイド / Monitoring & Operations Guide

## システム監視 / System Monitoring

### ダッシュボード確認 / Check Dashboard

http://localhost:8000 でリアルタイム監視

### Prometheusメトリクス / Prometheus Metrics

```bash
# メトリクス取得
curl http://localhost:8000/metrics
```

### Grafana設定 / Grafana Setup

1. Grafanaを起動
2. Prometheusデータソースを追加
3. ダッシュボードをインポート

## トラブルシューティング / Troubleshooting

### エージェントが起動しない / Agent Won't Start

1. ログを確認: `logs/agent.log`
2. データベースファイルを確認
3. 依存パッケージを再インストール

### データベースエラー / Database Error

```bash
# データベース再構築
rm agents/*/database.db
python3 agents/<agent>/db.py
```

### APIが応答しない / API Not Responding

```bash
# API再起動
pkill -f api.py
cd dashboard && python3 api.py
```

## バックアップ / Backup

```bash
# データベースバックアップ
cp agents/*/database.db backup/

# 設定ファイルバックアップ
tar -czf config-backup.tar.gz agents/*/config.json
```
