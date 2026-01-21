import { useState, useEffect, useCallback } from 'react';
import { fetchClient, ApiError } from '@/lib/api';

export function useFileContent(filePath: string | null) {
    const [content, setContent] = useState<string>('');
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);

    const fetchContent = useCallback(async () => {
        if (!filePath) {
            setContent('');
            setError(null);
            return;
        }

        setLoading(true);
        setError(null);
        try {
            const data = await fetchClient<{ content: string }>(`/api/files?path=${encodeURIComponent(filePath)}`);
            setContent(data.content);
        } catch (err) {
            console.error('API Error:', err);
            if (err instanceof ApiError) {
                setError(err.message);
            } else {
                setError('알 수 없는 오류가 발생했습니다.');
            }
            setContent('');
        } finally {
            setLoading(false);
        }
    }, [filePath]);

    // filePath 변경 시 자동 로드
    useEffect(() => {
        fetchContent();
    }, [fetchContent]);

    return {
        content,
        loading,
        error,
        refreshContent: fetchContent
    };
}
