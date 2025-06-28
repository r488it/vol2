# Storybook API Backend

FastAPIを使用した絵本データ管理APIサーバーです。絵本のJSONデータの保存、一覧取得、個別取得機能を提供します。

## 🚀 特徴

- **FastAPI** による高性能なREST API
- **uv** による高速なPython依存関係管理
- **Cloud Run** 対応のコンテナ化
- 絵本データのJSON形式保存
- Base64エンコード画像・音声データ対応
- CORS対応によるフロントエンド統合

## 📋 API仕様

### エンドポイント

| メソッド | パス | 説明 |
|---------|------|------|
| GET | `/` | ルートエンドポイント |
| GET | `/health` | ヘルスチェック |
| POST | `/api/upload-storybook` | 絵本データアップロード |
| GET | `/api/storybooks` | 絵本一覧取得 |
| GET | `/api/storybook/{filename}` | 個別絵本データ取得 |

### データ構造

```json
{
  \"metadata\": {
    \"title\": \"絵本のタイトル\",
    \"createdAt\": \"2024-01-01T00:00:00\",
    \"totalPages\": 10,
    \"savedPages\": 8,
    \"skippedPages\": 2,
    \"version\": \"1.0.0\",
    \"note\": \"備考\"
  },
  \"pages\": [
    {
      \"pageNumber\": 1,
      \"text\": \"ページのテキスト\",
      \"imagePrompt\": \"画像生成プロンプト\",
      \"imageBase64\": \"data:image/png;base64,...\",
      \"audioBase64\": \"data:audio/wav;base64,...\"
    }
  ]
}
```

## 🛠️ ローカル開発

### 前提条件

- Python 3.12以上
- uv (Python パッケージマネージャー)

### セットアップ

```bash
# 依存関係のインストール
uv sync

# 開発サーバー起動
uv run main.py
```

サーバーは `http://localhost:9998` で起動します。

### 開発用コマンド

```bash
# 依存関係の追加
uv add パッケージ名

# 依存関係の更新
uv sync --update

# Python環境の確認
uv python list
```

## 🚀 Cloud Runデプロイ

### 1. プロジェクト設定

```bash
# Google Cloud CLIのインストール（未インストールの場合）
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# 認証
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### 2. Dockerイメージのビルドとプッシュ

```bash
# Artifact Registryのリポジトリ作成（初回のみ）
gcloud artifacts repositories create storybook-backend \\
    --repository-format=docker \\
    --location=us-central1

# Dockerイメージのビルド
docker build -t gcr.io/YOUR_PROJECT_ID/storybook-backend:latest .

# Container Registryにプッシュ
docker push gcr.io/YOUR_PROJECT_ID/storybook-backend:latest
```

### 3. Cloud Runサービスのデプロイ

```bash
# Cloud Runにデプロイ
gcloud run deploy storybook-backend \\
    --image gcr.io/YOUR_PROJECT_ID/storybook-backend:latest \\
    --platform managed \\
    --region us-central1 \\
    --allow-unauthenticated \\
    --port 8080 \\
    --memory 1Gi \\
    --cpu 1 \\
    --max-instances 10
```

### 4. 環境変数の設定（必要に応じて）

```bash
gcloud run services update storybook-backend \\
    --region us-central1 \\
    --set-env-vars \"ENV_VAR=value\"
```

## 🐳 Docker

### ローカルでのDockerテスト

```bash
# イメージビルド
docker build -t storybook-backend .

# コンテナ実行
docker run -p 8080:8080 storybook-backend

# 環境変数を指定して実行
docker run -p 9999:9999 -e PORT=9999 storybook-backend
```

### Docker Compose（オプション）

```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - \"8080:8080\"
    environment:
      - PORT=8080
    volumes:
      - ./data:/app/data
```

## 📁 ディレクトリ構造

```
backend/
├── Dockerfile          # Cloud Run用Dockerファイル
├── README.md           # このファイル
├── main.py             # FastAPIアプリケーション
├── pyproject.toml      # Python依存関係定義
├── uv.lock            # ロックファイル
├── requirements.txt    # pip用依存関係（互換性）
└── data/              # 絵本データ保存ディレクトリ
    ├── s1.json
    ├── s2.json
    └── s3.json
```

## 🔧 トラブルシューティング

### よくある問題

1. **ポート衝突エラー**
   ```bash
   # 使用中のポートを確認
   lsof -i :9998
   # プロセスを終了
   kill -9 PID
   ```

2. **依存関係エラー**
   ```bash
   # uvの再インストール
   pip install --upgrade uv
   uv sync --reinstall
   ```

3. **Cloud Runデプロイエラー**
   ```bash
   # ログの確認
   gcloud run services logs tail storybook-backend --region us-central1
   ```

## 📊 モニタリング

### ヘルスチェック

```bash
# ローカル
curl http://localhost:9998/health

# Cloud Run
curl https://YOUR_SERVICE_URL/health
```

### ログ確認

```bash
# Cloud Runログ
gcloud run services logs tail storybook-backend --region us-central1

# ローカルログ
tail -f server.log
```

## 🔒 セキュリティ

- CORS設定により特定のオリジンからのアクセスを制限
- ファイルパスのセキュリティチェック実装
- 入力データのバリデーション

本番環境では以下の設定を推奨：
- CORS設定の厳格化
- 認証・認可の実装
- HTTPSの強制
- レート制限の実装

## 📄 ライセンス

本PJはOSSではありません

