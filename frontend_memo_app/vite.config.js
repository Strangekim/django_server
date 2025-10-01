import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  return {
    plugins: [vue()],
    // 개발 환경에서는 '/', 프로덕션에서는 '/static/' 사용
    base: mode === 'production' ? '/static/' : '/',
    server: {
      host: '0.0.0.0',
      port: 3000,
      strictPort: false,
      cors: true
    },
    build: {
      outDir: 'dist',
      assetsDir: 'assets',
      emptyOutDir: true,
      // 빌드 시 소스맵 생성 (프로덕션에서는 false 권장)
      sourcemap: mode === 'development'
    }
  }
})