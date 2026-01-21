# DocBridge - PRD (Product Requirements Document)

## 1. 개요

| 항목 | 내용 |
|------|------|
| **프로젝트명** | DocBridge |
| **목적** | 여러 프로젝트에 흩어진 명세서 폴더를 한 곳에서 통합 관리/열람 |
| **대상 사용자** | 개발자 (명세서 기반으로 LLM에게 코딩을 시키는 워크플로우) |
| **배포 방식** | Docker (docker-compose) |
| **개발 방법론** | TDD (Test-Driven Development) |
| **오픈소스** | Yes |

---

## 2. 문제 정의

### 현재 불편함
- VS Code는 프로젝트 전체를 열어야 함 → 명세서 폴더만 보고 싶을 때 불편
- 옵시디언은 하나의 Vault만 가능 → 여러 프로젝트 명세서 통합 불가
- 명세서를 LLM에게 전달할 때 여러 폴더를 왔다갔다 해야 함
- 기존의 정의된 명세서를 변형해서 사용하고 싶을 때 각종 폴더를 왔다리 갔다리 해야함

### DocBridge가 해결하는 것
- 여러 프로젝트의 `/spec` 폴더만 쏙쏙 등록(범용도 가능할 듯?)
- 한 화면에서 크로스 프로젝트 명세서 열람
- 필요한 명세서를 빠르게 찾아서 복사

---

## 3. 기술 스택

| 영역 | 기술 |
|------|------|
| **Frontend** | Next.js |
| **Backend** | FastAPI (Python) |
| **배포** | Docker, docker-compose |
| **파일 형식** | Markdown (.md) |

---

## 4. 핵심 기능 (MVP)

### 4.1 폴더 등록
- 프로젝트명과 경로를 등록
- 예: `projectA` → `/data/projectA/spec`
- 등록된 폴더 목록 저장 (JSON 또는 SQLite)

### 4.2 사이드바 트리 구조
- 등록된 폴더들을 사이드바에 표시
- 클릭 시 하위 폴더/파일 펼침 (VS Code 스타일)
- 폴더/파일 아이콘 구분

### 4.3 마크다운 뷰어
- 파일 선택 시 메인 영역에 렌더링
- 마크다운 → HTML 변환 (코드 하이라이팅 포함)
- 복사 버튼 (전체 내용 클립보드 복사)

### 4.4 파일 변경 자동 감지
- 등록된 폴더의 파일 변경 실시간 감지 (watchdog)
- WebSocket으로 프론트엔드에 변경 이벤트 push
- 트리 자동 새로고침
- 수동 새로고침 버튼도 제공 (fallback)

---

## 5. UI 와이어프레임

```
┌─────────────────────────────────────────────────────┐
│  DocBridge                        [+ 폴더 등록]     │
├──────────────┬──────────────────────────────────────┤
│ 사이드바      │  메인 뷰어                           │
│              │                                      │
│ ▼ projectA   │  # 회원가입 API 스펙         [복사]  │
│   ▼ api      │                                      │
│     auth.md  │  ## 1. 개요                          │
│     user.md ←│  - 목적: 신규 회원 가입 처리          │
│   ▶ models   │  - 담당: Backend                     │
│              │  ...                                 │
│ ▶ projectB   │                                      │
│ ▶ projectC   │                                      │
│              │                                      │
└──────────────┴──────────────────────────────────────┘
```

---

## 6. 도커 배포 구조

### 볼륨 마운트 방식
```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: ./backend
    volumes:
      - ${PROJECT_ROOT}:/data  # 사용자가 설정
    ports:
      - "8000:8000"

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
```

### 사용자 설정 (.env)
```
PROJECT_ROOT=/Users/myname/projects
```

### 실행 방법
```bash
# 1. .env 파일에 본인 프로젝트 폴더 경로 설정
# 2. 실행
docker-compose up
# 3. 브라우저에서 localhost:3000 접속
```

---

## 7. API 명세 (Backend)

### 7.1 폴더 등록
```
POST /api/folders
Body: { "name": "projectA", "path": "/data/projectA/spec" }
Response: { "id": 1, "name": "projectA", "path": "..." }
```

