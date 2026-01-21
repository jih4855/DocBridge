'use client';

import { useState } from 'react';
import SidebarHeader from './SidebarHeader';
import ProjectList from './ProjectList';
import { useFolderTree } from '@/hooks/useFolderTree';

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
    const {
        folders,
        isLoading,
        error,
        refreshTriggers,
        loadFolders,
        deleteFolder
    } = useFolderTree(refreshTrigger);

    const [isResizing, setIsResizing] = useState(false);

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
                    onDeleteFolder={deleteFolder}
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
