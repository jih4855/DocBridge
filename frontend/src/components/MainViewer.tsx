'use client';

import { Copy, FileText, Loader2, AlertCircle } from 'lucide-react';
import { useFileContent } from '@/hooks/useFileContent';
import MarkdownViewer from './MarkdownViewer';

interface MainViewerProps {
    filePath: string | null;
}

export default function MainViewer({ filePath }: MainViewerProps) {
    const { content, loading, error } = useFileContent(filePath);

    const handleCopy = async () => {
        if (!content) return;
        try {
            await navigator.clipboard.writeText(content);
            // Optional: Toast notification here
        } catch (err) {
            console.error('복사 실패:', err);
        }
    };

    // Empty State
    if (!filePath) {
        return (
            <main className="flex-1 bg-main flex flex-col items-center justify-center h-full select-none">
                <div className="flex flex-col items-center opacity-40 hover:opacity-60 transition-opacity duration-300">
                    <div className="p-6 rounded-full bg-hover/50 mb-4">
                        <FileText size={48} strokeWidth={1.5} className="text-muted" />
                    </div>
                    <p className="text-sm font-medium text-muted tracking-wide">
                        파일을 선택하여 미리보기
                    </p>
                </div>
            </main>
        );
    }

    const fileName = filePath.split('/').pop() || '';

    return (
        <main className="flex-1 bg-main overflow-auto flex flex-col h-full">
            {/* 탭 헤더 */}
            <div className="h-[35px] bg-main border-b border-border-main flex items-center px-4 flex-shrink-0 justify-between">
                <div className="flex items-center gap-2">
                    <FileText size={14} className="text-file-item" />
                    <span className="font-mono text-sm text-primary italic">{fileName}</span>
                </div>
                <div className="flex items-center gap-2">
                    {/* Copy Button */}
                    <button
                        onClick={handleCopy}
                        disabled={loading || !!error || !content}
                        className="p-1 text-secondary hover:text-primary transition-colors disabled:opacity-30"
                        title="내용 복사"
                        aria-label="Copy Content"
                    >
                        <Copy size={14} />
                    </button>
                </div>
            </div>

            {/* 컨텐츠 뷰어 */}
            <div className="flex-1 p-8 overflow-auto">
                {loading ? (
                    <div className="flex items-center justify-center h-full text-secondary">
                        <Loader2 className="animate-spin mr-2" size={20} />
                        <span>불러오는 중...</span>
                    </div>
                ) : error ? (
                    <div className="flex flex-col items-center justify-center h-full text-red-400">
                        <AlertCircle size={48} className="mb-4 opacity-50" />
                        <p className="font-mono text-sm">{error}</p>
                    </div>
                ) : (
                    <MarkdownViewer content={content} />
                )}
            </div>
        </main>
    );
}
