import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import FileTreeItem from './FileTreeItem';
import '@testing-library/jest-dom';
import { AppStateProvider, useAppState } from '@/lib/appState';

// Mock Recursive Component to avoid infinite loops in tests or complex rendering
jest.mock('./FileTree', () => ({
    __esModule: true,
    default: ({ nodes }: { nodes: unknown[] }) => <div data-testid="recursive-child">Child Count: {nodes.length}</div>
}));

const mockNodeFile = {
    name: 'readme.md',
    type: 'file' as const,
    path: '/test/readme.md'
};

const mockNodeFolder = {
    name: 'src',
    type: 'directory' as const,
    children: [mockNodeFile]
};

function renderWithState(ui: React.ReactElement, initSelected?: string) {
    function InitSelection() {
        const { selectFile } = useAppState();
        React.useEffect(() => {
            if (initSelected) {
                selectFile(initSelected);
            }
        }, [selectFile, initSelected]);
        return null;
    }

    function Wrapper() {
        return (
            <>
                <InitSelection />
                {ui}
            </>
        );
    }

    return render(
        <AppStateProvider>
            <Wrapper />
        </AppStateProvider>
    );
}

describe('FileTreeItem', () => {
    it('renders a file item correctly', () => {
        renderWithState(<FileTreeItem node={mockNodeFile} level={0} />);

        expect(screen.getByText('readme.md')).toBeInTheDocument();
        // Check for file-specific attributes/classes if needed
    });

    it('renders a folder item correctly', () => {
        renderWithState(<FileTreeItem node={mockNodeFolder} level={0} />);

        expect(screen.getByText('src')).toBeInTheDocument();
        // Folders show chevron/folder icons
    });

    it('calls onSelectFile when a file is clicked', () => {
        function SelectedProbe() {
            const { selectedFile } = useAppState();
            return <div data-testid="selected">{selectedFile || ''}</div>;
        }

        render(
            <AppStateProvider>
                <SelectedProbe />
                <FileTreeItem node={mockNodeFile} level={0} />
            </AppStateProvider>
        );

        fireEvent.click(screen.getByText('readme.md'));
        expect(screen.getByTestId('selected')).toHaveTextContent('/test/readme.md');
    });

    it('expands/collapses folder on click', () => {
        renderWithState(<FileTreeItem node={mockNodeFolder} level={0} />);

        const folderName = screen.getByText('src');
        // The click handler is on the parent div of the text/icons
        const folderItem = folderName.closest('div');

        // Initially collapsed (isExpanded false by default)
        expect(screen.queryByTestId('recursive-child')).not.toBeInTheDocument();

        // Expand
        fireEvent.click(folderItem!);
        expect(screen.getByTestId('recursive-child')).toBeInTheDocument();

        // Collapse
        fireEvent.click(folderItem!);
        expect(screen.queryByTestId('recursive-child')).not.toBeInTheDocument();
    });

    it('highlights selected file', () => {
        renderWithState(<FileTreeItem node={mockNodeFile} level={0} />, '/test/readme.md');

        const itemContainer = screen.getByText('readme.md').closest('div');
        // Check for the specific active class defined in the component
        // The component uses 'bg-active' for selected state
        return waitFor(() => {
            expect(itemContainer).toHaveClass('bg-active');
        });
    });

    it('does not highlight unselected file', () => {
        renderWithState(<FileTreeItem node={mockNodeFile} level={0} />, '/test/other.md');

        const itemContainer = screen.getByText('readme.md').closest('div');
        return waitFor(() => {
            expect(itemContainer).not.toHaveClass('bg-active');
        });
    });
});
