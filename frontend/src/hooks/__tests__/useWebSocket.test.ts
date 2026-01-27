import { renderHook, act } from '@testing-library/react';
import { useWebSocket } from '../useWebSocket';

describe('useWebSocket', () => {
    let mockWebSocket: any;

    beforeEach(() => {
        jest.useFakeTimers();
        mockWebSocket = {
            close: jest.fn(),
            send: jest.fn(),
        };
        (global as any).WebSocket = jest.fn(() => mockWebSocket);
    });

    afterEach(() => {
        jest.useRealTimers();
        jest.clearAllMocks();
    });

    it('should connect on mount', () => {
        const { result } = renderHook(() => useWebSocket({ url: 'ws://test.com' }));

        expect((global as any).WebSocket).toHaveBeenCalledWith('ws://test.com');
        expect(result.current.isConnected).toBe(false);

        // Simulate connection open
        act(() => {
            mockWebSocket.onopen();
        });
        expect(result.current.isConnected).toBe(true);
    });

    it('should attempt reconnect on close', () => {
        renderHook(() => useWebSocket({ url: 'ws://test.com', retryInterval: 1000 }));

        act(() => {
            mockWebSocket.onopen();
        });
        expect((global as any).WebSocket).toHaveBeenCalledTimes(1);

        // Simulate close
        act(() => {
            mockWebSocket.onclose();
        });

        // Should not have reconnected immediately
        expect((global as any).WebSocket).toHaveBeenCalledTimes(1);

        // Advance timers by retry interval (1000ms)
        act(() => {
            jest.advanceTimersByTime(1000);
        });

        // Should have reconnected
        expect((global as any).WebSocket).toHaveBeenCalledTimes(2);
    });

    it('should apply exponential backoff', () => {
        renderHook(() => useWebSocket({ url: 'ws://test.com', retryInterval: 1000 }));

        // Initial connection
        act(() => { mockWebSocket.onopen(); });

        // 1st disconnect
        act(() => { mockWebSocket.onclose(); });
        // Retry 1: 1000 * 2^0 = 1000ms
        act(() => { jest.advanceTimersByTime(1000); });
        expect((global as any).WebSocket).toHaveBeenCalledTimes(2);

        // 2nd disconnect (fail immediately)
        act(() => { mockWebSocket.onclose(); });
        // Retry 2: 1000 * 2^1 = 2000ms
        act(() => { jest.advanceTimersByTime(2000); });
        expect((global as any).WebSocket).toHaveBeenCalledTimes(3);

        // 3rd disconnect
        act(() => { mockWebSocket.onclose(); });
        // Retry 3: 1000 * 2^2 = 4000ms
        act(() => { jest.advanceTimersByTime(4000); });
        expect((global as any).WebSocket).toHaveBeenCalledTimes(4);
    });
});
