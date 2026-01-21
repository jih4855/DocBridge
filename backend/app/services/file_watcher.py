"""
파일 변경 감시 서비스

Spec: spec/api/file-watch-websocket.md - 섹션 5, 8
watchdog을 사용한 .md 파일 변경 감지 및 이벤트 전달

Audit Fix:
- Issue #2: asyncio.run() 이벤트 루프 충돌 방지
- Issue #6: 타이머 정리 로직 추가 (메모리 누수 방지)
"""

import asyncio
import os
import threading
import time
from app.core.config import settings
from app.utils.tree_builder import build_tree
from pathlib import Path
from typing import Any, Callable

from loguru import logger
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer
from watchdog.observers.polling import PollingObserver


# =============================================================================
# 유틸리티 함수
# =============================================================================

def is_markdown_file(path: str) -> bool:
    """
    마크다운 파일 여부 확인
    
    Args:
        path: 파일 경로
        
    Returns:
        .md 확장자면 True
    """
    return path.lower().endswith('.md')


def is_hidden_file(path: str) -> bool:
    """
    숨김 파일 여부 확인 (파일명이 .으로 시작)
    
    Args:
        path: 파일 경로
        
    Returns:
        숨김 파일이면 True
    """
    filename = os.path.basename(path)
    return filename.startswith('.')


COMMON_IGNORED_DIRS = {
    'node_modules', '__pycache__', 'venv', '.venv', 'env', '.env', 
    'dist', 'build', 'coverage', '.git', '.vscode', '.idea', '.next'
}

def is_ignored_path(path: str) -> bool:
    """
    무시할 경로인지 확인 (숨김 폴더 및 node_modules 등)
    
    Args:
        path: 파일 경로
        
    Returns:
        무시 대상이면 True
    """
    parts = Path(path).parts
    for part in parts:
        # 숨김 폴더 (.으로 시작) 또는 일반적인 제외 폴더
        if part.startswith('.') and part not in ('.', '..'):
            return True
        if part in COMMON_IGNORED_DIRS:
            return True
    return False


# =============================================================================
# MarkdownEventHandler
# =============================================================================

class MarkdownEventHandler(FileSystemEventHandler):
    """
    마크다운 파일 변경 이벤트 핸들러
    
    - .md 파일만 필터링
    - 숨김 파일/폴더 제외
    - 300ms debounce 적용
    """

    DEBOUNCE_SECONDS = 0.3  # 300ms

    def __init__(
        self,
        folder_id: int,
        callback: Callable[[dict[str, Any]], Any],
        loop: asyncio.AbstractEventLoop | None = None
    ) -> None:
        """
        Args:
            folder_id: 감시 중인 폴더 ID
            callback: 이벤트 발생 시 호출할 콜백 (async)
            loop: 이벤트 루프 (None이면 실행 시점에 가져옴)
        """
        super().__init__()
        self.folder_id = folder_id
        self.callback = callback
        self.loop = loop
        self._debounce_cache: dict[str, float] = {}
        self._debounce_timers: dict[str, threading.Timer] = {}
        self._lock = threading.Lock()

    def on_any_event(self, event: FileSystemEvent) -> None:
        """모든 파일 시스템 이벤트 처리"""
        # 디렉토리 이벤트 무시
        if event.is_directory:
            return
        
        src_path = event.src_path
        
        # .md 파일만 처리
        if not is_markdown_file(src_path):
            return
        
        # 숨김 파일 무시
        if is_hidden_file(src_path):
            return
        
        # 무시 대상 폴더 내 파일 무시
        if is_ignored_path(src_path):
            return
        
        # debounce 적용
        self._schedule_callback(src_path, event.event_type)

    def _schedule_callback(self, path: str, event_type: str) -> None:
        """debounce 적용하여 콜백 스케줄링"""
        with self._lock:
            # 기존 타이머 취소
            if path in self._debounce_timers:
                self._debounce_timers[path].cancel()
            
            # 새 타이머 설정
            timer = threading.Timer(
                self.DEBOUNCE_SECONDS,
                self._execute_callback,
                args=[path, event_type]
            )
            self._debounce_timers[path] = timer
            timer.start()

    def _execute_callback(self, path: str, event_type: str) -> None:
        """콜백 실행 (Audit Fix: Issue #2 - 안전한 이벤트 루프 처리)"""
        with self._lock:
            if path in self._debounce_timers:
                del self._debounce_timers[path]
        
        message = {
            "type": "file_change",
            "event": event_type,
            "path": path,
            "folder_id": self.folder_id
        }
        
        logger.debug(f"파일 변경 감지: {event_type} - {path}")
        
        # 비동기 콜백 실행 (개선: 이벤트 루프 충돌 방지)
        try:
            if self.loop and self.loop.is_running():
                asyncio.run_coroutine_threadsafe(self.callback(message), self.loop)
            else:
                # 실행 중인 이벤트 루프가 있는지 확인 후 안전하게 실행
                try:
                    loop = asyncio.get_running_loop()
                    asyncio.run_coroutine_threadsafe(self.callback(message), loop)
                except RuntimeError:
                    # 이벤트 루프가 없는 경우에만 asyncio.run 사용
                    asyncio.run(self.callback(message))
        except Exception as e:
            logger.exception(f"콜백 실행 오류: {e}")

    def cancel_all_timers(self) -> None:
        """
        모든 대기 중인 타이머 취소 (Audit Fix: Issue #6 - 메모리 누수 방지)
        
        Handler 삭제 전 호출하여 고아 타이머 방지
        """
        with self._lock:
            for timer in self._debounce_timers.values():
                timer.cancel()
            self._debounce_timers.clear()
            logger.debug(f"폴더 {self.folder_id}의 모든 타이머 취소됨")


