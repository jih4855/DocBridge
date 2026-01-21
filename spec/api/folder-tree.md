# 폴더 트리 조회 API 스펙

## 1. 개요
- **목적:** 특정 등록 폴더의 하위 구조(트리)를 조회
- **담당:** Backend
- **상태:** 검토중

---

## 2. 연관 자료
- PRD: [PRD.md](../PRD.md) - 섹션 7.4
- 관련 API: [folder-list.md](./folder-list.md)
- 관련 컴포넌트: [Sidebar.md](../components/Sidebar.md)

---

## 3. 요구사항
- 등록된 폴더 ID를 받아 해당 폴더의 전체 트리 구조 반환
- 재귀적으로 모든 하위 폴더와 파일 포함
- 폴더/파일 타입 구분
- 이름 기준 알파벳 정렬 (폴더 먼저, 파일 나중)
- 마크다운 파일(.md)만 파일로 표시 (옵션)

---

## 4. API 명세

### Endpoint
- **Method:** GET
- **Path:** `/api/folders/{id}/tree`
- **인증:** None (로컬 전용)

### Path Parameters
| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| id | int | O | 폴더 고유 ID |

### Query Parameters
| 필드 | 타입 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| md_only | boolean | X | false | true면 .md 파일만 포함 |

### Request 예시
```
GET /api/folders/1/tree
GET /api/folders/1/tree?md_only=true
```

### Response (200 OK)
```json
{
  "id": 1,
  "name": "My Project",
  "path": "/data/my-project/spec",
  "tree": {
    "name": "spec",
    "type": "directory",
    "children": [
      {
        "name": "api",
        "type": "directory",
        "children": [
          {
            "name": "auth.md",
            "type": "file",
            "path": "/data/my-project/spec/api/auth.md"
          },
          {
            "name": "user.md",
            "type": "file",
            "path": "/data/my-project/spec/api/user.md"
          }
        ]
      },
      {
        "name": "models",
        "type": "directory",
        "children": []
      },
      {
        "name": "README.md",
        "type": "file",
        "path": "/data/my-project/spec/README.md"
      }
    ]
  }
}
```

### Response 필드 설명
| 필드 | 타입 | 설명 |
|------|------|------|
| id | int | 폴더 고유 ID |
| name | string | 프로젝트 표시명 |
| path | string | 폴더 절대 경로 |
| tree | object | 트리 구조 객체 |
| tree.name | string | 폴더/파일 이름 |
| tree.type | string | `"directory"` 또는 `"file"` |
| tree.children | array | 하위 항목 (directory만 해당) |
| tree.path | string | 파일 절대 경로 (file만 해당) |

### Error Cases
| 상황 | 코드 | 메시지 |
|------|------|--------|
| 존재하지 않는 폴더 ID | 404 | `{ "error": "folder not found" }` |
| 폴더 경로가 더 이상 존재하지 않음 | 404 | `{ "error": "folder path does not exist" }` |
| 잘못된 ID 형식 | 400 | `{ "error": "invalid folder id" }` |

---

## 5. 비즈니스 로직

```
1. 폴더 ID로 DB에서 폴더 정보 조회
2. 폴더가 존재하지 않으면 404 반환
3. 폴더 경로가 실제로 존재하는지 확인
4. 경로가 존재하지 않으면 404 반환
5. 해당 경로의 트리 구조 재귀적으로 생성
   - 각 항목에 대해:
     - 디렉토리면: name, type="directory", children 재귀 호출
     - 파일이면: name, type="file", path
   - md_only=true면 .md 파일만 포함
   - 정렬: 디렉토리 먼저, 그 다음 파일 (알파벳순)
6. 트리 구조 반환
```

---

## 6. 엣지 케이스
- [x] 빈 폴더 → children: [] 반환
- [x] 깊은 중첩 폴더 → 재귀적으로 모두 포함
- [x] 숨김 파일/폴더 (`.`으로 시작) → 제외
- [x] 심볼릭 링크 → 무시 (보안상 이유)
- [x] 권한 없는 폴더 → 건너뛰기 (에러 아님)
- [x] 한글/특수문자 파일명 → 정상 처리

---

## 7. 테스트 케이스 (TDD - 필수 구현)

> 코딩 에이전트는 아래 테스트 케이스를 **반드시** 구현해야 합니다.
> 테스트 코드 작성 후 구현 코드를 작성하십시오.

