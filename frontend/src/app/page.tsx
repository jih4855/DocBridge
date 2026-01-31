import Header from '@/components/Header';
import Sidebar from '@/components/Sidebar';
import MainViewer from '@/components/MainViewer';
import FolderRegisterModal from '@/components/FolderRegisterModal';

export default function Home() {
    return (
        <div className="flex flex-col h-screen relative">
            {/* 헤더 */}
            <Header />

            {/* 메인 컨텐츠 */}
            <div className="flex flex-1 overflow-hidden">
                {/* 사이드바 */}
                <Sidebar />

                {/* 메인 뷰어 */}
                <MainViewer />
            </div>

            {/* 모달 (최상위 레벨) */}
            <FolderRegisterModal />
        </div>
    );
}
