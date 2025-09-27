from pydantic_settings import BaseSettings
from typing import Literal

class Settings(BaseSettings):
    PROJECT_NAME: str = "DQ管理系统"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database - SQLite for development, PostgreSQL for production
    DATABASE_URL: str = "sqlite:///./dq.db"
    POSTGRESQL_URL: str = "postgresql://user:password@localhost/dq_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://localhost:5176", "http://localhost:5177", "http://localhost:3000"]
    
    # Task Scheduler Configuration
    SCHEDULER_ENABLED: bool = True
    SCHEDULER_TYPE: Literal["background", "redis", "celery"] = "background"
    REDIS_SCHEDULER_URL: str = "redis://localhost:6379/0"
    MAX_WORKERS: int = 4
    TASK_TIMEOUT: int = 300  # seconds
    
    # Scheduler Performance Settings
    SCHEDULER_MAX_INSTANCES: int = 3
    SCHEDULER_MISFIRE_GRACE_TIME: int = 3600  # seconds
    SCHEDULER_COALESCE: bool = True
    
    # Alert Settings
    ALERT_ENABLED: bool = True
    ALERT_WEBHOOK_URL: str = ""
    
    class Config:
        env_file = ".env"

settings = Settings()