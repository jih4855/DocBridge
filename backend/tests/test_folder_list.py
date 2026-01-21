import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.folder import Folder


def test_list_folders_empty(client: TestClient, db: Session):
    """
    등록된 폴더가 없는 경우 -> 빈 배열 반환
    Response: { "folders": [] }
    """
    # Given: No folders in DB
    db.query(Folder).delete()
    db.commit()

    # When
    response = client.get("/api/folders")

    # Then
    assert response.status_code == 200
    data = response.json()
    assert "folders" in data
    assert len(data["folders"]) == 0
    assert data["folders"] == []


def test_list_folders_single(client: TestClient, db: Session):
    """
    1개 등록된 경우
    """
    # Given
    db.query(Folder).delete()
    folder = Folder(name="Project A", path="/tmp/project-a")
    db.add(folder)
    db.commit()

    # When
    response = client.get("/api/folders")

    # Then
    assert response.status_code == 200
    data = response.json()
    assert len(data["folders"]) == 1
    assert data["folders"][0]["name"] == "Project A"
    assert data["folders"][0]["path"] == "/tmp/project-a"


def test_list_folders_multiple_order(client: TestClient, db: Session):
    """
    다수 등록 및 정렬 (최신순) 확인
    """
    # Given
    db.query(Folder).delete()
    
    import time
    from datetime import datetime, timedelta

    # 1. First (Oldest) - Explicitly set time or just wait
    f1 = Folder(name="Old Project", path="/tmp/old", created_at=datetime.utcnow() - timedelta(minutes=1))
    db.add(f1)
    db.commit()
    
    # 2. Second (Newest)
    f2 = Folder(name="New Project", path="/tmp/new", created_at=datetime.utcnow())
    db.add(f2)
    db.commit()

    # When
    response = client.get("/api/folders")

    # Then
    assert response.status_code == 200
    data = response.json()
    folders = data["folders"]
    assert len(folders) == 2
    
    # Verify Order: Newest (f2) -> Oldest (f1)
    # Note: IDs usually increment, but we rely on created_at default. 
    # Since we committed separately or sequentially, created_at should differ slightly 
    # or ID will be higher for the second one. 
    # Spec says "created_at descending".
    
    assert folders[0]["name"] == "New Project"
    assert folders[1]["name"] == "Old Project"


def test_list_folders_with_invalid_path(client: TestClient, db: Session):
    """
    경로가 실제로 존재하지 않아도 목록에는 포함되어야 함
    """
    # Given
    db.query(Folder).delete()
    folder = Folder(name="Ghost Project", path="/non/existent/path")
    db.add(folder)
    db.commit()

    # When
    response = client.get("/api/folders")

    # Then
    assert response.status_code == 200
    data = response.json()
    assert len(data["folders"]) == 1
    assert data["folders"][0]["path"] == "/non/existent/path"


def test_list_folders_response_structure(client: TestClient, db: Session):
    """
    응답 구조 검증: id, name, path, created_at 포함
    """
    # Given
    db.query(Folder).delete()
    folder = Folder(name="Structure Test", path="/tmp/structure")
    db.add(folder)
    db.commit()

    # When
    response = client.get("/api/folders")

    # Then
    assert response.status_code == 200
    folder_data = response.json()["folders"][0]
    
    assert "id" in folder_data
    assert "name" in folder_data
    assert "path" in folder_data
    assert "created_at" in folder_data
    assert isinstance(folder_data["id"], int)
    assert isinstance(folder_data["name"], str)
