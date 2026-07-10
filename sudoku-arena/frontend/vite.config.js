import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    host: true, // 讓 Docker 容器外部可存取 (監聽 0.0.0.0)
    port: 5173,
  },
})
