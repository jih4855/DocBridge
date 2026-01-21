# Sidebar WebSocket Refactor Implementing Report

## 참조 스펙
- [Sidebar Component Spec](../components/Sidebar.md)
- [File Watch WebSocket Spec](../api/file-watch-websocket.md)

## 구현 내용

### 주요 변경 사항
기존의 파일 변경 감지 시 **전체 프로젝트 목록을 다시 로드(`loadFolders`)** 하는 방식에서, **변경된 프로젝트(`folder_id`)만 타겟팅하여 트리를 부분 갱신**하는 방식으로 리팩토링했습니다.

### 수정된 파일
| 파일 경로 | 변경 내용 |
|-----------|------|
| `frontend/src/components/Sidebar/index.tsx` | WebSocket 이벤트에서 `folder_id`를 추출하여 `refreshTriggers` 상태 업데이트 |
| `frontend/src/components/Sidebar/ProjectList.tsx` | `refreshTriggers` prop을 받아 각 `ProjectItem`에 전달 |
| `frontend/src/components/Sidebar/ProjectItem.tsx` | `refreshTrigger` 변경 시 해당 프로젝트가 `expanded` 상태일 경우에만 트리 데이터 재요청 (`loadTree`) |

## 개선 효과
1.  **UX 향상:** 파일이 변경되어도 사이드바 전체가 깜빡이거나 스크롤/펼침 상태가 초기화되지 않음.
2.  **성능 최적화:** 불필요한 네트워크 요청(전체 목록 조회) 및 리렌더링 제거.

## 테스트 결과
- 수동 테스트 완료:
    - [x] 파일 생성/삭제 시 해당 프로젝트 트리만 즉시 반영됨
    - [x] 다른 프로젝트 트리는 영향받지 않음
    - [x] 사이드바 스크롤 위치 유지됨

## 변경 이력
| 날짜 | 작업자 | 내용 |
|------|--------|------|
| 2026-01-21 | Gemini | Global Reload에서 Granular Key Update 방식으로 리팩토링 |
