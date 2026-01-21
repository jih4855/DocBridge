"""
폴더 서비스

비즈니스 로직 처리
Spec: spec/api/folder-register.md - 섹션 5
"""

import os

from sqlalchemy.orm import Session

from app.models.folder import Folder
from app.repositories.folder_repository import FolderRepository
from app.schemas.folder import FolderCreate, FolderResponse


class FolderService:
    """폴더 비즈니스 로직"""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._repository = FolderRepository(db)

    def register_folder(self, data: FolderCreate) -> FolderResponse:
        """
        폴더 등록

        비즈니스 로직:
        1. 경로 존재 확인
        2. 디렉토리 여부 확인
        3. 중복 경로 확인
        4. DB 저장
        """
        path = data.path  # 이미 스키마에서 정규화됨

        # 경로 존재 확인
        if not os.path.exists(path):
            raise PathNotExistsError()

        # 디렉토리 여부 확인
        if not os.path.isdir(path):
            raise PathNotDirectoryError()

        # 중복 경로 확인
        if self._repository.exists_by_path(path):
            raise PathAlreadyRegisteredError()

        # DB 저장
        folder: Folder = self._repository.create(name=data.name, path=path)

        return FolderResponse(
            id=folder.id,
            name=folder.name,
            path=folder.path,
            created_at=folder.created_at,
        )

    def get_folder_by_id(self, folder_id: int) -> Folder | None:
        """ID로 폴더 조회"""
        return self._repository.find_by_id(folder_id)

    def list_folders(self) -> list[Folder]:
        """전체 폴더 목록 조회"""
        return self._repository.find_all()

    def delete_folder(self, folder_id: int) -> bool:
        """폴더 삭제"""
        return self._repository.delete(folder_id)


class PathNotExistsError(Exception):
    """경로가 존재하지 않음"""
    pass


class PathNotDirectoryError(Exception):
    """경로가 디렉토리가 아님"""
    pass


class PathAlreadyRegisteredError(Exception):
    """경로가 이미 등록됨"""
    pass
