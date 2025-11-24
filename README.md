# 傾聴型AIチャットアプリケーション

「傾聴」に特化したAIチャットボットアプリケーション。  
ユーザーの話に共感的に耳を傾け、相手を否定せずで受容的な応答を提供します。

## 概要

このアプリケーションは、Vertex AIを活用した傾聴型のチャットボットです。 ユーザーが気軽に悩みや考えを話せる安全な対話環境を提供します。

## サイト

[https://active-listening-chat.web.app/]

## 主な機能

### 傾聴に特化したAI応答

システムプロンプトにより、以下の特徴を持つ応答を生成：

- 共感的で相手を否定しない応答
- 相手の話を遮らない積極的傾聴
- 一方的なアドバイスの回避
- ユーザーの感情表現をサポート
- 温かく受容的な態度の維持

### チャット履歴管理

- セッション内でのチャット履歴の保持
- 会話が一定量を超えると自動的に要約を生成
- 直近の会話と要約を組み合わせてコンテキストを最適化

### UI/UX

- 使い方が明瞭なシンプルなデザイン
- レスポンシブデザイン（モバイル対応）
- 対人とやり取りをしているようなメッセージ表示  
  (AI固有の過度なレスポンススピードやローディング的な機会的な印象を避ける)

#### PC

<img width="500" alt="Image" src="https://github.com/user-attachments/assets/028d8179-86a4-4b63-9d05-ccd1fb17b47e" />

#### モバイル

<img width="300" alt="Image" src="https://github.com/user-attachments/assets/30e8637b-a693-4732-b6f3-bff123c91786" />

## インフラ構成

### 全体図

```
┌────────────────────────────────────────────┐
│                    User                    │
└─────────────────────┬──────────────────────┘
                      │ HTTPS
Frontend              ▼
┌────────────────────────────────────────────┐
│              Firebase Hosting              │ - チャット機能
│            Vue.js + Vuetify SPA            │ - システムプロンプトの表示・編集
└─────────────────────┬──────────────────────┘
                      │ HTTPS (REST API)
Backend               ▼
┌────────────────────────────────────────────┐
│              Cloud Functions               │ - Vertex AIへの橋渡し
│           Python 3.11 + Flask              │
└─────────────────────┬──────────────────────┘
                      │ Vertex AI API
LLM                   ▼
┌────────────────────────────────────────────┐
│                 Vertex AI                  │ - 返答の生成
│               Gemini 2.5 Flash             │ - システムプロンプトの保持
└────────────────────────────────────────────┘

CI/CD
┌────────────────────────────────────────────┐
│              GitHub Actions                │ - Frontend, Backendに対して自動デプロイ
└────────────────────────────────────────────┘
```

### リージョン構成

- **Cloud Functions**: `asia-northeast1` (東京) - エンドユーザーに近い位置でレイテンシを最小化
- **Vertex AI**: `us-central1` - モデルの安定性と可用性を重視

## 技術スタック

### フロントエンド

- Vue.js 3
- Vuetify 3
- Vite
- Axios

### バックエンド

- Cloud Functions
- Python 3.11
- Flask
- Vertex AI SDK

### インフラ

- Firebase Hosting
- Google Cloud Platform
- Vertex AI
- GitHub Actions

### 開発環境

- Claude Code
- NeoVim

## プロジェクト構成

```
.
├── frontend/              # フロントエンドアプリケーション (Vue.js + Vuetify)
├── functions/             # バックエンドAPI (Cloud Functions)
├── firebase.json          # Firebase Hosting設定
└── .firebaserc           # Firebaseプロジェクト設定
```

詳細は各ディレクトリのREADMEを参照してください：

- [frontend/README.md](frontend/README.md)
- [functions/README.md](functions/README.md)

## ライセンス

このプロジェクトはポートフォリオ用のサンプルアプリケーションです。
