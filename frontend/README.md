# 傾聴チャットアプリ - フロントエンド

Vue.js 3 + Vuetify 3で構築された、傾聴に特化したAIチャットアプリケーションのフロントエンドです。

## 技術スタック

- **Vue.js 3**: Composition API (`<script setup>`)
- **Vuetify 3**: Material Design コンポーネントフレームワーク
- **Vite**: 高速ビルドツール & 開発サーバー
- **Axios**: HTTP クライアント（Cloud Functions との通信）
- **Firebase Hosting**: デプロイ先

## セットアップ

### 依存関係のインストール

```bash
npm install
```

### 環境変数の設定

#### ローカル開発用

`.env.local` ファイルを作成（gitignore対象）：

```bash
# ローカル開発時はバックエンドもローカルで起動する場合
VITE_API_ENDPOINT=http://localhost:8080

# またはデプロイ済みのCloud Functionsを使用する場合
# VITE_API_ENDPOINT=https://asia-northeast1-your-project-id.cloudfunctions.net/listening_chat_api
```

#### 本番環境用

`.env.production` ファイルを作成（gitignore対象）：

```bash
# Cloud FunctionsのエンドポイントURL
VITE_API_ENDPOINT=https://asia-northeast1-your-project-id.cloudfunctions.net/listening_chat_api
```

**注意:**
- プロジェクトIDとリージョンは実際の値に置き換えてください
- GitHub Actionsを使用する場合、環境変数は自動的に設定されます

## 開発サーバー

```bash
npm run dev
```

開発サーバーが起動し、`http://localhost:5173`でアクセスできます。

## ビルド

本番用にビルド：

```bash
npm run build
```

ビルドされたファイルは`dist/`ディレクトリに生成されます。

## プレビュー

本番ビルドのプレビュー：

```bash
npm run preview
```

## プロジェクト構成

```
frontend/
├── src/
│   ├── components/
│   │   ├── ChatWindow.vue       # メインチャットコンポーネント
│   │   ├── PromptEditor.vue     # システムプロンプト編集UI
│   │   └── HelloWorld.vue       # サンプルコンポーネント
│   ├── plugins/
│   │   └── vuetify.js           # Vuetify設定
│   ├── services/
│   │   └── api.js               # API通信サービス（axios）
│   ├── App.vue                  # ルートコンポーネント
│   └── main.js                  # エントリーポイント
├── public/                       # 静的アセット
├── .env.local                    # ローカル環境変数（gitignore）
├── .env.production               # 本番環境変数（gitignore）
├── vite.config.js               # Vite設定
├── index.html                   # HTMLテンプレート
└── package.json                 # 依存関係管理
```

## 主な機能

### ChatWindow.vue（メインチャット画面）

- **リアルタイムチャット表示**: ユーザーとAIの会話をリアルタイムで表示
- **メッセージ区別**: ユーザーメッセージ（右側・青色）とAI応答（左側・グレー）を視覚的に区別
- **日本語IME対応**: 変換確定のEnterキーを無視し、Shift+Enterで改行
- **ローディング状態**: AI応答生成中にスピナーを表示
- **エラーハンドリング**: ネットワークエラーやAPIエラーを適切に表示
- **チャット履歴管理**: セッション内の会話履歴を保持
- **会話要約機能**: バックエンドの自動要約機能をサポート
- **自動スクロール**: 新しいメッセージで自動的に最下部へスクロール
- **レスポンシブデザイン**: モバイルとデスクトップの両方に対応

### PromptEditor.vue（プロンプト編集機能）

- **システムプロンプト表示**: 現在のシステムプロンプトを取得・表示
- **プロンプト編集**: システムプロンプトをリアルタイムで編集可能
- **保存機能**: 編集したプロンプトをバックエンドに保存
- **エラーハンドリング**: 取得・更新時のエラーを適切に表示

### api.js（API通信サービス）

- **チャット送信**: `/chat` エンドポイントへのPOSTリクエスト
- **プロンプト取得**: `/get_prompt` エンドポイントからの取得
- **プロンプト更新**: `/update_prompt` エンドポイントへの更新
- **エラーハンドリング**: axios interceptorsを使用した統一的なエラー処理

## デプロイ

### 手動デプロイ（Firebase Hosting）

プロジェクトルートから実行：

```bash
# フロントエンドのビルド
cd frontend
npm run build

# Firebase Hostingへデプロイ
cd ..
firebase deploy --only hosting
```

### 自動デプロイ（GitHub Actions）

mainブランチへのプッシュで自動的にデプロイされます：

1. **フロントエンドのビルド**: 環境変数 `VITE_API_ENDPOINT` が自動設定
2. **Firebase Hostingへデプロイ**: ビルド済みファイルが自動的にデプロイ

詳細は `.github/workflows/deploy.yml` を参照してください。

## API通信について

フロントエンドは以下のエンドポイントと通信します：

### チャット送信

```javascript
POST /chat
Content-Type: application/json

{
  "message": "ユーザーのメッセージ",
  "history": [...],        // 会話履歴（オプション）
  "summary": "..."         // 会話要約（オプション）
}
```

### プロンプト取得

```javascript
GET /get_prompt
```

### プロンプト更新

```javascript
POST /update_prompt
Content-Type: application/json

{
  "prompt": "新しいシステムプロンプト"
}
```

## CORS設定について

バックエンド（Cloud Functions）側で以下のCORS設定が必要です：

- **ローカル開発**: 自動的に `*` が設定されます
- **本番環境**: `ALLOWED_ORIGINS` 環境変数でフロントエンドのURLを指定

詳細は `functions/README.md` の「CORS設定」セクションを参照してください。

## トラブルシューティング

### APIエンドポイントに接続できない

1. `.env.local` または `.env.production` が正しく設定されているか確認
2. バックエンド（Cloud Functions）がデプロイされているか確認
3. ブラウザの開発者ツールでネットワークタブを確認

### CORS エラーが発生する

1. バックエンドの `ALLOWED_ORIGINS` 環境変数が正しく設定されているか確認
2. フロントエンドのデプロイURLが `ALLOWED_ORIGINS` に含まれているか確認

### ビルドエラーが発生する

```bash
# node_modulesを削除して再インストール
rm -rf node_modules package-lock.json
npm install
npm run build
```
