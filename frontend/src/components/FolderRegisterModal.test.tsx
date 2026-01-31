import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import FolderRegisterModal from './FolderRegisterModal';
import { fetchClient, ApiError } from '@/lib/api';
import { AppStateProvider, useAppState } from '@/lib/appState';

// fetchClient Mock
jest.mock('@/lib/api', () => ({
    fetchClient: jest.fn(),
    ApiError: class extends Error {
        constructor(public status: number, public code: string, message: string) {
            super(message);
        }
    },
}));

describe('FolderRegisterModal', () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });

    function renderOpenModal() {
        function OpenModal() {
            const { openRegisterModal } = useAppState();
            React.useEffect(() => {
                openRegisterModal();
            }, [openRegisterModal]);
            return null;
        }

        return render(
            <AppStateProvider>
                <OpenModal />
                <FolderRegisterModal />
            </AppStateProvider>
        );
    }

    it('renders nothing when not open', () => {
        render(
            <AppStateProvider>
                <FolderRegisterModal />
            </AppStateProvider>
        );
        expect(screen.queryByText('새 프로젝트 등록')).not.toBeInTheDocument();
    });

    it('renders correct content when open', () => {
        renderOpenModal();
        expect(screen.getByText('새 프로젝트 등록')).toBeInTheDocument();
        expect(screen.getByPlaceholderText('예: My Project')).toBeInTheDocument();
        expect(screen.getByPlaceholderText('/data/...')).toBeInTheDocument();
    });

    it('shows error when submitting empty values', async () => {
        renderOpenModal();

        fireEvent.click(screen.getByText('등록'));

        expect(await screen.findByText('프로젝트명을 입력하세요')).toBeInTheDocument();
    });

    it('handles successful registration', async () => {
        (fetchClient as jest.Mock).mockResolvedValue({ id: 1, name: 'Test', path: '/test' });

        renderOpenModal();

        fireEvent.change(screen.getByPlaceholderText('예: My Project'), { target: { value: 'Test Project' } });
        fireEvent.change(screen.getByPlaceholderText('/data/...'), { target: { value: '/data/test' } });
        fireEvent.click(screen.getByText('등록'));

        await waitFor(() => {
            expect(fetchClient).toHaveBeenCalledWith('/api/folders', expect.objectContaining({
                method: 'POST',
                body: JSON.stringify({ name: 'Test Project', path: '/data/test' }),
            }));
        });
        await waitFor(() => {
            expect(screen.queryByText('새 프로젝트 등록')).not.toBeInTheDocument();
        });
    });

    it('handles API error', async () => {
        const errorMsg = '이미 존재하는 경로입니다.';
        (fetchClient as jest.Mock).mockRejectedValue(new ApiError(409, 'CONFLICT', errorMsg));

        renderOpenModal();

        fireEvent.change(screen.getByPlaceholderText('예: My Project'), { target: { value: 'Test Project' } });
        fireEvent.change(screen.getByPlaceholderText('/data/...'), { target: { value: '/data/test' } });
        fireEvent.click(screen.getByText('등록'));

        expect(await screen.findByText(errorMsg)).toBeInTheDocument();
    });
});
