import type { Metadata } from 'next';
import { Inter, JetBrains_Mono } from 'next/font/google';
import './globals.css';
import { AppStateProvider } from '@/lib/appState';

const inter = Inter({
    subsets: ['latin'],
    variable: '--font-inter',
    display: 'swap',
});

const jetbrainsMono = JetBrains_Mono({
    subsets: ['latin'],
    variable: '--font-jetbrains-mono',
    display: 'swap',
});

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
        <html lang="ko" style={{ colorScheme: 'dark' }}>
            <body
                className={`${inter.variable} ${jetbrainsMono.variable} font-sans bg-main text-primary antialiased h-screen overflow-hidden`}
            >
                <AppStateProvider>{children}</AppStateProvider>
            </body>
        </html>
    );
}
