from sqlalchemy import Boolean, Column, Integer, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base

class UserRole(enum.Enum):
    SYSTEM_ADMIN = "SYSTEM_ADMIN"
    PROJECT_ADMIN = "PROJECT_ADMIN" 
    REGULAR_USER = "REGULAR_USER"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.REGULAR_USER, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    projects = relationship("Project", back_populates="creator")
    data_sources = relationship("DataSource", back_populates="creator")
    inspection_tasks = relationship("InspectionTask", back_populates="creator")

class DataSourceType(enum.Enum):
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    CLICKHOUSE = "clickhouse"
    STARROCKS = "starrocks"

class DataSource(Base):
    __tablename__ = "data_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(10), nullable=False)
    host = Column(String(255), nullable=False)
    port = Column(Integer, nullable=False)
    database = Column(String(100), nullable=False)
    username = Column(String(100), nullable=False)
    password = Column(String(255), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    creator = relationship("User", back_populates="data_sources")
    inspection_tasks = relationship("InspectionTask", back_populates="data_source")

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    status = Column(String(20), default="active")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    creator = relationship("User", back_populates="projects")
    user_permissions = relationship("UserProjectPermission", back_populates="project")

class UserProjectPermission(Base):
    __tablename__ = "user_project_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", backref="project_permissions")
    project = relationship("Project", back_populates="user_permissions")

class InspectionTask(Base):
    __tablename__ = "inspection_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    check_sql = Column(Text, nullable=False)
    expected_sql = Column(Text, nullable=False)
    check_expression = Column(Text, nullable=False)
    cron_schedule = Column(String(100), nullable=False)
    data_source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(20), default="active")
    last_run_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    creator = relationship("User", back_populates="inspection_tasks")
    data_source = relationship("DataSource", back_populates="inspection_tasks")
    project = relationship("Project", backref="inspection_tasks")

class InspectionResult(Base):
    __tablename__ = "inspection_results"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("inspection_tasks.id"), nullable=False)
    check_value = Column(Text)
    expected_value = Column(Text)
    check_passed = Column(Boolean, nullable=False)
    execution_time = Column(DateTime(timezone=True), server_default=func.now())
    error_message = Column(Text)
    
    task = relationship("InspectionTask")