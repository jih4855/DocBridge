# DocBridge 개발 스타일 가이드 (프로젝트 헌법)

이 문서는 DocBridge 프로젝트의 **아키텍처 철학**과 **코딩 표준**을 정의합니다.
모든 AI 에이전트와 개발자는 이 규칙을 엄격히 준수해야 합니다.

---

## 1. 핵심 철학: "느슨한 결합, 높은 응집도"

우리의 최우선 목표는 **유지보수성**과 **테스트 가능성**입니다. 단순히 빨리 짜는 코드보다, 변경하기 쉽고 테스트하기 쉬운 코드를 지향합니다.

### 1.1 의존성 주입의 원칙 (Backend)
- **철학:** 클래스는 스스로 의존성을 생성하지 않는다. 외부에서 주입받아야 한다.
- **규칙:** 서비스(Service) 내부에서 리포지토리(Repository)를 직접 생성(`instantiate`)하지 마시오.
- **이유:** 단위 테스트 시 Mock 객체를 삽입하기 쉽게 하고, 레이어 간의 결합도를 낮추기 위함입니다.

**❌ 나쁜 예 (B- 등급):**
```python
class FolderService:
    def __init__(self, db: Session):
        # 위반: 서비스가 자신의 의존성을 직접 생성함
        self.repo = FolderRepository(db) 
```

**✅ 좋은 예 (A 등급):**
```python
class FolderService:
    # 의존성을 외부에서 주입받음
    def __init__(self, repo: FolderRepository):
        self.repo = repo
```

### 1.2 관심사 분리의 원칙 (Frontend)
- **철학:** UI 컴포넌트는 "어떻게 보이는가"에만 집중한다. 로직은 커스텀 훅(Custom Hook)이 담당한다.
- **규칙:** 복잡한 로직(데이터 페칭, WebSocket, 상태 계산)은 반드시 **Custom Hook**으로 분리하시오.
- **이유:** UI 코드의 가독성을 높이고, 로직을 독립적으로 테스트하거나 재사용하기 위함입니다.

**❌ 나쁜 예 (B- 등급):**
```tsx
// Sidebar.tsx
export default function Sidebar() {
    // UI와 로직이 뒤섞임
    useEffect(() => {
        const ws = new WebSocket(...);
        ws.onmessage = ...
    }, []);

    return <div>{/* UI 렌더링 로직 */}</div>;
}
```

**✅ 좋은 예 (A 등급):**
```tsx
// useFolderTree.ts (로직 분리)
export function useFolderTree() {
    const [tree, setTree] = useState(...);
    // WebSocket 로직은 여기서 관리
    return { tree, refresh };
}

// Sidebar.tsx (UI 전담)
export default function Sidebar() {
    const { tree } = useFolderTree(); // 로직 사용만 함
    return <TreeView data={tree} />;
}
```

---

## 2. 백엔드 가이드라인 (FastAPI)

### 2.1 계층형 아키텍처
다음 흐름을 엄격히 따르며, 레이어를 건너뛰는 행위는 금지합니다.
```
Router (컨트롤러) -> Service (비즈니스 로직) -> Repository (데이터 접근) -> Database
```

### 2.2 에러 처리 (Error Handling)
- **Repository:** 데이터가 없으면 `None`이나 빈 리스트를 반환합니다. HTTP 예외를 발생시키지 마십시오.
- **Service:** 비즈니스 규칙 위반 시 **도메인 예외**를 발생시킵니다. (예: `FolderNotFoundError`, `DuplicatePathError`)
- **Router:** 도메인 예외를 잡아 **HTTP 예외**(404, 400, 409 등)로 변환하여 클라이언트에 응답합니다.

### 2.3 타입 안정성
- Python 3.10+ 타입 힌트를 엄격하게 사용합니다.
- 명확한 이유 없이 `Any` 타입을 사용하지 마십시오.
- 모든 데이터 전송에는 Pydantic 모델(DTO)을 사용합니다.

---

## 3. 프론트엔드 가이드라인 (Next.js)

### 3.1 컴포넌트 구조
- **Container/Page:** 데이터 페칭이나 훅 호출을 담당하고 하위로 데이터를 전달합니다.
- **Presentational Component:** props를 통해 데이터를 받아 화면을 그리는 일만 합니다. 내부에서 API를 직접 호출하지 않습니다.

### 3.2 상태 관리
- 3단계 이상의 "Prop Drilling"은 피하십시오.
- 전역 상태(파일 선택, 사이드바 상태 등)가 필요한 경우 Context API나 Zustand를 사용합니다.

### 3.3 스타일링
- TailwindCSS 클래스 사용을 원칙으로 합니다.
- 인라인 스타일(`style={{ ... }}`)은 지양합니다.

---

## 4. 테스트 가이드라인 (TDD)

### 4.1 구현이 아닌 동작을 테스트하라
- 내부 구조를 리팩토링했다고 해서 테스트가 깨져서는 안 됩니다.
- **백엔드:**
    - **단위 테스트:** 서비스를 테스트할 때 리포지토리를 Mocking 하십시오.
    - **통합 테스트:** 실제 테스트용 DB를 사용하여 Router부터 DB까지의 전체 흐름을 검증하십시오.

### 4.2 Mocking
- 의존성 주입(DI)을 사용하므로, `unittest.mock`이나 `pytest-mock`을 사용하여 서비스에 가짜 리포지토리를 주입하십시오.

---

## 5. 최종 체크리스트

코드를 제출하기 전 다음 질문에 답하십시오:
1. 백엔드에서 **의존성 주입(DI)**을 사용했는가?
2. 프론트엔드에서 **로직(Hook)**과 **UI(Component)**를 분리했는가?
3. 이 기능이 작동함을 증명하는 **테스트 코드**가 포함되어 있는가?
