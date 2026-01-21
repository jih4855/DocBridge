"""
파일 내용 조회 API 라우터

Spec: spec/api/file-content.md
"""

import os
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.folder_service import FolderService

router = APIRouter()


@router.get(
    "",
    responses={
        200: {"description": "파일 내용 반환"},
        400: {"description": "잘못된 요청"},
        403: {"description": "접근 권한 없음"},
        404: {"description": "파일 없음"},
    }
)
async def get_file_content(path: str = None, db: Session = Depends(get_db)):
    """
    파일 내용 조회 API
    
    파일 절대 경로를 받아 해당 파일의 내용을 반환합니다.
    경로는 반드시 등록된 폴더 하위에 있어야 합니다.
    """
    # 1. 파라미터 체크
    if not path:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "path is required"}
        )

    # 2. 파일 확인 (존재 여부, 디렉토리 여부)
    if not os.path.exists(path):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "file not found"}
        )
        
    if os.path.isdir(path):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "path is not a file"}
        )

    # 3. 심볼릭 링크 체크 (보안 - Spec Edge Case)
    if os.path.islink(path):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"error": "access denied"}
        )

    # 4. 마크다운 확장자 체크 (Spec Req)
    if not path.endswith(".md"):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "only markdown files allowed"}
        )

    # 5. 등록된 폴더 하위 경로인지 확인 (보안)
    service = FolderService(db)
    registered_folders = service.list_folders()
    
    # 실제 경로로 정규화
    real_path = os.path.realpath(path)
    
    is_allowed = False
    for folder in registered_folders:
        # 폴더 경로 정규화
        folder_real = os.path.realpath(folder.path)
        
        # 파일 경로가 폴더 경로로 시작하는지 확인
        # os.sep을 붙여서 정확한 하위 경로인지 확인 (/tmp/foo vs /tmp/foobar)
        if real_path.startswith(folder_real + os.sep) or real_path == folder_real:
             # 폴더 루트 자체는 파일이 아니므로 startswith(folder + sep) 만으로 충분하지만
             # 혹시 모를 에러 방지를 위해 방어적으로 작성. 
             # 실제 파일은 하위에 있으므로 startswith가 맞음.
             is_allowed = True
             break
    
    if not is_allowed:
         return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"error": "access denied"}
        )
            
    # 6. 파일 읽기
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            
        return {"content": content}
    except Exception as e:
        # 예기치 못한 파일 읽기 에러
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": str(e)}
        )
