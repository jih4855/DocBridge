"""
파일 감시 유틸리티 및 서비스 테스트

Spec: spec/api/file-watch-websocket.md - 섹션 7
TDD Red 단계 - 실패하는 테스트 먼저 작성
"""

import asyncio
import time
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.services.file_watcher import (
    is_markdown_file, is_hidden_file, is_ignored_path,
    MarkdownEventHandler, FileWatcherService
)
from app.services.connection_manager import ConnectionManager


class TestIsMarkdownFile:
    """is_markdown_file 유틸리티 테스트"""

    def test_markdown_file_returns_true(self) -> None:
        """`.md` 확장자 파일 → True"""
        
        assert is_markdown_file("test.md") is True
        assert is_markdown_file("/path/to/file.md") is True
        assert is_markdown_file("README.MD") is True  # 대소문자 무관

    def test_non_markdown_file_returns_false(self) -> None:
        """`.md`가 아닌 파일 → False"""
        
        assert is_markdown_file("test.txt") is False
        assert is_markdown_file("test.py") is False
        assert is_markdown_file("test.markdown") is False  # .md만 허용
        assert is_markdown_file("test") is False


class TestIsHiddenFile:
    """is_hidden_file 유틸리티 테스트"""

    def test_hidden_file_returns_true(self) -> None:
        """`.`으로 시작하는 파일 → True"""
        
        assert is_hidden_file(".hidden.md") is True
        assert is_hidden_file(".gitignore") is True
        assert is_hidden_file("/path/to/.hidden.md") is True

    def test_normal_file_returns_false(self) -> None:
        """일반 파일 → False"""
        
        assert is_hidden_file("normal.md") is False
        assert is_hidden_file("/path/to/normal.md") is False


class TestIsIgnoredPath:
    """is_ignored_path 유틸리티 테스트"""

    def test_file_in_hidden_folder_returns_true(self) -> None:
        """숨김 폴더 내 파일 → True"""
        
        assert is_ignored_path("/.git/config.md") is True
        assert is_ignored_path("/path/.hidden/file.md") is True
        assert is_ignored_path("/project/.vscode/settings.md") is True

    def test_file_in_common_ignored_folder_returns_true(self) -> None:
        """일반적인 제외 폴더(node_modules 등) 내 파일 → True"""
        
        assert is_ignored_path("/project/node_modules/pkg/README.md") is True
        assert is_ignored_path("/project/venv/lib/site-packages/README.md") is True
        assert is_ignored_path("/project/__pycache__/cache.md") is True
        assert is_ignored_path("/project/dist/output.md") is True

    def test_file_in_normal_folder_returns_false(self) -> None:
        """일반 폴더 내 파일 → False"""
        
        assert is_ignored_path("/api/auth.md") is False
        assert is_ignored_path("/path/to/normal/file.md") is False


class TestDebounce:
    """debounce 로직 테스트"""

    @pytest.mark.asyncio
    async def test_debounce_duplicate_events(self) -> None:
        """동일 파일 100ms 간격 이벤트 2회 → 1회만 발생"""
        
        callback = AsyncMock()
        handler = MarkdownEventHandler(folder_id=1, callback=callback)
        
        # 첫 번째 이벤트
        mock_event1 = MagicMock()
        mock_event1.src_path = "/test/file.md"
        mock_event1.event_type = "modified"
        mock_event1.is_directory = False
        
        handler.on_any_event(mock_event1)
        
        # 100ms 후 동일 파일 이벤트
        await asyncio.sleep(0.1)
        mock_event2 = MagicMock()
        mock_event2.src_path = "/test/file.md"
        mock_event2.event_type = "modified"
        mock_event2.is_directory = False
        
        handler.on_any_event(mock_event2)
        
        # debounce 시간(300ms) 대기 후 확인
        await asyncio.sleep(0.4)
        
        # 이벤트는 1회만 발생해야 함
        assert callback.call_count == 1

    @pytest.mark.asyncio
    async def test_debounce_different_files(self) -> None:
        """다른 파일 100ms 간격 이벤트 2회 → 2회 발생"""
        
        callback = AsyncMock()
        handler = MarkdownEventHandler(folder_id=1, callback=callback)
        
        # 첫 번째 파일 이벤트
        mock_event1 = MagicMock()
        mock_event1.src_path = "/test/file1.md"
        mock_event1.event_type = "modified"
        mock_event1.is_directory = False
        
        handler.on_any_event(mock_event1)
        
        # 100ms 후 다른 파일 이벤트
        await asyncio.sleep(0.1)
        mock_event2 = MagicMock()
        mock_event2.src_path = "/test/file2.md"
        mock_event2.event_type = "modified"
        mock_event2.is_directory = False
        
        handler.on_any_event(mock_event2)
        
        # debounce 시간(300ms) 대기 후 확인
        await asyncio.sleep(0.4)
        
        # 이벤트는 2회 발생해야 함
        assert callback.call_count == 2


