# Cloud Run用Dockerfile for FastAPI Backend

# Python 3.12-slimをベースイメージとして使用
FROM python:3.12-slim

# 作業ディレクトリを設定
WORKDIR /app

# システムパッケージのアップデートと必要なパッケージのインストール
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# uvをインストール
RUN pip install uv

# Pythonプロジェクトファイルをコピー（キャッシュ効率のため）
COPY pyproject.toml uv.lock ./

# プロジェクトの依存関係をインストール
RUN uv sync --frozen

# アプリケーションコードをコピー
COPY . .

# dataディレクトリを作成（絵本データ保存用）
RUN mkdir -p /app/data

# スタートアップスクリプトを作成
RUN echo '#!/bin/bash' > /app/start.sh && \
    echo '# Cloud RunのPORT環境変数を使用（デフォルトは8080）' >> /app/start.sh && \
    echo 'PORT=${PORT:-8080}' >> /app/start.sh && \
    echo 'echo "Starting server on port $PORT"' >> /app/start.sh && \
    echo '' >> /app/start.sh && \
    echo '# uvicornを直接実行してCloud Run対応' >> /app/start.sh && \
    echo 'uv run uvicorn main:app --host 0.0.0.0 --port $PORT' >> /app/start.sh

RUN chmod +x /app/start.sh

# Cloud Runのポート（固定値でEXPOSE）
EXPOSE 8080

# ヘルスチェック（Cloud Run対応）
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:${PORT:-8080}/health || exit 1

# アプリケーションを起動
CMD ["/app/start.sh"]
