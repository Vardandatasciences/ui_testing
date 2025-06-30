import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import axios from 'axios'
import '@fortawesome/fontawesome-free/css/all.min.css'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import Popup from './modules/popup';
import './styles/theme.css'

// Create Vuetify instance
const vuetify = createVuetify({
  components,
  directives,
  icons: {
    defaultSet: 'mdi',
  },
})

// Configure axios defaults for session-based authentication
axios.defaults.baseURL = 'http://localhost:8000'  // Django backend URL
axios.defaults.headers.common['Content-Type'] = 'application/json'
axios.defaults.withCredentials = true  // CRITICAL: Send session cookies with ALL requests
axios.defaults.timeout = 15000  // 15 second timeout

console.log('🔐 Axios configured with session credentials for RBAC authentication')

const app = createApp(App)
app.config.compilerOptions.isCustomElement = tag => tag.includes('-')
app.config.performance = true
app.config.warnHandler = () => null 
app.use(router)
app.use(ElementPlus)
app.use(vuetify)
app.use(Popup)
app.mount('#app')
