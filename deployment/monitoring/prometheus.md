# Monitoring Configuration

## Prometheus

scrape_configs:
  - job_name: 'ai-agents'
    static_configs:
      - targets: ['localhost:8000']

## Alert Rules

- High error rate > 10/sec
- Response time > 1s
- Service down
