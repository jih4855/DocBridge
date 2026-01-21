# File Watch WebSocket 구현 결과

## 참조 스펙
- 스펙 파일: [file-watch-websocket.md](../api/file-watch-websocket.md)
- PRD: [PRD.md](../PRD.md) - 섹션 4.4, 7.6

---

## 생성된 파일

| 파일 경로 | 설명 |
|-----------|------|
| `app/services/connection_manager.py` | WebSocket 연결 관리자 (클라이언트 등록/해제, broadcast) |
| `app/services/file_watcher.py` | watchdog 연동 서비스 (유틸리티 함수, MarkdownEventHandler, FileWatcherService) |
| `app/api/websocket.py` | WebSocket 엔드포인트 (`/ws/watch`) |
| `tests/test_file_watcher.py` | Unit Tests (유틸리티 함수, ConnectionManager) |
| `tests/test_file_watch_websocket.py` | Integration + Edge Case Tests |

### 수정된 파일
| 파일 경로 | 설명 |
|-----------|------|
| `main.py` | lifespan에 FileWatcher 초기화 추가, WebSocket 라우터 등록 |
| `app/api/folders.py` | 폴더 등록/삭제 시 watcher 자동 추가/제거 |

---

## 의존성 변경

```
# requirements.txt (이미 포함됨)
watchdog>=3.0.0,<5.0.0
websockets>=12.0,<14.0
```

---

## 테스트 결과

```
총 22개 / 통과 17개 / 스킵 5개
전체 프로젝트: 65개 통과, 5개 스킵
```

### 테스트 실행 명령어
```bash
cd backend
pytest tests/test_file_watcher.py tests/test_file_watch_websocket.py -v
```

---

## 스펙 준수 여부

| 항목 | 스펙 | 구현 | 일치 |
|------|------|------|------|
| WebSocket 경로 | `ws://localhost:8000/ws/watch` | `ws://localhost:8000/ws/watch` | ✓ |
| 이벤트 타입 | `created`, `modified`, `deleted` | `created`, `modified`, `deleted` | ✓ |
| debounce | 300ms | 300ms | ✓ |
| .md 파일 필터링 | .md만 포함 | .md만 포함 | ✓ |
| 숨김 파일 제외 | `.`으로 시작하는 파일 | `.`으로 시작하는 파일 | ✓ |
| 숨김/제외 폴더 | `.git`, `node_modules`, `venv` 등 | `is_ignored_path`에서 필터링 | ✓ |
| Observer 타입 | PollingObserver (Docker) | PollingObserver | ✓ |
| 서버 시작 시 | 기존 폴더 watcher 추가 | lifespan에서 처리 | ✓ |
| 폴더 등록 시 | watcher 추가 | folders.py에서 처리 | ✓ |
| 폴더 삭제 시 | watcher 제거 | folders.py에서 처리 | ✓ |

---

## 특이사항

- **TestClient 제한**: FastAPI TestClient는 동기식 WebSocket으로 실시간 이벤트 수신 테스트에 제한이 있어 5개 테스트 스킵
- **실제 검증**: 브라우저 개발자 도구에서 WebSocket 연결 및 이벤트 수신 확인 권장
- **Docker 호환성**: PollingObserver 사용으로 볼륨 마운트 환경에서도 파일 변경 감지 가능
- **성능 최적화 1**: `node_modules` 등 대용량 폴더를 감시 대상에서 명시적으로 제외하여 CPU 부하 감소
- **성능 최적화 2**: 로컬 실행 시 Native Observer(kqueue) 자동 사용으로 CPU 점유율 최소화 (Docker는 Polling 사용)

---

## 변경 이력

| 날짜 | 작업자 | 내용 |
|------|--------|------|
| 2026-01-21 | Claude | 최초 구현 |
| 2026-01-21 | Gemini | 성능 최적화 (node_modules 제외, Native/Polling 자동 전환) |
