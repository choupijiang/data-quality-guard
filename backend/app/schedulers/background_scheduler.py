from typing import Dict, Any, Optional
from logging import getLogger
from apscheduler.schedulers.background import BackgroundScheduler as APScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import sessionmaker

from .base import BaseScheduler

logger = getLogger(__name__)


class BackgroundScheduler(BaseScheduler):
    """基于APScheduler BackgroundScheduler的实现"""
    
    def __init__(self, db_session_factory: sessionmaker, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.db_session_factory = db_session_factory
        self.scheduler = APScheduler(
            timezone='Asia/Shanghai',
            job_defaults={
                'coalesce': True,  # 错过的执行合并为一次
                'max_instances': 3,  # 最大并发实例数
                'misfire_grace_time': 3600  # 错过执行的最大宽容时间(秒)
            }
        )
        self._task_service = None
        
    def start(self):
        """启动调度器"""
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            logger.info("Background scheduler started successfully")
            
    def shutdown(self):
        """关闭调度器"""
        if self.is_running:
            self.scheduler.shutdown(wait=True)
            self.is_running = False
            logger.info("Background scheduler shutdown successfully")
            
    def add_task(self, task_id: int, cron_schedule: str, task_name: str = None):
        """添加定时任务"""
        try:
            if not self.validate_cron(cron_schedule):
                raise ValueError(f"Invalid cron schedule: {cron_schedule}")
                
            # 移除已存在的任务
            if self.scheduler.get_job(f"task_{task_id}"):
                self.remove_task(task_id)
                
            # 解析Cron表达式
            trigger = self._parse_cron_trigger(cron_schedule)
            
            # 添加任务
            self.scheduler.add_job(
                self._execute_task,
                trigger=trigger,
                args=[task_id],
                id=f"task_{task_id}",
                name=task_name or f"Task {task_id}",
                replace_existing=True,
                misfire_grace_time=3600
            )
            
            logger.info(f"Added task {task_id} with schedule: {cron_schedule}")
            
        except Exception as e:
            logger.error(f"Failed to add task {task_id}: {e}")
            raise
            
    def remove_task(self, task_id: int):
        """移除定时任务"""
        try:
            job_id = f"task_{task_id}"
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
                logger.info(f"Removed task {task_id}")
            else:
                logger.warning(f"Task {task_id} not found in scheduler")
                
        except Exception as e:
            logger.error(f"Failed to remove task {task_id}: {e}")
            
    def get_task_status(self, task_id: int) -> Dict[str, Any]:
        """获取任务状态"""
        try:
            job = self.scheduler.get_job(f"task_{task_id}")
            if not job:
                return {
                    'task_id': task_id,
                    'exists': False,
                    'running': False,
                    'next_run': None
                }
                
            return {
                'task_id': task_id,
                'exists': True,
                'running': True,
                'name': job.name,
                'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            }
            
        except Exception as e:
            logger.error(f"Failed to get status for task {task_id}: {e}")
            return {
                'task_id': task_id,
                'exists': False,
                'running': False,
                'error': str(e)
            }
            
    def list_tasks(self) -> Dict[int, Dict[str, Any]]:
        """列出所有任务"""
        try:
            tasks = {}
            for job in self.scheduler.get_jobs():
                # 从job ID中提取task_id
                task_id = int(job.id.replace('task_', ''))
                tasks[task_id] = {
                    'task_id': task_id,
                    'name': job.name,
                    'running': True,
                    'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                    'trigger': str(job.trigger)
                }
            return tasks
            
        except Exception as e:
            logger.error(f"Failed to list tasks: {e}")
            return {}
            
    def _parse_cron_trigger(self, cron_schedule: str) -> CronTrigger:
        """解析Cron表达式并创建触发器
        
        Args:
            cron_schedule: Cron表达式，格式: 分 时 日 月 周
            
        Returns:
            CronTrigger对象
        """
        try:
            parts = cron_schedule.strip().split()
            if len(parts) != 5:
                raise ValueError(f"Cron schedule must have 5 parts: {cron_schedule}")
                
            minute, hour, day, month, day_of_week = parts
            
            # 转换特殊字符
            def _convert_cron_field(field, field_name):
                if field == '*':
                    # 对于APScheduler，'*'表示所有值，而不是None
                    return '*'
                return field
                
            return CronTrigger(
                minute=_convert_cron_field(minute, 'minute'),
                hour=_convert_cron_field(hour, 'hour'),
                day=_convert_cron_field(day, 'day'),
                month=_convert_cron_field(month, 'month'),
                day_of_week=_convert_cron_field(day_of_week, 'day_of_week')
            )
            
        except Exception as e:
            logger.error(f"Failed to parse cron schedule '{cron_schedule}': {e}")
            raise ValueError(f"Invalid cron schedule: {cron_schedule}")
            
    def _execute_task(self, task_id: int):
        """执行任务的核心逻辑"""
        logger.info(f"Executing task {task_id} via scheduler")
        
        db = self.db_session_factory()
        try:
            # 动态导入任务服务，避免循环依赖
            from app.services.services import InspectionTaskService
            task_service = InspectionTaskService(db)
            result = task_service.execute_task(task_id)
            logger.info(f"Task {task_id} executed successfully: {result.check_passed}")
            
        except Exception as e:
            logger.error(f"Failed to execute task {task_id}: {e}")
            # 可以在这里添加错误处理逻辑，如重试、告警等
        finally:
            db.close()