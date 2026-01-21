# File Watch WebSocket 감사 수정 구현 결과

## 참조 스펙
- [감사 보고서](../audit/file-watch-websocket-audit.md)
- [원본 스펙](../api/file-watch-websocket.md)

## 생성/수정된 파일

| 파일 경로 | 설명 |
|-----------|------|
| `app/services/connection_manager.py` | Thread-safe broadcast (asyncio.Lock, set 사용) |
| `app/services/file_watcher.py` | asyncio.run 폴백 개선, 타이머 정리 로직 추가 |
| `app/api/websocket.py` | async disconnect 호출로 변경 |
| `tests/test_file_watcher.py` | FileWatcherService 유닛 테스트 8개 추가 |
| `tests/test_file_watch_websocket.py` | 필터링 assertion 추가, 예외 처리 범위 좁히기 |

## 수정된 이슈

| 이슈 # | 우선순위 | 설명 | 상태 |
|--------|----------|------|------|
| #3 | 🔴 High | broadcast() race condition | ✅ 완료 |
| #1 | 🔴 High | 필터링 테스트 assertion 없음 | ✅ 완료 |
| #2 | 🟡 Medium | asyncio.run() 이벤트 루프 충돌 | ✅ 완료 |
| #4 | 🟡 Medium | FileWatcherService 테스트 부재 | ✅ 완료 |
| #6 | 🟡 Medium | Timer 미정리 (메모리 누수) | ✅ 완료 |
| #5 | 🟢 Low | 예외 처리 범위 넓음 | ✅ 완료 |

## 테스트 결과

```
======================== 28 passed, 5 skipped in 5.90s ========================
```

- **총 테스트**: 33개
- **통과**: 28개
- **스킵**: 5개 (TestClient WebSocket 타임아웃 미지원)

## 주요 변경 사항

### 1. connection_manager.py - Thread-safe 개선

```python
# Before
self.active_connections: list[WebSocket] = []
def disconnect(self, websocket: WebSocket) -> None:
    self.active_connections.remove(websocket)

# After
self._connections: set[WebSocket] = set()
self._lock = asyncio.Lock()
async def disconnect(self, websocket: WebSocket) -> None:
    async with self._lock:
        self._connections.discard(websocket)
```

### 2. file_watcher.py - 안전한 비동기 콜백

```python
# Before
asyncio.run(self.callback(message))  # 이벤트 루프 충돌 가능

# After
try:
    loop = asyncio.get_running_loop()
    asyncio.run_coroutine_threadsafe(self.callback(message), loop)
except RuntimeError:
    asyncio.run(self.callback(message))  # 루프 없을 때만
```

### 3. 타이머 정리 로직 추가

```python
def cancel_all_timers(self) -> None:
    with self._lock:
        for timer in self._debounce_timers.values():
            timer.cancel()
        self._debounce_timers.clear()
```

## 변경 이력

| 날짜 | 작업자 | 내용 |
|------|--------|------|
| 2026-01-21 | Gemini | 감사 보고서 기반 6개 이슈 수정 |
