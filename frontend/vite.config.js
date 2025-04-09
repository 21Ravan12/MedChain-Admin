import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    proxy: {
      // API isteklerini backend'e yönlendirme
      '/api': {
        target: 'https://127.0.0.1:5000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, ''),
        // Gerekli header'ları ekle
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'Origin': 'http://localhost:5173' // Vite'in varsayılan portu
        }
      }
    }
  },
  // Build ayarları (isteğe bağlı)
  build: {
    outDir: 'dist',
    assetsInlineLimit: 4096,
    chunkSizeWarningLimit: 1000
  }
})