import { render, screen, fireEvent } from '@testing-library/react';
import FileTreeItem from './FileTreeItem';
import '@testing-library/jest-dom';

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

const defaultProps = {
    level: 0,
    selectedFile: null,
    onSelectFile: jest.fn()
};

describe('FileTreeItem', () => {
    it('renders a file item correctly', () => {
        render(<FileTreeItem {...defaultProps} node={mockNodeFile} />);

        expect(screen.getByText('readme.md')).toBeInTheDocument();
        // Check for file-specific attributes/classes if needed
    });

    it('renders a folder item correctly', () => {
        render(<FileTreeItem {...defaultProps} node={mockNodeFolder} />);

        expect(screen.getByText('src')).toBeInTheDocument();
        // Folders show chevron/folder icons
    });

    it('calls onSelectFile when a file is clicked', () => {
        const handleSelect = jest.fn();
        render(<FileTreeItem {...defaultProps} node={mockNodeFile} onSelectFile={handleSelect} />);

        fireEvent.click(screen.getByText('readme.md'));
        expect(handleSelect).toHaveBeenCalledWith('/test/readme.md');
    });

    it('expands/collapses folder on click', () => {
        render(<FileTreeItem {...defaultProps} node={mockNodeFolder} />);

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
        render(<FileTreeItem {...defaultProps} node={mockNodeFile} selectedFile="/test/readme.md" />);

        const itemContainer = screen.getByText('readme.md').closest('div');
        // Check for the specific active class defined in the component
        // The component uses 'bg-active' for selected state
        expect(itemContainer).toHaveClass('bg-active');
    });

    it('does not highlight unselected file', () => {
        render(<FileTreeItem {...defaultProps} node={mockNodeFile} selectedFile="/test/other.md" />);

        const itemContainer = screen.getByText('readme.md').closest('div');
        expect(itemContainer).not.toHaveClass('bg-active');
    });
});
