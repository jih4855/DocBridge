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
}

export default function FileTree({
    nodes,
    level,
}: FileTreeProps) {
    return (
        <div>
            {nodes.map((node, index) => (
                <FileTreeItem
                    key={`${node.name}-${index}`}
                    node={node}
                    level={level}
                />
            ))}
        </div>
    );
}
