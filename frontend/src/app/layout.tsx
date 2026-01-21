import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
    title: 'DocBridge',
    description: '명세서 폴더 통합 관리 도구',
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="ko">
            <body className="bg-main text-primary antialiased h-screen overflow-hidden">
                {children}
            </body>
        </html>
    );
}
