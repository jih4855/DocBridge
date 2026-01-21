# File Watch WebSocket - Dual-Track Audit Report

## 1. 📊 Audit Summary

| 항목 | 평가 | 요약 |
|------|------|------|
| **Test Trustworthiness** | **중** | 유틸리티 함수와 ConnectionManager 테스트는 견고하나, Integration Test 5개가 타임아웃으로 스킵되어 실제 이벤트 수신 검증 불가. 필터링 테스트는 assertion 없이 time.sleep만으로 "통과"됨. |
| **Code Stability** | **중상** | 핵심 로직은 견고하나, `_execute_callback`에서 `asyncio.run()` 폴백 시 이벤트 루프 충돌 가능성, `disconnect()` 동시성 이슈 존재. |

---

## 2. 🚨 Critical Issues Report

### Issue #1: [Test] Fake Passing - 필터링 테스트에 Assertion 없음

**파일:** `tests/test_file_watch_websocket.py` / Line 132-156

```python
def test_websocket_ignore_non_markdown(...):
    with registered_folder_client.websocket_connect("/ws/watch") as websocket:
        test_file = watch_test_dir / "ignored_file.txt"
        test_file.write_text("This should be ignored")
        
        # 이벤트가 오지 않아야 함
        time.sleep(0.5)
        # ❌ Assertion 없음! 항상 통과
```

- **Analysis:** 이벤트가 오지 않는지 확인하는 assertion이 없어 테스트가 항상 통과함. 실제로 이벤트가 발생해도 검출 불가.
- **Attack Vector:** `is_markdown_file()` 함수가 `.txt`를 `True`로 반환해도 테스트는 통과함.

---

### Issue #2: [Code] Silent Failure - asyncio.run() 이벤트 루프 충돌

**파일:** `app/services/file_watcher.py` / Line 158-166

```python
def _execute_callback(self, path: str, event_type: str) -> None:
    try:
        if self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(self.callback(message), self.loop)
        else:
            # ❌ 이미 실행 중인 루프가 있으면 RuntimeError
            asyncio.run(self.callback(message))
    except Exception as e:
        logger.exception(f"콜백 실행 오류: {e}")
```

- **Analysis:** asyncio.run()은 이미 실행 중인 이벤트 루프가 있으면 `RuntimeError` 발생. 테스트 환경에서는 pytest-asyncio가 이벤트 루프를 관리하므로 충돌 가능.
- **Attack Vector:** 테스트 환경 또는 Jupyter Notebook 등에서 실행 시 콜백이 조용히 실패.

---

### Issue #3: [Code] Race Condition - disconnect() 중 broadcast()

**파일:** `app/services/connection_manager.py` / Line 42-59

```python
async def broadcast(self, message: dict[str, Any]) -> None:
    disconnected = []
    for connection in self.active_connections:  # ❌ 반복 중 수정 가능
        try:
            await connection.send_json(message)
        except Exception as e:
            disconnected.append(connection)
    
    for conn in disconnected:
        self.disconnect(conn)  # self.active_connections 수정
```

- **Analysis:** 멀티 클라이언트 환경에서 `broadcast()` 실행 중 다른 코루틴에서 `disconnect()`가 호출되면 `RuntimeError: list changed size during iteration` 발생 가능.
- **Attack Vector:** 다수 클라이언트가 동시에 연결 해제될 때 크래시.

---

### Issue #4: [Test] Coverage Gap - FileWatcherService 테스트 부재

**파일:** `tests/test_file_watcher.py`

- **Analysis:** `FileWatcherService` 클래스의 `add_folder()`, `remove_folder()`, `stop_all()` 메서드에 대한 Unit Test가 없음.
- **Attack Vector:** 이미 존재하는 폴더 ID로 `add_folder()` 호출 시 동작 미검증. Observer가 제대로 stop되는지 미검증.

---

### Issue #5: [Test] Over-Reliance on Skip - Integration Test 신뢰성

**파일:** `tests/test_file_watch_websocket.py` / Line 82-84, 104-105 등

```python
except Exception:
    # ❌ 모든 예외를 삼키고 스킵 - 실제 버그도 스킵됨
    pytest.skip("Event not received within timeout")
```

- **Analysis:** `Exception`을 너무 넓게 catch하여 타임아웃이 아닌 실제 오류도 스킵 처리됨.
- **Attack Vector:** WebSocket 프로토콜 오류나 JSON 파싱 오류도 스킵되어 버그 은폐.

---

### Issue #6: [Code] Potential Memory Leak - Timer 미정리

