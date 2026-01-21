"""
애플리케이션 설정

환경 변수를 통한 설정 관리
"""

import os


class Settings:
    """애플리케이션 설정"""

    @property
    def DATA_DIR(self) -> str:
        return os.environ.get("DATA_DIR", "/app/data")

    @property
    def PROJECT_ROOT(self) -> str:
        return os.environ.get("PROJECT_ROOT", "/data")


settings = Settings()
