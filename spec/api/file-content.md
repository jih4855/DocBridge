# 파일 내용 조회 API 스펙

## 1. 개요
- **목적:** 마크다운 파일의 내용을 조회하여 메인 뷰어에 표시
- **담당:** Backend
- **상태:** 대기

---

## 2. 연관 자료
- PRD: [PRD.md](../PRD.md) - 섹션 7.5
- 관련 API: [folder-tree.md](./folder-tree.md) (트리에서 파일 경로 획득)
- 관련 컴포넌트: MainViewer (파일 내용 렌더링)

---

## 3. 요구사항
- 파일 경로를 받아 해당 파일의 내용을 반환
- 마크다운 파일(.md) 전용
- 파일 경로는 등록된 폴더 하위 경로만 허용 (보안)

---

## 4. API 명세

### Endpoint
- **Method:** GET
- **Path:** `/api/files`
- **인증:** None (로컬 전용)

### Query Parameters
| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| path | string | O | 파일 절대 경로 |

### Request 예시
```
GET /api/files?path=/Users/username/projects/spec/api/auth.md
```

### Response (200 OK)
```json
{
  "content": "# 회원가입 API 스펙\n\n## 1. 개요\n..."
}
```

### Response 필드 설명
| 필드 | 타입 | 설명 |
|------|------|------|
| content | string | 파일 내용 (raw text) |

### Error Cases
| 상황 | 코드 | 메시지 |
|------|------|--------|
| path 파라미터 누락 | 400 | `{ "error": "path is required" }` |
| 파일이 존재하지 않음 | 404 | `{ "error": "file not found" }` |
| 파일이 아닌 디렉토리 | 400 | `{ "error": "path is not a file" }` |
| 마크다운 파일이 아님 | 400 | `{ "error": "only markdown files allowed" }` |
| 허용되지 않은 경로 | 403 | `{ "error": "access denied" }` |

---

## 5. 비즈니스 로직

```
1. path 쿼리 파라미터 추출
2. path 빈 값 체크
3. 경로가 등록된 폴더 하위인지 확인 (보안)
4. 파일 존재 여부 확인
5. 디렉토리가 아닌 파일인지 확인
6. .md 확장자인지 확인
7. 파일 내용 읽기 (UTF-8)
8. 내용 반환
```

---

## 6. 엣지 케이스
- [x] 한글 파일명 → 정상 처리
- [x] 파일 내용에 특수문자/이모지 포함 → 정상 처리
- [x] 빈 파일 → content: "" 반환
- [x] 매우 큰 파일 (10MB 이상) → 제한 또는 경고
- [x] 심볼릭 링크 파일 → 거부 (보안)
- [x] Path Traversal 시도 (../../etc/passwd) → 거부

---

## 7. 테스트 케이스 (TDD - 필수 구현)

> 코딩 에이전트는 아래 테스트 케이스를 **반드시** 구현해야 합니다.
> 테스트 코드 작성 후 구현 코드를 작성하십시오.

### Integration Tests (API)
| 테스트명 | 요청 | 기대 응답 |
|----------|------|-----------|
| `test_get_file_success` | GET /api/files?path=valid.md | 200, 파일 내용 반환 |
| `test_get_file_missing_path` | GET /api/files | 400, `path is required` |
| `test_get_file_not_found` | GET /api/files?path=/invalid.md | 404, `file not found` |
| `test_get_file_is_directory` | GET /api/files?path=/some/dir | 400, `path is not a file` |
| `test_get_file_not_markdown` | GET /api/files?path=/file.txt | 400, `only markdown files allowed` |

### Edge Case Tests
| 테스트명 | 상황 | 기대 결과 |
|----------|------|-----------|
| `test_path_traversal_blocked` | path=../../etc/passwd | 403, `access denied` |
| `test_unregistered_path_blocked` | 등록 안 된 경로 | 403, `access denied` |
| `test_empty_file` | 빈 .md 파일 | 200, `{ "content": "" }` |
| `test_korean_filename` | 한글파일.md | 200, 정상 반환 |
| `test_symlink_blocked` | 심볼릭 링크 파일 | 403, `access denied` |

---

## 8. 참고 (의사코드)

```python
@app.get("/api/files")
def get_file_content(path: str = None):
    # 파라미터 체크
    if not path:
        raise HTTPException(400, "path is required")

    # 보안: 등록된 폴더 하위 경로인지 확인
    if not is_path_allowed(path):
        raise HTTPException(403, "access denied")

    # 심볼릭 링크 체크
    if os.path.islink(path):
        raise HTTPException(403, "access denied")

    # 존재 확인
    if not os.path.exists(path):
        raise HTTPException(404, "file not found")

    # 파일인지 확인
    if not os.path.isfile(path):
        raise HTTPException(400, "path is not a file")

    # 마크다운 확인
    if not path.endswith(".md"):
        raise HTTPException(400, "only markdown files allowed")

    # 파일 읽기
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    return {"content": content}


def is_path_allowed(path: str) -> bool:
    """등록된 폴더 하위 경로인지 확인"""
    registered_folders = db.get_all_folders()
    real_path = os.path.realpath(path)

    for folder in registered_folders:
        folder_real = os.path.realpath(folder.path)
        if real_path.startswith(folder_real + os.sep):
            return True

    return False
```

---

## 9. 구현 결과 (코딩 에이전트가 작성)

### 생성된 파일
| 파일 경로 | 설명 |
|-----------|------|
| [backend/app/api/files.py](file:///Users/jeong-inhyo/docbridge/backend/app/api/files.py) | 파일 내용 조회 API 라우터 (보안 검증 포함) |
| [backend/tests/test_file_content.py](file:///Users/jeong-inhyo/docbridge/backend/tests/test_file_content.py) | API 테스트 코드 (TDD) |

### 테스트 결과
- 총 10개 / 통과 10개 / 실패 0개
- Edge Case 포함 모든 테스트 케이스 통과

### 특이사항
- `response.json()["error"]` 형식으로 에러 응답 통일함 (Spec 준수)

### 변경 이력
| 날짜 | 작업자 | 내용 |
|------|--------|------|
| 2026-01-21 | - | 초안 작성 |
| 2026-01-21 | antigravity | API 구현 및 테스트 완료 |

---

## 10. 활용 가이드 & 참조
- **프론트엔드 연동:** MainViewer 컴포넌트에서 파일 선택 시 이 API 호출
- **응답 타입:** `{ content: string }` - 프론트엔드 타입 정의 필요
- **후속 작업:** 마크다운 렌더링 (react-markdown 등)

---

## 11. 보안 고려사항
- **Path Traversal 방지:** `../` 등을 통한 상위 디렉토리 접근 차단
- **등록 폴더 제한:** 등록된 폴더 하위 경로만 접근 허용
- **심볼릭 링크 차단:** 외부 경로로 연결된 심볼릭 링크 거부
- **파일 크기 제한:** 10MB 이상 파일은 거부 또는 경고 (선택사항)
