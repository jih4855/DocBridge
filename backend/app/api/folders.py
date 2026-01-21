"""
폴더 API 라우터

Spec: spec/api/folder-register.md
"""

from fastapi import APIRouter, HTTPException, Request, status, Depends
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.folder import FolderCreate, FolderListResponse, FolderResponse
from app.services.folder_service import (
    FolderService,
    PathAlreadyRegisteredError,
    PathNotDirectoryError,
    PathNotExistsError,
)
from app.repositories.folder_repository import FolderRepository
from app.services.file_watcher import file_watcher

router = APIRouter()


@router.post(
    "",
    response_model=FolderResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "유효성 검사 실패"},
        409: {"description": "중복 경로"},
    },
)
async def register_folder(folder_data: FolderCreate, db: Session = Depends(get_db)) -> FolderResponse:
    """폴더 등록 API"""
    # Note: JSON 파싱 및 Pydantic 유효성 검사는 FastAPI/Starlette가 자동 처리하며,
    # global_exception_handler에서 표준 에러 포맷으로 반환됩니다.

    # DB 세션 및 서비스 호출
    try:
        repository = FolderRepository(db)
        service = FolderService(repository)
        result = service.register_folder(folder_data)
        
        # watcher 추가
        file_watcher.add_folder(result.id, result.path)
        
        return result
    except PathNotExistsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="path does not exist"
        )
    except PathNotDirectoryError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="path is not a directory"
        )
    except PathAlreadyRegisteredError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="path already registered"
        )


@router.get(
    "",
    response_model=FolderListResponse,
    responses={
        200: {"description": "폴더 목록 반환"},
    },
)
async def list_folders(db: Session = Depends(get_db)):
    """폴더 목록 조회 API"""
    repository = FolderRepository(db)
    service = FolderService(repository)
    folders = service.list_folders()
    return FolderListResponse(
        folders=[
            FolderResponse(
                id=f.id,
                name=f.name,
                path=f.path,
                created_at=f.created_at,
            )
            for f in folders
        ]
    )


@router.get(
    "/{folder_id}/tree",
    response_model=None,
    responses={
        200: {"description": "트리 구조 반환"},
        404: {"description": "폴더 없음"},
    },
)
async def get_folder_tree(folder_id: int, md_only: bool = True, db: Session = Depends(get_db)):
    """
    폴더 트리 조회 API

    Spec: spec/api/folder-tree.md
    """
    import os
    from app.utils.tree_builder import build_tree
    from app.schemas.folder import FolderTreeResponse

    repository = FolderRepository(db)
    service = FolderService(repository)

    # 폴더 조회
    folder = service.get_folder_by_id(folder_id)
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="folder not found"
        )

    # 경로 존재 확인
    if not os.path.exists(folder.path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="folder path does not exist"
        )

    # 트리 구조 생성
    tree = build_tree(folder.path, md_only)

    return FolderTreeResponse(
        id=folder.id,
        name=folder.name,
        path=folder.path,
        tree=tree,
    )


@router.delete(
    "/{folder_id}",
    responses={
        200: {"description": "삭제 성공"},
        400: {"description": "잘못된 ID"},
        404: {"description": "폴더 없음"},
    },
)
async def delete_folder(folder_id: int, db: Session = Depends(get_db)):
    """
    폴더 삭제 API
    
    Spec: spec/api/folder-delete.md
    """
    if folder_id < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid folder id"
        )

    repository = FolderRepository(db)
    service = FolderService(repository)
    
    # 존재 확인
    folder = service.get_folder_by_id(folder_id)
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="folder not found"
        )
        
    # watcher 제거 (삭제 전)
    file_watcher.remove_folder(folder_id)
    
    # 삭제
    service.delete_folder(folder_id)
    
    return {
        "success": True,
        "deleted_id": folder_id
    }
