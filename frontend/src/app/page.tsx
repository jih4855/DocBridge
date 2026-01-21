'use client';

import { useState } from 'react';
import Header from '@/components/Header';
import Sidebar from '@/components/Sidebar';
import MainViewer from '@/components/MainViewer';
import FolderRegisterModal from '@/components/FolderRegisterModal';

export default function Home() {
    const [selectedFile, setSelectedFile] = useState<string | null>(null);
    const [sidebarWidth, setSidebarWidth] = useState(240);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [refreshTrigger, setRefreshTrigger] = useState(0);

    const handleRegisterSuccess = () => {
        // API 성공 시 목록 새로고침
        setRefreshTrigger((prev) => prev + 1);
    };

    return (
        <div className="flex flex-col h-screen relative">
            {/* 헤더 */}
            <Header />

            {/* 메인 컨텐츠 */}
            <div className="flex flex-1 overflow-hidden">
                {/* 사이드바 */}
                <Sidebar
                    width={sidebarWidth}
                    onWidthChange={setSidebarWidth}
                    selectedFile={selectedFile}
                    onSelectFile={setSelectedFile}
                    onOpenRegisterModal={() => setIsModalOpen(true)}
                    refreshTrigger={refreshTrigger}
                />

                {/* 메인 뷰어 */}
                <MainViewer filePath={selectedFile} />
            </div>

            {/* 모달 (최상위 레벨) */}
            <FolderRegisterModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onSuccess={handleRegisterSuccess}
            />
        </div>
    );
}
