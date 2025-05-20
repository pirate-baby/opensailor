import { defineConfig } from 'vite';

export default defineConfig({
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    rollupOptions: {
      input: './src/main.js',
      output: {
        format: 'iife',
        name: 'MilkdownCrepeBundle',
        entryFileNames: 'main.js',
        assetFileNames: '[name][extname]',
      },
    },
  },
});