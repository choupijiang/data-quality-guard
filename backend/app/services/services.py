from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging
import pymysql
import psycopg2
from clickhouse_driver import Client
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from app.models.models import User, Project, DataSource, InspectionTask, InspectionResult, UserProjectPermission, UserRole
from app.schemas.schemas import UserCreate, ProjectCreate, DataSourceCreate, DataSourceUpdate, InspectionTaskCreate, InspectionTaskUpdate, ConnectionTest, UserUpdate, UserProjectPermissionCreate
from app.core.security import get_password_hash, verify_password

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, user: UserCreate, role: UserRole = UserRole.REGULAR_USER) -> User:
        try:
            hashed_password = get_password_hash(user.password)
            db_user = User(
                username=user.username,
                email=user.email,
                hashed_password=hashed_password,
                role=role,
                is_active=True
            )
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            return db_user
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating user {user.username}: {str(e)}")
            raise e
    
    def create_user_with_role(self, user: UserCreate, role: UserRole) -> User:
        """Create user with specific role (for admin use)"""
        return self.create_user(user, role)
    
    def get_user_by_username(self, username: str) -> User:
        return self.db.query(User).filter(User.username == username).first()
    
    def get_user_by_email(self, email: str) -> User:
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_id(self, user_id: int) -> User:
        return self.db.query(User).filter(User.id == user_id).first()
    
    def authenticate_user(self, username: str, password: str) -> User:
        user = self.get_user_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        return self.db.query(User).offset(skip).limit(limit).all()
    
    def update_user(self, user_id: int, user_update: UserUpdate) -> User:
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return None
            
            update_data = user_update.dict(exclude_unset=True)
            
            # Handle password separately to hash it
            if 'password' in update_data and update_data['password']:
                hashed_password = get_password_hash(update_data['password'])
                user.hashed_password = hashed_password
                del update_data['password']
            
            # Update other fields
            for field, value in update_data.items():
                setattr(user, field, value)
            
            self.db.commit()
            self.db.refresh(user)
            return user
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating user {user_id}: {str(e)}")
            raise e
    
    def delete_user(self, user_id: int) -> bool:
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        self.db.delete(user)
        self.db.commit()
        return True
    
    def get_accessible_projects(self, user_id: int) -> List[int]:
        """Get list of project IDs user has access to"""
        user = self.get_user_by_id(user_id)
        if not user:
            return []
        
        # System and project admins have access to all projects
        if user.role in [UserRole.SYSTEM_ADMIN, UserRole.PROJECT_ADMIN]:
            projects = self.db.query(Project.id).all()
            return [project.id for project in projects]
        
        # Regular users have access to assigned projects only
        permissions = self.db.query(UserProjectPermission.project_id).filter(
            UserProjectPermission.user_id == user_id
        ).all()
        return [permission.project_id for permission in permissions]
    
    def assign_project_permission(self, user_id: int, project_id: int) -> UserProjectPermission:
        """Assign project permission to user"""
        # Check if permission already exists
        existing = self.db.query(UserProjectPermission).filter(
            UserProjectPermission.user_id == user_id,
            UserProjectPermission.project_id == project_id
        ).first()
        
        if existing:
            return existing
        
        permission = UserProjectPermission(
            user_id=user_id,
            project_id=project_id
        )
        self.db.add(permission)
        self.db.commit()
        self.db.refresh(permission)
        return permission
    
    def remove_project_permission(self, user_id: int, project_id: int) -> bool:
        """Remove project permission from user"""
        permission = self.db.query(UserProjectPermission).filter(
            UserProjectPermission.user_id == user_id,
            UserProjectPermission.project_id == project_id
        ).first()
        
        if not permission:
            return False
        
        self.db.delete(permission)
        self.db.commit()
        return True
    
    def get_user_project_permissions(self, user_id: int) -> List[UserProjectPermission]:
        """Get all project permissions for a user"""
        return self.db.query(UserProjectPermission).filter(
            UserProjectPermission.user_id == user_id
        ).all()

