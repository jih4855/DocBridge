"""
Pytest 공통 픽스처

테스트용 TestClient, 임시 디렉토리, DB 초기화 등
"""

import os
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """테스트용 임시 디렉토리 생성 (프로젝트 폴더용)"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # project 서브폴더 생성 (DB data 폴더와 분리)
        project_dir = Path(tmpdir) / "project"
        project_dir.mkdir()
        yield project_dir


@pytest.fixture
def temp_file(temp_dir: Path) -> Path:
    """테스트용 임시 파일 생성 (디렉토리가 아닌 파일)"""
    file_path = temp_dir / "test_file.txt"
    file_path.write_text("test content")
    return file_path


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """테스트용 FastAPI TestClient (독립 데이터 디렉토리)"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # 테스트용 데이터 디렉토리 설정 (별도 임시 폴더)
        os.environ["DATA_DIR"] = str(Path(tmpdir) / "data")
        os.environ["PROJECT_ROOT"] = tmpdir

        # 앱 임포트 (환경변수 설정 후)
        from main import app

        with TestClient(app) as test_client:
            yield test_client


@pytest.fixture
def db(client: TestClient) -> Generator["Session", None, None]:
    """직접 DB 접근을 위한 세션 (client 의존성으로 초기화 보장)"""
    from sqlalchemy.orm import Session
    from app.db.database import get_db

    # get_db()는 generator이므로 next()로 세션을, finally로 close를 처리해야 함
    gen = get_db()
    session = next(gen)
    yield session
    try:
        next(gen)
    except StopIteration:
        pass
