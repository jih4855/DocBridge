import { useState, useEffect, useCallback } from 'react';
import { fetchClient, ApiError } from '@/lib/api';
import { useWebSocket } from './useWebSocket';

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
    type FileChangeEvent = {
        type: 'file_change';
        event: string;
        path: string;
        folder_id?: number;
    };

    const handleFileChange = useCallback((data: unknown) => {
        const message = data as FileChangeEvent;
        if (message.type === 'file_change') {
            // console.log(`[useFolderTree] 파일 변경 감지: ${data.event} - ${data.path}`);

            // 폴더 ID가 있으면 해당 프로젝트만 트리 갱신 트리거
            if (message.folder_id) {
                setRefreshTriggers(prev => ({
                    ...prev,
                    // key is number, but object keys are coerced to strings in JS, but TS is happy with number index here
                    [message.folder_id as number]: (prev[message.folder_id!] || 0) + 1
                }));
            } else {
                // folder_id가 없거나 기타 상황이면 전체 로드 (fallback)
                loadFolders();
            }
        }
    }, [loadFolders]);

    useWebSocket({
        url: `${process.env.NEXT_PUBLIC_WS_URL || 'ws://127.0.0.1:8000'}/ws/watch`,
        onMessage: handleFileChange,
        onOpen: () => {
            // 연결 시 최신 상태 동기화를 위해 한 번 로드
            loadFolders();
        }
    });

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
