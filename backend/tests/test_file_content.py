import os
import pytest
from fastapi import status
from pathlib import Path

def test_get_file_success(client, temp_dir):
    """
    Scenario: Valid file path in registered folder
    Given a registered folder containing a markdown file
    When GET /api/files is called with the file path
    Then it returns 200 and the file content
    """
    # 1. Register folder
    folder_path = temp_dir / "docs"
    folder_path.mkdir()
    
    # Create a markdown file
    md_file = folder_path / "test.md"
    md_file.write_text("# Hello\nWorld", encoding="utf-8")
    
    client.post("/api/folders", json={"name": "test-project", "path": str(folder_path)})
    
    # 2. Get file content
    response = client.get(f"/api/files?path={md_file}")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["content"] == "# Hello\nWorld"

def test_get_file_missing_path(client):
    """
    Scenario: Missing path parameter
    When GET /api/files is called without path
    Then it returns 400
    """
    response = client.get("/api/files")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "path is required" in response.json()["error"]

def test_get_file_not_found(client, temp_dir):
    """
    Scenario: File not found
    Given a registered folder
    When GET /api/files is called with a non-existent file path
    Then it returns 404
    """
    # Register folder
    folder_path = temp_dir / "docs"
    folder_path.mkdir()
    client.post("/api/folders", json={"name": "test-project", "path": str(folder_path)})
    
    # Request non-existent file
    not_exist = folder_path / "unknown.md"
    response = client.get(f"/api/files?path={not_exist}")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "file not found" in response.json()["error"]

def test_get_file_is_directory(client, temp_dir):
    """
    Scenario: Path is a directory
    Given a registered folder containing a sub-directory
    When GET /api/files is called with the directory path
    Then it returns 400
    """
    # Register folder
    folder_path = temp_dir / "docs"
    folder_path.mkdir()
    client.post("/api/folders", json={"name": "test-project", "path": str(folder_path)})
    
    # Request directory
    sub_dir = folder_path / "sub"
    sub_dir.mkdir()
    
    response = client.get(f"/api/files?path={sub_dir}")
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "path is not a file" in response.json()["error"]

def test_get_file_not_markdown(client, temp_dir):
    """
    Scenario: File is not markdown
    Given a registered folder containing a text file
    When GET /api/files is called with the text file path
    Then it returns 400
    """
    # Register folder
    folder_path = temp_dir / "docs"
    folder_path.mkdir()
    client.post("/api/folders", json={"name": "test-project", "path": str(folder_path)})
    
    # Create text file
    txt_file = folder_path / "note.txt"
    txt_file.write_text("content")
    
    response = client.get(f"/api/files?path={txt_file}")
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "only markdown files allowed" in response.json()["error"]

def test_path_traversal_blocked(client, temp_dir):
    """
    Scenario: Path traversal attempt
    When GET /api/files is called with ../
    Then it returns 403 or 400 depending on implementation details, 
    but spec says 403 or 400. Let's assume strict validation against registered folders.
    Wait, spec says 403 access denied for unregistered path.
    Implementation should resolve path and check if it starts with registered folder.
    """
    # Register folder
    folder_path = temp_dir / "docs"
    folder_path.mkdir()
    client.post("/api/folders", json={"name": "test-project", "path": str(folder_path)})
    
    # Try to access sensitive file via traversal
    # Note: realpath resolution happens in backend, so strictly speaking
    # sending "../" directly in query param might be normalized by client/server
    # but let's try to simulate checking a file outside registered root.
    
    # Let's target a file outside registerd folder
    outside_file = temp_dir / "outside.md"
    outside_file.write_text("secret")
    
    response = client.get(f"/api/files?path={outside_file}")
    
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "access denied" in response.json()["error"]

def test_unregistered_path_blocked(client, temp_dir):
    """
    Scenario: Path not in any registered folder
    When GET /api/files is called with a path not in DB
    Then it returns 403
    """
    # Create file but don't register its parent
    folder_path = temp_dir / "unregistered"
    folder_path.mkdir()
    md_file = folder_path / "test.md"
    md_file.write_text("content")
    
    response = client.get(f"/api/files?path={md_file}")
    
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "access denied" in response.json()["error"]

def test_empty_file(client, temp_dir):
    """
    Scenario: Empty markdown file
    When GET /api/files with empty file
    Then return 200 and empty content
    """
    folder_path = temp_dir / "docs"
    folder_path.mkdir()
    client.post("/api/folders", json={"name": "test-project", "path": str(folder_path)})
    
    empty_file = folder_path / "empty.md"
    empty_file.write_text("")
    
    response = client.get(f"/api/files?path={empty_file}")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["content"] == ""

def test_korean_filename(client, temp_dir):
    """
    Scenario: Korean filename
    When GET /api/files with korean filename
    Then return 200
    """
    folder_path = temp_dir / "docs"
    folder_path.mkdir()
    client.post("/api/folders", json={"name": "test-project", "path": str(folder_path)})
    
    kor_file = folder_path / "한글.md"
    kor_file.write_text("내용", encoding="utf-8")
    
    response = client.get(f"/api/files?path={kor_file}")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["content"] == "내용"

def test_symlink_blocked(client, temp_dir):
    """
    Scenario: Symlink file
    Given a symlink pointing to a file
    When GET /api/files is called
    Then it returns 403
    """
    folder_path = temp_dir / "docs"
    folder_path.mkdir()
    client.post("/api/folders", json={"name": "test-project", "path": str(folder_path)})
    
    # Create real file
    real_file = folder_path / "real.md"
    real_file.write_text("content")
    
    # Create symlink
    link_file = folder_path / "link.md"
    try:
        os.symlink(real_file, link_file)
    except OSError:
        pytest.skip("Symlink creation failed")
        
    response = client.get(f"/api/files?path={link_file}")
    
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "access denied" in response.json()["error"]
