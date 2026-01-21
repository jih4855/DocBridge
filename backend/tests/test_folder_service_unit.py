import pytest
from unittest.mock import Mock, MagicMock
import os
from app.services.folder_service import FolderService, PathNotExistsError, PathNotDirectoryError, PathAlreadyRegisteredError
from app.repositories.folder_repository import FolderRepository
from app.schemas.folder import FolderCreate

class TestFolderServiceUnit:
    """
    FolderService Unit Tests with Mock Repository
    True Unit Test: No DB dependency
    """

    @pytest.fixture
    def mock_repo(self):
        return Mock(spec=FolderRepository)

    @pytest.fixture
    def service(self, mock_repo):
        return FolderService(mock_repo)

    def test_register_folder_success(self, service, mock_repo):
        # Given
        data = FolderCreate(name="Unit Test", path="/tmp/unit")
        
        # Mock behaviors
        import os
        # We need to mock os.path.exists and os.path.isdir since Service uses them directly
        # or we should refactor Service to not use os directly? 
        # For now, let's mock os in the test using patch
        
        with pytest.MonkeyPatch.context() as m:
            m.setattr(os.path, "exists", lambda p: True)
            m.setattr(os.path, "isdir", lambda p: True)
            
            mock_repo.exists_by_path.return_value = False
            
            mock_folder = Mock()
            mock_folder.id = 1
            mock_folder.name = "Unit Test"
            mock_folder.path = "/tmp/unit"
            mock_folder.created_at = "2024-01-01"
            
            mock_repo.create.return_value = mock_folder

            # When
            result = service.register_folder(data)

            # Then
            assert result.id == 1
            assert result.name == "Unit Test"
            mock_repo.create.assert_called_once_with(name="Unit Test", path="/tmp/unit")

    def test_register_folder_path_not_exists(self, service, mock_repo):
        # Given
        data = FolderCreate(name="Unit Test", path="/tmp/fake")
        
        with pytest.MonkeyPatch.context() as m:
            m.setattr(os.path, "exists", lambda p: False)
            
            # When/Then
            with pytest.raises(PathNotExistsError):
                service.register_folder(data)
                
            mock_repo.create.assert_not_called()

    def test_register_folder_duplicate(self, service, mock_repo):
        # Given
        data = FolderCreate(name="Unit Test", path="/tmp/unit")
        
        with pytest.MonkeyPatch.context() as m:
            m.setattr(os.path, "exists", lambda p: True)
            m.setattr(os.path, "isdir", lambda p: True)
            mock_repo.exists_by_path.return_value = True # Duplicate

            # When/Then
            with pytest.raises(PathAlreadyRegisteredError):
                service.register_folder(data)
                
            mock_repo.create.assert_not_called()

    def test_register_folder_path_not_directory(self, service, mock_repo):
        # Given
        data = FolderCreate(name="Unit Test", path="/tmp/file")
        
        with pytest.MonkeyPatch.context() as m:
            m.setattr(os.path, "exists", lambda p: True)
            m.setattr(os.path, "isdir", lambda p: False) # Not a directory
            
            # When/Then
            with pytest.raises(PathNotDirectoryError):
                service.register_folder(data)
                
            mock_repo.create.assert_not_called()

    def test_get_folder_by_id(self, service, mock_repo):
        # Given
        mock_folder = Mock(id=1, name="Test", path="/tmp")
        mock_repo.find_by_id.return_value = mock_folder

        # When
        result = service.get_folder_by_id(1)
        
        # Then
        assert result == mock_folder
        mock_repo.find_by_id.assert_called_once_with(1)

    def test_list_folders(self, service, mock_repo):
        # Given
        mock_list = [Mock(id=1), Mock(id=2)]
        mock_repo.find_all.return_value = mock_list

        # When
        result = service.list_folders()
        
        # Then
        assert result == mock_list
        assert len(result) == 2
        mock_repo.find_all.assert_called_once()

    def test_delete_folder(self, service, mock_repo):
        # Given
        mock_repo.delete.return_value = True

        # When
        result = service.delete_folder(1)
        
        # Then
        assert result is True
        mock_repo.delete.assert_called_once_with(1)
