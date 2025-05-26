<template>
  <div class="signup-container">
    <div class="signup-card">
      <h1>Create Account</h1>
      <form @submit.prevent="handleSignup" class="signup-form">
        <div class="form-group">
          <label for="username">Username</label>
          <input 
            type="text" 
            id="username"
            v-model="username"
            required
            placeholder="Choose a username (3-24 characters)"
            minlength="3"
            maxlength="24"
            pattern="^[a-zA-Z0-9_-]+$"
            title="Username can only contain letters, numbers, underscores and hyphens"
          />
          <span class="input-hint" v-if="username && !isUsernameValid">
            Username must be 3-24 characters and can only contain letters, numbers, underscores and hyphens
          </span>
        </div>
        <div class="form-group">
          <label for="email">Email</label>
          <input 
            type="email" 
            id="email"
            v-model="email"
            required
            placeholder="Enter your email"
          />
        </div>
        <div class="form-group">
          <label for="password">Password</label>
          <input 
            type="password" 
            id="password"
            v-model="password"
            required
            placeholder="Create a password (min 8 characters)"
            minlength="8"
          />
          <span class="input-hint" v-if="password && password.length < 8">
            Password must be at least 8 characters long
          </span>
        </div>
        <div class="form-group">
          <label for="confirmPassword">Confirm Password</label>
          <input 
            type="password" 
            id="confirmPassword"
            v-model="confirmPassword"
            required
            placeholder="Confirm your password"
          />
          <span class="input-hint error" v-if="confirmPassword && !doPasswordsMatch">
            Passwords do not match
          </span>
        </div>
        <div class="error-message" v-if="error">{{ error }}</div>
        <button type="submit" :disabled="loading || !isFormValid">
          {{ loading ? 'Creating Account...' : 'Create Account' }}
        </button>
      </form>
      <div class="login-link">
        Already have an account? 
        <router-link to="/login">Log in</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { API_URL } from '../config'

const router = useRouter()
const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const error = ref('')
const loading = ref(false)

const isUsernameValid = computed(() => {
  const usernameRegex = /^[a-zA-Z0-9_-]{3,24}$/
  return usernameRegex.test(username.value)
})

const doPasswordsMatch = computed(() => {
  return password.value === confirmPassword.value
})

const isFormValid = computed(() => {
  return isUsernameValid.value && 
         email.value.includes('@') && 
         password.value.length >= 8 && 
         doPasswordsMatch.value
})

const handleSignup = async () => {
  if (!isFormValid.value) {
    error.value = 'Please check all fields are valid'
    return
  }

  loading.value = true
  error.value = ''

  try {
    const response = await fetch(`${API_URL}/accounts/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: username.value,
        email: email.value,
        password: password.value
      })
    })

    if (!response.ok) {
      const data = await response.json()
      throw new Error(data.message || 'Registration failed')
    }

    const data = await response.json()

    // Auto-login after successful registration
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
.signup-container {
  min-height: calc(100vh - 64px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.signup-card {
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

.signup-form {
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

input:invalid {
  border-color: #ff4a4a;
}

.input-hint {
  font-size: 0.8rem;
  color: #888;
}

.input-hint.error {
  color: #ff4a4a;
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

.login-link {
  margin-top: 1.5rem;
  text-align: center;
  color: #888;
}

.login-link a {
  color: #4a9eff;
  text-decoration: none;
}

.login-link a:hover {
  text-decoration: underline;
}
</style> 