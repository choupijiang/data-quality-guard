from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.rbac import require_system_admin
from app.models.models import User
from app.schemas.schemas import User as UserSchema, UserCreate, UserUpdate, UserProjectPermission as UserProjectPermissionSchema, UserProjectPermissionCreate, UserProjectPermissionAssign
from app.services.services import UserService

router = APIRouter()

@router.get("/", response_model=List[UserSchema])
def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_system_admin),
    db: Session = Depends(get_db)
):
    """Get all users (System admin only)"""
    user_service = UserService(db)
    return user_service.get_users(skip=skip, limit=limit)

@router.get("/{user_id}", response_model=UserSchema)
def get_user(
    user_id: int,
    current_user: User = Depends(require_system_admin),
    db: Session = Depends(get_db)
):
    """Get specific user (System admin only)"""
    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.put("/{user_id}", response_model=UserSchema)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(require_system_admin),
    db: Session = Depends(get_db)
):
    """Update user (System admin only)"""
    user_service = UserService(db)
    
    # Get target user to check if it's admin
    target_user = user_service.get_user_by_id(user_id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent changing admin user's role or disabling admin account
    if target_user.username == "admin":
        # Only allow safe fields to be updated for admin
        if user_update.role is not None and user_update.role != target_user.role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot change admin user role"
            )
        if user_update.is_active is not None and user_update.is_active == False:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot disable admin user"
            )
    
    user = user_service.update_user(user_id, user_update)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(require_system_admin),
    db: Session = Depends(get_db)
):
    """Delete user (System admin only)"""
    user_service = UserService(db)
    
    # Prevent deletion of admin user for security
    target_user = user_service.get_user_by_id(user_id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if target_user.username == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete the admin superuser"
        )
    
    if not user_service.delete_user(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return {"message": "User deleted successfully"}

@router.post("/{user_id}/permissions")
def assign_project_permissions(
    user_id: int,
    permission: UserProjectPermissionCreate,
    current_user: User = Depends(require_system_admin),
    db: Session = Depends(get_db)
):
    """批量分配项目权限给用户 (System admin only)"""
    user_service = UserService(db)
    
    # 获取用户当前权限
    current_permissions = user_service.get_user_project_permissions(user_id)
    current_project_ids = {p.project_id for p in current_permissions}
    
    # 计算需要添加和删除的权限
    target_project_ids = set(permission.project_ids)
    to_add = target_project_ids - current_project_ids
    to_remove = current_project_ids - target_project_ids
    
    # 删除不需要的权限
    for project_id in to_remove:
        user_service.remove_project_permission(user_id, project_id)
    
    # 添加新权限
    added_permissions = []
    for project_id in to_add:
        perm = user_service.assign_project_permission(user_id, project_id)
        added_permissions.append(perm)
    
    # 返回更新后的权限列表
    updated_permissions = user_service.get_user_project_permissions(user_id)
    return {
        "message": f"成功更新 {len(added_permissions)} 个项目权限",
        "permissions": updated_permissions,
        "added": len(to_add),
        "removed": len(to_remove)
    }

@router.delete("/{user_id}/permissions/{project_id}")
def remove_project_permission(
    user_id: int,
    project_id: int,
    current_user: User = Depends(require_system_admin),
    db: Session = Depends(get_db)
):
    """Remove project permission from user (System admin only)"""
    user_service = UserService(db)
    if not user_service.remove_project_permission(user_id, project_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    return {"message": "Permission removed successfully"}

@router.get("/{user_id}/permissions", response_model=List[UserProjectPermissionSchema])
def get_user_permissions(
    user_id: int,
    current_user: User = Depends(require_system_admin),
    db: Session = Depends(get_db)
):
    """Get user's project permissions (System admin only)"""
    user_service = UserService(db)
    return user_service.get_user_project_permissions(user_id)

@router.put("/me", response_model=UserSchema)
def update_my_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's own profile"""
    user_service = UserService(db)
    
    # Users can only update their own email and password
    # Prevent users from changing their own role or username
    if user_update.username is not None and user_update.username != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot change username"
        )
    
    if user_update.role is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot change role"
        )
    
    if user_update.is_active is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot change active status"
        )
    
    # Only allow updating email and password
    update_data = UserUpdate(
        email=user_update.email,
        password=user_update.password
    )
    
    user = user_service.update_user(current_user.id, update_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user