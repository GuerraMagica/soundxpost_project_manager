import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // The workspace path contains a literal ":" which breaks Vite's default
    // fs.allow path matching. Disabling the strict check is safe for local
    // development in this lab-only setup.
    fs: {
      strict: false,
    },
  },
})
