<template>
  <div class="login-container">
    <div class="login-card">
      <h1>Welcome Back</h1>
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="identifier">Email or Username</label>
          <input 
            type="text" 
            id="identifier"
            v-model="identifier"
            required
            placeholder="Enter your email or username"
          />
        </div>
        <div class="form-group">
          <label for="password">Password</label>
          <input 
            type="password" 
            id="password"
            v-model="password"
            required
            placeholder="Enter your password"
          />
        </div>
        <div class="error-message" v-if="error">{{ error }}</div>
        <button type="submit" :disabled="loading">
          {{ loading ? 'Logging in...' : 'Login' }}
        </button>
      </form>
      <div class="signup-link">
        Don't have an account? 
        <router-link to="/signup">Sign up</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { API_URL } from '../config'

const router = useRouter()
const identifier = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const handleLogin = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await fetch(`${API_URL}/accounts/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        login: identifier.value,
        password: password.value
      })
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.message || 'Login failed')
    }

    localStorage.setItem('token', data.token)
    localStorage.setItem('isAuthenticated', 'true')
    router.push('/files')
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: calc(100vh - 64px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.login-card {
  background-color: #2a2a2a;
  padding: 2rem;
  border-radius: 8px;
  width: 100%;
  max-width: 400px;
}

h1 {
  margin: 0 0 2rem;
  text-align: center;
  color: #fff;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

label {
  color: #fff;
  font-size: 0.9rem;
}

input {
  padding: 0.75rem;
  border-radius: 4px;
  border: 1px solid #444;
  background-color: #1e1e1e;
  color: #fff;
  font-size: 1rem;
}

input:focus {
  outline: none;
  border-color: #2b5797;
}

button {
  background-color: #2b5797;
  color: white;
  padding: 0.75rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

button:hover:not(:disabled) {
  background-color: #1e3f6f;
}

button:disabled {
  background-color: #444;
  cursor: not-allowed;
}

.error-message {
  color: #ff4a4a;
  font-size: 0.9rem;
  text-align: center;
}

.signup-link {
  margin-top: 1.5rem;
  text-align: center;
  color: #888;
}

.signup-link a {
  color: #4a9eff;
  text-decoration: none;
}

.signup-link a:hover {
  text-decoration: underline;
}
</style>
  