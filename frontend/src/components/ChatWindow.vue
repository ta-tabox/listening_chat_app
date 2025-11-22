<template>
  <v-container fluid class="chat-container pa-0">
    <v-card class="chat-card" elevation="0">
      <!-- ヘッダー -->
      <v-card-title class="chat-header">
        <v-icon class="mr-2">mdi-chat</v-icon>
        傾聴チャット
      </v-card-title>

      <!-- メッセージ表示エリア -->
      <v-card-text class="messages-area" ref="messagesArea">
        <div v-if="messages.length === 0" class="text-center text-grey pa-4">
          お話を聞かせてください。何でも話していただいて大丈夫です。
        </div>
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
        <div v-if="isLoading" class="message-bubble ai-message">
          <div class="message-content">
            <v-progress-circular
              indeterminate
              size="24"
              width="3"
              color="primary"
            ></v-progress-circular>
            <span class="ml-2">入力中...</span>
          </div>
        </div>
      </v-card-text>

      <!-- 入力エリア -->
      <v-card-actions class="input-area pa-4">
        <v-textarea
          v-model="userInput"
          placeholder="メッセージを入力してください（Enterで送信、Shift+Enterで改行）"
          rows="2"
          auto-grow
          variant="outlined"
          density="comfortable"
          :disabled="isLoading"
          @keydown.enter.exact="handleEnter"
          @keydown.enter.shift.exact="addNewLine"
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
  </v-container>
</template>

<script>
import { ref, nextTick } from 'vue'
import { sendMessage as apiSendMessage } from '@/services/api'

export default {
  name: 'ChatWindow',
  setup() {
    const messages = ref([])
    const userInput = ref('')
    const isLoading = ref(false)
    const isComposing = ref(false)
    const messagesArea = ref(null)
    const chatHistory = ref([])
    const conversationSummary = ref(null)
    const showError = ref(false)
    const errorMessage = ref('')

    const scrollToBottom = () => {
      nextTick(() => {
        if (messagesArea.value) {
          const container = messagesArea.value.$el || messagesArea.value
          container.scrollTop = container.scrollHeight
        }
      })
    }

    const addNewLine = () => {
      userInput.value += '\n'
    }

    const handleEnter = (event) => {
      // 日本語入力中の変換確定のEnterは無視
      if (isComposing.value) {
        return
      }
      // 通常のEnterキーの場合は送信
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

        // AI応答を追加
        messages.value.push({
          text: response.response,
          isUser: false,
          timestamp: formatTime(),
        })

        // 履歴と要約を更新
        chatHistory.value = response.history
        if (response.summary) {
          conversationSummary.value = response.summary
        }

        scrollToBottom()
      } catch (error) {
        errorMessage.value = 'メッセージの送信に失敗しました。もう一度お試しください。'
        showError.value = true
      } finally {
        isLoading.value = false
      }
    }

    return {
      messages,
      userInput,
      isLoading,
      isComposing,
      messagesArea,
      showError,
      errorMessage,
      sendMessage,
      addNewLine,
      handleEnter,
    }
  },
}
</script>

<style scoped>
.chat-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.chat-card {
  width: 100%;
  max-width: 800px;
  height: 90vh;
  display: flex;
  flex-direction: column;
}

.chat-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: bold;
  padding: 16px 24px;
}

.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: #f5f5f5;
}

.message-bubble {
  margin-bottom: 16px;
  display: flex;
}

.message-bubble:first-child {
  margin-top: 16px;
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
  background: #667eea;
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
}

.message-time {
  font-size: 0.75rem;
  opacity: 0.7;
  margin-top: 4px;
  text-align: right;
}

.input-area {
  background: white;
  border-top: 1px solid #e0e0e0;
}
</style>