class ProjectService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_project(self, project: ProjectCreate, created_by: int) -> Project:
        db_project = Project(
            name=project.name,
            description=project.description,
            status=project.status,
            created_by=created_by
        )
        self.db.add(db_project)
        self.db.commit()
        self.db.refresh(db_project)
        return db_project
    
    def get_projects(self, skip: int = 0, limit: int = 100) -> List[Project]:
        return self.db.query(Project).offset(skip).limit(limit).all()
    
    def get_project(self, project_id: int) -> Project:
        return self.db.query(Project).filter(Project.id == project_id).first()
    
    def update_project(self, project_id: int, project_data: dict) -> Project:
        db_project = self.get_project(project_id)
        if db_project:
            for key, value in project_data.items():
                setattr(db_project, key, value)
            self.db.commit()
            self.db.refresh(db_project)
        return db_project
    
    def delete_project(self, project_id: int) -> bool:
        db_project = self.get_project(project_id)
        if db_project:
            # First delete related user permissions
            self.db.query(UserProjectPermission).filter(
                UserProjectPermission.project_id == project_id
            ).delete()
            # Then delete the project
            self.db.delete(db_project)
            self.db.commit()
            return True
        return False

class DataSourceService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_data_source(self, data_source: DataSourceCreate, created_by: int) -> DataSource:
        db_data_source = DataSource(
            name=data_source.name,
            type=data_source.type,
            host=data_source.host,
            port=data_source.port,
            database=data_source.database,
            username=data_source.username,
            password=data_source.password,
            description=data_source.description,
            is_active=data_source.is_active,
            created_by=created_by
        )
        self.db.add(db_data_source)
        self.db.commit()
        self.db.refresh(db_data_source)
        return db_data_source
    
    def get_data_sources(self, skip: int = 0, limit: int = 100) -> List[DataSource]:
        return self.db.query(DataSource).offset(skip).limit(limit).all()
    
    def get_data_source(self, data_source_id: int) -> DataSource:
        return self.db.query(DataSource).filter(DataSource.id == data_source_id).first()
    
    def delete_data_source(self, data_source_id: int) -> bool:
        data_source = self.get_data_source(data_source_id)
        if data_source:
            self.db.delete(data_source)
            self.db.commit()
            return True
        return False
    
    def update_data_source(self, data_source_id: int, data_source_update: DataSourceUpdate, updated_by: int) -> DataSource:
        """更新数据源"""
        data_source = self.get_data_source(data_source_id)
        if not data_source:
            raise ValueError(f"Data source with ID {data_source_id} not found")
        
        # 检查权限：只有创建者可以更新
        if data_source.created_by != updated_by:
            raise PermissionError("You don't have permission to update this data source")
        
        # 更新字段
        update_data = data_source_update.dict(exclude_unset=True)
        
        # 特殊处理密码字段：如果为空字符串，则保持原密码不变
        if 'password' in update_data and update_data['password'] == '':
            del update_data['password']
        
        # 应用更新
        for field, value in update_data.items():
            setattr(data_source, field, value)
        
        try:
            self.db.commit()
            self.db.refresh(data_source)
            logger.info(f"Successfully updated data source {data_source_id}")
            return data_source
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating data source {data_source_id}: {str(e)}")
            raise
    
    def test_connection(self, data_source_id: int) -> bool:
        data_source = self.get_data_source(data_source_id)
        if not data_source:
            return False
        
        connection_data = ConnectionTest(
            type=data_source.type,
            host=data_source.host,
            port=data_source.port,
            database=data_source.database,
            username=data_source.username,
            password=data_source.password
        )
        return self.test_connection_with_config(connection_data)
    
    def test_connection_with_config(self, connection_data: ConnectionTest) -> bool:
        logger = logging.getLogger(__name__)
        logger.info(f"开始测试连接 - 类型: {connection_data.type}, 主机: {connection_data.host}:{connection_data.port}, 数据库: {connection_data.database}")
        
        try:
            if connection_data.type == "mysql":
                logger.info("测试MySQL连接...")
                result = self._test_mysql_connection(connection_data)
                logger.info(f"MySQL连接测试结果: {result}")
                return result
            elif connection_data.type == "postgresql":
                logger.info("测试PostgreSQL连接...")
                result = self._test_postgresql_connection(connection_data)
                logger.info(f"PostgreSQL连接测试结果: {result}")
                return result
            elif connection_data.type == "clickhouse":
                logger.info("测试ClickHouse连接...")
                result = self._test_clickhouse_connection(connection_data)
                logger.info(f"ClickHouse连接测试结果: {result}")
                return result
            elif connection_data.type == "starrocks":
                logger.info("测试StarRocks连接...")
                result = self._test_starrocks_connection(connection_data)
                logger.info(f"StarRocks连接测试结果: {result}")
                return result
            else:
                logger.error(f"不支持的数据源类型: {connection_data.type}")
                return False
        except Exception as e:
            logger.error(f"连接测试失败 - 类型: {connection_data.type}, 错误: {str(e)}")
            return False
    
    def _test_mysql_connection(self, config: ConnectionTest) -> bool:
        logger = logging.getLogger(__name__)
        logger.info(f"尝试连接MySQL: {config.host}:{config.port}, 用户: {config.username}, 数据库: {config.database}")
        
        try:
            connection = pymysql.connect(
                host=config.host,
                port=config.port,
                user=config.username,
                password=config.password,
                database=config.database,
                connect_timeout=5
            )
            logger.info("MySQL连接成功")
            connection.close()
            return True
        except Exception as e:
            logger.error(f"MySQL连接失败: {str(e)}")
            return False
    
    def _test_postgresql_connection(self, config: ConnectionTest) -> bool:
        logger = logging.getLogger(__name__)
        logger.info(f"尝试连接PostgreSQL: {config.host}:{config.port}, 用户: {config.username}, 数据库: {config.database}")
        
        try:
            connection = psycopg2.connect(
                host=config.host,
                port=config.port,
                user=config.username,
                password=config.password,
                database=config.database,
                connect_timeout=5
            )
            logger.info("PostgreSQL连接成功")
            connection.close()
            return True
        except Exception as e:
            logger.error(f"PostgreSQL连接失败: {str(e)}")
            return False
    
    def _test_clickhouse_connection(self, config: ConnectionTest) -> bool:
        logger = logging.getLogger(__name__)
        logger.info(f"尝试连接ClickHouse: {config.host}:{config.port}, 用户: {config.username}, 数据库: {config.database}")
        
        try:
            client = Client(
                host=config.host,
                port=config.port,
                user=config.username,
                password=config.password,
                database=config.database
            )
            result = client.execute('SELECT 1')
            logger.info("ClickHouse连接成功")
            client.disconnect()
            return True
        except Exception as e:
            logger.error(f"ClickHouse连接失败: {str(e)}")
            return False
    
    def _test_starrocks_connection(self, config: ConnectionTest) -> bool:
        # StarRocks uses MySQL protocol
        return self._test_mysql_connection(config)
    
    def test_sql_query(self, data_source_id: int, sql: str) -> str:
        """Test SQL query and return single value result"""
        data_source = self.get_data_source(data_source_id)
        if not data_source:
            raise ValueError("Data source not found")
        
        try:
            return self._execute_sql_query(data_source, sql)
        except Exception as e:
            raise ValueError(f"SQL execution failed: {str(e)}")
    
    def _execute_sql_query(self, data_source: DataSource, sql_query: str) -> any:
        """Execute SQL query against data source and return single value"""
        try:
            if data_source.type == "mysql":
                return self._execute_mysql_sql(data_source, sql_query)
            elif data_source.type == "postgresql":
                return self._execute_postgresql_sql(data_source, sql_query)
            elif data_source.type == "clickhouse":
                return self._execute_clickhouse_sql(data_source, sql_query)
            elif data_source.type == "starrocks":
                return self._execute_starrocks_sql(data_source, sql_query)
            else:
                raise ValueError(f"Unsupported data source type: {data_source.type}")
        except Exception as e:
            raise ValueError(f"SQL execution failed: {str(e)}")
    
    def _execute_mysql_sql(self, data_source: DataSource, sql_query: str) -> any:
        import pymysql
        connection = pymysql.connect(
            host=data_source.host,
            port=data_source.port,
            user=data_source.username,
            password=data_source.password,
            database=data_source.database
        )
        
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_query)
                result = cursor.fetchone()
                return result[0] if result and len(result) > 0 else None
        finally:
            connection.close()
    
    def _execute_postgresql_sql(self, data_source: DataSource, sql_query: str) -> any:
        import psycopg2
        connection = psycopg2.connect(
            host=data_source.host,
            port=data_source.port,
            user=data_source.username,
            password=data_source.password,
            database=data_source.database
        )
        
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_query)
                result = cursor.fetchone()
                return result[0] if result and len(result) > 0 else None
        finally:
            connection.close()
    
    def _execute_clickhouse_sql(self, data_source: DataSource, sql_query: str) -> any:
        from clickhouse_driver import Client
        client = Client(
            host=data_source.host,
            port=data_source.port,
            user=data_source.username,
            password=data_source.password,
            database=data_source.database
        )
        
        try:
            result = client.execute(sql_query)
            return result[0][0] if result and len(result) > 0 and len(result[0]) > 0 else None
        finally:
            client.disconnect()
    
    def _execute_starrocks_sql(self, data_source: DataSource, sql_query: str) -> any:
        # StarRocks uses MySQL protocol
        return self._execute_mysql_sql(data_source, sql_query)
    
    def get_sql_schema(self, data_source_id: int) -> dict:
        # This would implement schema fetching from the data source
        # For now, return placeholder data
        return {
            "tables": [
                {"name": "users", "columns": ["id", "name", "email"]},
                {"name": "orders", "columns": ["id", "user_id", "amount", "created_at"]}
            ]
        }

