# Sidebar 컴포넌트 스펙

## 1. 개요
- **목적:** 등록된 프로젝트 폴더 목록을 표시하고, 선택 시 하위 파일 트리를 탐색하여 명세서를 선택
- **담당:** Frontend
- **상태:** 🔵 검토중

---

## 2. 연관 자료
- PRD: [PRD.md](../PRD.md) - 섹션 4.2 (사이드바 트리 구조)
- 관련 API:
  - [folder-list.md](../api/folder-list.md)
  - [folder-tree.md](../api/folder-tree.md)
  - [folder-delete.md](../api/folder-delete.md)

---

## 3. 요구사항
- **프로젝트 목록:** 등록된 모든 최상위 폴더(프로젝트) 표시
- **트리 탐색:**
  - 폴더 클릭 시 하위 목록 펼침/접기 (Toggle)
  - 필요한 시점에 서버에서 트리 데이터 로드 (Lazy Loading 지원)
- **파일 선택:** 파일 클릭 시 메인 뷰어에 활성화 (Active 상태 표시)
- **아이콘 구분:** 폴더, 일반 파일, 마크다운 파일(.md) 아이콘 구분
- **삭제 기능:** 프로젝트(루트 폴더)에 대한 삭제 버튼 제공
- **등록 연동:** 최상단 `[+]` 버튼으로 폴더 등록 모달 호출

---

## 4. 컴포넌트 명세

### 기본 정보
- **Path:** `src/components/Sidebar`
- **Type:** Server Component + Client Component (Hybrid)

### Props (Interface)
| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| className | string | X | 추가 스타일링 클래스 |

### Global State (Zustand/Context)
| 상태명 | 타입 | 설명 |
|--------|------|------|
| `selectedFile` | object | 현재 선택된 파일 정보 (path, name) |
| `isRegisterModalOpen` | boolean | 폴더 등록 모달 표시 여부 |
| `refreshTrigger` | number | 목록 새로고침 트리거 |

### UI Events
| 이벤트명 | 트리거 | 동작 |
|----------|--------|------|
| `onToggleFolder` | 폴더 클릭 | `GET /api/folders/{id}/tree` 호출 및 `expanded` 상태 토글 |
| `onSelectFile` | 파일 클릭 | `selectedFile` 전역 상태 업데이트 |
| `onDeleteProject` | 삭제 아이콘 클릭 | `DELETE /api/folders/{id}` 호출 및 목록 갱신 |
| `onOpenRegister` | [+] 버튼 클릭 | `isRegisterModalOpen = true` |

---

## 5. 비즈니스 로직 (UI Flow)

```
1. [초기 로드]
   - 컴포넌트 마운트 시 `GET /api/folders` 호출
   - 프로젝트 목록 렌더링

2. [폴더 클릭]
   - 이미 로드된 트리 데이터가 있는지 확인
   - (No) `GET /api/folders/{id}/tree` API 호출 -> 자식 노드 렌더링
   - (Yes) `expanded` 상태 토글 (펼치기/접기)

3. [파일 클릭]
   - 해당 파일의 경로(path)를 `selectedFile` 상태로 설정
   - UI에서 해당 항목 Highlight 처리

4. [프로젝트 삭제]
   - 삭제 아이콘 클릭 -> "삭제하시겠습니까?" 컨펌
   - `DELETE /api/folders/{id}` API 호출
   - 성공 시 프로젝트 목록 다시 로드
```

---

## 6. 컴포넌트 구조

### File Structure
```
src/components/Sidebar/
├── index.tsx              # 메인 컨테이너 (데이터 Fetching)
├── SidebarHeader.tsx      # 로고 및 등록 버튼
├── ProjectList.tsx        # 프로젝트 목록 렌더링
├── ProjectItem.tsx        # 개별 프로젝트 항목 (삭제 버튼 포함)
├── FileTree.tsx           # 재귀적 트리 렌더링
└── FileTreeItem.tsx       # 파일/폴더 UI (아이콘, 들여쓰기)
```

### Style Guide (Tailwind)
- **Width:** `w-64` ~ `w-80` (Fixed or Resizable)
- **Background:** `bg-gray-50` (Light), `bg-gray-900` (Dark)
- **Item Hover:** `hover:bg-gray-200`
- **Item Active:** `bg-blue-100` text `blue-600`

