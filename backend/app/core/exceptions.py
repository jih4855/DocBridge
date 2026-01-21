"""
전역 예외 처리 핸들러

Spec: spec/report/exception_handling_audit.md
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from loguru import logger

async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    예상치 못한 서버 에러 (500) 처리
    """
    logger.exception(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": "INTERNAL_SERVER_ERROR",
            "message": "서버 내부 오류가 발생했습니다.",
            "details": str(exc)  # 배포 환경에서는 보안을 위해 제거 권장
        },
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    HTTPException 처리 (4xx, 5xx)
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": "HTTP_ERROR",
            "message": str(exc.detail),
            "details": None
        },
    )

from fastapi.encoders import jsonable_encoder

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    유효성 검사 실패 (422) 처리
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": "VALIDATION_ERROR",
            "message": "입력값이 유효하지 않습니다.",
            "details": jsonable_encoder(exc.errors())
        },
    )
