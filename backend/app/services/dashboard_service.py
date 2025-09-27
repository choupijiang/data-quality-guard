from sqlalchemy import func
from app.models.models import Project, InspectionResult, InspectionTask
from app.schemas.schemas import ProjectStatistics
from typing import List, Dict, Any

class DashboardService:
    def __init__(self, db_session_factory):
        self.db_session_factory = db_session_factory
    
    def get_project_statistics(self) -> List[Dict[str, Any]]:
        db = self.db_session_factory()
        try:
            # Get all projects with their task statistics
            projects = db.query(Project).all()
            statistics = []
            
            for project in projects:
                # Get all tasks for this project
                tasks = db.query(InspectionTask).filter(InspectionTask.project_id == project.id).all()
                task_ids = [task.id for task in tasks]
                
                total_tasks = len(tasks)
                
                # Count all execution results for this project's tasks
                if task_ids:
                    total_executions = db.query(InspectionResult).filter(
                        InspectionResult.task_id.in_(task_ids)
                    ).count()
                    
                    successful_executions = db.query(InspectionResult).filter(
                        InspectionResult.task_id.in_(task_ids),
                        InspectionResult.check_passed == True
                    ).count()
                    
                    failed_executions = db.query(InspectionResult).filter(
                        InspectionResult.task_id.in_(task_ids),
                        InspectionResult.check_passed == False
                    ).count()
                else:
                    total_executions = 0
                    successful_executions = 0
                    failed_executions = 0
                
                statistics.append({
                    "project_id": project.id,
                    "project_name": project.name,
                    "total_tasks": total_tasks,
                    "successful_tasks": successful_executions,
                    "failed_tasks": failed_executions,
                    "total_executions": total_executions,
                    "success_rate": (successful_executions / total_executions * 100) if total_executions > 0 else 0
                })
            
            return statistics
        finally:
            db.close()
    
    def get_global_statistics(self) -> Dict[str, Any]:
        db = self.db_session_factory()
        try:
            # Get global statistics
            total_projects = db.query(Project).count()
            total_tasks = db.query(InspectionTask).count()
            
            # Count only inspection results that have existing tasks (JOIN to avoid orphaned records)
            existing_task_ids = db.query(InspectionTask.id).all()
            existing_task_ids = [task_id[0] for task_id in existing_task_ids]
            
            if existing_task_ids:
                total_results = db.query(InspectionResult).filter(
                    InspectionResult.task_id.in_(existing_task_ids)
                ).count()
                
                successful_tasks = db.query(InspectionResult).filter(
                    InspectionResult.task_id.in_(existing_task_ids),
                    InspectionResult.check_passed == True
                ).count()
                
                failed_tasks = db.query(InspectionResult).filter(
                    InspectionResult.task_id.in_(existing_task_ids),
                    InspectionResult.check_passed == False
                ).count()
            else:
                total_results = 0
                successful_tasks = 0
                failed_tasks = 0
            
            return {
                "total_projects": total_projects,
                "total_tasks": total_tasks,
                "successful_tasks": successful_tasks,
                "failed_tasks": failed_tasks,
                "total_results": total_results,
                "overall_success_rate": (successful_tasks / total_results * 100) if total_results > 0 else 0
            }
        finally:
            db.close()