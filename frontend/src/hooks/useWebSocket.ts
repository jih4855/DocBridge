import { useState, useEffect, useCallback, useRef } from 'react';

interface WebSocketOptions {
    url: string;
    onMessage?: (data: unknown) => void;
    onOpen?: () => void;
    onClose?: () => void;
    retryInterval?: number;
    maxRetryInterval?: number;
}

export function useWebSocket({
    url,
    onMessage,
    onOpen,
    onClose,
    retryInterval = 1000,
    maxRetryInterval = 30000
}: WebSocketOptions) {
    const [isConnected, setIsConnected] = useState(false);
    const wsRef = useRef<WebSocket | null>(null);
    const retryCountRef = useRef(0);
    const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

    const connect = useCallback(() => {
        if (!url) return;

        // Clean up existing connection
        if (wsRef.current) {
            wsRef.current.close();
        }

        const ws = new WebSocket(url);
        wsRef.current = ws;

        ws.onopen = () => {
            // console.log('[useWebSocket] Connected');
            setIsConnected(true);
            retryCountRef.current = 0; // Reset retry count on success
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current);
                reconnectTimeoutRef.current = null;
            }
            onOpen?.();
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                onMessage?.(data);
            } catch (error) {
                console.error('[useWebSocket] Message parse error:', error);
            }
        };

        ws.onclose = () => {
            // console.log('[useWebSocket] Disconnected');
            setIsConnected(false);
            onClose?.();

            // Exponential Backoff Logic
            const nextRetryDelay = Math.min(
                retryInterval * Math.pow(2, retryCountRef.current),
                maxRetryInterval
            );

            // console.log(`[useWebSocket] Reconnecting in ${nextRetryDelay}ms...`);

            reconnectTimeoutRef.current = setTimeout(() => {
                retryCountRef.current++;
                connect();
            }, nextRetryDelay);
        };

        ws.onerror = () => {
            // console.warn('[useWebSocket] Error:', error);
            // onclose will be called automatically after onerror
            ws.close();
        };

    }, [url, retryInterval, maxRetryInterval, onMessage, onOpen, onClose]);

    useEffect(() => {
        connect();

        return () => {
            if (wsRef.current) {
                wsRef.current.close();
            }
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current);
            }
        };
    }, [connect]);

    return { isConnected };
}
