"""
WebSocket 엔드포인트

Spec: spec/api/file-watch-websocket.md - 섹션 4
파일 변경 이벤트를 클라이언트에 실시간 전달
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger

from app.services.connection_manager import manager
from app.services.file_watcher import file_watcher


router = APIRouter()


@router.websocket("/ws/watch")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """
    파일 변경 감시 WebSocket 엔드포인트
    
    연결 시:
    - ConnectionManager에 클라이언트 등록
    - 현재 감시 중인 폴더 수 로깅
    
    연결 해제 시:
    - ConnectionManager에서 클라이언트 제거
    """
    await manager.connect(websocket)
    
    logger.info(
        f"WebSocket 클라이언트 연결 - "
        f"활성 연결: {manager.connection_count}, "
        f"감시 폴더: {file_watcher.watching_count}"
    )
    
    try:
        while True:
            # 클라이언트로부터 메시지 수신 대기 (keep-alive)
            # 클라이언트는 ping을 보내거나 단순히 연결 유지
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
        logger.info(f"WebSocket 클라이언트 연결 해제 - 남은 연결: {manager.connection_count}")
    except Exception as e:
        logger.exception(f"WebSocket 오류: {e}")
        await manager.disconnect(websocket)
