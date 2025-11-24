<template>
  <v-container fluid class="chat-container pa-0">
    <v-card class="chat-card" elevation="12">
      <!-- ヘッダー -->
      <v-card-title class="chat-header d-flex align-center">
        <v-icon class="mr-2">mdi-chat</v-icon>
        傾聴チャット
        <v-spacer></v-spacer>
        <v-btn
          icon="mdi-cog"
          variant="text"
          @click="showPromptEditor = true"
          size="small"
        ></v-btn>
      </v-card-title>

      <!-- メッセージ表示エリア -->
      <v-card-text class="messages-area" ref="messagesArea">
        <transition-group name="message" tag="div">
          <div
            v-for="(message, index) in messages"
            :key="index"
            :class="['message-bubble', message.isUser ? 'user-message' : 'ai-message']"
          >
            <div class="message-content">
              <div class="message-text">{{ message.text }}</div>
              <div class="message-time">{{ message.timestamp }}</div>
            </div>
          </div>
        </transition-group>
        <div v-if="isLoading" class="message-bubble ai-message">
          <div class="message-content typing-indicator">
            <span class="dot"></span>
            <span class="dot"></span>
            <span class="dot"></span>
          </div>
        </div>
      </v-card-text>

      <!-- 入力エリア -->
      <v-card-actions class="input-area pa-4">
        <v-textarea
          ref="inputRef"
          v-model="userInput"
          :placeholder="placeholder"
          rows="2"
          auto-grow
          variant="outlined"
          density="comfortable"
          hide-details
          color="secondary"
          :disabled="isLoading"
          @keydown.enter.exact="handleEnter"
          @compositionstart="isComposing = true"
          @compositionend="isComposing = false"
        ></v-textarea>
        <v-btn
          icon="mdi-send"
          color="primary"
          :disabled="!userInput.trim() || isLoading"
          @click="sendMessage"
          class="ml-2"
        ></v-btn>
      </v-card-actions>
    </v-card>

    <!-- エラー表示 -->
    <v-snackbar v-model="showError" color="error" timeout="5000">
      {{ errorMessage }}
      <template v-slot:actions>
        <v-btn variant="text" @click="showError = false">閉じる</v-btn>
      </template>
    </v-snackbar>

    <!-- プロンプト編集モーダル -->
    <PromptEditor v-model="showPromptEditor" />
  </v-container>
</template>

<script setup>
import { ref, nextTick, onMounted, onUnmounted, computed } from 'vue'
import { sendMessage as apiSendMessage } from '@/services/api'
import PromptEditor from '@/components/PromptEditor.vue'

const messages = ref([])
const userInput = ref('')
const isLoading = ref(false)
const isComposing = ref(false)
const messagesArea = ref(null)
const inputRef = ref(null)
const chatHistory = ref([])
const conversationSummary = ref(null)
const showError = ref(false)
const errorMessage = ref('')
const showPromptEditor = ref(false)
const windowWidth = ref(window.innerWidth)

// 画面サイズに応じてプレースホルダーを切り替え
const placeholder = computed(() => {
  return windowWidth.value <= 768
    ? 'メッセージを入力'
    : 'メッセージを入力してください（Enterで送信、Shift+Enterで改行）'
})

// ウィンドウサイズ変更を監視
const handleResize = () => {
  windowWidth.value = window.innerWidth
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesArea.value) {
      const container = messagesArea.value.$el || messagesArea.value
      container.scrollTo({
        top: container.scrollHeight,
        behavior: 'smooth'
      })
    }
  })
}

const focusInput = () => {
  nextTick(() => {
    if (inputRef.value) {
      // Vuetifyのv-textareaの場合、内部のinput要素にアクセスする必要がある
      const textarea = inputRef.value.$el?.querySelector('textarea') || inputRef.value
      textarea?.focus()
    }
  })
}

const handleEnter = (event) => {
  // 日本語入力中の変換確定のEnterは無視
  if (isComposing.value) {
    return
  }
  // スマホサイズ（768px以下）では改行を許可し、送信しない
  if (windowWidth.value <= 768) {
    return
  }
  // デスクトップでは通常のEnterキーで送信
  event.preventDefault()
  sendMessage()
}

const formatTime = () => {
  const now = new Date()
  return `${now.getHours()}:${String(now.getMinutes()).padStart(2, '0')}`
}

const sendMessage = async () => {
  const message = userInput.value.trim()
  if (!message || isLoading.value) return

  // ユーザーメッセージを追加
  messages.value.push({
    text: message,
    isUser: true,
    timestamp: formatTime(),
  })
  userInput.value = ''
  scrollToBottom()

  isLoading.value = true

  try {
    // APIリクエスト
    const response = await apiSendMessage(message, chatHistory.value, conversationSummary.value)

    // 履歴と要約を更新
    chatHistory.value = response.history
    if (response.summary) {
      conversationSummary.value = response.summary
    }

    // 少し間を置いてからAI応答を表示（考えているような雰囲気）
    setTimeout(() => {
      messages.value.push({
        text: response.response,
        isUser: false,
        timestamp: formatTime(),
      })
      scrollToBottom()
      isLoading.value = false
      // 送信後に入力欄にフォーカスを戻す
      focusInput()
    }, 1500)
  } catch (error) {
    errorMessage.value = 'メッセージの送信に失敗しました。もう一度お試しください。'
    showError.value = true
    isLoading.value = false
  }
}

