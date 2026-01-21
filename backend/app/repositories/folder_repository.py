"""
폴더 리포지토리

SQLAlchemy ORM 기반 데이터 접근
"""

from typing import Optional

from sqlalchemy.orm import Session

from app.models.folder import Folder


class FolderRepository:
    """폴더 데이터 접근 레이어"""

    def __init__(self, db: Session) -> None:
        self._db = db

    def create(self, name: str, path: str) -> Folder:
        """폴더 생성"""
        folder = Folder(name=name, path=path)
        self._db.add(folder)
        self._db.commit()
        self._db.refresh(folder)
        return folder

    def exists_by_path(self, path: str) -> bool:
        """경로로 폴더 존재 여부 확인"""
        return self._db.query(Folder).filter(Folder.path == path).first() is not None

    def find_by_id(self, folder_id: int) -> Optional[Folder]:
        """ID로 폴더 조회"""
        return self._db.query(Folder).filter(Folder.id == folder_id).first()

    def find_all(self) -> list[Folder]:
        """모든 폴더 조회 (최신순)"""
        return self._db.query(Folder).order_by(Folder.created_at.desc()).all()

    def delete(self, folder_id: int) -> bool:
        """폴더 삭제"""
        folder = self.find_by_id(folder_id)
        if folder:
            self._db.delete(folder)
            self._db.commit()
            return True
        return False
