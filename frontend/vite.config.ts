import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    // Deep CJS subpath not covered by Vite's default dependency scan; without
    // this it's served raw (untransformed `require(...)`) and breaks at runtime.
    include: ['react-big-calendar/lib/addons/dragAndDrop/withDragAndDrop'],
  },
})
