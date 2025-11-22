# 傾聴チャットアプリ - フロントエンド

Vue.js 3 + Vuetify 3で構築された、傾聴に特化したAIチャットアプリケーションのフロントエンドです。

## 技術スタック

- **Vue.js 3**: Composition API (`<script setup>`)
- **Vuetify 3**: Material Designコンポーネントフレームワーク
- **Vite**: 高速ビルドツール
- **Axios**: HTTPクライアント

## セットアップ

### 依存関係のインストール

```bash
npm install
```

### 環境変数の設定

`.env.local`ファイルを作成し、Cloud FunctionsのエンドポイントURLを設定します：

```bash
VITE_API_ENDPOINT=<your-cloud-functions-endpoint>
```

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
│   │   └── ChatWindow.vue     # メインチャットコンポーネント
│   ├── plugins/
│   │   └── vuetify.js         # Vuetify設定
│   ├── services/
│   │   └── api.js             # API通信サービス
│   ├── App.vue                # ルートコンポーネント
│   └── main.js                # エントリーポイント
├── public/                     # 静的アセット
├── vite.config.js             # Vite設定
└── package.json
```

## 主な機能

### ChatWindow.vue

- リアルタイムチャット表示
- ユーザーメッセージとAI応答の区別
- 日本語IME対応（変換確定のEnterを無視）
- ローディング状態表示
- エラーハンドリング
- チャット履歴管理
- 会話要約機能のサポート

## デプロイ

Firebase Hostingへのデプロイは、プロジェクトルートから実行します：

```bash
# ビルド
npm run build

# デプロイ（プロジェクトルートで実行）
cd ..
firebase deploy --only hosting
```
