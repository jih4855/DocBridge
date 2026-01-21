'use client';

export default function Header() {
    return (
        <header className="h-[35px] bg-sidebar border-b border-border-main flex items-center px-4 select-none flex-shrink-0">
            {/* 로고 */}
            <span className="text-xs font-bold text-brand tracking-tight">DocBridge</span>
        </header>
    );
}
