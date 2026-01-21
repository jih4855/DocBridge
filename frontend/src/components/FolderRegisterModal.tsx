'use client';

import { useState } from 'react';
import { X, FolderPlus } from 'lucide-react';
import { fetchClient, ApiError } from '@/lib/api';

interface FolderRegisterModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSuccess: () => void;
}

export default function FolderRegisterModal({
    isOpen,
    onClose,
    onSuccess,
}: FolderRegisterModalProps) {
    const [name, setName] = useState('');
    const [path, setPath] = useState('');
    const [error, setError] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);

    if (!isOpen) return null;

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);

        if (!name.trim()) {
            setError('프로젝트명을 입력하세요');
            return;
        }
        if (!path.trim()) {
            setError('경로를 입력하세요');
            return;
        }

        setIsLoading(true);

        try {
            await fetchClient('/api/folders', {
                method: 'POST',
                body: JSON.stringify({ name: name.trim(), path: path.trim() }),
            });

            setName('');
            setPath('');
            onSuccess();
            onClose();
        } catch (err) {
            if (err instanceof ApiError) {
                setError(err.message);
            } else {
                setError('서버 연결에 실패했습니다');
            }
        } finally {
            setIsLoading(false);
        }
    };

    const handleClose = () => {
        setName('');
        setPath('');
        setError(null);
        onClose();
    };

    return (
        <div className="fixed inset-0 z-[9999] flex items-center justify-center font-sans">
            {/* 배경 오버레이 */}
            <div
                className="absolute inset-0 bg-black/60 backdrop-blur-[1px]"
                onClick={handleClose}
            />

            {/* 모달 컨테이너 */}
            <div className="relative bg-panel w-full max-w-[480px] border border-border-main shadow-2xl">
                {/* 헤더 */}
                <div className="flex items-center justify-between px-4 py-3 bg-hover border-b border-border-main">
                    <h2 className="text-sm font-semibold text-primary flex items-center gap-2">
                        <FolderPlus size={16} className="text-brand" />
                        새 프로젝트 등록
                    </h2>
                    <button
                        onClick={handleClose}
                        className="text-secondary hover:text-primary hover:bg-panel p-1 rounded transition-colors"
                    >
                        <X size={16} />
                    </button>
                </div>

                {/* 폼 콘텐츠 */}
                <form onSubmit={handleSubmit} className="p-6 space-y-6">
                    {/* 프로젝트 이름 */}
                    <div className="space-y-2">
                        <label className="block text-xs font-semibold text-secondary uppercase tracking-wide">
                            프로젝트 이름
                        </label>
                        <input
                            type="text"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            placeholder="예: My Project"
                            className="w-full px-3 py-2.5 bg-hover border border-border-main text-sm text-primary placeholder-text-muted focus:border-brand focus:outline-none focus:ring-1 focus:ring-brand transition-all"
                            autoFocus
                        />
                    </div>

                    {/* 폴더 경로 */}
                    <div className="space-y-2">
                        <label className="block text-xs font-semibold text-secondary uppercase tracking-wide">
                            폴더 경로
                        </label>
                        <input
                            type="text"
                            value={path}
                            onChange={(e) => setPath(e.target.value)}
                            placeholder="/data/..."
                            className="w-full px-3 py-2.5 bg-hover border border-border-main text-sm text-primary placeholder-text-muted focus:border-brand focus:outline-none focus:ring-1 focus:ring-brand font-mono transition-all"
                        />
                        <p className="text-[11px] text-muted flex items-center gap-1">
                            Docker 컨테이너 내부 경로 (/data/...)
                        </p>
                    </div>

                    {/* 에러 메시지 */}
                    {error && (
                        <div className="px-3 py-2 bg-red-950/50 text-red-400 text-xs flex items-center gap-2 border-l-2 border-red-500">
                            <span>⚠️</span>
                            {error}
                        </div>
                    )}

                    {/* 버튼 그룹 */}
                    <div className="flex justify-end gap-3 pt-2">
                        <button
                            type="button"
                            onClick={handleClose}
                            className="px-5 py-2 text-xs font-medium text-primary bg-panel border border-border-main hover:bg-hover transition-colors"
                        >
                            취소
                        </button>
                        <button
                            type="submit"
                            disabled={isLoading}
                            className="px-5 py-2 text-xs font-bold text-white bg-brand hover:bg-brand-hover transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-md"
                        >
                            {isLoading ? '등록 중...' : '등록'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
