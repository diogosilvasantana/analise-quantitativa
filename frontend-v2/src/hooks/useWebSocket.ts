'use client';

import { useEffect, useRef, useCallback, useState } from 'react';

export function useWebSocket(
    url: string,
    onMessage: (message: any) => void
) {
    const wsRef = useRef<WebSocket | null>(null);
    const [isConnected, setIsConnected] = useState(false);
    const reconnectCountRef = useRef(0);
    const maxReconnectAttempts = 5;

    const connect = useCallback(() => {
        try {
            // Converter ws:// para http:// se necessário para Next.js (embora ws seja o correto)
            // Mantendo a lógica original do prompt, mas garantindo que url comece com ws/wss
            let wsUrl = url;
            if (wsUrl.startsWith('http')) {
                wsUrl = wsUrl.replace(/^http/, 'ws');
            }

            wsRef.current = new WebSocket(wsUrl);

            wsRef.current.onopen = () => {
                console.log('✅ WebSocket conectado');
                setIsConnected(true);
                reconnectCountRef.current = 0;
            };

            wsRef.current.onmessage = (event) => {
                try {
                    const message = JSON.parse(event.data);
                    onMessage(message);
                } catch (error) {
                    console.error('Erro ao parsear mensagem WebSocket:', error);
                }
            };

            wsRef.current.onerror = (error) => {
                console.error('Erro WebSocket:', error);
                setIsConnected(false);
            };

            wsRef.current.onclose = () => {
                console.warn('⚠️ WebSocket desconectado');
                setIsConnected(false);

                // Tentar reconectar com backoff exponencial
                if (reconnectCountRef.current < maxReconnectAttempts) {
                    const delay = Math.min(1000 * Math.pow(2, reconnectCountRef.current), 30000);
                    reconnectCountRef.current += 1;
                    console.log(`🔄 Reconectando em ${delay}ms...`);
                    setTimeout(() => connect(), delay);
                }
            };
        } catch (error) {
            console.error('Erro ao conectar WebSocket:', error);
        }
    }, [url, onMessage]);

    useEffect(() => {
        connect();

        return () => {
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, [connect]);

    return { isConnected, ws: wsRef.current };
}
