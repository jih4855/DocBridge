const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export class ApiError extends Error {
    constructor(
        public status: number,
        public code: string,
        message: string
    ) {
        super(message);
        this.name = 'ApiError';
    }
}

interface RequestOption extends RequestInit {
    headers?: Record<string, string>;
}

/**
 * 표준화된 API 클라이언트 (fetch wrapper)
 * 
 * 기능:
 * - Base URL 자동 적용
 * - JSON 헤더 자동 설정
 * - 에러 응답 표준화 (ApiError throw)
 */
export async function fetchClient<T>(endpoint: string, options: RequestOption = {}): Promise<T> {
    // endpoint가 /로 시작하지 않으면 추가
    const path = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
    const url = `${BASE_URL}${path}`;

    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };

    try {
        const response = await fetch(url, {
            ...options,
            headers,
        });

        // 204 No Content 처리
        if (response.status === 204) {
            return {} as T;
        }

        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
        // 백엔드 표준 에러 스키마: { error, code, details }
            const errorCode = data.code || 'UNKNOWN_ERROR';
            const errorMessage = data.error || data.message || '알 수 없는 오류가 발생했습니다.';

            throw new ApiError(response.status, errorCode, errorMessage);
        }

        return data as T;
    } catch (error) {
        if (error instanceof ApiError) {
            throw error;
        }
        // 네트워크 에러 등 fetch 자체 실패 handling
        console.error('API Request Failed:', error);
        throw new ApiError(500, 'NETWORK_ERROR', '서버와 연결할 수 없습니다.');
    }
}