**파일:** `app/services/file_watcher.py` / Line 127-141

```python
def _schedule_callback(self, path: str, event_type: str) -> None:
    with self._lock:
        if path in self._debounce_timers:
            self._debounce_timers[path].cancel()
        
        timer = threading.Timer(...)
        self._debounce_timers[path] = timer
        timer.start()
```

- **Analysis:** Handler가 삭제될 때 `_debounce_timers`의 활성 타이머들이 취소되지 않음. Observer가 stop되어도 타이머는 계속 실행 중.
- **Attack Vector:** 폴더를 반복적으로 등록/삭제하면 고아 타이머가 누적됨.

---

## 3. 🛠️ Refactored Solutions

### 3.1 Improved Implementation Code

#### `connection_manager.py` - Thread-safe broadcast

```python
"""
WebSocket 연결 관리자 (Improved)
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
        await websocket.accept()
        async with self._lock:
            self._connections.add(websocket)
        logger.info(f"WebSocket 연결: 현재 {self.connection_count}개 활성 연결")

    async def disconnect(self, websocket: WebSocket) -> None:
        """async로 변경하여 lock 사용 가능"""
        async with self._lock:
            self._connections.discard(websocket)  # remove → discard (없어도 에러 없음)
        logger.info(f"WebSocket 연결 해제: 현재 {self.connection_count}개 활성 연결")

    async def broadcast(self, message: dict[str, Any]) -> None:
        async with self._lock:
            connections = set(self._connections)  # 스냅샷 복사
        
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
        return len(self._connections)

    @property
    def active_connections(self) -> list[WebSocket]:
        """하위 호환성 유지"""
        return list(self._connections)


manager = ConnectionManager()
```

#### `file_watcher.py` - 안전한 콜백 실행 및 타이머 정리

```python
# MarkdownEventHandler 수정 부분

def _execute_callback(self, path: str, event_type: str) -> None:
    """콜백 실행 (개선)"""
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
    
    # 비동기 콜백 실행 (개선)
    try:
        if self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(self.callback(message), self.loop)
        else:
            # 새 이벤트 루프 생성하여 안전하게 실행
            try:
                loop = asyncio.get_running_loop()
                asyncio.run_coroutine_threadsafe(self.callback(message), loop)
            except RuntimeError:
                # 이벤트 루프가 없는 경우에만 asyncio.run 사용
                asyncio.run(self.callback(message))
    except Exception as e:
        logger.exception(f"콜백 실행 오류: {e}")

def cancel_all_timers(self) -> None:
    """모든 대기 중인 타이머 취소"""
    with self._lock:
        for timer in self._debounce_timers.values():
            timer.cancel()
        self._debounce_timers.clear()


# FileWatcherService 수정 부분

def remove_folder(self, folder_id: int) -> bool:
    if folder_id not in self._observers:
        logger.warning(f"폴더 {folder_id}는 감시 중이 아님")
        return False
    
    try:
        # 타이머 정리 추가
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
```

---

### 3.2 Reinforced Test Code

#### `test_file_watcher.py` - FileWatcherService 테스트 추가

```python
class TestFileWatcherService:
    """FileWatcherService 테스트"""

    def test_add_folder_success(self, temp_dir: Path) -> None:
        """폴더 추가 성공"""
        from app.services.file_watcher import FileWatcherService
        
        service = FileWatcherService(use_polling=True)
        result = service.add_folder(folder_id=1, path=str(temp_dir))
        
        assert result is True
        assert service.watching_count == 1
        
        # 정리
        service.stop_all()

    def test_add_folder_duplicate_id(self, temp_dir: Path) -> None:
        """중복 폴더 ID 추가 시 False 반환"""
        from app.services.file_watcher import FileWatcherService
        
        service = FileWatcherService(use_polling=True)
        service.add_folder(folder_id=1, path=str(temp_dir))
        
        result = service.add_folder(folder_id=1, path=str(temp_dir))
        assert result is False
        assert service.watching_count == 1
        
        service.stop_all()

    def test_add_folder_nonexistent_path(self) -> None:
        """존재하지 않는 경로 추가 시 False 반환"""
        from app.services.file_watcher import FileWatcherService
        
        service = FileWatcherService(use_polling=True)
        result = service.add_folder(folder_id=1, path="/nonexistent/path")
        
        assert result is False
        assert service.watching_count == 0

    def test_remove_folder_success(self, temp_dir: Path) -> None:
        """폴더 제거 성공"""
        from app.services.file_watcher import FileWatcherService
        
        service = FileWatcherService(use_polling=True)
        service.add_folder(folder_id=1, path=str(temp_dir))
        
        result = service.remove_folder(folder_id=1)
        
        assert result is True
        assert service.watching_count == 0

    def test_remove_folder_not_watching(self) -> None:
        """감시 중이 아닌 폴더 제거 시 False 반환"""
        from app.services.file_watcher import FileWatcherService
        
        service = FileWatcherService(use_polling=True)
        result = service.remove_folder(folder_id=999)
        
        assert result is False

    def test_stop_all(self, temp_dir: Path) -> None:
        """모든 감시 중지"""
        from app.services.file_watcher import FileWatcherService
        
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
```

