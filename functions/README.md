# つながりAI - バックエンドAPI

傾聴型AIチャットアプリケーションのバックエンドAPI（Cloud Functions）

## 技術スタック

- **ランタイム**: Python 3.11
- **フレームワーク**: Flask + functions-framework
- **AI モデル**: Vertex AI Gemini 2.5 Flash Lite
- **デプロイ**: Google Cloud Functions (asia-northeast1)

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

## API仕様

### エンドポイント

```
POST https://asia-northeast1-tsunagari-llm-chat-app.cloudfunctions.net/chat
```

### リクエスト

```json
{
  "message": "最近、仕事で悩んでいます",
  "history": [...],      // オプション: 会話履歴
  "summary": "..."       // オプション: 既存の要約
}
```

### レスポンス

```json
{
  "response": "そうなんですね。お話を聞かせていただけますか？",
  "history": [...],      // 更新された履歴
  "summary": "..."       // 要約（作成された場合のみ）
}
```

## ローカル開発

```bash
# セットアップ
pipenv install

# サーバー起動
export GCP_PROJECT_ID="tsunagari-llm-chat-app"
export GCP_LOCATION="us-central1"
pipenv run functions-framework --target=chat --debug

# テスト実行
pipenv run python test_summary.py
```

## デプロイ

```bash
gcloud functions deploy chat \
  --runtime python311 \
  --trigger-http \
  --allow-unauthenticated \
  --region asia-northeast1 \
  --env-vars-file .env.yaml \
  --entry-point chat \
  --max-instances 10 \
  --memory 256MB
```

## プロジェクト構成

```
functions/
├── main.py              # Cloud Functions実装
├── requirements.txt     # 依存関係
├── Pipfile              # 開発環境用
├── .env.yaml            # 環境変数（gitignore）
└── test_summary.py      # テストスクリプト
```
