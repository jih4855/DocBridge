# MarkdownViewer 컴포넌트 스펙

## 1. 개요
- **목적:** 마크다운 형식의 명세서 내용을 HTML로 렌더링하여 사용자에게 표시
- **담당:** Frontend
- **상태:** 🔵 검토중

---

## 2. 연관 자료
- PRD: [PRD.md](../PRD.md) - 섹션 4.3 (마크다운 뷰어)
- 관련 컴포넌트: [Sidebar.md](./sidebar.md) (파일 선택 시 내용 전달)

---

## 3. 요구사항

### 3.1 핵심 기능
- **Standard Markdown:** GFM (GitHub Flavored Markdown) 스펙 준수 (표, 리스트, 인용구 등)
- **Code Highlighting:** 코드 블록에 대한 Syntax Highlighting 지원 (PrismJS, Highlight.js 등)
- **Diagram Rendering:** **Mermaid.js** 코드 블록을 감지하여 다이어그램으로 변환 렌더링 (필수)
- **Copy Code:** 코드 블록 우측 상단에 복사 버튼 제공

### 3.2 스타일링
- `typography` 플러그인(Tailwind)을 사용하여 가독성 높은 문서 스타일 적용
- 다크 모드에 최적화된 색상 테마

### [참고] 권장 다이어그램 활용 (Mermaid)
| 유형 | 목적 | 활용 예시 |
|------|------|-----------|
| `flowchart` | 비즈니스 로직, 프로세스 흐름 | 로그인 처리 절차, 데이터 검증 흐름 |
| `sequenceDiagram` | 컴포넌트/객체 간 상호작용 | 프론트-백엔드 API 통신, 웹소켓 메시지 교환 |
| `block-beta` | **UI 레이아웃, 와이어프레임** | 페이지 전체 구조 배치 (헤더/사이드바/메인) |
| `stateDiagram` | 상태 변화 관리 | 모달 오픈/클로즈, 데이터 로딩/성공/실패 상태 |

---

## 4. 컴포넌트 명세

### 기본 정보
- **Path:** `src/components/MarkdownViewer`
- **Type:** Client Component (Mermaid 등 브라우저 API 사용)

### Props (Interface)
| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| content | string | O | 렌더링할 마크다운 원문 텍스트 |
| className | string | X | 추가 스타일링 클래스 |

### Dependencies
- `react-markdown` 또는 `next-mdx-remote`: 마크다운 파싱
- `mermaid`: 다이어그램 렌더링
- `rehype-highlight` / `rehype-raw`: 구문 강조 및 HTML 허용
- `@tailwindcss/typography`: 문서 스타일링 (`prose` 클래스)

---

## 5. 비즈니스 로직 (Rendering Flow)

```
1. [Input] content prop으로 마크다운 텍스트 수신
2. [Parsing] 마크다운 -> HTML AST 변환
3. [Filtering]
   - 코드 블록 중 언어가 `mermaid`인 경우 별도 처리
   - 일반 코드는 Syntax Highlighting 적용
4. [Mermaid Init]
   - 컴포넌트 마운트/업데이트 시 `mermaid.initialize()` 호출
   - `mermaid.run()`으로 `.mermaid` 클래스를 가진 요소를 SVG로 변환
5. [Display] 최종 렌더링
```

---

## 6. 엣지 케이스
- [ ] **빈 내용:** "내용이 없습니다" 메시지 표시 또는 빈 화면
- [ ] **잘못된 문법:** 마크다운 파싱 에러 시 원문 그대로 표시 (Crash 방지)
- [ ] **Mermaid 문법 오류:** 렌더링 실패 시 붉은색 에러 박스 표시 (라이브러리 기본 동작)
- [ ] **XSS 방지:** 사용자 입력이 아닌 내부 파일이라도 기본적인 스크립트 실행 방지

---

## 7. 테스트 케이스 (TDD - 필수 구현)

> 코딩 에이전트는 아래 테스트 케이스를 **반드시** 구현해야 합니다.

### Unit Tests
| 테스트명 | 상황 | 기대 결과 |
|----------|------|-----------|
| `test_render_heading` | `# Title` 입력 | `<h1>Title</h1>` 렌더링 |
| `test_render_list` | `- item` 입력 | `<ul><li>item</li></ul>` 렌더링 |
| `test_render_mermaid_block` | ` ```mermaid ` 블록 존재 | `<div class="mermaid">` 또는 SVG 렌더링 트리거 확인 |
| `test_code_highlight` | ` ```python ` 블록 존재 | `<code class="language-python">` 렌더링 |

---

## 8. 참고 (의사코드)

```tsx
import ReactMarkdown from 'react-markdown';
import mermaid from 'mermaid';

mermaid.initialize({ startOnLoad: false, theme: 'dark' });

export default function MarkdownViewer({ content }) {
  useEffect(() => {
    mermaid.run({ querySelector: '.mermaid' });
  }, [content]);

  return (
    <div className="prose prose-invert max-w-none">
      <ReactMarkdown
        components={{
          code({ node, inline, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || '');
            const isMermaid = match && match[1] === 'mermaid';

            if (isMermaid) {
              return <div className="mermaid">{String(children).replace(/\n$/, '')}</div>;
            }
            // ... 일반 코드 렌더링
          }
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
```

---

## 9. 구현 결과 (코딩 에이전트가 작성)

### 생성된 파일
| 파일 경로 | 설명 |
|-----------|------|
| `frontend/src/components/MarkdownViewer/MarkdownViewer.tsx` | 구현체 (Mermaid, Syntax Highlighting 포함) |
| `frontend/src/components/MarkdownViewer/index.ts` | Export 파일 |
| `frontend/src/components/MarkdownViewer/MarkdownViewer.test.tsx` | 단위 테스트 (Mocking 적용) |
| `frontend/jest.config.js` | Jest 설정 (Next.js 호환) |
| `frontend/jest.setup.js` | Jest Setup (RTL) |

### 테스트 결과
- 총 5개 / 통과 5개 / 실패 0개

### 특이사항
-

### 변경 이력
| 날짜 | 작업자 | 내용 |
|------|--------|------|
| 2026-01-21 | - | 초안 작성 |
| 2026-01-21 | Antigravity | 구현 완료 (Jest/RTL 환경 구축 포함) |

---

## 10. 활용 가이드 & 참조 (Next Steps)
- **작업 결과물 활용:** 이 컴포넌트는 메인 페이지(`page.tsx`)에서 선택된 파일의 내용을 보여주는 데 사용됨.
- **포맷 공유:** Mermaid 다이어그램 작성법은 팀 전체에 `STYLE_GUIDE.md` 등을 통해 전파 필요.
- **후속 작업:** `FileContentAPI` 구현 후, 실제 파일 내용을 Fetch 해와서 이 컴포넌트에 주입해야 함.