class InspectionTaskService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_task(self, task: InspectionTaskCreate, created_by: int) -> InspectionTask:
        db_task = InspectionTask(
            name=task.name,
            description=task.description,
            check_sql=task.check_sql,
            expected_sql=task.expected_sql,
            check_expression=task.check_expression,
            cron_schedule=task.cron_schedule,
            status=task.status,
            data_source_id=task.data_source_id,
            project_id=task.project_id,
            created_by=created_by
        )
        self.db.add(db_task)
        self.db.commit()
        self.db.refresh(db_task)
        return db_task
    
    def get_tasks(self, skip: int = 0, limit: int = 100) -> List[InspectionTask]:
        return self.db.query(InspectionTask).offset(skip).limit(limit).all()
    
    def get_tasks_by_user_permissions(self, user_id: int, skip: int = 0, limit: int = 100) -> List[InspectionTask]:
        """获取用户有权限的项目下的inspection tasks"""
        # 使用UserService的get_accessible_projects方法来获取用户有权限的项目ID列表
        user_service = UserService(self.db)
        project_ids = user_service.get_accessible_projects(user_id)
        
        if not project_ids:
            return []
        
        # 只返回用户有权限的项目下的tasks
        return self.db.query(InspectionTask).filter(
            InspectionTask.project_id.in_(project_ids)
        ).offset(skip).limit(limit).all()
    
    def get_task(self, task_id: int) -> InspectionTask:
        return self.db.query(InspectionTask).filter(InspectionTask.id == task_id).first()
    
    def execute_task(self, task_id: int) -> InspectionResult:
        task = self.get_task(task_id)
        if not task:
            raise ValueError("Task not found")
        
        try:
            # Get data source for SQL execution
            data_source_service = DataSourceService(self.db)
            data_source = data_source_service.get_data_source(task.data_source_id)
            
            if not data_source:
                raise ValueError("Data source not found")
            
            # Execute check SQL
            check_value = self._execute_sql(data_source, task.check_sql)
            
            # Execute expected SQL
            expected_value = self._execute_sql(data_source, task.expected_sql)
            
            # Evaluate the check expression
            check_passed = self._evaluate_expression(task.check_expression, str(check_value), str(expected_value))
            
            result = InspectionResult(
                task_id=task_id,
                check_value=str(check_value),
                expected_value=str(expected_value),
                check_passed=check_passed
            )
            
            self.db.add(result)
            self.db.commit()
            self.db.refresh(result)
            
            # Update task last run time
            from datetime import datetime
            task.last_run_at = datetime.utcnow()
            self.db.commit()
            
            # Trigger alert if task failed
            if not check_passed:
                self._trigger_alert(task, result)
            
            return result
            
        except Exception as e:
            result = InspectionResult(
                task_id=task_id,
                check_passed=False,
                error_message=str(e)
            )
            self.db.add(result)
            self.db.commit()
            
            # Trigger alert for execution error
            self._trigger_alert(task, result)
            
            return result
    
    def _execute_sql(self, data_source: DataSource, sql_query: str) -> any:
        try:
            if data_source.type == "mysql":
                return self._execute_mysql_sql(data_source, sql_query)
            elif data_source.type == "postgresql":
                return self._execute_postgresql_sql(data_source, sql_query)
            elif data_source.type == "clickhouse":
                return self._execute_clickhouse_sql(data_source, sql_query)
            elif data_source.type == "starrocks":
                return self._execute_starrocks_sql(data_source, sql_query)
            else:
                raise ValueError(f"Unsupported data source type: {data_source.type}")
        except Exception as e:
            raise ValueError(f"SQL execution failed: {str(e)}")
    
    def _execute_mysql_sql(self, data_source: DataSource, sql_query: str) -> any:
        connection = pymysql.connect(
            host=data_source.host,
            port=data_source.port,
            user=data_source.username,
            password=data_source.password,
            database=data_source.database
        )
        
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_query)
                result = cursor.fetchone()
                return result[0] if result and len(result) > 0 else None
        finally:
            connection.close()
    
    def _execute_postgresql_sql(self, data_source: DataSource, sql_query: str) -> any:
        import psycopg2
        connection = psycopg2.connect(
            host=data_source.host,
            port=data_source.port,
            user=data_source.username,
            password=data_source.password,
            database=data_source.database
        )
        
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_query)
                result = cursor.fetchone()
                return result[0] if result and len(result) > 0 else None
        finally:
            connection.close()
    
    def _execute_clickhouse_sql(self, data_source: DataSource, sql_query: str) -> any:
        client = Client(
            host=data_source.host,
            port=data_source.port,
            user=data_source.username,
            password=data_source.password,
            database=data_source.database
        )
        
        try:
            result = client.execute(sql_query)
            return result[0][0] if result and len(result) > 0 and len(result[0]) > 0 else None
        finally:
            client.disconnect()
    
    def _execute_starrocks_sql(self, data_source: DataSource, sql_query: str) -> any:
        # StarRocks uses MySQL protocol
        return self._execute_mysql_sql(data_source, sql_query)
    
    def _trigger_alert(self, task: InspectionTask, result: InspectionResult):
        # This would implement alert notification logic
        # For now, just log the alert
        logger = logging.getLogger(__name__)
        logger.error(f"Task {task.name} failed: {result.error_message or 'Check expression failed'}")
        
        # Here you could implement email, webhook, or other notification methods
    
    def _evaluate_expression(self, expression: str, check_value: str, expected_value: str) -> bool:
        # Simple expression evaluation
        # In production, use a safer evaluation method
        try:
            check_num = float(check_value) if check_value else 0
            expected_num = float(expected_value) if expected_value else 0
            
            if "==" in expression:
                return check_num == expected_num
            elif "!=" in expression:
                return check_num != expected_num
            elif ">" in expression:
                return check_num > expected_num
            elif "<" in expression:
                return check_num < expected_num
            elif ">=" in expression:
                return check_num >= expected_num
            elif "<=" in expression:
                return check_num <= expected_num
            else:
                return False
        except:
            return False
    
    def delete_task(self, task_id: int) -> bool:
        task = self.get_task(task_id)
        if task:
            # 首先删除关联的执行结果历史记录
            self.db.query(InspectionResult).filter(
                InspectionResult.task_id == task_id
            ).delete()
            
            # 然后删除任务本身
            self.db.delete(task)
            self.db.commit()
            return True
        return False
    
    def delete_result(self, result_id: int) -> bool:
        """删除指定的执行结果记录"""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"Service层开始删除执行结果, result_id: {result_id}")
        
        try:
            result = self.db.query(InspectionResult).filter(InspectionResult.id == result_id).first()
            logger.info(f"查询结果: {result is not None}, result_id: {result_id}")
            
            if result:
                logger.info(f"找到执行结果, 准备删除: {result.id}, task_id: {result.task_id}")
                self.db.delete(result)
                logger.info(f"已标记删除, 准备提交事务")
                self.db.commit()
                logger.info(f"事务提交成功, result_id: {result_id}")
                return True
            else:
                logger.warning(f"未找到执行结果, result_id: {result_id}")
                return False
        except Exception as e:
            logger.error(f"Service层删除执行结果时发生错误, result_id: {result_id}, 错误: {str(e)}")
            self.db.rollback()
            logger.info(f"事务已回滚")
            raise
    
    def get_task_results(self, task_id: int, skip: int = 0, limit: int = 100) -> List[InspectionResult]:
        """获取指定任务的执行结果历史"""
        task = self.get_task(task_id)
        if not task:
            raise ValueError("Task not found")
        
        return self.db.query(InspectionResult)\
            .filter(InspectionResult.task_id == task_id)\
            .order_by(InspectionResult.execution_time.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    def get_all_results(self, skip: int = 0, limit: int = 100) -> List[InspectionResult]:
        """获取所有任务的执行结果历史"""
        return self.db.query(InspectionResult)\
            .order_by(InspectionResult.execution_time.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    def get_task_results_with_details(self, task_id: int, skip: int = 0, limit: int = 100) -> List[dict]:
        """获取指定任务的执行结果历史（包含详细信息）"""
        task = self.get_task(task_id)
        if not task:
            raise ValueError("Task not found")
        
        results = self.db.query(InspectionResult)\
            .filter(InspectionResult.task_id == task_id)\
            .order_by(InspectionResult.execution_time.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()
        
        # 添加任务详细信息
        return [
            {
                "id": result.id,
                "task_id": result.task_id,
                "task_name": task.name,
                "data_source_name": task.data_source.name if task.data_source else "未知数据源",
                "check_value": result.check_value,
                "expected_value": result.expected_value,
                "check_passed": result.check_passed,
                "execution_time": result.execution_time,
                "error_message": result.error_message,
                "duration": 0  # 暂时设为0，后续可以添加实际计算
            }
            for result in results
        ]

    def get_task_stats(self, task_id: int) -> dict:
        """获取指定任务的统计信息"""
        task = self.get_task(task_id)
        if not task:
            raise ValueError("Task not found")
        
        # 计算总执行次数
        total_executions = self.db.query(InspectionResult)\
            .filter(InspectionResult.task_id == task_id)\
            .count()
        
        # 计算成功次数
        successful_executions = self.db.query(InspectionResult)\
            .filter(InspectionResult.task_id == task_id, InspectionResult.check_passed == True)\
            .count()
        
        # 计算成功率
        success_rate = 0
        if total_executions > 0:
            success_rate = round((successful_executions / total_executions) * 100, 1)
        
        return {
            "task_id": task_id,
            "task_name": task.name,
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "success_rate": success_rate,
            "last_run_at": task.last_run_at,
            "status": task.status
        }
    
    def get_all_results_with_details(self, skip: int = 0, limit: int = 100) -> List[dict]:
        """获取所有任务的执行结果历史（包含详细信息）"""
        # 只查询存在任务的执行结果，使用join过滤掉已删除任务的历史记录
        results = self.db.query(InspectionResult)\
            .join(InspectionTask, InspectionResult.task_id == InspectionTask.id)\
            .order_by(InspectionResult.execution_time.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()
        
        # 添加任务详细信息
        detailed_results = []
        for result in results:
            task = self.get_task(result.task_id)
            if task:  # 双重检查，确保任务存在
                detailed_results.append({
                    "id": result.id,
                    "task_id": result.task_id,
                    "task_name": task.name,
                    "data_source_name": task.data_source.name if task.data_source else "未知数据源",
                    "check_value": result.check_value,
                    "expected_value": result.expected_value,
                    "check_passed": result.check_passed,
                    "execution_time": result.execution_time,
                    "error_message": result.error_message,
                    "duration": 0  # 暂时设为0，后续可以添加实际计算
                })
        
        return detailed_results
    
    def update_task(self, task_id: int, task_update: InspectionTaskUpdate) -> InspectionTask:
        task = self.get_task(task_id)
        if not task:
            raise ValueError("Task not found")
        
        # Update fields
        for field, value in task_update.dict(exclude_unset=True).items():
            setattr(task, field, value)
        
        task.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(task)
        return task
    
    def get_tasks_stats(self) -> List[dict]:
        """获取所有任务的统计信息"""
        tasks = self.get_tasks()
        stats = []
        
        for task in tasks:
            # 获取该任务的所有执行结果
            results = self.get_task_results(task_id=task.id)
            
            # 计算统计数据
            total_executions = len(results)
            successful_executions = len([r for r in results if r.check_passed])
            success_rate = round((successful_executions / total_executions * 100) if total_executions > 0 else 0, 1)
            
            stats.append({
                "task_id": task.id,
                "execution_count": total_executions,
                "success_rate": success_rate,
                "last_execution": results[0].execution_time if results else None
            })
        
        return stats

class TaskScheduler:
    def __init__(self, db_session_factory):
        self.scheduler = BackgroundScheduler()
        self.db_session_factory = db_session_factory
        self.scheduler.start()
    
    def add_task(self, task_id: int, cron_schedule: str):
        self.scheduler.add_job(
            self._execute_task,
            trigger='cron',
            minute=cron_schedule.split()[1] if len(cron_schedule.split()) > 1 else '0',
            hour=cron_schedule.split()[0] if len(cron_schedule.split()) > 0 else '0',
            args=[task_id],
            id=f"task_{task_id}"
        )
    
    def remove_task(self, task_id: int):
        self.scheduler.remove_job(f"task_{task_id}")
    
    def _execute_task(self, task_id: int):
        db = self.db_session_factory()
        try:
            task_service = InspectionTaskService(db)
            task_service.execute_task(task_id)
        finally:
            db.close()
    
    def shutdown(self):
        self.scheduler.shutdown()