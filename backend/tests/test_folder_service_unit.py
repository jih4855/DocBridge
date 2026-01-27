import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
import os
from app.services.folder_service import FolderService, PathNotExistsError, PathNotDirectoryError, PathAlreadyRegisteredError
from app.repositories.folder_repository import FolderRepository
from app.schemas.folder import FolderCreate
from app.models.folder import Folder

class TestFolderServiceUnit:
    """
    FolderService Unit Tests with Mock Repository
    True Unit Test: No DB dependency
    """

    @pytest.fixture
    def mock_repo(self):
        return Mock(spec=FolderRepository)

    @pytest.fixture
    def service(self, mock_repo, mock_file_watcher, mock_settings):
        return FolderService(mock_repo, mock_file_watcher, mock_settings)

    @pytest.fixture
    def mock_file_watcher(self): # New mock
        return Mock()
        
    @pytest.fixture
    def mock_settings(self): # New mock
        settings = Mock()
        settings.DENY_LIST = frozenset({'/', '/etc', '/root', '/bin', '/sbin', '/usr', '/proc', '/sys', '/dev'})
        return settings

    def test_register_folder_success(self, service, mock_repo, mock_file_watcher):
        # Given
        data = FolderCreate(name="Test Project", path="/Users/me/projects/test")
        
        mock_repo.exists_by_path.return_value = False
        mock_repo.create.return_value = Folder(
            id=1, 
            name=data.name, 
            path=data.path,
            created_at=datetime.utcnow()
        )
        
        # Mock os.path
        with patch("os.path.exists", return_value=True), \
             patch("os.path.isdir", return_value=True):
            
            # When
            result = service.register_folder(data)
            
            # Then
            assert result.id == 1
            assert result.path == data.path
            mock_repo.create.assert_called_once()
            mock_file_watcher.add_folder.assert_called_once_with(1, data.path) # Verify watcher call

    def test_register_folder_path_not_exists(self, service, mock_repo):
        # Given
        data = FolderCreate(name="Test", path="/invalid/path")
        
        with patch("os.path.exists", return_value=False):
            # When/Then
            with pytest.raises(PathNotExistsError):
                service.register_folder(data)
                
    def test_register_folder_duplicate(self, service, mock_repo):
        # Given
        data = FolderCreate(name="Test", path="/exist/path")
        
        with patch("os.path.exists", return_value=True), \
             patch("os.path.isdir", return_value=True):
            mock_repo.exists_by_path.return_value = True
            
            # When/Then
            with pytest.raises(PathAlreadyRegisteredError):
                service.register_folder(data)

    def test_register_folder_path_not_directory(self, service, mock_repo):
        # Given
        data = FolderCreate(name="Test", path="/file/path")
        
        with patch("os.path.exists", return_value=True), \
             patch("os.path.isdir", return_value=False):
            
            # When/Then
            with pytest.raises(PathNotDirectoryError):
                service.register_folder(data)

    def test_get_folder_by_id(self, service, mock_repo):
        # Given
        mock_repo.find_by_id.return_value = Folder(id=1, name="Test", path="/test")
        
        # When
        result = service.get_folder_by_id(1)
        
        # Then
        assert result.id == 1
        mock_repo.find_by_id.assert_called_once_with(1)

    def test_list_folders(self, service, mock_repo):
        # Given
        mock_repo.find_all.return_value = [
            Folder(id=1, name="A", path="/a"),
            Folder(id=2, name="B", path="/b")
        ]
        
        # When
        results = service.list_folders()
        
        # Then
        assert len(results) == 2
        mock_repo.find_all.assert_called_once()

    def test_delete_folder(self, service, mock_repo, mock_file_watcher):
        # Given
        mock_repo.delete.return_value = True
        
        # When
        result = service.delete_folder(1)
        
        # Then
        assert result is True
        mock_repo.delete.assert_called_once_with(1)
        mock_file_watcher.remove_folder.assert_called_once_with(1) # Verify watcher removal
