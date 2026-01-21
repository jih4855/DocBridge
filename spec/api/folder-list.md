# 폴더 목록 조회 API 스펙

## 1. 개요
- **목적:** 등록된 모든 폴더 목록을 조회
- **담당:** Backend
- **상태:** 검토중

---

## 2. 연관 자료
- PRD: [PRD.md](../PRD.md) - 섹션 7.2
- 관련 API: [folder-register.md](./folder-register.md)
- 관련 컴포넌트: [Sidebar.md](../components/Sidebar.md)

---

## 3. 요구사항
- 등록된 모든 폴더 목록을 반환
- 생성일시 기준 내림차순 정렬 (최신 등록 순)
- 사이드바에서 폴더 목록 표시에 사용

---

## 4. API 명세

### Endpoint
- **Method:** GET
- **Path:** `/api/folders`
- **인증:** None (로컬 전용)

### Request
요청 파라미터 없음

### Response (200 OK)
```json
{
  "folders": [
    {
      "id": 1,
      "name": "My Project",
      "path": "/data/my-project/spec",
      "created_at": "2025-01-21T12:00:00Z"
    },
    {
      "id": 2,
      "name": "Another Project",
      "path": "/data/another/spec",
      "created_at": "2025-01-21T11:00:00Z"
    }
  ]
}
```

### Response 필드 설명
| 필드 | 타입 | 설명 |
|------|------|------|
| folders | array | 폴더 객체 배열 |
| folders[].id | int | 폴더 고유 ID |
| folders[].name | string | 프로젝트 표시명 |
| folders[].path | string | 폴더 절대 경로 |
| folders[].created_at | string (ISO8601) | 생성 시각 |

### Response (200 OK) - 빈 목록
```json
{
  "folders": []
}
```

### Error Cases
| 상황 | 코드 | 메시지 |
|------|------|--------|
| 서버 내부 오류 | 500 | `{ "error": "internal server error" }` |

---

## 5. 비즈니스 로직

```
1. 데이터베이스에서 모든 폴더 조회
2. created_at 기준 내림차순 정렬
3. 폴더 목록 반환
```

---

## 6. 엣지 케이스
- [x] 등록된 폴더가 없는 경우 → 빈 배열 반환
- [x] 폴더 경로가 더 이상 존재하지 않는 경우 → 목록에는 포함 (삭제된 경로 표시는 프론트 책임)
- [x] 다수의 폴더가 등록된 경우 → 페이지네이션 없음 (MVP에서는 전체 반환)

---

## 7. 테스트 케이스 (TDD - 필수 구현)

> 코딩 에이전트는 아래 테스트 케이스를 **반드시** 구현해야 합니다.
> 테스트 코드 작성 후 구현 코드를 작성하십시오.

### Integration Tests (API)
| 테스트명 | 요청 | 기대 응답 |
|----------|------|-----------|
| `test_list_folders_empty` | GET /api/folders (폴더 없음) | 200, `{"folders": []}` |
| `test_list_folders_single` | GET /api/folders (1개 등록됨) | 200, 폴더 1개 포함 |
| `test_list_folders_multiple` | GET /api/folders (3개 등록됨) | 200, 폴더 3개 포함 |
| `test_list_folders_order` | GET /api/folders (시간 차 등록) | 200, 최신순 정렬 확인 |

### Edge Case Tests
| 테스트명 | 상황 | 기대 결과 |
|----------|------|-----------|
| `test_list_folders_with_invalid_path` | 등록 후 경로 삭제 | 200, 목록에 포함 (경로 존재 여부 무관) |
| `test_list_folders_response_structure` | 응답 구조 검증 | folders 배열, 각 항목에 id/name/path/created_at 포함 |

---

## 8. 참고 (의사코드)

```python
@app.get("/api/folders")
def list_folders():
    # 전체 폴더 조회 (최신순)
    folders = db.get_all_folders(order_by="created_at DESC")

    return {"folders": folders}
```

---

## 9. 구현 결과 (코딩 에이전트가 작성)

### 생성된 파일
| 파일 경로 | 설명 |
|-----------|------|
| src/routers/folders.py | `list_folders` 응답 모델 변경 및 구현 |
| src/repositories/folder_repository.py | `find_all` 정렬 로직 추가 |
| src/schemas/folder.py | `FolderListResponse` 추가 |
| tests/test_folder_list.py | API 통합 테스트 및 엣지 케이스 테스트 |

### 테스트 결과
- 총 5개 / 통과 5개 / 실패 0개

### 특이사항
- `datetime.utcnow()` 사용으로 인한 DeprecationWarning 발생 (추후 수정 필요)
- `created_at` 기준 정렬 보장을 위해 테스트 코드에서 명시적 시간 설정 사용

### 변경 이력
| 날짜 | 작업자 | 내용 |
|------|--------|------|
| 2025-01-21 | - | 초안 작성 |
| 2026-01-21 | Antigravity | 폴더 목록 조회 API 구현 및 테스트 작성 |
