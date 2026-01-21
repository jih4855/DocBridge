"""
폴더 관련 Pydantic 스키마

Spec: spec/api/folder-register.md
"""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class FolderCreate(BaseModel):
    """폴더 등록 요청 스키마"""

    name: str = Field(..., description="프로젝트 표시명")
    path: str = Field(..., description="폴더 절대 경로")

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("name is required")
        if len(v) > 100:
            raise ValueError("name must be 100 characters or less")
        return v.strip()

    @field_validator("path")
    @classmethod
    def path_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("path is required")
        # 끝 슬래시 정규화 (제거)
        return v.rstrip("/")


class FolderResponse(BaseModel):
    """폴더 응답 스키마"""

    id: int = Field(..., description="폴더 ID")
    name: str = Field(..., description="프로젝트 표시명")
    path: str = Field(..., description="폴더 절대 경로")
    created_at: datetime = Field(..., description="생성 시각")

    model_config = {"from_attributes": True}


class TreeNode(BaseModel):
    """트리 노드 스키마"""

    name: str = Field(..., description="파일/폴더 이름")
    type: str = Field(..., description="directory 또는 file")
    path: str | None = Field(default=None, description="파일 절대 경로 (file만)")
    children: list["TreeNode"] | None = Field(
        default=None, description="하위 항목 (directory만)"
    )


class FolderTreeResponse(BaseModel):
    """폴더 트리 응답 스키마"""

    id: int = Field(..., description="폴더 ID")
    name: str = Field(..., description="프로젝트 표시명")
    path: str = Field(..., description="폴더 절대 경로")
    tree: TreeNode = Field(..., description="트리 구조")


class FolderListResponse(BaseModel):
    """폴더 목록 응답 스키마"""

    folders: list[FolderResponse] = Field(..., description="폴더 목록")