class TestConnectionManager:
    """ConnectionManager 테스트"""

    @pytest.mark.asyncio
    async def test_connect_adds_to_active_connections(self) -> None:
        """연결 시 active_connections에 추가"""
        
        manager = ConnectionManager()
        mock_websocket = AsyncMock()
        
        await manager.connect(mock_websocket)
        
        assert mock_websocket in manager.active_connections
        mock_websocket.accept.assert_called_once()

    @pytest.mark.asyncio
    async def test_disconnect_removes_from_active_connections(self) -> None:
        """연결 해제 시 active_connections에서 제거 (async 버전)"""
        
        manager = ConnectionManager()
        mock_websocket = AsyncMock()
        
        await manager.connect(mock_websocket)
        await manager.disconnect(mock_websocket)  # async로 변경
        
        assert mock_websocket not in manager.active_connections

    @pytest.mark.asyncio
    async def test_broadcast_sends_to_all_connections(self) -> None:
        """broadcast 시 모든 연결에 메시지 전송"""
        
        manager = ConnectionManager()
        mock_ws1 = AsyncMock()
        mock_ws2 = AsyncMock()
        
        await manager.connect(mock_ws1)
        await manager.connect(mock_ws2)
        
        message = {"type": "file_change", "event": "created", "path": "/test.md", "folder_id": 1}
        await manager.broadcast(message)
        
        mock_ws1.send_json.assert_called_once_with(message)
        mock_ws2.send_json.assert_called_once_with(message)

    @pytest.mark.asyncio
    async def test_broadcast_removes_failed_connections(self) -> None:
        """broadcast 시 실패한 연결 자동 제거"""
        
        manager = ConnectionManager()
        mock_ws1 = AsyncMock()
        mock_ws2 = AsyncMock()
        mock_ws2.send_json.side_effect = Exception("Connection closed")
        
        await manager.connect(mock_ws1)
        await manager.connect(mock_ws2)
        
        message = {"type": "file_change", "event": "created", "path": "/test.md", "folder_id": 1}
        await manager.broadcast(message)
        
        # 실패한 연결은 제거됨
        assert mock_ws1 in manager.active_connections
        assert mock_ws2 not in manager.active_connections


class TestFileWatcherService:
    """FileWatcherService 테스트 (Audit Fix: Issue #4)"""

    @pytest.fixture
    def temp_dir(self, tmp_path: Path) -> Path:
        """테스트용 임시 디렉토리"""
        return tmp_path

    def test_add_folder_success(self, temp_dir: Path) -> None:
        """폴더 추가 성공"""
        
        service = FileWatcherService(use_polling=True)
        result = service.add_folder(folder_id=1, path=str(temp_dir))
        
        assert result is True
        assert service.watching_count == 1
        
        # 정리
        service.stop_all()

    def test_add_folder_duplicate_id(self, temp_dir: Path) -> None:
        """중복 폴더 ID 추가 시 False 반환"""
        
        service = FileWatcherService(use_polling=True)
        service.add_folder(folder_id=1, path=str(temp_dir))
        
        result = service.add_folder(folder_id=1, path=str(temp_dir))
        assert result is False
        assert service.watching_count == 1
        
        service.stop_all()

    def test_add_folder_nonexistent_path(self) -> None:
        """존재하지 않는 경로 추가 시 False 반환"""
        
        service = FileWatcherService(use_polling=True)
        result = service.add_folder(folder_id=1, path="/nonexistent/path")
        
        assert result is False
        assert service.watching_count == 0

    def test_add_folder_file_path(self, temp_dir: Path) -> None:
        """파일 경로 추가 시 False 반환"""
        
        # 파일 생성
        test_file = temp_dir / "test.txt"
        test_file.write_text("test")
        
        service = FileWatcherService(use_polling=True)
        result = service.add_folder(folder_id=1, path=str(test_file))
        
        assert result is False
        assert service.watching_count == 0

    def test_remove_folder_success(self, temp_dir: Path) -> None:
        """폴더 제거 성공"""
        
        service = FileWatcherService(use_polling=True)
        service.add_folder(folder_id=1, path=str(temp_dir))
        
        result = service.remove_folder(folder_id=1)
        
        assert result is True
        assert service.watching_count == 0

    def test_remove_folder_not_watching(self) -> None:
        """감시 중이 아닌 폴더 제거 시 False 반환"""
        
        service = FileWatcherService(use_polling=True)
        result = service.remove_folder(folder_id=999)
        
        assert result is False

    def test_stop_all(self, temp_dir: Path) -> None:
        """모든 감시 중지"""
        
        service = FileWatcherService(use_polling=True)
        
        # 여러 폴더 추가 (서브 디렉토리)
        sub1 = temp_dir / "sub1"
        sub2 = temp_dir / "sub2"
        sub1.mkdir()
        sub2.mkdir()
        
        service.add_folder(folder_id=1, path=str(sub1))
        service.add_folder(folder_id=2, path=str(sub2))
        
        assert service.watching_count == 2
        
        service.stop_all()
        
        assert service.watching_count == 0


class TestMarkdownEventHandlerTimerCleanup:
    """MarkdownEventHandler 타이머 정리 테스트 (Audit Fix: Issue #6)"""

    @pytest.mark.asyncio
    async def test_cancel_all_timers(self) -> None:
        """cancel_all_timers가 모든 타이머를 취소하는지 확인"""
        
        callback = AsyncMock()
        handler = MarkdownEventHandler(folder_id=1, callback=callback)
        
        # 여러 파일에 대해 타이머 스케줄
        handler._schedule_callback("/test/file1.md", "modified")
        handler._schedule_callback("/test/file2.md", "modified")
        handler._schedule_callback("/test/file3.md", "modified")
        
        assert len(handler._debounce_timers) == 3
        
        # 타이머 취소
        handler.cancel_all_timers()
        
        assert len(handler._debounce_timers) == 0
        
        # 충분히 대기해도 콜백이 호출되지 않음
        await asyncio.sleep(0.5)
        assert callback.call_count == 0