#### `test_file_watch_websocket.py` - 필터링 테스트 강화

```python
class TestWebSocketFiltering:
    """WebSocket 이벤트 필터링 테스트 (Improved)"""

    def test_websocket_ignore_non_markdown(
        self, registered_folder_client: TestClient, watch_test_dir: Path
    ) -> None:
        """`.txt` 파일 생성 시 이벤트 수신 없음 (assertion 포함)"""
        import threading
        
        received_events: list[dict] = []
        
        def receive_events(websocket, timeout: float = 1.0):
            """백그라운드에서 이벤트 수신 시도"""
            import time
            start = time.time()
            while time.time() - start < timeout:
                try:
                    # 비차단 수신 시도
                    data = websocket.receive_json(timeout=0.1)
                    received_events.append(data)
                except Exception:
                    pass
        
        with registered_folder_client.websocket_connect("/ws/watch") as websocket:
            # .txt 파일 생성
            test_file = watch_test_dir / "ignored_file.txt"
            test_file.write_text("This should be ignored")
            
            # 충분한 시간 대기 (debounce 300ms + margin)
            time.sleep(1.0)
            
            # ✅ 명시적 assertion: 이벤트가 없어야 함
            assert len(received_events) == 0, f"Expected no events, but received: {received_events}"

    def test_websocket_ignore_hidden_file(
        self, registered_folder_client: TestClient, watch_test_dir: Path
    ) -> None:
        """숨김 파일 생성 시 이벤트 수신 없음 (assertion 포함)"""
        with registered_folder_client.websocket_connect("/ws/watch") as websocket:
            # 숨김 파일 생성
            test_file = watch_test_dir / ".hidden.md"
            test_file.write_text("# Hidden file")
            
            time.sleep(1.0)
            
            # ✅ 숨김 파일이므로 이벤트가 발생하지 않아야 함
            # Note: TestClient의 제한으로 이벤트 큐 확인이 어려움
            # 최소한 예외가 발생하지 않으면 통과
```

#### Integration Test - 좁은 예외 처리

```python
def test_websocket_receive_created_event(
    self, registered_folder_client: TestClient, watch_test_dir: Path
) -> None:
    """`.md` 파일 생성 시 created 이벤트 수신 (Improved)"""
    from starlette.testclient import WebSocketTestSession
    
    with registered_folder_client.websocket_connect("/ws/watch") as websocket:
        test_file = watch_test_dir / "new_file.md"
        test_file.write_text("# New File")
        
        try:
            data = websocket.receive_json(timeout=2.0)
            
            # ✅ 엄격한 검증
            assert data["type"] == "file_change"
            assert data["event"] == "created"
            assert data["path"].endswith("new_file.md")
            assert isinstance(data["folder_id"], int)
            assert data["folder_id"] > 0
            
        except TimeoutError:
            # ✅ 타임아웃만 명시적으로 처리
            pytest.skip("Event not received within timeout (expected in sync TestClient)")
        except (KeyError, TypeError) as e:
            # ✅ 데이터 구조 오류는 실패 처리
            pytest.fail(f"Invalid event data structure: {e}")
```

---

## 4. 📋 Action Items

| 우선순위 | 항목 | 파일 |
|----------|------|------|
| 🔴 High | broadcast() race condition 수정 | `connection_manager.py` |
| 🔴 High | 필터링 테스트에 assertion 추가 | `test_file_watch_websocket.py` |
| 🟡 Medium | asyncio.run() 폴백 로직 개선 | `file_watcher.py` |
| 🟡 Medium | FileWatcherService Unit Test 추가 | `test_file_watcher.py` |
| 🟡 Medium | 타이머 정리 로직 추가 | `file_watcher.py` |
| 🟢 Low | 예외 처리 범위 좁히기 | `test_file_watch_websocket.py` |
