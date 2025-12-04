'use client';

import { useEffect, useRef, useCallback, useState } from 'react';
import { logger } from '@/lib/logger';

export function useWebSocket(
    url: string,
    onMessage: (message: any) => void
) {
    const wsRef = useRef<WebSocket | null>(null);
    const [isConnected, setIsConnected] = useState(false);
    const reconnectCountRef = useRef(0);
    const maxReconnectAttempts = 10;
    const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

    const connect = useCallback(() => {
        try {
            // Use environment variable if available, otherwise fallback to provided url
            const wsUrl = process.env.NEXT_PUBLIC_WS_URL || url;

            // Ensure ws/wss protocol
            const finalUrl = wsUrl.startsWith('http')
                ? wsUrl.replace(/^http/, 'ws')
                : wsUrl;

            logger.debug(`Tentando conectar WebSocket em: ${finalUrl}`);

            if (wsRef.current?.readyState === WebSocket.OPEN) {
                logger.warn('WebSocket já conectado.');
                return;
            }

            wsRef.current = new WebSocket(finalUrl);

            wsRef.current.onopen = () => {
                logger.info('✅ WebSocket conectado com sucesso');
                setIsConnected(true);
                reconnectCountRef.current = 0;
            };

            wsRef.current.onmessage = (event) => {
                try {
                    const message = JSON.parse(event.data);
                    onMessage(message);
                } catch (error) {
                    logger.error('Erro ao parsear mensagem WebSocket:', error);
                }
            };

            wsRef.current.onerror = (error) => {
                logger.error('Erro WebSocket:', error);
                setIsConnected(false);
            };

            wsRef.current.onclose = (event) => {
                logger.warn(`⚠️ WebSocket desconectado (Código: ${event.code})`);
                setIsConnected(false);

                // Tentar reconectar com backoff exponencial
                if (reconnectCountRef.current < maxReconnectAttempts) {
                    const delay = Math.min(1000 * Math.pow(1.5, reconnectCountRef.current), 10000);
                    reconnectCountRef.current += 1;

                    logger.info(`🔄 Tentativa de reconexão ${reconnectCountRef.current}/${maxReconnectAttempts} em ${delay}ms...`);

                    if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
                    reconnectTimeoutRef.current = setTimeout(() => connect(), delay);
                } else {
                    logger.error('❌ Falha na conexão após várias tentativas. Verifique se o backend está rodando.');
                }
            };
        } catch (error) {
            logger.error('Erro fatal ao conectar WebSocket:', error);
        }
    }, [url, onMessage]);

    const disconnect = useCallback(() => {
        if (wsRef.current) {
            wsRef.current.close();
            wsRef.current = null;
        }
        if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
        }
        setIsConnected(false);
    }, []);

    const reconnect = useCallback(() => {
        logger.info('🔄 Reconexão manual solicitada');
        disconnect();
        reconnectCountRef.current = 0;
        connect();
    }, [connect, disconnect]);

    useEffect(() => {
        connect();

        return () => {
            disconnect();
        };
    }, [connect, disconnect]);

    return { isConnected, ws: wsRef.current, reconnect };
}
