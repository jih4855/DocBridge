'use client';

import FileTreeItem from './FileTreeItem';

interface TreeNode {
    name: string;
    type: 'file' | 'directory';
    path?: string;
    children?: TreeNode[];
}

interface FileTreeProps {
    nodes: TreeNode[];
    level: number;
    selectedFile: string | null;
    onSelectFile: (path: string) => void;
}

export default function FileTree({
    nodes,
    level,
    selectedFile,
    onSelectFile,
}: FileTreeProps) {
    return (
        <div>
            {nodes.map((node, index) => (
                <FileTreeItem
                    key={`${node.name}-${index}`}
                    node={node}
                    level={level}
                    selectedFile={selectedFile}
                    onSelectFile={onSelectFile}
                />
            ))}
        </div>
    );
}