### Integration Tests (API)
| 테스트명 | 요청 | 기대 응답 |
|----------|------|-----------|
| `test_get_tree_success` | GET /api/folders/1/tree | 200, 트리 구조 반환 |
| `test_get_tree_not_found` | GET /api/folders/999/tree | 404, `folder not found` |
| `test_get_tree_path_deleted` | 경로 삭제 후 조회 | 404, `folder path does not exist` |
| `test_get_tree_invalid_id` | GET /api/folders/abc/tree | 400, `invalid folder id` |

### Unit Tests (Tree Builder)
| 테스트명 | 입력 | 기대 결과 |
|----------|------|-----------|
| `test_build_tree_empty_folder` | 빈 폴더 | `{ children: [] }` |
| `test_build_tree_files_only` | 파일만 있는 폴더 | 파일 목록 (type: file) |
| `test_build_tree_nested` | 중첩 폴더 | 재귀 구조 |
| `test_build_tree_sorting` | 혼합 항목 | 폴더 먼저, 파일 나중, 알파벳순 |
| `test_build_tree_md_only` | md_only=true | .md 파일만 포함 |

### Edge Case Tests
| 테스트명 | 상황 | 기대 결과 |
|----------|------|-----------|
| `test_tree_hidden_files_excluded` | 숨김 파일 존재 | 숨김 파일 제외 |
| `test_tree_korean_filename` | 한글 파일명 | 정상 처리 |
| `test_tree_special_chars` | 특수문자 파일명 | 정상 처리 |
| `test_tree_symlink_ignored` | 심볼릭 링크 | 무시 |

---

## 8. 참고 (의사코드)

```python
@app.get("/api/folders/{folder_id}/tree")
def get_folder_tree(folder_id: int, md_only: bool = False):
    # 폴더 조회
    folder = db.get_folder(folder_id)
    if not folder:
        raise HTTPException(404, "folder not found")

    # 경로 존재 확인
    if not os.path.exists(folder.path):
        raise HTTPException(404, "folder path does not exist")

    # 트리 구조 생성
    tree = build_tree(folder.path, md_only)

    return {
        "id": folder.id,
        "name": folder.name,
        "path": folder.path,
        "tree": tree
    }

def build_tree(path: str, md_only: bool) -> dict:
    name = os.path.basename(path)

    if os.path.isfile(path):
        return {"name": name, "type": "file", "path": path}

    children = []
    items = sorted(os.listdir(path))

    # 폴더 먼저, 파일 나중
    dirs = [i for i in items if os.path.isdir(os.path.join(path, i))]
    files = [i for i in items if os.path.isfile(os.path.join(path, i))]

    for item in dirs + files:
        if item.startswith("."):  # 숨김 파일 제외
            continue
        if os.path.islink(os.path.join(path, item)):  # 심볼릭 링크 제외
            continue

        full_path = os.path.join(path, item)

        if os.path.isdir(full_path):
            children.append(build_tree(full_path, md_only))
        elif not md_only or item.endswith(".md"):
            children.append({
                "name": item,
                "type": "file",
                "path": full_path
            })

    return {"name": name, "type": "directory", "children": children}
```

---

## 9. 구현 결과 (코딩 에이전트가 작성)

### 생성된 파일
| 파일 경로 | 설명 |
|-----------|------|
| app/schemas/folder.py | TreeNode, FolderTreeResponse 스키마 추가 |
| app/utils/tree_builder.py | 트리 구조 생성 유틸리티 |
| app/api/folders.py | GET /api/folders/{id}/tree 엔드포인트 추가 |
| app/services/folder_service.py | get_folder_by_id 메서드 추가 |
| tests/test_folder_tree.py | TDD 테스트 코드 (13개) |

### 테스트 결과
- 총 13개 / 통과 13개 / 실패 0개

### 특이사항
- 폴더 먼저, 파일 나중 (알파벳순 정렬)
- 숨김 파일/폴더 (.으로 시작) 자동 제외
- 심볼릭 링크 무시 (보안)
- md_only 쿼리 파라미터로 .md 파일만 필터 가능

### 변경 이력
| 날짜 | 작업자 | 내용 |
|------|--------|------|
| 2025-01-21 | - | 초안 작성 |
| 2025-01-21 | AI | TDD 방식으로 구현 완료 |
