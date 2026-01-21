"""
폴더 등록 API 테스트

Spec: spec/api/folder-register.md
TDD Red 단계 - 실패하는 테스트 먼저 작성
"""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient


class TestFolderRegisterSuccess:
    """폴더 등록 성공 케이스"""

    def test_register_folder_success(
        self, client: TestClient, temp_dir: Path
    ) -> None:
        """정상적인 폴더 등록 시 201 반환"""
        # Given
        request_body = {
            "name": "My Project",
            "path": str(temp_dir),
        }

        # When
        response = client.post("/api/folders", json=request_body)

        # Then
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "My Project"
        assert data["path"] == str(temp_dir)
        assert "created_at" in data

    def test_register_folder_with_special_chars_in_name(
        self, client: TestClient, temp_dir: Path
    ) -> None:
        """name에 특수문자/이모지 포함 허용"""
        # Given
        request_body = {
            "name": "프로젝트 🚀 #1",
            "path": str(temp_dir),
        }

        # When
        response = client.post("/api/folders", json=request_body)

        # Then
        assert response.status_code == 201
        assert response.json()["name"] == "프로젝트 🚀 #1"

    def test_register_folder_normalizes_trailing_slash(
        self, client: TestClient, temp_dir: Path
    ) -> None:
        """path 끝 슬래시 정규화 (제거)"""
        # Given
        path_with_slash = str(temp_dir) + "/"
        request_body = {
            "name": "Test Project",
            "path": path_with_slash,
        }

        # When
        response = client.post("/api/folders", json=request_body)

        # Then
        assert response.status_code == 201
        # 저장된 path에 끝 슬래시 없어야 함
        assert response.json()["path"] == str(temp_dir)


class TestFolderRegisterValidation:
    """폴더 등록 유효성 검사 케이스"""

    def test_register_folder_missing_name(
        self, client: TestClient, temp_dir: Path
    ) -> None:
        """name 누락 시 400 반환"""
        # Given
        request_body = {
            "path": str(temp_dir),
        }

        # When
        response = client.post("/api/folders", json=request_body)

        # Then
        assert response.status_code == 400
        assert response.json()["error"] == "name is required"

    def test_register_folder_empty_name(
        self, client: TestClient, temp_dir: Path
    ) -> None:
        """name 빈 문자열 시 400 반환"""
        # Given
        request_body = {
            "name": "",
            "path": str(temp_dir),
        }

        # When
        response = client.post("/api/folders", json=request_body)

        # Then
        assert response.status_code == 400
        assert response.json()["error"] == "name is required"

    def test_register_folder_missing_path(
        self, client: TestClient
    ) -> None:
        """path 누락 시 400 반환"""
        # Given
        request_body = {
            "name": "My Project",
        }

        # When
        response = client.post("/api/folders", json=request_body)

        # Then
        assert response.status_code == 400
        assert response.json()["error"] == "path is required"

    def test_register_folder_empty_path(
        self, client: TestClient
    ) -> None:
        """path 빈 문자열 시 400 반환"""
        # Given
        request_body = {
            "name": "My Project",
            "path": "",
        }

        # When
        response = client.post("/api/folders", json=request_body)

        # Then
        assert response.status_code == 400
        assert response.json()["error"] == "path is required"

    def test_register_folder_name_too_long(
        self, client: TestClient, temp_dir: Path
    ) -> None:
        """name 100자 초과 시 400 반환"""
        # Given
        long_name = "a" * 101
        request_body = {
            "name": long_name,
            "path": str(temp_dir),
        }

        # When
        response = client.post("/api/folders", json=request_body)

        # Then
        assert response.status_code == 400


class TestFolderRegisterPathValidation:
    """폴더 등록 경로 검증 케이스"""

    def test_register_folder_path_not_exists(
        self, client: TestClient
    ) -> None:
        """존재하지 않는 경로 시 400 반환"""
        # Given
        request_body = {
            "name": "My Project",
            "path": "/non/existent/path",
        }

        # When
        response = client.post("/api/folders", json=request_body)

        # Then
        assert response.status_code == 400
        assert response.json()["error"] == "path does not exist"

    def test_register_folder_path_not_directory(
        self, client: TestClient, temp_file: Path
    ) -> None:
        """디렉토리가 아닌 경로 시 400 반환"""
        # Given
        request_body = {
            "name": "My Project",
            "path": str(temp_file),
        }

        # When
        response = client.post("/api/folders", json=request_body)

        # Then
        assert response.status_code == 400
        assert response.json()["error"] == "path is not a directory"


class TestFolderRegisterDuplicate:
    """폴더 등록 중복 검사 케이스"""

    def test_register_folder_duplicate_path(
        self, client: TestClient, temp_dir: Path
    ) -> None:
        """이미 등록된 경로 시 409 반환"""
        # Given - 먼저 등록
        request_body = {
            "name": "First Project",
            "path": str(temp_dir),
        }
        client.post("/api/folders", json=request_body)

        # When - 같은 경로로 다시 등록 시도
        duplicate_body = {
            "name": "Second Project",
            "path": str(temp_dir),
        }
        response = client.post("/api/folders", json=duplicate_body)

        # Then
        assert response.status_code == 409
        assert response.json()["error"] == "path already registered"

    def test_register_folder_same_path_with_trailing_slash(
        self, client: TestClient, temp_dir: Path
    ) -> None:
        """끝 슬래시 유무만 다른 같은 경로도 중복 처리"""
        # Given - 먼저 등록 (슬래시 없이)
        request_body = {
            "name": "First Project",
            "path": str(temp_dir),
        }
        client.post("/api/folders", json=request_body)

        # When - 같은 경로 + 끝 슬래시로 다시 등록 시도
        duplicate_body = {
            "name": "Second Project",
            "path": str(temp_dir) + "/",
        }
        response = client.post("/api/folders", json=duplicate_body)

        # Then
        assert response.status_code == 409
        assert response.json()["error"] == "path already registered"

    def test_register_folder_same_name_allowed(
        self, client: TestClient, temp_dir: Path
    ) -> None:
        """같은 name은 허용 (path만 unique)"""
        # Given - 첫 번째 등록
        subdir1 = temp_dir / "project1"
        subdir1.mkdir()
        request_body = {
            "name": "Same Name",
            "path": str(subdir1),
        }
        client.post("/api/folders", json=request_body)

        # When - 같은 이름, 다른 경로로 등록
        subdir2 = temp_dir / "project2"
        subdir2.mkdir()
        same_name_body = {
            "name": "Same Name",
            "path": str(subdir2),
        }
        response = client.post("/api/folders", json=same_name_body)

        # Then
        assert response.status_code == 201
