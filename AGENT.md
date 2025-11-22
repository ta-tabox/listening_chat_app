# AGENT.md

This file provides guidance to AI agents (including Claude Code, Cursor, and other AI development tools) when working with code in this repository.

## 言語設定

**重要: このリポジトリで作業する際は、必ず日本語で応答してください。**

コミュニケーション、説明、コミットメッセージ、ドキュメントなど、すべて日本語で行ってください（特に英語での記述を求められた場合を除く）。

## Gitコミットメッセージのルール

**要約（1行目）:**
- 50文字程度に簡潔にまとめる
- 何を変更したかを明確に示す

**詳細（2行目以降）:**
- 250文字以内に要点のみまとめる
- 箇条書きで変更内容を列挙
- 技術的な詳細や背景は簡潔に

**禁止事項:**
- 「Claudeが編集した」などのツール情報は含めない
- 不要な署名や生成情報は省略

## プロジェクト概要

** 傾聴型AIチャットアプリケーション**

「傾聴」に特化したAIチャットボットで、Vertex AI（Gemini 2.5 Flash）を使用して共感的で非批判的な会話応答を提供します。


## アーキテクチャ

### システム構成

```
フロントエンド (Vue.js + Vuetify)
    ↓ HTTPS
Cloud Functions (Python 3.11)
    ↓ API Call
Vertex AI (Gemini 1.5 Flash)
```

### 技術スタック

- **フロントエンド**: Vue.js 3, Vuetify 3, Vite, Axios
- **バックエンド**: Cloud Functions (Python 3.11), Flask, functions-framework
- **AI**: Vertex AI Gemini（傾聴に特化したカスタムシステムプロンプト）
- **ホスティング**: Firebase Hosting
- **プロジェクト構成**:
  - `frontend/` - Vue.jsアプリケーション
  - `functions/` - Cloud Functions Pythonコード

## 開発コマンド

### フロントエンド（Vue.js）

```bash
cd frontend

# 依存関係のインストール
npm install

# 開発サーバー起動 (http://localhost:5173)
npm run dev

# 本番用ビルド
npm run build

# 本番ビルドのプレビュー
npm run preview
```

### バックエンド（Cloud Functions）

```bash
cd functions

# Python仮想環境のセットアップ
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係のインストール
pip install -r requirements.txt

# 環境変数の設定
export GCP_PROJECT_ID="YOUR_PROJECT_ID"
export VERTEX_AI_LOCATION="YOUR_REGION"
export SYSTEM_PROMPT_ID="YOUR_PROMPT_ID"

# ローカル実行 (http://localhost:8080)
functions-framework --target=listening_chat_api --debug --port=8080

# ローカルエンドポイントのテスト
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "最近、仕事で悩んでいることがあります"}'
```

### デプロイ

```bash
# Cloud Functionsのデプロイ
cd functions
gcloud functions deploy listening_chat_api \
  --runtime python311 \
  --trigger-http \
  --allow-unauthenticated \
  --region ${VERTEX_AI_LOCATION} \
  --env-vars-file .env.yaml \
  --entry-point listening_chat_api \
  --max-instances 10 \
  --memory 256MB

# Firebase Hostingのデプロイ
cd ..
firebase deploy --only hosting
```

## コードアーキテクチャ

### フロントエンド構成

- **コンポーネント**:
  - `ChatWindow.vue` - メインチャット画面（メッセージ表示と入力エリア）
  - `MessageBubble.vue` - 個別メッセージ表示コンポーネント（ユーザー/AI識別）

- **サービス**:
  - `api.js` - Cloud Functionsとの通信、チャット履歴管理

- **状態管理**:
  - チャット履歴はコンポーネント状態で管理（永続化なし）
  - メッセージにはtext、timestamp、isUserフラグを含む

### バックエンド構成

- **main.py** - 統合APIエンドポイント:
  - `listening_chat_api()`関数がパスベースルーティングを処理（CORS有効）
  - エンドポイント:
    - `/chat` - チャット機能（POST）
    - `/get_prompt` - プロンプト取得（GET）
    - `/update_prompt` - プロンプト更新（POST）
  - 受信: `{message: string, history: array, summary?: string}`
  - 返却: `{response: string, history: array, summary?: string}`

- **システムプロンプトの思想**:
  AIは以下を重視するシステム指示で設定されています:
  1. 共感的で非批判的な応答
  2. 相手の話を遮らない積極的傾聴
  3. 一方的なアドバイスの回避
  4. ユーザーの感情表現をサポート
  5. 温かく受容的な態度の維持
  6. ユーザーのペースの尊重

### 環境変数

**フロントエンド** (`frontend/.env.local`):
```
VITE_API_ENDPOINT=https://${VERTEX_AI_LOCATION}-${GCP_PROJECT_ID}.cloudfunctions.net/listening_chat_api
```

**バックエンド** (`functions/.env.yaml`):
```yaml
GCP_PROJECT_ID: "YOUR_PROJECT_ID"
VERTEX_AI_LOCATION: "YOUR_REGION"  # 例: us-central1, asia-northeast1
SYSTEM_PROMPT_ID: "YOUR_PROMPT_ID"
```

⚠️ これらのファイルはgitignore対象 - 実際の認証情報は絶対にコミットしないこと。

## 重要な実装詳細

### CORS処理
Cloud FunctionsはプリフライトOPTIONSリクエストを処理し、すべてのレスポンスに`Access-Control-Allow-Origin: *`ヘッダーを含める必要があります。

### チャット履歴管理
- フロントエンドは各リクエストで完全なチャット履歴を送信
- バックエンドはGeminiの`start_chat(history=...)`を使用してコンテキスト維持
- 履歴フォーマットはVertex AIの会話構造に従う

### エラーハンドリング
- フロントエンドとバックエンドの両方でtry-catchエラー処理を実装
- ユーザー向けエラーメッセージは日本語
- バックエンドのエラーはprint()でCloud Functionsログに記録

### UI/UX考慮事項
- AI応答生成中のローディング状態表示
- 新しいメッセージで自動的に最下部へスクロール
- Vuetifyによるレスポンシブデザイン（モバイル対応）
- Enterキーでメッセージ送信、Shift+Enterで改行

## GCPセットアップ要件

開発前に以下を実行:

```bash
# 認証
gcloud auth login
gcloud auth application-default login

# プロジェクト設定
gcloud config set project ${GCP_PROJECT_ID}

# 必要なAPIの有効化
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable aiplatform.googleapis.com
```

## Firebase設定

`firebase.json`は以下を設定:
- 公開ディレクトリ: `frontend/dist`
- `/index.html`へのシングルページアプリリライト
- firebase.jsonとnode_modulesの除外パターン

## 設計思想

これは**最小限のポートフォリオプロジェクト**で、以下に焦点を当てています:
- AI統合スキルの実証（Vertex AI）
- クリーンなVue.jsコンポーネントアーキテクチャ
- サーバーレスバックエンド実装
- 認証なし（意図的にポートフォリオ用に簡素化）
- セッション内のみのチャット履歴（データベース永続化なし）

コアバリューは**共感的傾聴のシステムプロンプト**とクリーンなユーザー体験であり、機能の豊富さではありません。
