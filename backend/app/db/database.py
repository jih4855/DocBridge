"""
SQLAlchemy 데이터베이스 설정

ORM 엔진, 세션, Base 클래스 정의
"""

from pathlib import Path
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    """SQLAlchemy 모델 베이스 클래스"""
    pass


def get_db_path() -> Path:
    """DB 파일 경로 반환"""
    data_dir = Path(settings.DATA_DIR)
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "docbridge.db"


def get_engine():
    """SQLAlchemy 엔진 생성"""
    db_path = get_db_path()
    return create_engine(
        f"sqlite:///{db_path}",
        echo=False,
        connect_args={"check_same_thread": False},
    )


# 전역 엔진 및 세션 팩토리
engine = None
SessionLocal = None


def init_db() -> None:
    """데이터베이스 초기화 - 테이블 생성"""
    global engine, SessionLocal

    engine = get_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # 모델 임포트 (테이블 생성 전에 필요)
    from app.models import folder  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """DB 세션 반환 (의존성 주입용)"""
    if SessionLocal is None:
        init_db()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
