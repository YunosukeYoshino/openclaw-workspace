# Production Deployment Guide

## Prerequisites

- Docker 24.0+
- Docker Compose 2.20+
- Nginx 1.24+

## Setup

```bash
git clone <repo>
cd <repo>
cp .env.example .env
nano .env
docker compose up -d
```

## SSL

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

## Monitoring

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000
