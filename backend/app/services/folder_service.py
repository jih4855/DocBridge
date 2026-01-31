"""
폴더 서비스

비즈니스 로직 처리
Spec: spec/api/folder-register.md - 섹션 5
"""

import os

from sqlalchemy.orm import Session

from pathlib import Path
from loguru import logger
from app.services.file_watcher import FileWatcherService
from app.core.config import Settings
from app.models.folder import Folder
from app.repositories.folder_repository import FolderRepository
from app.schemas.folder import FolderCreate, FolderResponse


class FolderService:
    """폴더 비즈니스 로직"""

    def __init__(
        self, 
        repository: FolderRepository, 
        file_watcher: FileWatcherService,
        settings: Settings
    ) -> None:
        self._repository = repository
        self._file_watcher = file_watcher
        self._settings = settings

    def register_folder(self, data: FolderCreate) -> FolderResponse:
        """
        폴더 등록

        비즈니스 로직:
        1. 경로 정규화 및 보안 검사 (Deny List)
        2. 경로 존재 확인
        3. 디렉토리 여부 확인
        4. 중복 경로 확인
        5. DB 저장
        6. Watcher 추가
        """
        # 1. 경로 정규화 및 보안 검사
        path = data.path
        target_path = Path(path).resolve()
        
        # 시스템 루트 판별 (Windows: C:\, Unix: /)
        is_root = target_path == target_path.anchor
        
        if str(target_path) in self._settings.DENY_LIST or is_root:
            raise PathDeniedError()

        # 2. 경로 존재 확인
        if not os.path.exists(path):
            raise PathNotExistsError()

        # 3. 디렉토리 여부 확인
        if not os.path.isdir(path):
            raise PathNotDirectoryError()

        # 4. 중복 경로 확인
        if self._repository.exists_by_path(path):
            raise PathAlreadyRegisteredError()

        # 5. DB 저장
        folder: Folder = self._repository.create(name=data.name, path=path)

        # 6. Watcher 추가
        self._file_watcher.add_folder(folder.id, folder.path)

        return FolderResponse(
            id=folder.id,
            name=folder.name,
            path=folder.path,
            created_at=folder.created_at,
        )

    def initialize_watchers(self) -> None:
        """
        서버 시작 시 Watcher 초기화 (Self-Healing)
        
        - DB에 있는 모든 폴더를 조회하여 Watcher에 등록
        - 실제 존재하지 않는 폴더는 경고 로그 출력 후 스킵
        """
        folders = self._repository.find_all()
        logger.info(f"기존 폴더 {len(folders)}개 감시 초기화 시작")
        
        for folder in folders:
            if not os.path.exists(folder.path):
                logger.warning(f"고아 폴더 감지됨: {folder.path}")
                continue
                
            self._file_watcher.add_folder(folder.id, folder.path)

    def get_folder_by_id(self, folder_id: int) -> Folder | None:
        """ID로 폴더 조회"""
        return self._repository.find_by_id(folder_id)

    def list_folders(self) -> list[Folder]:
        """전체 폴더 목록 조회"""
        return self._repository.find_all()

    def delete_folder(self, folder_id: int) -> bool:
        """폴더 삭제"""
        result = self._repository.delete(folder_id)
        if result:
            self._file_watcher.remove_folder(folder_id)
        return result


class PathNotExistsError(Exception):
    """경로가 존재하지 않음"""
    pass


class PathNotDirectoryError(Exception):
    """경로가 디렉토리가 아님"""
    pass


class PathAlreadyRegisteredError(Exception):
    """경로가 이미 등록됨"""
    pass


class PathDeniedError(Exception):
    """시스템 보호 경로 접근 차단"""
    pass
