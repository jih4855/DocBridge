import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ProjectItem from './ProjectItem';
import { fetchClient } from '@/lib/api';

// fetchClient Mock
jest.mock('@/lib/api', () => ({
    fetchClient: jest.fn(),
    ApiError: class extends Error {
        constructor(public status: number, public code: string, message: string) {
            super(message);
        }
    },
}));

// Mock FileTree component since we only want to test ProjectItem logic
jest.mock('./FileTree', () => {
    return function DummyFileTree() {
        return <div data-testid="file-tree">FileTree Component</div>;
    };
});

describe('ProjectItem', () => {
    const mockFolder = { id: 1, name: 'Project A', path: '/data/project-a', created_at: '' }; // Added created_at to satisfy interface
    const mockOnDelete = jest.fn();

    beforeEach(() => {
        jest.clearAllMocks();
    });

    it('renders folder name', () => {
        render(
            <ProjectItem
                folder={mockFolder}
                onDelete={mockOnDelete}
                refreshTrigger={0}
            />
        );
        expect(screen.getByText('Project A')).toBeInTheDocument();
    });

    it('fetches tree data when expanded', async () => {
        const mockTreeData = { tree: { children: [{ name: 'file1.md', type: 'file' }] } };
        (fetchClient as jest.Mock).mockResolvedValue(mockTreeData);

        render(
            <ProjectItem
                folder={mockFolder}
                onDelete={mockOnDelete}
                refreshTrigger={0}
            />
        );

        // Click to expand
        fireEvent.click(screen.getByText('Project A'));

        await waitFor(() => {
            expect(fetchClient).toHaveBeenCalledWith(`/api/folders/${mockFolder.id}/tree`);
            expect(screen.getByTestId('file-tree')).toBeInTheDocument();
        });
    });

    it('handles delete button click', () => {
        render(
            <ProjectItem
                folder={mockFolder}
                onDelete={mockOnDelete}
                refreshTrigger={0}
            />
        );

        // Hover to show delete button
        fireEvent.mouseEnter(screen.getByText('Project A').parentElement!);

        const deleteBtn = screen.getByTitle('프로젝트 삭제');
        fireEvent.click(deleteBtn);

        expect(mockOnDelete).toHaveBeenCalled();
    });
});
