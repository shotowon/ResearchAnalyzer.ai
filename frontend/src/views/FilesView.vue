<template>
  <div class="layout">
    <!-- Sidebar -->
    <div class="sidebar">
      <!-- Upload Section -->
      <div class="upload-section">
        <div class="upload-area" @dragover.prevent @drop.prevent="handleDrop">
          <input 
            type="file" 
            ref="fileInput" 
            @change="handleFileSelect" 
            accept="application/pdf"
            class="file-input"
          />
          <div class="upload-content" @click="$refs.fileInput.click()">
            <span class="upload-icon">📄</span>
            <span class="upload-text">Drop PDF or click to upload</span>
          </div>
        </div>
        <div class="doi-input">
          <input 
            v-model="doi"
            placeholder="Or enter DOI..."
            class="search-input"
          />
          <button @click="processDOI" class="doi-btn" :disabled="!doi.trim()">
            Process DOI
          </button>
        </div>
      </div>

      <!-- Files List -->
      <div class="files-list">
        <div class="list-header">
          <h3>Your Files</h3>
          <div class="view-toggle">
            <button 
              @click="showIngested = false" 
              :class="{ active: !showIngested }"
            >
              All
            </button>
            <button 
              @click="showIngested = true" 
              :class="{ active: showIngested }"
            >
              Ingested
            </button>
          </div>
        </div>
        
        <div v-if="loading" class="loading">Loading...</div>
        
        <template v-else>
          <div v-if="showIngested">
            <div 
              v-for="file in ingestedFiles" 
              :key="file.id"
              class="file-item"
              :class="{ active: selectedFile?.id === file.id }"
            >
              <div class="file-info" @click="selectFile(file)">
                <span class="file-name">{{ file.name }}</span>
                <div class="file-actions">
                  <button @click.stop="downloadFile(file)" class="action-btn">
                    ⬇️
                  </button>
                  <button @click.stop="summarizeFile(file)" class="action-btn">
                    📝
                  </button>
                  <button @click.stop="chatWithFile(file)" class="action-btn">
                    💬
                  </button>
                </div>
              </div>
            </div>
          </div>
          <div v-else>
            <div 
              v-for="file in files" 
              :key="file.id"
              class="file-item"
              :class="{ active: selectedFile?.id === file.id }"
            >
              <div class="file-info" @click="selectFile(file)">
                <span class="file-name">{{ file.name }}</span>
                <div class="file-actions">
                  <button @click.stop="downloadFile(file)" class="action-btn">
                    ⬇️
                  </button>
                  <button 
                    v-if="!isFileIngested(file)"
                    @click.stop="ingestFile(file)" 
                    class="action-btn"
                  >
                    ➕
                  </button>
                </div>
              </div>
            </div>
          </div>
        </template>
      </div>

      <!-- User Section -->
      <div class="user-section">
        <div class="user-info">
          <span class="user-avatar">👤</span>
          <span class="user-name">Shotobek</span>
        </div>
        <button class="menu-btn">⋮</button>
      </div>
    </div>

    <!-- Main Content -->
    <div class="main-content">
      <template v-if="selectedFile">
        <div v-if="activeView === 'chat'" class="chat-view">
          <ChatView :file="selectedFile" />
        </div>
        <div v-else-if="activeView === 'summary'" class="summary-view">
          <div class="summary-content">
            <h2>Summary</h2>
            <div v-if="summary" class="summary-text">
              {{ summary }}
            </div>
            <div v-else class="loading">
              Generating summary...
            </div>
          </div>
        </div>
      </template>
      <div v-else class="empty-state">
        Select a file to start chatting or get a summary
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import ChatView from '../components/ChatView.vue'
import { API_URL } from '../config'

const router = useRouter()
const fileInput = ref(null)
const files = ref([])
const ingestedFiles = ref([])
const selectedFile = ref(null)
const showIngested = ref(false)
const loading = ref(false)
const doi = ref('')
const activeView = ref('chat')
const summary = ref(null)

// Fetch files on mount
onMounted(async () => {
  await fetchFiles()
  await fetchIngestedFiles()
})

