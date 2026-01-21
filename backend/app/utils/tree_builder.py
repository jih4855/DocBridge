"""
트리 빌더 유틸리티

폴더 경로로부터 트리 구조 생성
Spec: spec/api/folder-tree.md
"""

import os
from pathlib import Path

from app.schemas.folder import TreeNode


def build_tree(path: str, md_only: bool = False) -> TreeNode:
    """
    폴더 경로의 트리 구조 생성

    Args:
        path: 폴더 절대 경로
        md_only: True면 .md 파일만 포함

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

        child = build_tree(str(item), md_only)
        children.append(child)

    # 파일 처리
    for item in files:
        # 숨김 파일 제외
        if item.name.startswith("."):
            continue

        # md_only 필터
        if md_only and not item.name.endswith(".md"):
            continue

        children.append(
            TreeNode(
                name=item.name,
                type="file",
                path=str(item),
            )
        )

    return TreeNode(name=name, type="directory", children=children)
