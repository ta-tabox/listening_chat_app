# 傾聴チャットバックエンドAPI

傾聴型AIチャットアプリケーションのバックエンドAPI（Cloud Functions）

## 技術スタック

- **ランタイム**: Python 3.11
- **フレームワーク**: Flask + functions-framework
- **AI モデル**: Vertex AI Gemini 2.5 Flash (gemini-2.5-flash)
- **デプロイ**: Google Cloud Functions (asia-northeast1)
- **AI ロケーション**: us-central1（Vertex AI）

## 主要機能

### 1. 傾聴特化型システムプロンプト

共感的で非批判的な対話を実現するカスタムプロンプトを使用：
- 相手の気持ちに寄り添い、共感的に応答
- 安易なアドバイスや解決策を押し付けない
- 相手の感情を言語化し、理解を深める手助け

### 2. 会話要約機能によるコスト最適化 🌟

**課題**: 長時間の会話で履歴が増大し、トークン消費量が増加

**解決策**: 段階的要約システムを実装

```
履歴10件（5往復）到達時
  ↓
最古10件を要約 + 直近2件を保持
  ↓
要約 + 最大2件でコンテキスト維持
```

**効果**:
- リクエストサイズを一定範囲に制限
- トークン消費量を最適化
- 過去の文脈は要約で保持

### 3. その他機能

- 会話履歴管理（Vertex AI Content オブジェクト）
- CORS対応
- エラーハンドリング

## APIエンドポイント

統合APIエンドポイント `listening_chat_api` がパスベースルーティングで複数の機能を提供：

### 1. `/chat` - チャット機能（POST）

メインの会話機能。ユーザーメッセージを受け取り、AI応答を返却します。

#### リクエスト

```json
{
  "message": "最近、仕事で悩んでいます",
  "history": [...],      // オプション: 会話履歴
  "summary": "..."       // オプション: 既存の要約
}
```

#### レスポンス

```json
{
  "response": "そうなんですね。お話を聞かせていただけますか？",
  "history": [...],      // 更新された履歴
  "summary": "..."       // 要約（作成された場合のみ）
}
```

### 2. `/get_prompt` - プロンプト取得（GET）

現在のシステムプロンプトを取得します。

#### レスポンス

```json
{
  "prompt": "あなたは優れた傾聴者です。..."
}
```

### 3. `/update_prompt` - プロンプト更新（POST）

システムプロンプトを更新します（SYSTEM_PROMPT_ID が設定されている場合のみ）。

#### リクエスト

```json
{
  "prompt": "新しいシステムプロンプトのテキスト"
}
```

#### レスポンス

```json
{
  "success": true,
  "message": "プロンプトを更新しました"
}
```

## ローカル開発

### セットアップ方法

#### 方法1: Pipenv（推奨）

```bash
# 依存関係のインストール
pipenv install

# 仮想環境のアクティベート
pipenv shell
```

#### 方法2: venv + pip

```bash
# 仮想環境の作成
python -m venv venv

# 仮想環境のアクティベート
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係のインストール
pip install -r requirements.txt
```

### 環境変数の設定

```bash
# 必須
export GCP_PROJECT_ID="your-project-id"
export VERTEX_AI_LOCATION="us-central1"

# オプション
export VERTEX_AI_MODEL="gemini-2.5-flash"           # デフォルト: gemini-2.5-flash
export SYSTEM_PROMPT_ID="your-prompt-id"            # システムプロンプトの動的更新が必要な場合
export ALLOWED_ORIGINS="https://your-domain.com"    # 本番環境用（カンマ区切りで複数可）

# 注意: ローカル開発時は ALLOWED_ORIGINS を設定不要（自動的に * に設定されます）
```

### サーバー起動

```bash
# Pipenvを使用する場合
pipenv run functions-framework --target=listening_chat_api --debug --port=8080

# venvを使用する場合
functions-framework --target=listening_chat_api --debug --port=8080
```

### テスト実行

```bash
# チャットエンドポイントのテスト
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "最近、仕事で悩んでいることがあります"}'

# プロンプト取得のテスト
curl -X GET http://localhost:8080/get_prompt

# 要約機能のテスト
python test_summary.py
```

## デプロイ

### 環境変数ファイルの準備

デプロイ前に `.env.yaml` を作成してください（gitignore対象のため手動作成が必要）：

```yaml
# .env.yaml（例）
GCP_PROJECT_ID: "your-project-id"
VERTEX_AI_LOCATION: "us-central1"
VERTEX_AI_MODEL: "gemini-2.5-flash"           # オプション（デフォルト: gemini-2.5-flash）
SYSTEM_PROMPT_ID: "your-prompt-id"            # オプション
ALLOWED_ORIGINS: "https://your-domain.com"    # 本番環境用（必須推奨）

# 複数のオリジンを許可する場合
# ALLOWED_ORIGINS: "https://domain1.com,https://domain2.com"
```

