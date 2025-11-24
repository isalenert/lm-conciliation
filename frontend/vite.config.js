import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/setupTests.js'], // se você tiver
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'json-summary', 'html'], // ✅ json-summary gera o arquivo que o CI espera
      reportsDirectory: './coverage',
      exclude: [
        'node_modules/',
        'src/setupTests.js',
        '**/*.d.ts',
        '**/*.config.{js,ts}',
        '**/main.jsx',
      ],
    },
  },
})