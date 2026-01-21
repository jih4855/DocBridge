"""
폴더 트리 조회 API 테스트

Spec: spec/api/folder-tree.md
TDD Red 단계 - 실패하는 테스트 먼저 작성
"""

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


class TestFolderTreeAPI:
    """Integration Tests - API 레벨"""

    def test_get_tree_success(
        self, client: TestClient, temp_dir: Path
    ) -> None:
        """GET /api/folders/{id}/tree - 정상 조회 시 200 반환"""
        # Given - 폴더 등록
        register_response = client.post(
            "/api/folders",
            json={"name": "TestProject", "path": str(temp_dir)},
        )
        folder_id = register_response.json()["id"]

        # 하위 구조 생성
        (temp_dir / "api").mkdir()
        (temp_dir / "api" / "auth.md").write_text("# Auth")
        (temp_dir / "README.md").write_text("# README")

        # When
        response = client.get(f"/api/folders/{folder_id}/tree")

        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == folder_id
        assert data["name"] == "TestProject"
        assert data["path"] == str(temp_dir)
        assert "tree" in data
        assert data["tree"]["type"] == "directory"

    def test_get_tree_not_found(self, client: TestClient) -> None:
        """GET /api/folders/999/tree - 존재하지 않는 폴더 시 404"""
        # When
        response = client.get("/api/folders/999/tree")

        # Then
        assert response.status_code == 404
        assert response.json()["error"] == "folder not found"

    def test_get_tree_path_deleted(
        self, client: TestClient, temp_dir: Path
    ) -> None:
        """폴더 경로가 삭제된 경우 404 반환"""
        # Given - 폴더 등록
        sub_dir = temp_dir / "to_delete"
        sub_dir.mkdir()
        register_response = client.post(
            "/api/folders",
            json={"name": "ToDelete", "path": str(sub_dir)},
        )
        folder_id = register_response.json()["id"]

        # 경로 삭제
        sub_dir.rmdir()

        # When
        response = client.get(f"/api/folders/{folder_id}/tree")

        # Then
        assert response.status_code == 404
        assert response.json()["error"] == "folder path does not exist"

    def test_get_tree_invalid_id(self, client: TestClient) -> None:
        """잘못된 ID 형식 시 422 또는 400 반환"""
        # When
        response = client.get("/api/folders/abc/tree")

        # Then
        # FastAPI는 기본적으로 path parameter 타입 불일치 시 422 반환하지만,
        # 글로벌 핸들러를 통해 400으로 통일함 (Spec 준수)
        assert response.status_code == 400


class TestTreeBuilder:
    """Unit Tests - 트리 빌더 로직"""

    def test_build_tree_empty_folder(
        self, client: TestClient, temp_dir: Path
    ) -> None:
        """빈 폴더 시 children: [] 반환"""
        # Given
        register_response = client.post(
            "/api/folders",
            json={"name": "Empty", "path": str(temp_dir)},
        )
        folder_id = register_response.json()["id"]

        # When
        response = client.get(f"/api/folders/{folder_id}/tree")

        # Then
        assert response.status_code == 200
        assert response.json()["tree"]["children"] == []

    def test_build_tree_files_only(
        self, client: TestClient, temp_dir: Path
    ) -> None:
        """파일만 있는 폴더"""
        # Given
        (temp_dir / "file1.md").write_text("# File 1")
        (temp_dir / "file2.md").write_text("# File 2")
        register_response = client.post(
            "/api/folders",
            json={"name": "FilesOnly", "path": str(temp_dir)},
        )
        folder_id = register_response.json()["id"]

        # When
        response = client.get(f"/api/folders/{folder_id}/tree")

        # Then
        assert response.status_code == 200
        children = response.json()["tree"]["children"]
        assert len(children) == 2
        assert all(c["type"] == "file" for c in children)

    def test_build_tree_nested(
        self, client: TestClient, temp_dir: Path
    ) -> None:
        """중첩 폴더 구조"""
        # Given
        (temp_dir / "level1").mkdir()
        (temp_dir / "level1" / "level2").mkdir()
        (temp_dir / "level1" / "level2" / "deep.md").write_text("# Deep")
        register_response = client.post(
            "/api/folders",
            json={"name": "Nested", "path": str(temp_dir)},
        )
        folder_id = register_response.json()["id"]

        # When
        response = client.get(f"/api/folders/{folder_id}/tree")

        # Then
        assert response.status_code == 200
        tree = response.json()["tree"]
        level1 = tree["children"][0]
        assert level1["name"] == "level1"
        assert level1["type"] == "directory"
        level2 = level1["children"][0]
        assert level2["name"] == "level2"
        deep_file = level2["children"][0]
        assert deep_file["name"] == "deep.md"

    def test_build_tree_sorting(
        self, client: TestClient, temp_dir: Path
    ) -> None:
        """정렬: 폴더 먼저, 파일 나중, 알파벳순"""
        # Given
        (temp_dir / "zebra.md").write_text("# Zebra")
        (temp_dir / "alpha.md").write_text("# Alpha")
        (temp_dir / "beta").mkdir()
        (temp_dir / "gamma").mkdir()
        register_response = client.post(
            "/api/folders",
            json={"name": "Sorted", "path": str(temp_dir)},
        )
        folder_id = register_response.json()["id"]

        # When
        response = client.get(f"/api/folders/{folder_id}/tree")

        # Then
        assert response.status_code == 200
        children = response.json()["tree"]["children"]
        # 폴더가 먼저 (beta, gamma), 파일이 나중 (alpha, zebra)
        names = [c["name"] for c in children]
        assert names == ["beta", "gamma", "alpha.md", "zebra.md"]

    def test_build_tree_md_only(
        self, client: TestClient, temp_dir: Path
    ) -> None:
        """md_only=true 시 .md 파일만 포함"""
        # Given
        (temp_dir / "readme.md").write_text("# README")
        (temp_dir / "script.py").write_text("print('hello')")
        (temp_dir / "data.json").write_text("{}")
        register_response = client.post(
            "/api/folders",
            json={"name": "MdOnly", "path": str(temp_dir)},
        )
        folder_id = register_response.json()["id"]

        # When
        response = client.get(f"/api/folders/{folder_id}/tree?md_only=true")

        # Then
        assert response.status_code == 200
        children = response.json()["tree"]["children"]
        assert len(children) == 1
        assert children[0]["name"] == "readme.md"


