<template>
  <nav class="navbar">
    <div class="nav-brand">
      <router-link to="/" class="brand">ResearchAnalyzer.ai</router-link>
    </div>
    <div class="nav-menu">
      <!-- Show these items only when authenticated -->
      <template v-if="isAuthenticated">
        <router-link to="/files" class="nav-item">Files</router-link>
        <router-link to="/chat" class="nav-item">Chat</router-link>
        <button @click="handleLogout" class="nav-item logout-btn">Logout</button>
      </template>
      <!-- Show these items only when not authenticated -->
      <template v-else>
        <router-link to="/login" class="nav-item">Login</router-link>
        <router-link to="/signup" class="nav-item register-btn">Register</router-link>
      </template>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const isAuthenticated = ref(false)

const checkAuth = () => {
  isAuthenticated.value = localStorage.getItem('isAuthenticated') === 'true'
}

const handleLogout = () => {
  localStorage.removeItem('isAuthenticated')
  localStorage.removeItem('token')
  isAuthenticated.value = false
  router.push('/login')
}

onMounted(() => {
  checkAuth()
  window.addEventListener('storage', checkAuth)
})
</script>

<style scoped>
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background-color: #2a2a2a;
  color: white;
}

.nav-brand {
  font-size: 1.25rem;
  font-weight: bold;
}

.brand {
  color: white;
  text-decoration: none;
}

.nav-menu {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.nav-item {
  color: #ffffff;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: background-color 0.2s;
  font-size: 0.95rem;
}

.nav-item:hover {
  background-color: #3a3a3a;
}

.logout-btn {
  background: none;
  border: 1px solid #666;
  cursor: pointer;
  font-size: 0.95rem;
}

.logout-btn:hover {
  border-color: #888;
}

.register-btn {
  background-color: #2b5797;
}

.register-btn:hover {
  background-color: #1e3f6f;
}
</style>
  