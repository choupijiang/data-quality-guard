from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.models.models import User, UserRole
from app.core.security import get_current_user

security = HTTPBearer()

def require_role(required_role: UserRole):
    """Decorator to require specific user role"""
    def role_checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker

def require_at_least_role(min_role: UserRole):
    """Decorator to require at least specific role level"""
    def role_checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        role_hierarchy = {
            UserRole.REGULAR_USER: 0,
            UserRole.PROJECT_ADMIN: 1,
            UserRole.SYSTEM_ADMIN: 2
        }
        
        if role_hierarchy.get(current_user.role, 0) < role_hierarchy.get(min_role, 0):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker

def require_system_admin(current_user: User = Depends(get_current_user)):
    """Require system admin role"""
    if current_user.role != UserRole.SYSTEM_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="System admin access required"
        )
    return current_user

def require_project_admin_or_system_admin(current_user: User = Depends(get_current_user)):
    """Require project admin or system admin role"""
    if current_user.role not in [UserRole.PROJECT_ADMIN, UserRole.SYSTEM_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Project admin or system admin access required"
        )
    return current_user

def check_project_access(project_id: int):
    """Check if user has access to specific project"""
    def project_access_checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        # System admin has access to all projects
        if current_user.role == UserRole.SYSTEM_ADMIN:
            return current_user
        
        # Project admin has access to all projects
        if current_user.role == UserRole.PROJECT_ADMIN:
            return current_user
        
        # Regular user must have explicit permission
        from app.models.models import UserProjectPermission
        permission = db.query(UserProjectPermission).filter(
            UserProjectPermission.user_id == current_user.id,
            UserProjectPermission.project_id == project_id
        ).first()
        
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No access to this project"
            )
        
        return current_user
    return project_access_checker

def get_accessible_projects(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get list of project IDs user has access to"""
    if current_user.role in [UserRole.SYSTEM_ADMIN, UserRole.PROJECT_ADMIN]:
        # Admins have access to all projects
        from app.models.models import Project
        projects = db.query(Project.id).all()
        return [project.id for project in projects]
    else:
        # Regular users have access to assigned projects only
        from app.models.models import UserProjectPermission
        permissions = db.query(UserProjectPermission.project_id).filter(
            UserProjectPermission.user_id == current_user.id
        ).all()
        return [permission.project_id for permission in permissions]