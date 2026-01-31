import { useState, useEffect, useCallback, useRef } from 'react';

interface WebSocketOptions {
    url: string;
    onMessage?: (data: unknown) => void;
    onOpen?: () => void;
    onClose?: () => void;
    retryInterval?: number;
    maxRetryInterval?: number;
    maxRetryCount?: number;
}

export function useWebSocket({
    url,
    onMessage,
    onOpen,
    onClose,
    retryInterval = 1000,
    maxRetryInterval = 30000,
    maxRetryCount = 5
}: WebSocketOptions) {
    const [isConnected, setIsConnected] = useState(false);
    const wsRef = useRef<WebSocket | null>(null);
    const retryCountRef = useRef(0);
    const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

    // Event handlers refs to prevent reconnection on handler change
    const onMessageRef = useRef(onMessage);
    const onOpenRef = useRef(onOpen);
    const onCloseRef = useRef(onClose);

    // Update refs on render
    useEffect(() => {
        onMessageRef.current = onMessage;
        onOpenRef.current = onOpen;
        onCloseRef.current = onClose;
    }, [onMessage, onOpen, onClose]);

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
            onOpenRef.current?.();
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                onMessageRef.current?.(data);
            } catch (error) {
                console.error('[useWebSocket] Message parse error:', error);
            }
        };

        ws.onclose = () => {
            // console.log('[useWebSocket] Disconnected');
            setIsConnected(false);
            onCloseRef.current?.();

            if (retryCountRef.current >= maxRetryCount) {
                return;
            }

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

    }, [url, retryInterval, maxRetryInterval, maxRetryCount]);

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
