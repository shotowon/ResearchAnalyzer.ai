<template>
  <div class="chat-container">
    <div class="messages" ref="messagesContainer">
      <div v-for="(message, index) in messages" :key="index" :class="['message', message.type]">
        <div class="message-content">
          {{ message.content }}
        </div>
      </div>
    </div>

    <div class="input-area">
      <div class="input-container">
        <div class="attachment-btn">
          📎
        </div>
        <input
          v-model="prompt"
          @keydown.enter="handleSubmit"
          placeholder="Message RA"
          class="message-input"
        />
        <button @click="handleSubmit" class="send-btn" :disabled="!prompt.trim()">
          ➤
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { API_URL } from '../config'

export default {
  name: 'ChatView',
  setup() {
    const route = useRoute()
    const fileName = ref(decodeURIComponent(route.params.fileName || ''))
    const prompt = ref('')
    const messages = ref([])
    const messagesContainer = ref(null)
    const chatId = ref(null)

    const scrollToBottom = async () => {
      await nextTick()
      if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
      }
    }

    const handleSubmit = async () => {
      if (!prompt.value.trim()) return

      // Add user message
      messages.value.push({
        content: prompt.value,
        type: 'user'
      })

      try {
        const response = await fetch(`${API_URL}/files/chat-with-doc`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({
            filename: fileName.value,
            prompt: prompt.value,
            chat_id: chatId.value
          })
        })

        const data = await response.json()

        if (!response.ok) {
          throw new Error(data.message || 'Chat failed')
        }

        // Add AI response
        messages.value.push({
          content: data.response,
          type: 'ai'
        })

        // Store chat ID for conversation continuity
        chatId.value = data.chat_id

        // Clear input
        prompt.value = ''
      } catch (error) {
        messages.value.push({
          content: 'Sorry, there was an error processing your request.',
          type: 'error'
        })
        console.error('Chat error:', error)
      }
    }

    // Scroll to bottom when messages change
    watch(messages, scrollToBottom)

    return {
      fileName,
      prompt,
      messages,
      messagesContainer,
      handleSubmit
    }
  }
}
</script>

<style scoped>
.chat-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
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

.message.ai {
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

.input-area {
  padding: 1rem;
  background-color: #1e1e1e;
}

.input-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background-color: #2a2a2a;
  padding: 0.5rem;
  border-radius: 8px;
}

.attachment-btn {
  padding: 0.5rem;
  color: #888;
  cursor: pointer;
}

.message-input {
  flex: 1;
  background: none;
  border: none;
  color: #fff;
  padding: 0.5rem;
  font-size: 0.95rem;
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
}

.send-btn:disabled {
  color: #555;
  cursor: not-allowed;
}
</style> 