const fetchFiles = async () => {
  loading.value = true
  try {
    const response = await fetch(`${API_URL}/files/list`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    const data = await response.json()
    if (!response.ok) throw new Error(data.message || 'Failed to fetch files')
    files.value = data.files
  } catch (error) {
    console.error('Error fetching files:', error)
  } finally {
    loading.value = false
  }
}

const fetchIngestedFiles = async () => {
  const logger = console.getChild?.('files.ingested') || console;
  try {
    const response = await fetch(`${API_URL}/files/ingested`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    const data = await response.json()
    if (!response.ok) throw new Error(data.message || 'Failed to fetch ingested files')
    ingestedFiles.value = data.files
  } catch (error) {
    logger.error(`Failed to fetch ingested files: ${error.message}`)
    console.error('Error fetching ingested files:', error)
  }
}

const handleFileSelect = async (event) => {
  const file = event.target.files[0]
  if (file) await uploadFile(file)
}

const handleDrop = async (event) => {
  const file = event.dataTransfer.files[0]
  if (file && file.type === 'application/pdf') {
    await uploadFile(file)
  }
}

const uploadFile = async (file) => {
  const logger = console.getChild?.('files.upload') || console;
  const formData = new FormData()
  formData.append('file', file)

  try {
    const response = await fetch(`${API_URL}/files/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: formData
    })
    const data = await response.json()
    if (!response.ok) throw new Error(data.message || 'Upload failed')
    
    // Refresh file lists
    await fetchFiles()
    await fetchIngestedFiles()
  } catch (error) {
    logger.error(`Failed to upload file: ${error.message}`)
    console.error('Error uploading file:', error)
  }
}

const processDOI = async () => {
  const logger = console.getChild?.('files.processDOI') || console;
  if (!doi.value.trim()) return

  try {
    const response = await fetch(`${API_URL}/files/process-doi`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ doi: doi.value })
    })
    const data = await response.json()
    if (!response.ok) throw new Error(data.message || 'DOI processing failed')
    
    // Refresh file lists
    await fetchFiles()
    await fetchIngestedFiles()
    doi.value = '' // Clear input
  } catch (error) {
    logger.error(`Failed to process DOI: ${error.message}`)
    console.error('Error processing DOI:', error)
  }
}

const downloadFile = async (file) => {
  const logger = console.getChild?.('files.download') || console;
  try {
    const response = await fetch(`${API_URL}/files/file/${file.id}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    if (!response.ok) throw new Error('Download failed')
    
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = file.name
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    a.remove()
  } catch (error) {
    logger.error(`Failed to download file: ${error.message}`)
    console.error('Error downloading file:', error)
  }
}

const ingestFile = async (file) => {
  const logger = console.getChild?.('files.ingest') || console;
  try {
    const response = await fetch(`${API_URL}/files/ingest/${file.id}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    const data = await response.json()
    if (!response.ok) throw new Error(data.message || 'Ingestion failed')
    
    // Refresh ingested files list
    await fetchIngestedFiles()
  } catch (error) {
    logger.error(`Failed to ingest file: ${error.message}`)
    console.error('Error ingesting file:', error)
  }
}

const summarizeFile = async (file) => {
  const logger = console.getChild?.('files.summarize') || console;
  activeView.value = 'summary'
  summary.value = null
  selectedFile.value = file

  try {
    const response = await fetch(`${API_URL}/files/summarize/${file.id}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    const data = await response.json()
    if (!response.ok) throw new Error(data.message || 'Summarization failed')
    summary.value = data.summary
  } catch (error) {
    logger.error(`Failed to summarize file: ${error.message}`)
    console.error('Error summarizing file:', error)
  }
}

const chatWithFile = (file) => {
  activeView.value = 'chat'
  selectedFile.value = file
}

const selectFile = (file) => {
  selectedFile.value = file
  activeView.value = 'chat'
}

const isFileIngested = (file) => {
  return ingestedFiles.value.some(f => f.id === file.id)
}
</script>

<style scoped>
.layout {
  display: flex;
  height: 100vh;
  background-color: #1e1e1e;
}

.sidebar {
  width: 320px;
  background-color: #252525;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #333;
}

.upload-section {
  padding: 1rem;
  border-bottom: 1px solid #333;
}

.upload-area {
  background-color: #2a2a2a;
  border: 2px dashed #444;
  border-radius: 8px;
  padding: 1.5rem;
  text-align: center;
  cursor: pointer;
  margin-bottom: 1rem;
}

.upload-area:hover {
  border-color: #666;
}

.file-input {
  display: none;
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.upload-icon {
  font-size: 2rem;
}

.upload-text {
  color: #888;
  font-size: 0.9rem;
}

.doi-input {
  display: flex;
  gap: 0.5rem;
}

.search-input {
  flex: 1;
  background-color: #2a2a2a;
  border: 1px solid #444;
  border-radius: 4px;
  padding: 0.5rem;
  color: #fff;
  font-size: 0.9rem;
}

.doi-btn {
  background-color: #2b5797;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 0.5rem 1rem;
  cursor: pointer;
}

.doi-btn:disabled {
  background-color: #444;
  cursor: not-allowed;
}

.files-list {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.list-header h3 {
  color: #fff;
  margin: 0;
}

.view-toggle {
  display: flex;
  gap: 0.5rem;
}

.view-toggle button {
  background: none;
  border: 1px solid #444;
  color: #888;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  cursor: pointer;
}

.view-toggle button.active {
  background-color: #2b5797;
  border-color: #2b5797;
  color: white;
}

.file-item {
  margin-bottom: 0.5rem;
}

.file-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #2a2a2a;
  padding: 0.75rem;
  border-radius: 4px;
  cursor: pointer;
}

.file-info:hover {
  background-color: #333;
}

.file-name {
  color: #fff;
  font-size: 0.9rem;
}

.file-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  background: none;
  border: none;
  color: #888;
  cursor: pointer;
  padding: 0.25rem;
  font-size: 1.1rem;
}

.action-btn:hover {
  color: #fff;
}

.main-content {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #666;
  font-size: 1.1rem;
}

.summary-view {
  max-width: 800px;
  margin: 0 auto;
}

.summary-content {
  background-color: #2a2a2a;
  padding: 2rem;
  border-radius: 8px;
}

.summary-content h2 {
  color: #fff;
  margin-top: 0;
  margin-bottom: 1.5rem;
}

.summary-text {
  color: #ddd;
  line-height: 1.6;
  white-space: pre-wrap;
}

.loading {
  text-align: center;
  color: #888;
  padding: 2rem;
}

.active {
  background-color: #2b5797 !important;
}

.user-section {
  padding: 1rem;
  border-top: 1px solid #333;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #fff;
}

.user-avatar {
  font-size: 1.2rem;
}

.user-name {
  font-size: 0.9rem;
}

.menu-btn {
  background: none;
  border: none;
  color: #888;
  cursor: pointer;
  padding: 0.25rem;
  font-size: 1.2rem;
}

.chat-view {
  height: 100%;
}
</style>
