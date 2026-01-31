import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path

from app.services.folder_service import FolderService, PathNotExistsError, PathDeniedError
from app.repositories.folder_repository import FolderRepository
from app.services.file_watcher import FileWatcherService
from app.core.config import Settings
from app.models.folder import Folder

# Mock Settings
@pytest.fixture
def mock_settings():
    settings = Mock(spec=Settings)
    settings.DENY_LIST = {"/", "/etc", "/root", "/bin", "/usr"}
    return settings

@pytest.fixture
def mock_repo():
    return Mock(spec=FolderRepository)

@pytest.fixture
def mock_file_watcher():
    return Mock(spec=FileWatcherService)

@pytest.fixture
def folder_service(mock_repo, mock_file_watcher, mock_settings):
    # Update DI to match implementation
    service = FolderService(mock_repo, mock_file_watcher, mock_settings)
    return service

class TestSecurityPathValidation:
    def test_register_system_root_should_fail(self, folder_service):
        """시스템 루트 경로는 등록할 수 없어야 한다"""
        with pytest.raises(PathDeniedError):
            # Mock os.path to simulate existence
            with patch("os.path.exists", return_value=True):
                with patch("os.path.isdir", return_value=True):
                    folder_service.register_folder(Mock(path="/", name="Root"))

    def test_register_etc_should_fail(self, folder_service, mock_repo):
        """/etc 경로는 등록할 수 없어야 한다"""
        mock_repo.exists_by_path.return_value = False 
        
        # macOS resolves /etc to /private/etc. Mock resolve to return /etc for strict testing.
        with patch.object(Path, "resolve", return_value=Path("/etc")):
            with pytest.raises(PathDeniedError):
                 with patch("os.path.exists", return_value=True):
                    with patch("os.path.isdir", return_value=True):
                        folder_service.register_folder(Mock(path="/etc", name="Etc"))

    def test_register_normal_path_should_succeed(self, folder_service, mock_repo):
        """일반 경로는 정상 등록되어야 한다"""
        from datetime import datetime
        normal_path = "/Users/test/projects"
        mock_repo.exists_by_path.return_value = False
        mock_repo.create.return_value = Folder(
            id=1, 
            name="Project", 
            path=normal_path,
            created_at=datetime.now() # Fix: Pydantic validation
        )
        
        with patch("os.path.exists", return_value=True):
            with patch("os.path.isdir", return_value=True):
                folder_service.register_folder(Mock(path=normal_path, name="Project"))
        
        mock_repo.create.assert_called_once()


class TestStabilityStartupCheck:
    def test_initialize_watchers_should_skip_orphan_folders(self, folder_service, mock_repo, mock_file_watcher):
        """존재하지 않는 폴더는 watcher에 추가되지 않고 warning 로그를 남겨야 한다"""
        # Given
        existing_folder = Folder(id=1, path="/exist", name="Exist")
        orphan_folder = Folder(id=2, path="/lost", name="Lost")
        mock_repo.find_all.return_value = [existing_folder, orphan_folder]
        
        # When
        with patch("os.path.exists") as mock_exists:
            mock_exists.side_effect = lambda p: p == "/exist"
            with patch("app.services.folder_service.logger") as mock_logger:
                folder_service.initialize_watchers()
                
                # Then
                # 1. 존재하는 폴더만 watcher 추가
                mock_file_watcher.add_folder.assert_called_once_with(existing_folder.id, existing_folder.path)
                
                # 2. 고아 폴더는 warning 로그
                mock_logger.warning.assert_called_with(f"고아 폴더 감지됨: {orphan_folder.path}")
