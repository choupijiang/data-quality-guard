import logging
import atexit
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, SessionLocal
from app.models.models import Base
from app.api import auth, projects, data_sources, inspection_tasks, dashboard
from app.schedulers.factory import SchedulerManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
logger.info("Creating database tables...")
Base.metadata.create_all(bind=engine)
logger.info("Database tables created successfully")

# Initialize scheduler manager
scheduler_manager = SchedulerManager(settings, SessionLocal)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="数据库质量巡检系统API"
)

logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")

@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化逻辑"""
    logger.info("Starting up application...")
    
    try:
        # 初始化调度器
        scheduler_manager.initialize()
        
        # 加载活跃任务
        scheduler_manager.load_active_tasks()
        
        logger.info("Application startup completed successfully")
        
    except Exception as e:
        logger.error(f"Failed to startup application: {e}")
        # 不要在这里抛出异常，让应用继续启动

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的清理逻辑"""
    logger.info("Shutting down application...")
    
    try:
        # 关闭调度器
        scheduler_manager.shutdown()
        logger.info("Application shutdown completed successfully")
        
    except Exception as e:
        logger.error(f"Failed to shutdown application gracefully: {e}")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["authentication"])
app.include_router(projects.router, prefix=f"{settings.API_V1_STR}/projects", tags=["projects"])
app.include_router(data_sources.router, prefix=f"{settings.API_V1_STR}/data-sources", tags=["data-sources"])
app.include_router(inspection_tasks.router, prefix=f"{settings.API_V1_STR}/inspection-tasks", tags=["inspection-tasks"])
app.include_router(dashboard.router, prefix=f"{settings.API_V1_STR}/dashboard", tags=["dashboard"])

# Make scheduler manager available to routers
app.state.scheduler_manager = scheduler_manager

@app.get("/")
def read_root():
    return {"message": "欢迎使用数据库质量巡检系统API", "version": settings.VERSION}

@app.get("/health")
def health_check():
    scheduler_status = {
        "enabled": settings.SCHEDULER_ENABLED,
        "type": settings.SCHEDULER_TYPE,
        "running": scheduler_manager.is_scheduler_running(),
        "initialized": scheduler_manager.is_initialized
    }
    return {
        "status": "healthy", 
        "version": settings.VERSION,
        "scheduler": scheduler_status
    }

# 注册优雅退出处理
atexit.register(scheduler_manager.shutdown)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)