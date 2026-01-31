'use client';

import { useState, useEffect, useCallback } from 'react';
import {
    ChevronRight,
    ChevronDown,
    Folder,
    FolderOpen,
    Trash2,
} from 'lucide-react';
import FileTree from './FileTree';
import { fetchClient } from '@/lib/api';

interface FolderData {
    id: number;
    name: string;
    path: string;
}

interface TreeNode {
    name: string;
    type: 'file' | 'directory';
    path?: string;
    children?: TreeNode[];
}

interface ProjectItemProps {
    folder: FolderData;
    onDelete: () => void;
    refreshTrigger: number;
}


export default function ProjectItem({
    folder,
    onDelete,
    refreshTrigger,
}: ProjectItemProps) {
    const [isExpanded, setIsExpanded] = useState(false);
    const [isHovered, setIsHovered] = useState(false);
    const [treeData, setTreeData] = useState<TreeNode[] | null>(null);
    const [isLoading, setIsLoading] = useState(false);

    // 트리 데이터 로드 함수 분리
    // 트리 데이터 로드 함수 분리
    const loadTree = useCallback(async () => {
        setIsLoading(true);
        try {
            const data = await fetchClient<{ tree: { children: TreeNode[] } }>(`/api/folders/${folder.id}/tree`);
            setTreeData(data.tree.children || []);
        } catch (err) {
            console.error('트리 로드 실패:', err);
        } finally {
            setIsLoading(false);
        }
    }, [folder.id]);

    // 토글 핸들러
    const handleToggle = async () => {
        if (!isExpanded && !treeData) {
            await loadTree();
        }
        setIsExpanded(!isExpanded);
    };

    // refreshTrigger 변경 시 트리 갱신 (이미 펼쳐져 있는 경우만)
    useEffect(() => {
        if (isExpanded && refreshTrigger > 0) {
            loadTree();
        }
    }, [refreshTrigger, isExpanded, loadTree]);

    return (
        <div className="mb-0.5">
            {/* 프로젝트 헤더 */}
            <div
                className={`
                    flex items-center gap-1 py-[3px] pl-2 pr-1.5 cursor-pointer
                    hover:bg-hover transition-all duration-150 group select-none
                    ${isExpanded ? 'text-primary' : 'text-secondary hover:text-primary'}
                `}
                onClick={handleToggle}
                onMouseEnter={() => setIsHovered(true)}
                onMouseLeave={() => setIsHovered(false)}
            >
                {/* 펼침/접힘 아이콘 */}
                {isExpanded ? (
                    <ChevronDown size={16} className="flex-shrink-0 opacity-70" strokeWidth={2} />
                ) : (
                    <ChevronRight size={16} className="flex-shrink-0 opacity-70" strokeWidth={2} />
                )}

                {/* 폴더 아이콘 */}
                {isExpanded ? (
                    <FolderOpen size={16} className="text-yellow-500 flex-shrink-0" strokeWidth={1.5} />
                ) : (
                    <Folder size={16} className="text-yellow-600/80 flex-shrink-0" strokeWidth={1.5} />
                )}

                {/* 프로젝트 이름 */}
                <span
                    className="flex-1 truncate text-[13px] font-medium tracking-tight"
                    title={folder.name}
                >
                    {folder.name}
                </span>

                {/* 삭제 버튼 */}
                {isHovered && (
                    <button
                        className="p-0.5 text-secondary hover:text-red-400 hover:bg-hover rounded transition-all duration-150"
                        onClick={(e) => {
                            e.stopPropagation();
                            onDelete();
                        }}
                        title="프로젝트 삭제"
                    >
                        <Trash2 size={14} strokeWidth={1.5} />
                    </button>
                )}

                {/* 로딩 인디케이터 */}
                {isLoading && (
                    <div className="w-3 h-3 border-2 border-muted border-t-transparent rounded-full animate-spin" />
                )}
            </div>

            {/* 하위 트리 */}
            {isExpanded && treeData && (
                <FileTree
                    nodes={treeData}
                    level={1}
                />
            )}
        </div>
    );
}
