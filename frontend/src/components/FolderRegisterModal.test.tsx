import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import FolderRegisterModal from './FolderRegisterModal';
import { fetchClient, ApiError } from '@/lib/api';

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
    const mockOnClose = jest.fn();
    const mockOnSuccess = jest.fn();

    beforeEach(() => {
        jest.clearAllMocks();
    });

    it('renders nothing when not open', () => {
        render(
            <FolderRegisterModal
                isOpen={false}
                onClose={mockOnClose}
                onSuccess={mockOnSuccess}
            />
        );
        expect(screen.queryByText('새 프로젝트 등록')).not.toBeInTheDocument();
    });

    it('renders correct content when open', () => {
        render(
            <FolderRegisterModal
                isOpen={true}
                onClose={mockOnClose}
                onSuccess={mockOnSuccess}
            />
        );
        expect(screen.getByText('새 프로젝트 등록')).toBeInTheDocument();
        expect(screen.getByPlaceholderText('예: My Project')).toBeInTheDocument();
        expect(screen.getByPlaceholderText('/data/...')).toBeInTheDocument();
    });

    it('shows error when submitting empty values', async () => {
        render(
            <FolderRegisterModal
                isOpen={true}
                onClose={mockOnClose}
                onSuccess={mockOnSuccess}
            />
        );

        fireEvent.click(screen.getByText('등록'));

        expect(await screen.findByText('프로젝트명을 입력하세요')).toBeInTheDocument();
    });

    it('handles successful registration', async () => {
        (fetchClient as jest.Mock).mockResolvedValue({ id: 1, name: 'Test', path: '/test' });

        render(
            <FolderRegisterModal
                isOpen={true}
                onClose={mockOnClose}
                onSuccess={mockOnSuccess}
            />
        );

        fireEvent.change(screen.getByPlaceholderText('예: My Project'), { target: { value: 'Test Project' } });
        fireEvent.change(screen.getByPlaceholderText('/data/...'), { target: { value: '/data/test' } });
        fireEvent.click(screen.getByText('등록'));

        await waitFor(() => {
            expect(fetchClient).toHaveBeenCalledWith('/api/folders', expect.objectContaining({
                method: 'POST',
                body: JSON.stringify({ name: 'Test Project', path: '/data/test' }),
            }));
            expect(mockOnSuccess).toHaveBeenCalled();
            expect(mockOnClose).toHaveBeenCalled();
        });
    });

    it('handles API error', async () => {
        const errorMsg = '이미 존재하는 경로입니다.';
        (fetchClient as jest.Mock).mockRejectedValue(new ApiError(409, 'CONFLICT', errorMsg));

        render(
            <FolderRegisterModal
                isOpen={true}
                onClose={mockOnClose}
                onSuccess={mockOnSuccess}
            />
        );

        fireEvent.change(screen.getByPlaceholderText('예: My Project'), { target: { value: 'Test Project' } });
        fireEvent.change(screen.getByPlaceholderText('/data/...'), { target: { value: '/data/test' } });
        fireEvent.click(screen.getByText('등록'));

        expect(await screen.findByText(errorMsg)).toBeInTheDocument();
        expect(mockOnSuccess).not.toHaveBeenCalled();
    });
});
