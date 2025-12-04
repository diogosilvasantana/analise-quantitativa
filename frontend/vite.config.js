import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    server: {
        host: true, // Permite acesso externo ao container
        port: 3000,
        watch: {
            usePolling: true // Necessário para hot-reload em Docker
        }
    }
});
