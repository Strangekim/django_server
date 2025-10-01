import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  base: '/static/',  // Django의 STATIC_URL과 일치
  server: {
    host: '0.0.0.0',
    port: 3000,
    strictPort: false,
    cors: true
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    emptyOutDir: true
  }
})