<template>
  <v-dialog v-model="dialog" max-width="800" persistent>
    <v-card>
      <v-card-title class="text-h5">
        システムプロンプト編集
      </v-card-title>

      <v-card-text>
        <v-alert v-if="errorMessage" type="error" class="mb-4">
          {{ errorMessage }}
        </v-alert>

        <v-alert v-if="successMessage" type="success" class="mb-4">
          {{ successMessage }}
        </v-alert>

        <v-textarea
          v-model="promptText"
          label="システムプロンプト"
          :loading="loading"
          :disabled="loading"
          rows="15"
          auto-grow
          variant="outlined"
          hint="AIの振る舞いを定義するシステムプロンプトを編集できます"
          persistent-hint
        ></v-textarea>
      </v-card-text>

      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn
          color="grey"
          variant="text"
          @click="closeDialog"
          :disabled="loading"
        >
          キャンセル
        </v-btn>
        <v-btn
          color="primary"
          variant="elevated"
          @click="savePrompt"
          :loading="loading"
          :disabled="loading"
        >
          保存
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { getPrompt, updatePrompt } from '../services/api'

const props = defineProps({
  modelValue: Boolean
})

const emit = defineEmits(['update:modelValue'])

const dialog = ref(props.modelValue)
const promptText = ref('')
const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

watch(() => props.modelValue, (newVal) => {
  dialog.value = newVal
  if (newVal) {
    loadPrompt()
  }
})

watch(dialog, (newVal) => {
  emit('update:modelValue', newVal)
})

const loadPrompt = async () => {
  loading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const data = await getPrompt()
    promptText.value = data.prompt
  } catch (error) {
    errorMessage.value = 'プロンプトの読み込みに失敗しました: ' + (error.response?.data?.error || error.message)
  } finally {
    loading.value = false
  }
}

const savePrompt = async () => {
  loading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    await updatePrompt(promptText.value)
    successMessage.value = 'プロンプトを保存しました'

    // 2秒後に閉じる
    setTimeout(() => {
      closeDialog()
    }, 2000)
  } catch (error) {
    errorMessage.value = 'プロンプトの保存に失敗しました: ' + (error.response?.data?.error || error.message)
  } finally {
    loading.value = false
  }
}

const closeDialog = () => {
  dialog.value = false
  errorMessage.value = ''
  successMessage.value = ''
}
</script>
