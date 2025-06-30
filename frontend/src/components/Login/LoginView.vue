<template>
  <div class="login-page">
    <div class="login-panel">
      <div class="login-container">
        <h2 class="title">Login</h2>
        <p class="subtitle">Enter your account details</p>
        <form @submit.prevent="login">
          <div class="form-group">
            <label for="username">Username</label>
            <input type="text" id="username" v-model="username" required>
          </div>
          <div class="form-group">
            <label for="password">Password</label>
            <div class="input-wrapper">
              <input :type="passwordFieldType" id="password" v-model="password" required>
              <span @click="togglePasswordVisibility" class="password-toggle">
                <svg v-if="passwordFieldType === 'password'" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-eye"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-eye-off"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>
              </span>
            </div>
          </div>
          <a href="#" class="forgot-password">Forgot Password?</a>
          <button type="submit">Login</button>
        </form>
        <div class="signup-prompt">
          <p>Don't have an account?</p>
          <button class="signup-button">Sign up</button>
        </div>
        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
      </div>
    </div>
    <div class="welcome-panel">
        <div class="welcome-content">
            <h2>Welcome to the GRC Platform for MAU Bank</h2>
            <p>Streamlining Governance, Risk, and Compliance for MAU Bank.</p>
            <div class="features">
              <div class="feature-item">
                <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="feature-icon"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path><path d="m9 12 2 2 4-4"></path></svg>
                <span>Secure & Compliant</span>
              </div>
              <div class="feature-item">
                <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="feature-icon"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg>
                <span>Insightful Reporting</span>
              </div>
              <div class="feature-item">
                <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="feature-icon"><line x1="12" y1="20" x2="12" y2="10"></line><line x1="18" y1="20" x2="18" y2="4"></line><line x1="6" y1="20" x2="6" y2="16"></line></svg>
                <span>Risk Analytics</span>
              </div>
              <div class="feature-item">
                <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="feature-icon"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect><line x1="9" y1="15" x2="15" y2="15"></line><line x1="9" y1="11" x2="15" y2="11"></line></svg>
                <span>Audit Management</span>
              </div>
            </div>
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'  // Use regular axios with global configuration from main.js
import { useRouter } from 'vue-router'

const username = ref('')
const password = ref('')
const errorMessage = ref('')
const router = useRouter()
const passwordFieldType = ref('password');

const login = async () => {
  try {
    // Clear previous error message
    errorMessage.value = ''
    
    // Validate inputs
    if (!username.value || !password.value) {
      errorMessage.value = 'Username and password are required'
      return
    }
    
    // Send login request with credentials to create Django session  
    const response = await axios.post('/api/login/', {
      username: username.value,
      password: password.value
    })  // withCredentials configured globally in main.js
    
    if (response.data.success) {
      // Store authentication state in localStorage for UI state management
      localStorage.setItem('isAuthenticated', 'true')
      localStorage.setItem('user', JSON.stringify(response.data.user))
      
      // Store user_id for RBAC debugging (not the primary auth method)
      localStorage.setItem('user_id', response.data.user.id)
      
      console.log('🔐 Login successful! Session created:', {
        user_id: response.data.user.id,
        username: response.data.user.username,
        session_key: response.data.user.session_key
      })
      
      // Emit auth change event for App.vue to listen
      window.dispatchEvent(new Event('authChanged'))
      
      // Redirect to home
      router.push('/home')
    } else {
      errorMessage.value = response.data.message || 'Login failed'
    }
  } catch (error) {
    if (error.response && error.response.data) {
      errorMessage.value = error.response.data.message || 'Invalid credentials'
    } else {
      errorMessage.value = 'Connection error. Please check if the server is running.'
    }
    console.error('❌ Login error:', error)
  }
}

const togglePasswordVisibility = () => {
  passwordFieldType.value = passwordFieldType.value === 'password' ? 'text' : 'password';
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');

.login-page {
  display: flex;
  height: 100vh;
  font-family: 'Poppins', sans-serif;
  background-color: #1E1E1E;
}

.login-panel {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem;
  background-color: #1E1E1E;
}

.login-container {
  width: 100%;
  max-width: 400px;
  color: #fff;
}

.title {
  font-size: 2.5rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.subtitle {
  font-size: 1rem;
  color: #a0a0a0;
  margin-bottom: 2rem;
}

.form-group {
  margin-bottom: 1.5rem;
  position: relative;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  color: #a0a0a0;
  font-size: 0.9rem;
}

input {
  width: 100%;
  padding: 0.75rem 1rem;
  background-color: #2b2b2b;
  border: 1px solid #444;
  border-radius: 8px;
  color: #fff;
  font-size: 1rem;
}

input:-webkit-autofill,
input:-webkit-autofill:hover,
input:-webkit-autofill:focus,
input:-webkit-autofill:active {
    -webkit-box-shadow: 0 0 0 30px #2b2b2b inset !important;
    -webkit-text-fill-color: #fff !important;
}

.input-wrapper {
  position: relative;
}

.password-group {
  position: relative;
}

.password-toggle {
  position: absolute;
  top: 50%;
  right: 1rem;
  transform: translateY(-50%);
  cursor: pointer;
  color: #a0a0a0;
}

.password-toggle svg {
    /* margin-top removed for proper alignment */
}

.forgot-password {
  display: block;
  text-align: right;
  margin-bottom: 1.5rem;
  color: #a0a0a0;
  text-decoration: none;
  font-size: 0.9rem;
}

button {
  width: 100%;
  padding: 0.85rem;
  background-color: #7E57C2;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1.1rem;
  font-weight: 500;
  transition: background-color 0.3s;
}

button:hover {
  background-color: #673AB7;
}

.signup-prompt {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 2rem;
  color: #a0a0a0;
}

.signup-button {
  background: none;
  border: 1px solid #a0a0a0;
  color: #fff;
  padding: 0.5rem 1.5rem;
  margin-left: 1rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  width: auto;
}

.signup-button:hover {
    background: #2b2b2b;
}

.welcome-panel {
  flex: 1;
  background-color: #7E57C2;
  border-top-left-radius: 20px;
  border-bottom-left-radius: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
  color: white;
  padding: 3rem;
  position: relative;
  overflow: hidden;
}

.welcome-panel::before {
    content: '';
    position: absolute;
    top: -100px;
    left: -100px;
    width: 400px;
    height: 400px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 50%;
}

.welcome-panel::after {
    content: '';
    position: absolute;
    bottom: -150px;
    right: -150px;
    width: 500px;
    height: 500px;
    background: rgba(255, 255, 255, 0.08);
    border-radius: 50%;
}


.welcome-content {
  text-align: left;
  z-index: 1;
  max-width: 450px;
}

.welcome-content h2 {
  font-size: 3rem;
  font-weight: 700;
  margin-bottom: 1rem;
  line-height: 1.2;
}

.welcome-content p {
  font-size: 1.1rem;
  margin-bottom: 2rem;
  color: #e0e0e0;
}

.features {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 2rem;
  margin-top: 3rem;
}

.feature-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.feature-icon {
  margin-bottom: 1rem;
  color: #fff;
}

.feature-item span {
  font-size: 1rem;
  font-weight: 500;
  color: #e0e0e0;
}

.illustration {
  display: none;
}

.error-message {
  color: red;
  margin-top: 1rem;
  text-align: center;
}
</style> 