# =============================================================================
# FileWatcherService
# =============================================================================

class FileWatcherService:
    """
    파일 감시 서비스
    
    - 여러 폴더를 동시에 감시
    - 폴더 추가/제거 지원
    - Docker 환경을 위한 PollingObserver 사용
    """

    def __init__(self, use_polling: bool = True) -> None:
        """
        Args:
            use_polling: True면 PollingObserver 사용 (Docker 호환)
        """
        self.use_polling = use_polling
        self._observers: dict[int, Observer] = {}  # folder_id -> Observer
        self._handlers: dict[int, MarkdownEventHandler] = {}  # folder_id -> Handler
        self._loop: asyncio.AbstractEventLoop | None = None
        self._broadcast_callback: Callable[[dict[str, Any]], Any] | None = None

    def set_event_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """이벤트 루프 설정"""
        self._loop = loop

    def set_broadcast_callback(self, callback: Callable[[dict[str, Any]], Any]) -> None:
        """broadcast 콜백 설정"""
        self._broadcast_callback = callback

    def add_folder(self, folder_id: int, path: str) -> bool:
        """
        감시할 폴더 추가
        
        Args:
            folder_id: 폴더 ID
            path: 감시할 폴더 경로
            
        Returns:
            성공 여부
        """
        if folder_id in self._observers:
            logger.warning(f"폴더 {folder_id}는 이미 감시 중")
            return False
        
        if not os.path.exists(path):
            logger.error(f"폴더가 존재하지 않음: {path}")
            return False
        
        if not os.path.isdir(path):
            logger.error(f"디렉토리가 아님: {path}")
            return False
        
        try:
            # Observer 생성
            observer_class = PollingObserver if self.use_polling else Observer
            observer = observer_class()
            
            # Handler 생성
            handler = MarkdownEventHandler(
                folder_id=folder_id,
                callback=self._on_file_change,
                loop=self._loop
            )
            
            # 감시 시작
            observer.schedule(handler, path, recursive=True)
            observer.start()
            
            self._observers[folder_id] = observer
            self._handlers[folder_id] = handler
            
            logger.info(f"폴더 감시 시작: {folder_id} - {path}")
            return True
            
        except Exception as e:
            logger.exception(f"폴더 감시 시작 실패: {e}")
            return False

    def remove_folder(self, folder_id: int) -> bool:
        """
        폴더 감시 중지 및 제거 (Audit Fix: Issue #6 - 타이머 정리 추가)
        
        Args:
            folder_id: 폴더 ID
            
        Returns:
            성공 여부
        """
        if folder_id not in self._observers:
            logger.warning(f"폴더 {folder_id}는 감시 중이 아님")
            return False
        
        try:
            # 타이머 정리 추가 (Audit Fix)
            handler = self._handlers.get(folder_id)
            if handler:
                handler.cancel_all_timers()
            
            observer = self._observers[folder_id]
            observer.stop()
            observer.join(timeout=1.0)
            
            del self._observers[folder_id]
            del self._handlers[folder_id]
            
            logger.info(f"폴더 감시 중지: {folder_id}")
            return True
            
        except Exception as e:
            logger.exception(f"폴더 감시 중지 실패: {e}")
            return False

    async def _on_file_change(self, message: dict[str, Any]) -> None:
        """파일 변경 이벤트 처리"""
        if self._broadcast_callback:
            await self._broadcast_callback(message)

    def stop_all(self) -> None:
        """모든 폴더 감시 중지"""
        folder_ids = list(self._observers.keys())
        for folder_id in folder_ids:
            self.remove_folder(folder_id)
        logger.info("모든 폴더 감시 중지 완료")

    @property
    def watching_count(self) -> int:
        """현재 감시 중인 폴더 수"""
        return len(self._observers)


# 전역 FileWatcherService 인스턴스
# 로컬 실행(Native) vs Docker(Polling) 자동 전환
# settings.WATCHDOG_USE_POLLING 값 사용 (기본값 False)
file_watcher = FileWatcherService(use_polling=settings.WATCHDOG_USE_POLLING)
