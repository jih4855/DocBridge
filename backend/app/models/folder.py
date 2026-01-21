"""
Folder ORM 모델

SQLAlchemy 테이블 정의
"""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Folder(Base):
    """폴더 테이블 모델"""

    __tablename__ = "folders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    path: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<Folder(id={self.id}, name='{self.name}', path='{self.path}')>"
