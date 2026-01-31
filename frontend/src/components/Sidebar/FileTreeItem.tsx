'use client';

import { useState } from 'react';
import {
    ChevronRight,
    ChevronDown,
    Folder,
    FolderOpen,
    FileText,
} from 'lucide-react';
import FileTree from './FileTree';
import { useAppState } from '@/lib/appState';

interface TreeNode {
    name: string;
    type: 'file' | 'directory';
    path?: string;
    children?: TreeNode[];
}

interface FileTreeItemProps {
    node: TreeNode;
    level: number;
}

export default function FileTreeItem({
    node,
    level,
}: FileTreeItemProps) {
    const [isExpanded, setIsExpanded] = useState(false);
    const { selectedFile, selectFile } = useAppState();

    const paddingLeft = 8 + level * 16; // Base 8px + depth * 16px
    const isSelected = node.path === selectedFile;
    const isMarkdown = node.name.endsWith('.md');

    // 파일 클릭
    if (node.type === 'file') {
        return (
            <div
                className={`
                    relative flex items-center gap-1.5 py-[3px] pr-2 cursor-pointer
                    transition-all duration-150 select-none
                    ${isSelected
                        ? 'bg-active text-accent before:absolute before:left-0 before:top-0 before:bottom-0 before:w-[2px] before:bg-accent'
                        : 'text-secondary hover:bg-hover hover:text-primary'
                    }
                `}
                style={{ paddingLeft }}
                onClick={() => node.path && selectFile(node.path)}
                title={node.name}
            >
                <FileText
                    size={16}
                    className={`flex-shrink-0 ${isMarkdown ? 'text-file-item' : 'text-muted'}`}
                    strokeWidth={1.5}
                />
                <span className="text-[13px] truncate tracking-tight">{node.name}</span>
            </div>
        );
    }

    // 폴더 클릭
    return (
        <div>
            <div
                className={`
                    flex items-center gap-1 py-[3px] pr-2 cursor-pointer
                    transition-all duration-150 select-none
                    ${isExpanded ? 'text-primary' : 'text-secondary hover:text-primary'}
                    hover:bg-hover
                `}
                style={{ paddingLeft }}
                onClick={() => setIsExpanded(!isExpanded)}
                title={node.name}
            >
                {isExpanded ? (
                    <ChevronDown size={16} className="flex-shrink-0 opacity-70" strokeWidth={2} />
                ) : (
                    <ChevronRight size={16} className="flex-shrink-0 opacity-70" strokeWidth={2} />
                )}
                {isExpanded ? (
                    <FolderOpen size={16} className="text-yellow-500 flex-shrink-0" strokeWidth={1.5} />
                ) : (
                    <Folder size={16} className="text-yellow-600/80 flex-shrink-0" strokeWidth={1.5} />
                )}
                <span className="text-[13px] truncate tracking-tight">{node.name}</span>
            </div>

            {isExpanded && node.children && (
                <FileTree
                    nodes={node.children}
                    level={level + 1}
                />
            )}
        </div>
    );
}