---

## 7. 엣지 케이스
- [ ] **등록된 폴더 없음:** "등록된 프로젝트가 없습니다." 메시지 및 등록 유도 UI 표시
- [ ] **긴 파일명:** 한 줄 말줄임표(`text-ellipsis`) 처리 + Tooltip(`title` 속성)
- [ ] **네트워크 에러:** 목록 로드 실패 시 "재시도" 버튼 표시
- [ ] **삭제된 경로:** API에서 트리를 못 가져올 경우(404), 에러 아이콘 표시

---

## 8. 테스트 케이스 (TDD - 필수 구현)

> 코딩 에이전트는 아래 테스트 케이스를 **반드시** 구현해야 합니다.

### Unit Tests
| 테스트명 | 상황 | 기대 결과 |
|----------|------|-----------|
| `test_sidebar_render_empty` | 폴더 목록 비어있음 | "프로젝트 없음" 메시지 표시 |
| `test_sidebar_render_list` | 폴더 목록 데이터 있음 | 프로젝트 이름 리스트 렌더링 |
| `test_file_tree_item_icon` | 파일 확장자가 .md | 마크다운 아이콘(Ⓜ️) 표시 |
| `test_file_tree_item_indent` | 깊이(depth) prop 전달 | 깊이에 비례한 padding-left 적용 |

### Integration Tests (Interaction)
| 테스트명 | 액션 | 기대 결과 |
|----------|------|-----------|
| `test_toggle_folder` | 닫힌 폴더 클릭 | 하위 트리 API 호출 & 펼쳐짐 |
| `test_select_file` | 파일 클릭 | `onSelectFile` 호출 & Active 스타일 적용 |
| `test_delete_project` | 삭제 버튼 클릭 & 확인 | 삭제 API 호출 & 목록에서 제거 |

---

## 9. 참고 (의사코드)

```tsx
// src/components/Sidebar/index.tsx
export default function Sidebar() {
  const { data: folders } = useQuery(['folders'], fetchFolders);
  
  return (
    <aside className="w-64 h-screen border-r flex flex-col">
      <SidebarHeader />
      <div className="flex-1 overflow-y-auto">
        {folders?.length === 0 ? (
          <EmptyState />
        ) : (
          folders.map(folder => (
            <ProjectItem key={folder.id} folder={folder} />
          ))
        )}
      </div>
      <FolderRegisterModal />
    </aside>
  );
}
```

---

## 10. 구현 결과 (코딩 에이전트가 작성)

### 생성된 파일
| 파일 경로 | 설명 |
|-----------|------|
| `src/components/Sidebar/index.tsx` | 메인 컨테이너 + WebSocket 연결 |
| `src/components/Sidebar/SidebarHeader.tsx` | 로고 및 등록 버튼 |
| `src/components/Sidebar/ProjectList.tsx` | 프로젝트 목록 렌더링 |
| `src/components/Sidebar/ProjectItem.tsx` | 개별 프로젝트 항목 |
| `src/components/Sidebar/FileTree.tsx` | 재귀적 트리 렌더링 |
| `src/components/Sidebar/FileTreeItem.tsx` | 파일/폴더 UI |

### WebSocket 연동
- **엔드포인트:** `ws://localhost:8000/ws/watch`
- **동작:** 
    - .md 파일 변경 시 **해당 프로젝트의 트리만** 부분적으로 새로고침 (`refreshTrigger` 사용)
    - 사용자 UI 상태(스크롤, 펼침 등) 유지
- **환경변수:** `NEXT_PUBLIC_WS_URL`로 URL 변경 가능

### 테스트 결과
- 총 1개 / 통과 1개 / 실패 0개

### 특이사항
- WebSocket 연결 실패 시에도 수동 새로고침 가능 (graceful degradation)
- `folder_id`를 기반으로 변경된 프로젝트만 타겟팅하여 불필요한 리렌더링 방지

### 변경 이력
| 날짜 | 작업자 | 내용 |
|------|--------|------|
| 2026-01-21 | Gemini | WebSocket 실시간 새로고침 추가 |
| 2026-01-21 | - | 초안 작성 |

