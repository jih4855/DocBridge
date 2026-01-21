'use client';

import { useState, useEffect, useCallback } from 'react';
import { fetchClient, ApiError } from '@/lib/api';
import SidebarHeader from './SidebarHeader';
import ProjectList from './ProjectList';

interface Folder {
    id: number;
    name: string;
    path: string;
    created_at: string;
}

interface SidebarProps {
    width: number;
    onWidthChange: (width: number) => void;
    selectedFile: string | null;
    onSelectFile: (path: string) => void;
    onOpenRegisterModal: () => void;
    refreshTrigger: number;
}

export default function Sidebar({
    width,
    onWidthChange,
    selectedFile,
    onSelectFile,
    onOpenRegisterModal,
    refreshTrigger,
}: SidebarProps) {
    const [folders, setFolders] = useState<Folder[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isResizing, setIsResizing] = useState(false);

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

    useEffect(() => {
        loadFolders();
    }, [loadFolders, refreshTrigger]); // 상위 refreshTrigger도 반영

    // WebSocket 연결 - 파일 변경 시 부분 업데이트
    useEffect(() => {
        const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';
        const ws = new WebSocket(`${wsUrl}/ws/watch`);

        ws.onopen = () => {
            console.log('[Sidebar] WebSocket 연결됨');
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.type === 'file_change') {
                    console.log(`[Sidebar] 파일 변경 감지: ${data.event} - ${data.path}`);

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
                console.error('[Sidebar] WebSocket 메시지 파싱 오류:', e);
            }
        };

        ws.onerror = (error) => {
            console.warn('[Sidebar] WebSocket 연결 오류:', error);
        };

        ws.onclose = () => {
            console.log('[Sidebar] WebSocket 연결 종료');
        };

        return () => {
            ws.close();
        };
    }, [loadFolders]);

    // 폴더 삭제 핸들러
    const handleDeleteFolder = async (folderId: number) => {
        if (!confirm('이 프로젝트를 삭제하시겠습니까?')) {
            return;
        }

        try {
            await fetchClient<{ success: boolean }>(`/api/folders/${folderId}`, {
                method: 'DELETE',
            });

            // 목록에서 제거
            setFolders((prev) => prev.filter((f) => f.id !== folderId));
        } catch (err) {
            if (err instanceof ApiError) {
                alert(err.message);
            } else {
                alert('삭제에 실패했습니다.');
            }
        }
    };

    // 리사이즈 핸들러
    const handleMouseDown = () => {
        setIsResizing(true);
        document.addEventListener('mousemove', handleMouseMove);
        document.addEventListener('mouseup', handleMouseUp);
    };

    const handleMouseMove = (e: MouseEvent) => {
        const newWidth = Math.min(Math.max(e.clientX, 200), 400);
        onWidthChange(newWidth);
    };

    const handleMouseUp = () => {
        setIsResizing(false);
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
    };

    return (
        <aside
            className="bg-sidebar border-r border-border-main flex flex-col relative select-none"
            style={{ width, minWidth: 200, maxWidth: 400 }}
        >
            {/* 헤더 */}
            <SidebarHeader onOpenRegisterModal={onOpenRegisterModal} />

            {/* 프로젝트 목록 */}
            <div className="flex-1 overflow-auto">
                <ProjectList
                    folders={folders}
                    isLoading={isLoading}
                    error={error}
                    selectedFile={selectedFile}
                    onSelectFile={onSelectFile}
                    onDeleteFolder={handleDeleteFolder}
                    onRetry={loadFolders}
                    refreshTriggers={refreshTriggers}
                />
            </div>

            {/* 리사이즈 핸들 */}
            <div
                className={`absolute right-0 top-0 bottom-0 w-1 cursor-col-resize hover:bg-accent/50 transition-all duration-150 ${isResizing ? 'bg-accent' : ''
                    }`}
                onMouseDown={handleMouseDown}
            />
        </aside>
    );
}
