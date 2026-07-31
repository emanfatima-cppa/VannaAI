import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',   // accessible from network (phone, other devices)
    port: 5173,         // always use 5173
    strictPort: true,   // fail loudly if 5173 is taken (no silent port switching)
  },
})