### Cloud Functionsへのデプロイ

```bash
gcloud functions deploy listening_chat_api \
  --runtime python311 \
  --trigger-http \
  --allow-unauthenticated \
  --region asia-northeast1 \
  --env-vars-file .env.yaml \
  --entry-point listening_chat_api \
  --max-instances 10 \
  --memory 512MB
```

**注意事項：**
- Cloud Functionsのデプロイリージョン: `asia-northeast1`（日本）
- Vertex AIのロケーション: `us-central1`（環境変数で指定）
- この2つは異なるリージョンですが、正常に動作します

### GitHub Actionsでのデプロイ

このプロジェクトは、mainブランチへのプッシュで自動的にデプロイされるよう設定されています。

#### 必要なGitHub Secrets

GitHubリポジトリの **Settings > Secrets and variables > Actions** で以下を設定してください：

**Secrets（機密情報）:**
- `GCP_PROJECT_ID` - GCPプロジェクトID
- `WORKLOAD_IDENTITY_PROVIDER` - Workload Identity Providerのリソース名
- `SERVICE_ACCOUNT_EMAIL` - サービスアカウントのメールアドレス
- `SYSTEM_PROMPT_ID` - システムプロンプトID（オプション）

**Variables（非機密情報）:**
- `VERTEX_AI_LOCATION` - Vertex AIのロケーション（例: `us-central1`）
- `VERTEX_AI_MODEL` - 使用するモデル名（例: `gemini-2.5-flash`）
- `ALLOWED_ORIGINS` - 許可するオリジン（例: `https://your-app.web.app`）

**注意:**
- `ALLOWED_ORIGINS` は本番環境のフロントエンドURLを指定してください
- 複数のオリジンを許可する場合は、カンマ区切りで指定：`https://app.com,https://staging.app.com`

## プロジェクト構成

```
functions/
├── main.py              # Cloud Functions実装（listening_chat_api関数）
├── requirements.txt     # 本番用依存関係（pip freeze出力）
├── Pipfile              # 開発環境用依存関係管理
├── Pipfile.lock         # 開発環境用ロックファイル
├── .env.yaml            # 環境変数（gitignore対象）
├── test_summary.py      # 要約機能テストスクリプト
├── test_prompt.py       # プロンプト機能テストスクリプト
└── create_prompt.py     # プロンプト作成ユーティリティ
```

## 主要な依存関係

- `functions-framework==3.5.0` - Cloud Functions ローカル実行
- `google-cloud-aiplatform>=1.60.0` - Vertex AI 統合（レガシー）
- `google-genai` - Vertex AI Gemini チャット機能
- `flask==3.0.0` - HTTPリクエストハンドリング

## その他の注意事項

### モデル設定について

- `VERTEX_AI_MODEL` 環境変数でモデルを指定可能（デフォルト: `gemini-2.5-flash`）
- チャット機能と要約機能の両方で同じモデルを使用

### システムプロンプトについて

- `SYSTEM_PROMPT_ID` が設定されている場合、Vertex AI Prompt Management から動的に取得
- 設定されていない場合は、コード内のデフォルトプロンプトを使用
- `/update_prompt` エンドポイントでプロンプトを更新できます（Prompt Management利用時のみ）

### CORS設定

環境に応じて自動的に適切なCORS設定が適用されます：

**ローカル開発環境:**
- `K_SERVICE` 環境変数が存在しない場合、自動的にローカル環境と判定
- すべてのオリジン (`*`) を許可
- `ALLOWED_ORIGINS` の設定は不要

**本番環境（Cloud Functions）:**
- `K_SERVICE` 環境変数が存在する場合、本番環境と判定
- `ALLOWED_ORIGINS` で指定されたオリジンのみを許可
- 複数のオリジンを許可する場合はカンマ区切りで指定
- **重要**: `ALLOWED_ORIGINS` が未設定の場合は警告ログが出力され、一時的に `*` が使用されます

**設定例:**
```yaml
# 単一オリジン
ALLOWED_ORIGINS: "https://your-frontend-app.web.app"

# 複数オリジン
ALLOWED_ORIGINS: "https://your-app.com,https://staging.your-app.com"
```

### コスト最適化

会話履歴が10件に達すると自動的に要約が生成され、トークン消費量を最適化します。詳細は「会話要約機能によるコスト最適化」セクションを参照。