class TestTreeEdgeCases:
    """Edge Case Tests"""

    def test_tree_hidden_files_excluded(
        self, client: TestClient, temp_dir: Path
    ) -> None:
        """숨김 파일 제외"""
        # Given
        (temp_dir / ".hidden").write_text("hidden")
        (temp_dir / ".git").mkdir()
        (temp_dir / "visible.md").write_text("# Visible")
        register_response = client.post(
            "/api/folders",
            json={"name": "Hidden", "path": str(temp_dir)},
        )
        folder_id = register_response.json()["id"]

        # When
        response = client.get(f"/api/folders/{folder_id}/tree")

        # Then
        assert response.status_code == 200
        children = response.json()["tree"]["children"]
        names = [c["name"] for c in children]
        assert ".hidden" not in names
        assert ".git" not in names
        assert "visible.md" in names

    def test_tree_korean_filename(
        self, client: TestClient, temp_dir: Path
    ) -> None:
        """한글 파일명 정상 처리"""
        # Given
        (temp_dir / "한글파일.md").write_text("# 한글")
        register_response = client.post(
            "/api/folders",
            json={"name": "Korean", "path": str(temp_dir)},
        )
        folder_id = register_response.json()["id"]

        # When
        response = client.get(f"/api/folders/{folder_id}/tree")

        # Then
        assert response.status_code == 200
        children = response.json()["tree"]["children"]
        assert children[0]["name"] == "한글파일.md"

    def test_tree_special_chars(
        self, client: TestClient, temp_dir: Path
    ) -> None:
        """특수문자 파일명 정상 처리"""
        # Given
        (temp_dir / "file-name_v2 (1).md").write_text("# Special")
        register_response = client.post(
            "/api/folders",
            json={"name": "Special", "path": str(temp_dir)},
        )
        folder_id = register_response.json()["id"]

        # When
        response = client.get(f"/api/folders/{folder_id}/tree")

        # Then
        assert response.status_code == 200
        children = response.json()["tree"]["children"]
        assert children[0]["name"] == "file-name_v2 (1).md"

    def test_tree_symlink_ignored(
        self, client: TestClient, temp_dir: Path
    ) -> None:
        """심볼릭 링크 무시"""
        # Given
        real_file = temp_dir / "real.md"
        real_file.write_text("# Real")
        symlink = temp_dir / "link.md"
        try:
            symlink.symlink_to(real_file)
        except OSError:
            pytest.skip("Symlink creation not supported")

        register_response = client.post(
            "/api/folders",
            json={"name": "Symlink", "path": str(temp_dir)},
        )
        folder_id = register_response.json()["id"]

        # When
        response = client.get(f"/api/folders/{folder_id}/tree")

        # Then
        assert response.status_code == 200
        children = response.json()["tree"]["children"]
        names = [c["name"] for c in children]
        assert "real.md" in names
        assert "link.md" not in names  # 심볼릭 링크 제외
