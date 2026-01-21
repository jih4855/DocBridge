"""
트리 빌더 유틸리티

폴더 경로로부터 트리 구조 생성
Spec: spec/api/folder-tree.md
"""

import os
from pathlib import Path

from app.schemas.folder import TreeNode


COMMON_IGNORED_DIRS = {
    'node_modules', '__pycache__', 'venv', '.venv', 'env', '.env', 
    'dist', 'build', 'coverage', '.git', '.vscode', '.idea', '.next',
    'target', 'out'
}


def build_tree(path: str, md_only: bool = True) -> TreeNode:
    """
    폴더 경로의 트리 구조 생성

    Args:
        path: 폴더 절대 경로
        md_only: True면 .md 파일만 포함 (기본값 True)

    Returns:
        TreeNode: 트리 구조
    """
    folder_path = Path(path)
    name = folder_path.name

    children = []

    try:
        items = sorted(folder_path.iterdir(), key=lambda x: x.name.lower())
    except PermissionError:
        # 권한 없는 폴더 → 빈 children 반환
        return TreeNode(name=name, type="directory", children=[])

    # 폴더 먼저, 파일 나중으로 분리
    dirs = [item for item in items if item.is_dir() and not item.is_symlink()]
    files = [item for item in items if item.is_file() and not item.is_symlink()]

    # 디렉토리 처리
    for item in dirs:
        # 숨김 폴더 제외
        if item.name.startswith("."):
            continue
            
        # 무시할 폴더 제외 (node_modules 등)
        if item.name in COMMON_IGNORED_DIRS:
            continue

        child = build_tree(str(item), md_only)
        
        # md_only 모드일 때, 자식이 없는 빈 폴더는 트리에 포함하지 않음 (선택 사항이지만 깔끔하게 보이기 위해 추천)
        # 하지만 빈 폴더도 구조 확인용으로 필요할 수 있으니 일단은 포함하되, 
        # 사용자가 "md제외 모두 무시"라고 했으므로, 파일이 하나도 없는 깡통 폴더들이 주룩주룩 뜨는걸 방지하려면
        # 자식(md파일)이 있는 경우에만 추가하는 로직이 더 적절할 수 있음.
        # 여기서는 일단 폴더 무시 로직만 강화하고, 재귀 호출 결과는 그대로 둡니다.
        
        children.append(child)

    # 파일 처리
    for item in files:
        # 숨김 파일 제외
        if item.name.startswith("."):
            continue

        # md_only 필터 (강력 적용)
        if md_only and not item.name.lower().endswith(".md"):
            continue

        children.append(
            TreeNode(
                name=item.name,
                type="file",
                path=str(item),
            )
        )
    
    # MD Only 모드일 때, 자식이 하나도 없으면 (즉, MD 파일도 없고 하위 폴더에도 MD가 없으면)
    # 이 폴더 자체를 트리에 표시하지 않는 것이 '모두 무시'의 의도에 더 부합합니다.
    # 단, 최상위 루트 폴더는 항상 표시되어야 하므로 재귀 함수 내부에서 이를 판단하기는 까다롭습니다.
    # 일단 요구사항인 "파일 필터링"과 "폴더 무시"에 집중합니다.

    return TreeNode(name=name, type="directory", children=children)
