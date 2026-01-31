"""
전역 예외 처리 핸들러

Spec: spec/report/exception_handling_audit.md
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from loguru import logger
from app.core.config import settings

async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    예상치 못한 서버 에러 (500) 처리
    """
    logger.exception(f"Unhandled exception: {exc}")
    content = {
        "error": "서버 내부 오류가 발생했습니다.",
        "code": "INTERNAL_SERVER_ERROR",
    }
    if settings.DEBUG:
        content["details"] = str(exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=content,
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    HTTPException 처리 (4xx, 5xx)
    """
    content = {
        "error": str(exc.detail),
        "code": "HTTP_ERROR",
    }
    if settings.DEBUG:
        content["details"] = None
    return JSONResponse(
        status_code=exc.status_code,
        content=content,
    )

from fastapi.encoders import jsonable_encoder

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    유효성 검사 실패 (422) 처리
    """
    content = {
        "error": "입력값이 유효하지 않습니다.",
        "code": "VALIDATION_ERROR",
    }
    if settings.DEBUG:
        content["details"] = jsonable_encoder(exc.errors())
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=content,
    )
