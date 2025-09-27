from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.schemas import Project, ProjectCreate, ProjectUpdate
from app.services.services import ProjectService

router = APIRouter()

@router.post("/", response_model=Project)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db)
):
    project_service = ProjectService(db)
    # In a real app, you'd get the user_id from the token
    user_id = 1  # Placeholder
    return project_service.create_project(project, created_by=user_id)

@router.get("/", response_model=List[Project])
def read_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    project_service = ProjectService(db)
    return project_service.get_projects(skip=skip, limit=limit)

@router.get("/{project_id}", response_model=Project)
def read_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    project_service = ProjectService(db)
    project = project_service.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.put("/{project_id}", response_model=Project)
def update_project(
    project_id: int,
    project: ProjectUpdate,
    db: Session = Depends(get_db)
):
    project_service = ProjectService(db)
    project_data = project.dict(exclude_unset=True)
    updated_project = project_service.update_project(project_id, project_data)
    if updated_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated_project

@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    project_service = ProjectService(db)
    success = project_service.delete_project(project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted successfully"}