#!/usr/bin/env python3
"""
增强版后端服务，包含详细的MySQL连接测试日志
"""
import logging
import sys
import os

# 设置详细的日志配置
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/backend_debug.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    """主函数"""
    logger.info("启动增强版后端服务...")
    
    # 添加当前目录到Python路径
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # 导入并启动主应用
        from main import app
        
        logger.info("FastAPI应用加载成功")
        
        # 测试MySQL连接功能
        logger.info("测试MySQL连接功能...")
        test_mysql_connection_logic()
        
        # 启动服务器
        import uvicorn
        logger.info("启动Uvicorn服务器...")
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="debug",
            access_log=True
        )
        
    except Exception as e:
        logger.error(f"启动失败: {str(e)}")
        logger.exception("详细错误信息:")
        sys.exit(1)

def test_mysql_connection_logic():
    """测试MySQL连接逻辑"""
    logger.info("开始测试MySQL连接逻辑...")
    
    try:
        # 导入必要的模块
        from app.services.services import DataSourceService
        from app.schemas.schemas import ConnectionTest
        from app.core.database import SessionLocal
        
        # 创建测试配置
        test_config = ConnectionTest(
            type="mysql",
            host="localhost",
            port=3306,
            username="root",
            password="wrong_password",  # 故意使用错误密码
            database="mysql"
        )
        
        logger.info(f"测试配置: {test_config}")
        
        # 创建数据库会话和服务
        db = SessionLocal()
        service = DataSourceService(db)
        
        # 测试连接
        logger.info("执行连接测试...")
        result = service.test_connection_with_config(test_config)
        logger.info(f"连接测试结果: {result}")
        
        db.close()
        
    except Exception as e:
        logger.error(f"MySQL连接测试失败: {str(e)}")
        logger.exception("详细错误信息:")

if __name__ == "__main__":
    main()