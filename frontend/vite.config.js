import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react({
      // Explicitly include JSX files
      include: /\.(jsx|js)$/,
      // Add Babel options
      babel: {
        presets: ['@babel/preset-react'],
        plugins: [],
        babelrc: false,
        configFile: false,
      },
    })
  ],
  build: {
    outDir: 'dist',
    rollupOptions: {
      input: {
        main: './index.html',
      },
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
}) 