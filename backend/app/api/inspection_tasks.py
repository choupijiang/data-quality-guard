import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.schemas import InspectionTask, InspectionTaskCreate, InspectionTaskUpdate, InspectionResult
from app.services.services import InspectionTaskService
from app.models.models import User

router = APIRouter()
logger = logging.getLogger(__name__)

@router.on_event("startup")
async def startup_event():
    logger.info("Inspection tasks API router initialized")

@router.post("/", response_model=InspectionTask)
def create_task(
    task: InspectionTaskCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    task_service = InspectionTaskService(db)
    # In a real app, you'd get the user_id from the token
    user_id = 1  # Placeholder
    
    # 创建任务
    created_task = task_service.create_task(task, created_by=user_id)
    
    # 如果任务有调度配置且状态为active，添加到调度器
    if task.cron_schedule and task.status == 'active':
        try:
            scheduler_manager = request.app.state.scheduler_manager
            scheduler = scheduler_manager.get_scheduler()
            if scheduler:
                scheduler.add_task(created_task.id, task.cron_schedule, task.name)
                logger.info(f"Added task {created_task.id} to scheduler")
        except Exception as e:
            logger.error(f"Failed to add task {created_task.id} to scheduler: {e}")
            # 不影响任务创建，只记录错误
    
    return created_task

@router.get("/", response_model=List[InspectionTask])
def read_tasks(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    logger.info(f"Fetching inspection tasks for user {current_user.username} with skip={skip}, limit={limit}")
    task_service = InspectionTaskService(db)
    try:
        # 如果是系统管理员，可以看到所有任务
        if current_user.role == "SYSTEM_ADMIN":
            result = task_service.get_tasks(skip=skip, limit=limit)
        else:
            # 普通用户只能看到自己有权限的项目下的任务
            result = task_service.get_tasks_by_user_permissions(current_user.id, skip=skip, limit=limit)
        logger.info(f"Successfully fetched {len(result)} inspection tasks for user {current_user.username}")
        return result
    except Exception as e:
        logger.error(f"Error fetching inspection tasks: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/{task_id}", response_model=InspectionTask)
def read_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task_service = InspectionTaskService(db)
    task = task_service.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # 权限检查：系统管理员可以看到所有任务，普通用户只能看到有权限的项目下的任务
    if current_user.role != "SYSTEM_ADMIN":
        user_tasks = task_service.get_tasks_by_user_permissions(current_user.id)
        if not any(t.id == task_id for t in user_tasks):
            raise HTTPException(status_code=403, detail="You don't have permission to access this task")
    
    return task

@router.put("/{task_id}", response_model=InspectionTask)
def update_task(
    task_id: int,
    task: InspectionTaskUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    task_service = InspectionTaskService(db)
    try:
        updated_task = task_service.update_task(task_id, task)
        
        # 同步更新调度器
        try:
            scheduler_manager = request.app.state.scheduler_manager
            scheduler = scheduler_manager.get_scheduler()
            if scheduler:
                # 先移除旧的任务
                scheduler.remove_task(task_id)
                
                # 如果任务有调度配置且状态为active，重新添加到调度器
                if updated_task.cron_schedule and updated_task.status == 'active':
                    scheduler.add_task(task_id, updated_task.cron_schedule, updated_task.name)
                    logger.info(f"Updated task {task_id} in scheduler")
        except Exception as e:
            logger.error(f"Failed to update task {task_id} in scheduler: {e}")
            # 不影响任务更新，只记录错误
        
        return updated_task
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{task_id}/execute", response_model=InspectionResult)
def execute_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    task_service = InspectionTaskService(db)
    try:
        result = task_service.execute_task(task_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/results/all")
def get_all_results(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取所有任务的执行结果历史"""
    task_service = InspectionTaskService(db)
    results = task_service.get_all_results_with_details(skip=skip, limit=limit)
    return results

@router.get("/stats")
def get_task_stats(
    db: Session = Depends(get_db)
):
    """获取所有任务的统计信息"""
    task_service = InspectionTaskService(db)
    stats = task_service.get_tasks_stats()
    return stats

@router.delete("/results/{result_id}")
def delete_result(
    result_id: int,
    db: Session = Depends(get_db)
):
    """删除指定的执行结果记录"""
    logger.info(f"收到删除执行结果请求, result_id: {result_id}")
    task_service = InspectionTaskService(db)
    try:
        logger.info(f"开始删除执行结果, result_id: {result_id}")
        success = task_service.delete_result(result_id)
        logger.info(f"删除操作结果: {success}, result_id: {result_id}")
        
        if success:
            logger.info(f"执行结果删除成功, result_id: {result_id}")
            return {"message": "Result deleted successfully"}
        else:
            logger.warning(f"执行结果未找到, result_id: {result_id}")
            raise HTTPException(status_code=404, detail="Result not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除执行结果时发生错误, result_id: {result_id}, 错误: {str(e)}")
        logger.error(f"错误类型: {type(e)}")
        import traceback
        logger.error(f"详细错误信息: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    task_service = InspectionTaskService(db)
    try:
        # 先从调度器中移除任务
        try:
            scheduler_manager = request.app.state.scheduler_manager
            scheduler = scheduler_manager.get_scheduler()
            if scheduler:
                scheduler.remove_task(task_id)
                logger.info(f"Removed task {task_id} from scheduler")
        except Exception as e:
            logger.error(f"Failed to remove task {task_id} from scheduler: {e}")
            # 不影响任务删除，只记录错误
        
        # 删除任务
        task_service.delete_task(task_id)
        return {"message": "Task deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{task_id}/results")
def get_task_results(
    task_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取指定任务的执行结果历史"""
    task_service = InspectionTaskService(db)
    try:
        results = task_service.get_task_results_with_details(task_id, skip=skip, limit=limit)
        return results
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{task_id}/stats")
def get_task_stats(
    task_id: int,
    db: Session = Depends(get_db)
):
    """获取指定任务的统计信息"""
    task_service = InspectionTaskService(db)
    try:
        stats = task_service.get_task_stats(task_id)
        return stats
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{task_id}/scheduler-status")
def get_task_scheduler_status(
    task_id: int,
    request: Request
):
    """获取任务在调度器中的状态"""
    try:
        scheduler_manager = request.app.state.scheduler_manager
        scheduler = scheduler_manager.get_scheduler()
        if not scheduler:
            return {
                "task_id": task_id,
                "scheduler_enabled": False,
                "status": "scheduler_not_available"
            }
        
        status = scheduler.get_task_status(task_id)
        return {
            "task_id": task_id,
            "scheduler_enabled": True,
            "scheduler_status": status
        }
    except Exception as e:
        logger.error(f"Failed to get scheduler status for task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{task_id}/reload-scheduler")
def reload_task_scheduler(
    task_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """重新加载任务到调度器"""
    try:
        task_service = InspectionTaskService(db)
        task = task_service.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        scheduler_manager = request.app.state.scheduler_manager
        scheduler = scheduler_manager.get_scheduler()
        if not scheduler:
            raise HTTPException(status_code=400, detail="Scheduler not available")
        
        # 移除旧的任务
        scheduler.remove_task(task_id)
        
        # 如果任务有调度配置且状态为active，重新添加到调度器
        if task.cron_schedule and task.status == 'active':
            scheduler.add_task(task_id, task.cron_schedule, task.name)
            logger.info(f"Reloaded task {task_id} into scheduler")
            return {"message": "Task reloaded into scheduler successfully"}
        else:
            return {"message": "Task not active or no cron schedule, removed from scheduler"}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reload task {task_id} scheduler: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scheduler/status")
def get_scheduler_status(request: Request):
    """获取调度器整体状态"""
    try:
        scheduler_manager = request.app.state.scheduler_manager
        scheduler = scheduler_manager.get_scheduler()
        
        if not scheduler:
            return {
                "scheduler_enabled": False,
                "scheduler_type": None,
                "running": False,
                "tasks": {}
            }
        
        tasks = scheduler.list_tasks()
        return {
            "scheduler_enabled": True,
            "scheduler_type": "background",
            "running": scheduler.is_running,
            "total_tasks": len(tasks),
            "tasks": tasks
        }
    except Exception as e:
        logger.error(f"Failed to get scheduler status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/scheduler/reload-all")
def reload_all_schedulers(
    request: Request,
    db: Session = Depends(get_db)
):
    """重新加载所有活跃任务到调度器"""
    try:
        scheduler_manager = request.app.state.scheduler_manager
        scheduler = scheduler_manager.get_scheduler()
        if not scheduler:
            raise HTTPException(status_code=400, detail="Scheduler not available")
        
        # 获取所有活跃任务
        from app.models.models import InspectionTask
        active_tasks = db.query(InspectionTask).filter(
            InspectionTask.status == 'active'
        ).all()
        
        loaded_count = 0
        for task in active_tasks:
            if task.cron_schedule:
                try:
                    # 移除旧任务
                    scheduler.remove_task(task.id)
                    # 重新添加
                    scheduler.add_task(task.id, task.cron_schedule, task.name)
                    loaded_count += 1
                    logger.info(f"Reloaded task {task.id}: {task.name}")
                except Exception as e:
                    logger.error(f"Failed to reload task {task.id}: {e}")
        
        return {
            "message": f"Reloaded {loaded_count} active tasks into scheduler",
            "total_active_tasks": len(active_tasks),
            "loaded_tasks": loaded_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reload all schedulers: {e}")
        raise HTTPException(status_code=500, detail=str(e))