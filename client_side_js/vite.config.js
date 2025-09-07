import { defineConfig } from 'vite';

export default defineConfig({
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    manifest: true,
    rollupOptions: {
      input: {
        main: './src/main.js'
      },
      output: {
        format: 'iife',
        entryFileNames: 'main.[hash].js',
        assetFileNames: '[name].[hash][extname]',
      },
    },
  },
});