### 7.2 등록된 폴더 목록
```
GET /api/folders
Response: [{ "id": 1, "name": "projectA", "path": "..." }, ...]
```

### 7.3 폴더 삭제
```
DELETE /api/folders/{id}
Response: { "success": true }
```

### 7.4 폴더 트리 조회
```
GET /api/folders/{id}/tree
Response: {
  "name": "spec",
  "type": "directory",
  "children": [
    { "name": "api", "type": "directory", "children": [...] },
    { "name": "README.md", "type": "file" }
  ]
}
```

### 7.5 파일 내용 조회
```
GET /api/files?path=/data/projectA/spec/api/auth.md
Response: { "content": "# 회원가입 API 스펙\n\n..." }
```

### 7.6 파일 변경 감지 (WebSocket)
```
Endpoint: ws://localhost:8000/ws/watch
```

**연결 시:**
- 등록된 모든 폴더 감시 시작 (watchdog)

**수신 메시지 형식:**
```json
{
  "event": "created" | "modified" | "deleted",
  "path": "/data/projectA/spec/new-file.md",
  "folder_id": 1
}
```

**이벤트 종류:**
| event | 설명 |
|-------|------|
| `created` | 새 파일/폴더 생성됨 |
| `modified` | 파일 내용 변경됨 |
| `deleted` | 파일/폴더 삭제됨 |

**프론트엔드 처리:**
- `created` / `deleted` → 해당 folder_id의 트리 새로고침
- `modified` → 현재 열린 파일이면 내용 새로고침

---

## 8. 추후 확장 (v2+)

| 기능 | 설명 | 우선순위 |
|------|------|----------|
| 키워드 검색 | 등록된 모든 폴더에서 전문 검색 | 높음 |
| 의미 검색 (임베딩) | 유사 명세서 찾기 | 중간 |
| 마크다운 편집 | 웹에서 직접 수정 | 중간 |
| 태그 시스템 | 명세서에 태그 부여 | 낮음 |
| 즐겨찾기 | 자주 쓰는 명세서 고정 | 낮음 |

---

## 9. 폴더 구조

```
DocBridge/
├── docker-compose.yml
├── .env.example
├── README.md
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py
│   └── ...
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   └── ...
└── spec/
    └── PRD.md (이 문서)
```

---

## 10. 마일스톤

### Phase 0: 환경설정 (세션 시작 시 최초 1회)
- [ ] 폴더 구조 생성 (섹션 9 참고)
- [ ] Backend 초기화
  - [ ] `backend/requirements.txt` 생성
  - [ ] `backend/Dockerfile` 생성
  - [ ] `backend/main.py` FastAPI 기본 설정
  - [ ] 로깅 설정 (loguru)
  - [ ] CORS 설정
- [ ] Frontend 초기화
  - [ ] Next.js 프로젝트 생성
  - [ ] `frontend/Dockerfile` 생성
- [ ] Docker 설정
  - [ ] `docker-compose.yml` 생성
  - [ ] `.env.example` 생성
- [ ] 테스트 환경 설정
  - [ ] pytest 설정
  - [ ] 테스트 디렉토리 구조

### Phase 1: MVP
- [x] 폴더 등록 API (+ 테스트)
- [x] 폴더 목록 조회 API (+ 테스트)
- [x] 폴더 삭제 API (+ 테스트)
- [x] 폴더 트리 조회 API (+ 테스트)
- [x] 파일 내용 조회 API (+ 테스트)
- [x] 파일 변경 감지 WebSocket (+ 테스트)
- [x] 사이드바 UI (트리 구조)
- [x] 마크다운 뷰어
- [x] 복사 버튼
- [ ] 수동 새로고침 버튼

### Phase 2: 편의 기능
- [ ] 키워드 검색
- [ ] 마크다운 편집
- [ ] 다크 모드

### Phase 3: 고급 기능
- [ ] 의미 검색 (임베딩)
- [ ] 태그 시스템

---

## 변경 이력

| 날짜 | 내용 |
|------|------|
| 2025-01-21 | PRD 초안 작성 |
| 2025-01-21 | 파일 변경 자동 감지 기능 추가 (WebSocket + watchdog) |
| 2025-01-21 | TDD 개발 방법론 추가, Phase 0 환경설정 분리 |
