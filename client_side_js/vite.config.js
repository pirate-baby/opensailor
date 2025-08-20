import { defineConfig } from 'vite';

export default defineConfig({
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        main: './src/main.js',
        htmx: './src/htmx.js',
      },
      output: {
        entryFileNames: '[name].js',
        assetFileNames: '[name][extname]',
      },
    },
  },
});