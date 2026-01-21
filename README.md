# DocBridge

**흩어져 있는 프로젝트 명세서를 한 곳에서 통합 관리하고 LLM 워크플로우를 가속화하는 도구**

DocBridge는 여러 프로젝트에 분산된 `/spec` 폴더들을 하나의 인터페이스에서 열람하고 관리할 수 있게 해주는 개발자용 도구입니다. VS Code 스타일의 친숙한 UI와 실시간 파일 변경 감지 기능을 통해 명세서 기반의 코딩 작업을 효율적으로 지원합니다.

---

## 🌟 주요 기능

### 1. 📂 멀티 프로젝트 통합 관리
- 서로 다른 경로에 있는 여러 프로젝트의 명세서 폴더를 DocBridge에 등록하여 한 곳에서 관리할 수 있습니다.
- 도커 볼륨 마운트를 통해 로컬 파일 시스템의 어떤 경로든 연결 가능합니다.

### 2. 🌲 VS Code 스타일의 트리 뷰어
- 개발자에게 익숙한 트리 구조의 사이드바로 폴더와 파일을 탐색합니다.
- 프로젝트별로 명확하게 구분된 계층 구조를 제공합니다.

### 3. 📄 LLM 최적화 마크다운 뷰어
- `PrismJS` 기반의 코드 하이라이팅이 적용된 깔끔한 마크다운 렌더링을 제공합니다.
- **원클릭 복사** 버튼으로 파일 내용을 클립보드에 담아 ChatGPT, Claude 등에 즉시 컨텍스트를 주입할 수 있습니다.

### 4. ⚡️ 실시간 변경 감지 (Watchdog)
- **Watchdog**과 **WebSocket**을 이용하여 로컬 파일이 수정되거나 생성/삭제되는 즉시 UI에 반영됩니다.
- 새로고침 없이 항상 최신 상태의 명세서를 확인할 수 있습니다.

---

## 🛠 기술 스택

| 영역 | 기술 | 설명 |
|------|------|------|
| **Frontend** | Next.js 14 | React 기반 웹 프레임워크 (App Router) |
| **Backend** | FastAPI | 고성능 Python 비동기 API 서버 |
| **Database** | SQLite | 경량화된 로컬 데이터 저장소 |
| **Infrastructure** | Docker | 컨테이너 기반의 간편한 배포 및 실행 |
| **File Watch** | Watchdog | 파일 시스템 이벤트 감지 |

---

## 🚀 빠른 시작 (Docker)

DocBridge는 Docker Compose를 통해 간편하게 실행할 수 있습니다.

### 1. 환경 설정

프로젝트 루트의 `.env.example` 파일을 복사하여 `.env` 파일을 생성하고, 관리하고 싶은 프로젝트들이 위치한 최상위 경로(`PROJECT_ROOT`)를 설정합니다.

```bash
cp .env.example .env
```

`.env` 파일 수정:
```ini
# (예시) 모든 프로젝트가 /Users/me/projects 아래에 있다면
PROJECT_ROOT=/Users/me/projects
```

### 2. 실행

```bash
docker-compose up -d
```

### 3. 접속

브라우저에서 [http://localhost:3000](http://localhost:3000)으로 접속하세요.

---

## 💻 로컬 개발 환경 설정

기여를 원하시거나 직접 빌드하여 실행하고 싶은 경우 아래 절차를 따르세요.

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 서버 실행
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install

# 개발 서버 실행
npm run dev
```

---

## 📚 API 문서

백엔드 서버 실행 후 아래 주소에서 Swagger UI를 통해 API 명세를 확인할 수 있습니다.

- [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🤝 기여하기

Issue와 Pull Request는 언제나 환영합니다. 버그 제보나 기능 제안은 GitHub Issue를 통해 남겨주세요.

## 📄 라이선스

이 프로젝트는 MIT License를 따릅니다.
