'use client';

import { FolderPlus, Settings } from 'lucide-react';

interface SidebarHeaderProps {
    onOpenRegisterModal: () => void;
}

export default function SidebarHeader({ onOpenRegisterModal }: SidebarHeaderProps) {
    return (
        <div className="h-[35px] flex items-center justify-between px-4 bg-sidebar text-secondary border-b border-border-main select-none flex-shrink-0">
            <span className="text-[11px] font-bold tracking-wider uppercase opacity-80">탐색기</span>
            <div className="flex items-center gap-0.5">
                <button
                    onClick={onOpenRegisterModal}
                    className="p-1 rounded hover:bg-hover text-secondary hover:text-primary transition-all duration-150"
                    title="새 프로젝트 등록"
                >
                    <FolderPlus size={16} strokeWidth={1.5} />
                </button>
                <button
                    className="p-1 rounded hover:bg-hover text-secondary hover:text-primary transition-all duration-150"
                    title="설정"
                >
                    <Settings size={16} strokeWidth={1.5} />
                </button>
            </div>
        </div>
    );
}
