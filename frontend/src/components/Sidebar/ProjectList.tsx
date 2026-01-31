'use client';

import ProjectItem from './ProjectItem';

interface Folder {
    id: number;
    name: string;
    path: string;
    created_at: string;
}

interface ProjectListProps {
    folders: Folder[];
    isLoading: boolean;
    error: string | null;
    onDeleteFolder: (id: number) => void;
    onRetry: () => void;
    refreshTriggers: Record<number, number>;
}

// 로딩 스켈레톤
function LoadingSkeleton() {
    return (
        <div className="p-2 space-y-1">
            {[1, 2, 3].map((i) => (
                <div key={i} className="flex items-center gap-2 px-2 py-[3px]">
                    <div className="w-4 h-4 bg-hover/60 rounded animate-pulse" />
                    <div className="flex-1 h-3.5 bg-hover/60 rounded animate-pulse" />
                </div>
            ))}
        </div>
    );
}

// 에러 상태
function ErrorState({ message, onRetry }: { message: string; onRetry: () => void }) {
    return (
        <div className="px-4 py-8 text-center bg-sidebar">
            <p className="text-red-400/90 text-[13px] mb-4">{message}</p>
            <button
                onClick={onRetry}
                className="px-3 py-1.5 text-[12px] bg-brand text-white rounded hover:bg-brand-hover transition-all duration-150"
            >
                다시 시도
            </button>
        </div>
    );
}

// 빈 상태
function EmptyState() {
    return (
        <div className="px-4 py-8 text-center text-muted text-[13px] bg-sidebar">
            등록된 프로젝트가 없습니다.
            <br />
            <span className="text-accent/80 mt-2 inline-block text-[12px]">
                상단 [+] 버튼으로 프로젝트를 등록하세요.
            </span>
        </div>
    );
}

export default function ProjectList({
    folders,
    isLoading,
    error,
    onDeleteFolder,
    onRetry,
    refreshTriggers,
}: ProjectListProps) {
    if (isLoading) {
        return <LoadingSkeleton />;
    }

    if (error) {
        return <ErrorState message={error} onRetry={onRetry} />;
    }

    if (folders.length === 0) {
        return <EmptyState />;
    }

    return (
        <div className="py-2 bg-sidebar min-h-full">
            {folders.map((folder) => (
                <ProjectItem
                    key={folder.id}
                    folder={folder}
                    onDelete={() => onDeleteFolder(folder.id)}
                    refreshTrigger={refreshTriggers[folder.id] || 0}
                />
            ))}
        </div>
    );
}
