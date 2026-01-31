import pytest
from logging import getLogger
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.folder import Folder

logger = getLogger(__name__)

class TestFolderDeleteSuccess:
    """폴더 삭제 성공 케이스"""

    def test_delete_folder_success(self, client: TestClient, db: Session, temp_dir: Path):
        """정상적인 폴더 삭제 시 200 반환"""
        # Given: Create a folder first
        db.query(Folder).delete()
        folder = Folder(name="To Delete", path=str(temp_dir))
        db.add(folder)
        db.commit()
        db.refresh(folder) # Get ID
        folder_id = folder.id

        # When
        response = client.delete(f"/api/folders/{folder_id}")

        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["deleted_id"] == folder_id

        # Verify DB deletion
        deleted = db.query(Folder).filter(Folder.id == folder_id).first()
        assert deleted is None


class TestFolderDeleteValidation:
    """폴더 삭제 유효성 검사"""

    def test_delete_folder_not_found(self, client: TestClient, db: Session):
        """존재하지 않는 폴더 ID 삭제 시 404"""
        # Given
        db.query(Folder).delete()
        
        # When
        response = client.delete("/api/folders/999")

        # Then
        assert response.status_code == 404
        assert response.json()["error"] == "folder not found"

    def test_delete_folder_invalid_id(self, client: TestClient):
        """숫자가 아닌 ID 입력 시 400"""
        
        # When
        response = client.delete("/api/folders/abc")
        
        # Then
        # 글로벌 핸들러에서 400 반환
        assert response.status_code == 400

    def test_delete_folder_negative_id(self, client: TestClient, db: Session):
        """음수 ID 입력 시 400"""
        # This can be handled by validator in code.
        # When
        response = client.delete("/api/folders/-1")

        # Then
        assert response.status_code == 400
        assert response.json()["error"] == "invalid folder id"


class TestFolderDeleteEdgeCases:
    """엣지 케이스"""

    def test_delete_folder_twice(self, client: TestClient, db: Session, temp_dir: Path):
        """동일 폴더 2회 삭제 시도 -> 첫 번째 200, 두 번째 404"""
        # Given
        db.query(Folder).delete()
        folder = Folder(name="Twice", path=str(temp_dir))
        db.add(folder)
        db.commit()
        folder_id = folder.id

        # When 1
        res1 = client.delete(f"/api/folders/{folder_id}")
        assert res1.status_code == 200

        # When 2
        res2 = client.delete(f"/api/folders/{folder_id}")
        assert res2.status_code == 404

    def test_delete_folder_files_remain(self, client: TestClient, db: Session, temp_dir: Path):
        """삭제 후 실제 파일은 그대로 존재해야 함"""
        # Given
        db.query(Folder).delete()
        folder = Folder(name="Preserve", path=str(temp_dir))
        db.add(folder)
        db.commit()
        folder_id = folder.id
        
        # Verify file exists
        test_file = temp_dir / "remain.txt"
        test_file.write_text("should remain")
        assert test_file.exists()

        # When
        client.delete(f"/api/folders/{folder_id}")

        # Then
        assert test_file.exists()  # File should still be there

    def test_delete_folder_not_in_list(self, client: TestClient, db: Session, temp_dir: Path):
        """삭제 후 목록에서 제거됨"""
        # Given
        db.query(Folder).delete()
        folder = Folder(name="List Check", path=str(temp_dir))
        db.add(folder)
        db.commit()
        
        # Check list before
        res_before = client.get("/api/folders")
        assert len(res_before.json()["folders"]) == 1

        # When
        client.delete(f"/api/folders/{folder.id}")

        # Then
        res_after = client.get("/api/folders")
        assert len(res_after.json()["folders"]) == 0
