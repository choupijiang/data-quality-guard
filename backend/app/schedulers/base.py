from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class BaseScheduler(ABC):
    """调度器基础抽象类"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.is_running = False
        
    @abstractmethod
    def start(self):
        """启动调度器"""
        pass
        
    @abstractmethod
    def shutdown(self):
        """关闭调度器"""
        pass
        
    @abstractmethod
    def add_task(self, task_id: int, cron_schedule: str, task_name: str = None):
        """添加定时任务
        
        Args:
            task_id: 任务ID
            cron_schedule: Cron表达式，格式: 分 时 日 月 周
            task_name: 任务名称 (可选)
        """
        pass
        
    @abstractmethod
    def remove_task(self, task_id: int):
        """移除定时任务
        
        Args:
            task_id: 任务ID
        """
        pass
        
    @abstractmethod
    def get_task_status(self, task_id: int) -> Dict[str, Any]:
        """获取任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务状态信息
        """
        pass
        
    @abstractmethod
    def list_tasks(self) -> Dict[int, Dict[str, Any]]:
        """列出所有任务
        
        Returns:
            所有任务的状态信息
        """
        pass
        
    def is_task_running(self, task_id: int) -> bool:
        """检查任务是否正在运行"""
        try:
            status = self.get_task_status(task_id)
            return status.get('running', False)
        except Exception:
            return False
            
    def validate_cron(self, cron_schedule: str) -> bool:
        """验证Cron表达式格式
        
        Args:
            cron_schedule: Cron表达式
            
        Returns:
            是否有效
        """
        try:
            parts = cron_schedule.strip().split()
            if len(parts) != 5:
                return False
                
            # 简单验证每个字段
            for part in parts:
                if part not in ['*'] and not any(c.isdigit() for c in part):
                    return False
                    
            return True
        except Exception:
            return False