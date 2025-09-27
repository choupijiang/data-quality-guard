from typing import Dict, Any, Optional
from enum import Enum
import logging

from .base import BaseScheduler
from .background_scheduler import BackgroundScheduler

logger = logging.getLogger(__name__)


class SchedulerType(Enum):
    """调度器类型枚举"""
    BACKGROUND = "background"
    REDIS = "redis" 
    CELERY = "celery"


def create_scheduler(
    scheduler_type: SchedulerType,
    db_session_factory,
    config: Optional[Dict[str, Any]] = None
) -> BaseScheduler:
    """创建调度器实例的工厂函数
    
    Args:
        scheduler_type: 调度器类型
        db_session_factory: 数据库会话工厂
        config: 调度器配置
        
    Returns:
        调度器实例
        
    Raises:
        ValueError: 不支持的调度器类型
    """
    config = config or {}
    
    if scheduler_type == SchedulerType.BACKGROUND:
        return BackgroundScheduler(db_session_factory, config)
    elif scheduler_type == SchedulerType.REDIS:
        raise NotImplementedError("Redis scheduler not implemented yet")
    elif scheduler_type == SchedulerType.CELERY:
        raise NotImplementedError("Celery scheduler not implemented yet")
    else:
        raise ValueError(f"Unsupported scheduler type: {scheduler_type}")


def get_scheduler_config(settings) -> Dict[str, Any]:
    """从应用配置中提取调度器配置
    
    Args:
        settings: 应用设置对象
        
    Returns:
        调度器配置字典
    """
    return {
        'max_workers': settings.MAX_WORKERS,
        'task_timeout': settings.TASK_TIMEOUT,
        'max_instances': settings.SCHEDULER_MAX_INSTANCES,
        'misfire_grace_time': settings.SCHEDULER_MISFIRE_GRACE_TIME,
        'coalesce': settings.SCHEDULER_COALESCE,
        'redis_url': settings.REDIS_SCHEDULER_URL,
    }


class SchedulerManager:
    """调度器管理器，负责调度器的生命周期管理"""
    
    def __init__(self, settings, db_session_factory):
        self.settings = settings
        self.db_session_factory = db_session_factory
        self.scheduler: Optional[BaseScheduler] = None
        self.is_initialized = False
        
    def initialize(self):
        """初始化调度器"""
        if not self.settings.SCHEDULER_ENABLED:
            logger.info("Scheduler is disabled in configuration")
            return
            
        if self.is_initialized:
            logger.warning("Scheduler already initialized")
            return
            
        try:
            # 获取调度器配置
            config = get_scheduler_config(self.settings)
            
            # 创建调度器
            scheduler_type = SchedulerType(self.settings.SCHEDULER_TYPE)
            self.scheduler = create_scheduler(
                scheduler_type, 
                self.db_session_factory, 
                config
            )
            
            # 启动调度器
            self.scheduler.start()
            self.is_initialized = True
            
            logger.info(f"Scheduler initialized successfully with type: {scheduler_type.value}")
            
        except Exception as e:
            logger.error(f"Failed to initialize scheduler: {e}")
            raise
            
    def shutdown(self):
        """关闭调度器"""
        if not self.is_initialized or not self.scheduler:
            return
            
        try:
            self.scheduler.shutdown()
            self.scheduler = None
            self.is_initialized = False
            logger.info("Scheduler shutdown successfully")
            
        except Exception as e:
            logger.error(f"Failed to shutdown scheduler: {e}")
            
    def load_active_tasks(self):
        """加载活跃的任务到调度器"""
        if not self.scheduler or not self.is_initialized:
            logger.warning("Scheduler not initialized, cannot load tasks")
            return
            
        try:
            from app.services.services import InspectionTaskService
            from app.models.models import InspectionTask
            
            db = self.db_session_factory()
            try:
                task_service = InspectionTaskService(db)
                
                # 获取所有活跃的任务
                active_tasks = db.query(InspectionTask).filter(
                    InspectionTask.status == 'active'
                ).all()
                
                logger.info(f"Loading {len(active_tasks)} active tasks into scheduler")
                
                # 将每个任务添加到调度器
                for task in active_tasks:
                    if task.cron_schedule:
                        try:
                            self.scheduler.add_task(
                                task.id, 
                                task.cron_schedule, 
                                task.name
                            )
                            logger.info(f"Loaded task {task.id}: {task.name}")
                        except Exception as e:
                            logger.error(f"Failed to load task {task.id}: {e}")
                            
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Failed to load active tasks: {e}")
            
    def get_scheduler(self) -> Optional[BaseScheduler]:
        """获取调度器实例"""
        return self.scheduler
        
    def is_scheduler_running(self) -> bool:
        """检查调度器是否运行"""
        return self.is_initialized and self.scheduler and self.scheduler.is_running