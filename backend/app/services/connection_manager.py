"""
WebSocket 연결 관리자 (Improved)

Spec: spec/api/file-watch-websocket.md - 섹션 8
연결된 모든 클라이언트에 메시지 broadcast

Audit Fix: Issue #3 - Race Condition in broadcast()
- list → set (중복 방지, O(1) 삭제)
- asyncio.Lock() 추가 (Thread-safe)
- disconnect() → async 변경
"""

import asyncio
from typing import Any

from fastapi import WebSocket
from loguru import logger


class ConnectionManager:
    """WebSocket 연결 관리 (Thread-safe)"""

    def __init__(self) -> None:
        self._connections: set[WebSocket] = set()  # list → set (중복 방지, O(1) 삭제)
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        """
        클라이언트 연결 수락 및 등록
        
        Args:
            websocket: 연결할 WebSocket 객체
        """
        await websocket.accept()
        async with self._lock:
            self._connections.add(websocket)
        logger.info(f"WebSocket 연결: 현재 {self.connection_count}개 활성 연결")

    async def disconnect(self, websocket: WebSocket) -> None:
        """
        클라이언트 연결 해제 (async로 변경하여 lock 사용 가능)
        
        Args:
            websocket: 해제할 WebSocket 객체
        """
        async with self._lock:
            self._connections.discard(websocket)  # remove → discard (없어도 에러 없음)
        logger.info(f"WebSocket 연결 해제: 현재 {self.connection_count}개 활성 연결")

    async def broadcast(self, message: dict[str, Any]) -> None:
        """
        모든 클라이언트에 메시지 전송
        
        Args:
            message: 전송할 메시지 딕셔너리
        """
        # 스냅샷 복사로 iteration 중 수정 방지
        async with self._lock:
            connections = set(self._connections)
        
        disconnected = []
        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"메시지 전송 실패: {e}")
                disconnected.append(connection)
        
        # 실패한 연결 비동기 정리
        for conn in disconnected:
            await self.disconnect(conn)

    @property
    def connection_count(self) -> int:
        """현재 연결된 클라이언트 수"""
        return len(self._connections)

    @property
    def active_connections(self) -> list[WebSocket]:
        """하위 호환성 유지를 위한 프로퍼티"""
        return list(self._connections)


# 전역 ConnectionManager 인스턴스
manager = ConnectionManager()
