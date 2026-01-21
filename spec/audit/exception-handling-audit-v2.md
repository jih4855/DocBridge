# [예외 처리] 2차 감사 보고서 (Post-Refactoring)

## 참조 스펙
- 워크플로우: `[/exceptionhandling]` Exception Handling Audit
- 1차 보고서: [exception-handling-audit-v1.md](./exception-handling-audit-v1.md)
- 상태: 리팩토링 **후** (After)

---

## 1. 📊 Consistency Scorecard (After Refactoring)

| Category | Score | Evaluation |
|---|---|---|
| **Backend Schema Uniformity** | **A** | **(개선됨)** `app/core/exceptions.py`의 전역 예외 처리기가 500, 4xx, 422 에러를 모두 표준 포맷으로 변환함. 라우터에서 중복 처리 로직이 제거되고 `HTTPException` 발생으로 통일됨. |
| **Frontend Client Resilience** | **A-** | **(개선됨)** `src/lib/api.ts`의 `fetchClient` 도입으로 Base URL 자동 처리 및 에러 파싱이 중앙화됨. 컴포넌트(`Sidebar`, `MainViewer`)에서 더 이상 `try-catch`로 파싱하거나 URL을 하드코딩하지 않음. |

---

## 2. 🛡️ Verification Report

### Backend Implementation
*   **File:** `app/core/exceptions.py`
    *   `global_exception_handler` -> 500 Error Standardized (OK)
    *   `http_exception_handler` -> 4xx Error Standardized (OK)
    *   `validation_exception_handler` -> 422 Error Standardized (OK)
*   **Integration:** `main.py`에 handler 등록 완료.

### Frontend Implementation
*   **File:** `src/lib/api.ts`
    *   `fetchClient` wrapper 구현 완료.
    *   `ApiError` 클래스 도입으로 에러 구분 명확화.
*   **Refactoring:**
    *   `Sidebar/index.tsx`: `fetchClient` 적용 및 구조 복구 완료.
    *   `MainViewer.tsx`: `fetchClient` 적용 및 하드코딩 URL 제거 완료.

### 2차 감사 결론
백엔드와 프론트엔드 모두 **표준화된 예외 처리 규약(Protocol)**을 준수하도록 리팩토링되었습니다.
- **Protocol:** `Code`, `Message`, `Details` 구조의 JSON 응답.
- **Safety:** 서버 500 에러 시에도 클라이언트는 JSON 응답을 받아 우아하게 처리 가능.

---

## 3. 남은 과제 (Minor)
- 다른 컴포넌트(ProjectList 등)도 점진적으로 `fetchClient`를 사용하도록 리팩토링 필요.
