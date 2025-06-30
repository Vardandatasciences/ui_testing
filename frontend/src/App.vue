<template>
  <div id="app">
    <div v-if="isAuthenticated" class="app-container">
      <Sidebar />
      <div class="main-content">
        <router-view></router-view>
      </div>
    </div>
    <div v-else class="login-container">
      <router-view></router-view>
    </div>
    <PopupModal />
  </div>
</template>

<script>
import Sidebar from './components/Policy/Sidebar.vue'
import PopupModal from './modules/popup/PopupModal.vue';


export default {
  name: 'App',
  components: {
    Sidebar,
    PopupModal
  },
  data() {
    return {
      isAuthenticated: false
    }
  },
  created() {
    // Check authentication status on app load
    this.checkAuthStatus()
    
    // Listen for auth changes
    window.addEventListener('authChanged', this.checkAuthStatus)
  },
  beforeUnmount() {
    window.removeEventListener('authChanged', this.checkAuthStatus)
  },
  methods: {
    checkAuthStatus() {
      this.isAuthenticated = localStorage.getItem('isAuthenticated') === 'true'
    }
  }
}
</script>

<style>
body {
  margin: 0;
  font-family: Arial, Helvetica, sans-serif;
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  min-height: 100vh;
}

.app-container {
  display: flex;
  min-height: 100vh;
}

.main-content {
  flex: 1;
  padding: 20px;
  background-color: #f5f5f5;
}

.login-container {
  min-height: 100vh;
}
</style>