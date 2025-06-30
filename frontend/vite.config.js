import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  define: {
    __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: 'false'
  },
  server: {
    proxy: {
      '/grc': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
}) 