// @ts-check
import { defineConfig } from 'astro/config';
import react from '@astrojs/react';
import tailwindcss from '@tailwindcss/vite';

const PROXY_TARGET = 'http://localhost:8765';

// https://astro.build/config
export default defineConfig({
  integrations: [react()],
  output: 'static',
  vite: {
    plugins: [tailwindcss()],
    define: {
      'import.meta.env.PUBLIC_API_URL': JSON.stringify(process.env.PUBLIC_API_URL || ''),
    },
    server: {
      proxy: {
        '/api': {
          target: PROXY_TARGET,
          changeOrigin: true,
        },
      },
    },
  },
});
