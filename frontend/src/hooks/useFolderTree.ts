import { useState, useEffect, useCallback } from 'react';
import { fetchClient, ApiError } from '@/lib/api';

export interface Folder {
    id: number;
    name: string;
    path: string;
    created_at: string;
}

export function useFolderTree(refreshTrigger: number) {
    const [folders, setFolders] = useState<Folder[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [refreshTriggers, setRefreshTriggers] = useState<Record<number, number>>({});

    // 폴더 목록 로드
    const loadFolders = useCallback(async () => {
        setIsLoading(true);
        try {
            const data = await fetchClient<{ folders: Folder[] }>('/api/folders');
            setFolders(data.folders || []);
            setError(null);
        } catch (err) {
            if (err instanceof ApiError) {
                setError(err.message);
            } else {
                setError('서버에 연결할 수 없습니다.');
            }
        } finally {
            setIsLoading(false);
        }
    }, []);

    // 초기 로드 및 외부 트리거 대응
    useEffect(() => {
        loadFolders();
    }, [loadFolders, refreshTrigger]);

    // WebSocket 연결 - 파일 변경 시 부분 업데이트
    useEffect(() => {
        const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';
        const ws = new WebSocket(`${wsUrl}/ws/watch`);

        ws.onopen = () => {
            // console.log('[useFolderTree] WebSocket 연결됨');
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.type === 'file_change') {
                    // console.log(`[useFolderTree] 파일 변경 감지: ${data.event} - ${data.path}`);

                    // 폴더 ID가 있으면 해당 프로젝트만 트리 갱신 트리거
                    if (data.folder_id) {
                        setRefreshTriggers(prev => ({
                            ...prev,
                            [data.folder_id]: (prev[data.folder_id] || 0) + 1
                        }));
                    } else {
                        // folder_id가 없거나 기타 상황이면 전체 로드 (fallback)
                        loadFolders();
                    }
                }
            } catch (e) {
                console.error('[useFolderTree] WebSocket 메시지 파싱 오류:', e);
            }
        };

        ws.onerror = (error) => {
            console.warn('[useFolderTree] WebSocket 연결 오류:', error);
        };

        ws.onclose = () => {
            // console.log('[useFolderTree] WebSocket 연결 종료');
        };

        return () => {
            ws.close();
        };
    }, [loadFolders]);

    // 폴더 삭제 핸들러
    const deleteFolder = async (folderId: number): Promise<boolean> => {
        if (!confirm('이 프로젝트를 삭제하시겠습니까?')) {
            return false;
        }

        try {
            await fetchClient<{ success: boolean }>(`/api/folders/${folderId}`, {
                method: 'DELETE',
            });

            // 목록에서 제거
            setFolders((prev) => prev.filter((f) => f.id !== folderId));
            return true;
        } catch (err) {
            if (err instanceof ApiError) {
                alert(err.message);
            } else {
                alert('삭제에 실패했습니다.');
            }
            return false;
        }
    };

    return {
        folders,
        isLoading,
        error,
        refreshTriggers,
        loadFolders,
        deleteFolder
    };
}
