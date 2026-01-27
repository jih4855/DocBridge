"""
DocBridge Backend - FastAPI Application

명세서 폴더 통합 관리 API 서버
"""

import asyncio
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from app.api.folders import router as folders_router
from app.db.database import init_db, get_db
from app.services.connection_manager import manager
from app.services.file_watcher import file_watcher


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """앱 시작/종료 시 실행"""
    # 시작 시: DB 초기화
    init_db()
    
    # FileWatcher 초기화
    loop = asyncio.get_running_loop()
    file_watcher.set_event_loop(loop)
    file_watcher.set_broadcast_callback(manager.broadcast)
    
    # 기존 등록된 폴더들 watcher 추가
    try:
        from app.repositories.folder_repository import FolderRepository
        from app.services.folder_service import FolderService
        from app.core.config import settings

        db_gen = get_db()
        db = next(db_gen)
        try:
            repo = FolderRepository(db)
            service = FolderService(repo, file_watcher, settings)
            service.initialize_watchers()
        finally:
            try:
                next(db_gen)
            except StopIteration:
                pass
    except Exception as e:
        logger.exception(f"폴더 감시 초기화 오류: {e}")
    
    yield
    
    # 종료 시: 모든 watcher 중지
    file_watcher.stop_all()
    logger.info("DocBridge 서버 종료")


app = FastAPI(
    title="DocBridge API",
    description="명세서 폴더 통합 관리 API",
    version="0.1.0",
    lifespan=lifespan,

)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.core.exceptions import (
    global_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from starlette.exceptions import HTTPException as StarletteHTTPException

# 예외 핸들러 등록 (순서 중요: 구체적인 것 -> 일반적인 것)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# 라우터 등록
app.include_router(folders_router, prefix="/api/folders", tags=["folders"])

from app.api.files import router as files_router
app.include_router(files_router, prefix="/api/files", tags=["files"])

# WebSocket 라우터 등록
from app.api.websocket import router as websocket_router
app.include_router(websocket_router, tags=["websocket"])


@app.get("/")
async def root() -> dict[str, str]:
    """루트 엔드포인트"""
    return {"status": "ok", "service": "DocBridge API"}


@app.get("/health")
async def health() -> dict[str, str]:
    """헬스체크 엔드포인트 (Docker/K8s용)"""
    return {"status": "healthy"}


