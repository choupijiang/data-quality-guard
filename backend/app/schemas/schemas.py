from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    SYSTEM_ADMIN = "SYSTEM_ADMIN"
    PROJECT_ADMIN = "PROJECT_ADMIN"
    REGULAR_USER = "REGULAR_USER"

class DataSourceType(str, Enum):
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    CLICKHOUSE = "clickhouse"
    STARROCKS = "starrocks"

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class User(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserProjectPermissionBase(BaseModel):
    user_id: int
    project_id: int

class UserProjectPermissionCreate(BaseModel):
    project_ids: List[int]

class UserProjectPermissionAssign(UserProjectPermissionBase):
    pass

class UserProjectPermission(UserProjectPermissionBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class DataSourceBase(BaseModel):
    name: str
    type: DataSourceType
    host: str
    port: int
    database: str
    username: str
    password: str
    description: Optional[str] = None
    is_active: bool = True

class DataSourceCreate(DataSourceBase):
    pass

class DataSourceUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[DataSourceType] = None
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class DataSource(DataSourceBase):
    id: int
    created_by: int
    created_at: datetime
    status: str = "active"
    
    class Config:
        from_attributes = True

class InspectionTaskBase(BaseModel):
    name: str
    description: Optional[str] = None
    check_sql: str = Field(..., description="SQL query that returns a single value")
    expected_sql: str = Field(..., description="SQL query that returns a single value")
    check_expression: str = Field(..., description="Expression to compare check and expected values")
    cron_schedule: str = Field(..., description="Cron schedule for task execution")
    status: str = "active"

class InspectionTaskCreate(InspectionTaskBase):
    data_source_id: int
    project_id: int

class InspectionTaskUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    check_sql: Optional[str] = None
    expected_sql: Optional[str] = None
    check_expression: Optional[str] = None
    cron_schedule: Optional[str] = None
    status: Optional[str] = None
    data_source_id: Optional[int] = None

class InspectionTask(InspectionTaskBase):
    id: int
    data_source_id: int
    project_id: int
    created_by: int
    last_run_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class InspectionResult(BaseModel):
    id: int
    task_id: int
    check_value: Optional[str] = None
    expected_value: Optional[str] = None
    check_passed: bool
    execution_time: datetime
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: str = "active"

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class Project(ProjectBase):
    id: int
    created_by: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class ConnectionTest(BaseModel):
    type: DataSourceType
    host: str
    port: int
    database: str
    username: str
    password: str

class ProjectStatistics(BaseModel):
    project_id: int
    project_name: str
    total_tasks: int
    successful_tasks: int
    failed_tasks: int
    success_rate: float

class GlobalStatistics(BaseModel):
    total_projects: int
    total_tasks: int
    successful_tasks: int
    failed_tasks: int
    overall_success_rate: float