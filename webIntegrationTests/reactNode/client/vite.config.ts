import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'https://webintegrationsolution.onrender.com',
        changeOrigin: true
      }
    }
  },
  preview: {
    port: 5173,
    host: '0.0.0.0',
    // Allow all hosts for Render deployment (dynamic domains)
    allowedHosts: [
      'localhost',
      '127.0.0.1',
      '.onrender.com'  // Allow all Render subdomains
    ]
  }
})
