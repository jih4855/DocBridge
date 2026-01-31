"""
애플리케이션 설정

환경 변수를 통한 설정 관리
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # 기본값은 로컬 개발 환경에 맞춤
    DATA_DIR: str = "./data"
    PROJECT_ROOT: str = "./docbridge"
    WATCHDOG_USE_POLLING: bool = False
    DEBUG: bool = False

    IGNORED_DIRS: frozenset[str] = frozenset({
        'node_modules', '__pycache__', 'venv', '.venv', 'env', '.env', 
        'dist', 'build', 'coverage', '.git', '.vscode', '.idea', '.next'
    })
    
    DENY_LIST: frozenset[str] = frozenset({
        '/', '/etc', '/root', '/bin', '/sbin', '/usr', '/proc', '/sys', '/dev'
    })

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
