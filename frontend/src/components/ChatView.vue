<template>
  <div class="chat-container">
    <div class="messages" ref="messagesContainer">
      <div v-for="(message, index) in messages" :key="index" :class="['message', message.role]">
        <div class="message-content">
          {{ message.content }}
        </div>
        <div v-if="message.source" class="message-source">
          Source: {{ message.source }}
        </div>
      </div>
    </div>

    <div class="input-area">
      <div class="input-container">
        <textarea
          v-model="prompt"
          @keydown.enter.prevent="handleSubmit"
          placeholder="Ask a question about the document..."
          class="message-input"
          rows="1"
          ref="promptInput"
          @input="autoResize"
        ></textarea>
        <button @click="handleSubmit" class="send-btn" :disabled="!prompt.trim() || loading">
          <span v-if="loading">...</span>
          <span v-else>➤</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import { API_URL } from '../config'

const props = defineProps({
  file: {
    type: Object,
    required: true
  }
})

const messages = ref([])
const prompt = ref('')
const loading = ref(false)
const messagesContainer = ref(null)
const promptInput = ref(null)
const chatId = ref(null)

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const autoResize = () => {
  const textarea = promptInput.value
  if (!textarea) return
  
  // Reset height to auto to properly calculate new height
  textarea.style.height = 'auto'
  // Set new height based on scrollHeight
  textarea.style.height = textarea.scrollHeight + 'px'
}

const handleSubmit = async () => {
  const logger = console.getChild?.('chat.submit') || console;
  if (!prompt.value.trim() || loading.value) return

  // Add user message
  messages.value.push({
    content: prompt.value,
    role: 'user'
  })

  const currentPrompt = prompt.value
  prompt.value = ''
  loading.value = true

  try {
    const response = await fetch(`${API_URL}/files/chat-with-doc`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        file_id: props.file.id,
        prompt: currentPrompt,
        chat_id: chatId.value
      })
    })

    const data = await response.json()
    if (!response.ok) throw new Error(data.message || 'Chat failed')

    // Add AI response
    messages.value.push({
      content: data.response,
      role: 'assistant',
      source: data.source
    })

    // Store chat ID for conversation continuity
    chatId.value = data.chat_id
  } catch (error) {
    logger.error(`Failed to get chat response: ${error.message}`)
    console.error('Chat error:', error)
    messages.value.push({
      content: 'Sorry, there was an error processing your request.',
      role: 'error'
    })
  } finally {
    loading.value = false
    await scrollToBottom()
    await nextTick()
    autoResize()
  }
}

// Watch messages to scroll to bottom
watch(messages, scrollToBottom)

// Initialize textarea height
onMounted(() => {
  autoResize()
})
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: #1e1e1e;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.message {
  max-width: 85%;
  padding: 1rem;
  border-radius: 8px;
  line-height: 1.5;
}

.message.user {
  background-color: #2b5797;
  color: white;
  align-self: flex-end;
  border-bottom-right-radius: 2px;
}

.message.assistant {
  background-color: #2a2a2a;
  color: white;
  align-self: flex-start;
  border-bottom-left-radius: 2px;
}

.message.error {
  background-color: #ff4a4a;
  color: white;
  align-self: center;
}

.message-content {
  white-space: pre-wrap;
}

.message-source {
  margin-top: 0.5rem;
  font-size: 0.8rem;
  color: #888;
}

.input-area {
  padding: 1rem;
  background-color: #1e1e1e;
}

.input-container {
  display: flex;
  align-items: flex-end;
  gap: 0.5rem;
  background-color: #2a2a2a;
  padding: 0.75rem;
  border-radius: 8px;
}

.message-input {
  flex: 1;
  background: none;
  border: none;
  color: #fff;
  padding: 0;
  font-size: 0.95rem;
  resize: none;
  max-height: 150px;
  line-height: 1.5;
  font-family: inherit;
}

.message-input::placeholder {
  color: #888;
}

.message-input:focus {
  outline: none;
}

.send-btn {
  background: none;
  border: none;
  color: #4a9eff;
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 2rem;
}

.send-btn:disabled {
  color: #555;
  cursor: not-allowed;
}
</style> 