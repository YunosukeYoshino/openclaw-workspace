
FROM python:3.11-slim

WORKDIR /app

# システム依存のインストール
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python依存のインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのコピー
COPY . .

# ポートの公開
EXPOSE 8000

# 起動コマンド
CMD ["python3", "dashboard/api.py"]
