import { useEffect, useRef, useCallback, useState } from 'react';

export function useWebSocket(url, onMessage) {
    const wsRef = useRef(null);
    const [isConnected, setIsConnected] = useState(false);
    const [lastMessage, setLastMessage] = useState(null);
    const reconnectAttemptsRef = useRef(0);
    const maxReconnectAttempts = 10; // Aumentado para mais resiliência
    const reconnectDelayRef = useRef(1000); // Começa com 1 segundo

    const connect = useCallback(() => {
        if (wsRef.current && (wsRef.current.readyState === WebSocket.OPEN || wsRef.current.readyState === WebSocket.CONNECTING)) {
            return; // Já conectado ou conectando
        }

        try {
            wsRef.current = new WebSocket(url);

            wsRef.current.onopen = () => {
                console.log('✅ WebSocket conectado');
                setIsConnected(true);
                reconnectAttemptsRef.current = 0; // Resetar tentativas ao conectar com sucesso
                reconnectDelayRef.current = 1000; // Resetar delay
            };

            wsRef.current.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    setLastMessage(data);
                    if (onMessage) onMessage(data);
                } catch (e) {
                    console.error('❌ Erro ao parsear mensagem WebSocket:', e, event.data);
                }
            };

            wsRef.current.onerror = (error) => {
                console.error('❌ WebSocket erro:', error);
            };

            wsRef.current.onclose = () => {
                console.log('❌ WebSocket desconectado');
                setIsConnected(false);

                if (reconnectAttemptsRef.current < maxReconnectAttempts) {
                    reconnectAttemptsRef.current++;
                    const delay = reconnectDelayRef.current * (2 * (reconnectAttemptsRef.current - 1)); // Exponential backoff
                    reconnectDelayRef.current = Math.min(delay, 30000); // Limite de 30 segundos

                    console.log(`🔄 Tentando reconectar em ${reconnectDelayRef.current}ms (Tentativa ${reconnectAttemptsRef.current}/${maxReconnectAttempts})...`);
                    setTimeout(connect, reconnectDelayRef.current);
                } else {
                    console.error('❌ Limite de tentativas de reconexão atingido. Não será mais tentado.');
                }
            };
        } catch (error) {
            console.error('❌ Erro fatal ao criar WebSocket:', error);
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

    return { isConnected, lastMessage };
}
