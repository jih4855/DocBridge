'use client';

import { createContext, useCallback, useContext, useMemo, useState } from 'react';

type AppState = {
    selectedFile: string | null;
    selectFile: (path: string | null) => void;
    isRegisterModalOpen: boolean;
    openRegisterModal: () => void;
    closeRegisterModal: () => void;
    refreshTrigger: number;
    bumpRefreshTrigger: () => void;
};

const AppStateContext = createContext<AppState | undefined>(undefined);

export function AppStateProvider({ children }: { children: React.ReactNode }) {
    const [selectedFile, setSelectedFile] = useState<string | null>(null);
    const [isRegisterModalOpen, setIsRegisterModalOpen] = useState(false);
    const [refreshTrigger, setRefreshTrigger] = useState(0);

    const selectFile = useCallback((path: string | null) => {
        setSelectedFile(path);
    }, []);

    const openRegisterModal = useCallback(() => {
        setIsRegisterModalOpen(true);
    }, []);

    const closeRegisterModal = useCallback(() => {
        setIsRegisterModalOpen(false);
    }, []);

    const bumpRefreshTrigger = useCallback(() => {
        setRefreshTrigger((prev) => prev + 1);
    }, []);

    const value = useMemo(
        () => ({
            selectedFile,
            selectFile,
            isRegisterModalOpen,
            openRegisterModal,
            closeRegisterModal,
            refreshTrigger,
            bumpRefreshTrigger,
        }),
        [
            selectedFile,
            selectFile,
            isRegisterModalOpen,
            openRegisterModal,
            closeRegisterModal,
            refreshTrigger,
            bumpRefreshTrigger,
        ],
    );

    return <AppStateContext.Provider value={value}>{children}</AppStateContext.Provider>;
}

export function useAppState() {
    const context = useContext(AppStateContext);
    if (!context) {
        throw new Error('useAppState must be used within AppStateProvider');
    }
    return context;
}