// ページ読み込み時に入力欄にフォーカス
onMounted(() => {
  // ウィンドウサイズ変更を監視
  window.addEventListener('resize', handleResize)

  // ローディングを表示
  isLoading.value = true

  // 少し間を置いてから初期メッセージを表示（考えている雰囲気を演出）
  setTimeout(() => {
    messages.value.push({
      text: 'お話を聞かせてください。\n\n何でも話していただいて大丈夫です。',
      isUser: false,
      timestamp: formatTime(),
    })
    isLoading.value = false
    focusInput()
  }, 1500)
})

// クリーンアップ
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.chat-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #5d4178 0%, #7a5690 50%, #a66b65 80%, #d88b6e 100%);
}

.chat-card {
  width: calc(100% - 48px);
  max-width: 800px;
  height: 90vh;
  display: flex;
  flex-direction: column;
  background: transparent !important;
  margin: 0 24px;
}

.chat-header {
  background: linear-gradient(135deg, rgb(var(--v-theme-accent)) 0%, rgb(var(--v-theme-secondary)) 100%);
  color: white;
  font-weight: bold;
  padding: 16px 24px;
  box-shadow:
    0 2px 8px rgba(0, 0, 0, 0.15),
    0 8px 24px rgba(0, 0, 0, 0.12),
    0 16px 40px rgba(0, 0, 0, 0.08);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  border-top-left-radius: 4px;
  border-top-right-radius: 4px;
  position: relative;
  z-index: 10;
}

.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: #f5f5f5;
}

.message-bubble {
  margin-top: 16px;
  margin-bottom: 16px;
  display: flex;
}

.user-message {
  justify-content: flex-end;
}

.ai-message {
  justify-content: flex-start;
}

.message-content {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 16px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.user-message .message-content {
  background: linear-gradient(135deg, rgb(var(--v-theme-secondary)) 0%, rgb(var(--v-theme-primary)) 100%);
  color: white;
}

.ai-message .message-content {
  background: white;
  color: #333;
}

.message-text {
  word-wrap: break-word;
  white-space: pre-wrap;
  line-height: 1.5;
  font-size: 16px;
}

.message-time {
  font-size: 0.625rem;
  opacity: 0.7;
  margin-top: 4px;
  text-align: right;
}

.input-area {
  background: white;
  border-top: 1px solid #e0e0e0;
}

/* フォーカス時のパープル系カラーとアニメーション */
.input-area :deep(.v-field--focused) {
  animation: heartbeat 1.5s ease-in-out infinite;
}

/* 鼓動アニメーション */
@keyframes heartbeat {
  0% {
    box-shadow: 0 0 0 0 rgba(var(--v-theme-secondary), 0.5);
  }
  100% {
    box-shadow: 0 0 0 6px rgba(var(--v-theme-secondary), 0);
  }
}

/* 三点リーダのタイピングアニメーション */
.typing-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 16px 20px;
}

.typing-indicator .dot {
  width: 6px;
  height: 6px;
  background-color: rgb(var(--v-theme-primary));
  border-radius: 50%;
  animation: typing 1.4s infinite;
}

.typing-indicator .dot:nth-child(1) {
  animation-delay: 0s;
}

.typing-indicator .dot:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator .dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    opacity: 0.3;
    transform: translateY(0);
  }
  30% {
    opacity: 1;
    transform: translateY(-8px);
  }
}

/* メッセージ表示アニメーション */
.message-enter-active {
  transition: all 0.5s ease-out;
}

.message-enter-from {
  opacity: 0;
}

.user-message.message-enter-from {
  transform: translateX(30px);
}

.ai-message.message-enter-from {
  transform: translateX(-30px);
}

/* モバイル対応 */
@media (max-width: 768px) {
  .chat-container {
    height: 100vh; /* フォールバック */
    height: 100dvh; /* ブラウザUIを考慮した動的な高さ */
  }

  .chat-card {
    max-width: 100vw;
    width: 100vw;
    height: 100vh; /* フォールバック */
    height: 100dvh; /* ブラウザUIを考慮した動的な高さ */
    border-radius: 0 !important;
    margin: 0;
  }

  .chat-header {
    background: linear-gradient(135deg, #5d4178 0%, #7a5690 50%, #a66b65 80%, #d88b6e 100%);
    border-top-left-radius: 0 !important;
    border-top-right-radius: 0 !important;
  }
}
</style>
