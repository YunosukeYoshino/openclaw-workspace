# デプロイメントガイド / Deployment Guide

## 本番環境へのデプロイ / Production Deployment

### Dockerデプロイ / Docker Deployment

```bash
# イメージビルド
docker build -t ai-agents:latest .

# コンテナ起動
docker run -d -p 8000:8000 ai-agents:latest
```

### Docker Compose

```bash
# 本番環境で起動
docker-compose -f docker-compose.prod.yml up -d

# ログ確認
docker-compose logs -f
```

### Kubernetesデプロイ / Kubernetes Deployment

```bash
# マニフェスト適用
kubectl apply -f full_deployment/deployment/kubernetes-config/

# ポートフォワード
kubectl port-forward service/agents-api 8000:8000
```

### 環境変数設定 / Environment Variables

```bash
export DATABASE_URL="postgresql://..."
export SLACK_BOT_TOKEN="xoxb-..."
export NOTION_API_KEY="secret_..."
```

### SSL/TLS設定 / SSL/TLS Setup

Let's Encryptを使用してHTTPSを有効化：

```bash
certbot certonly --webroot -w /var/www/html -d yourdomain.com
```
