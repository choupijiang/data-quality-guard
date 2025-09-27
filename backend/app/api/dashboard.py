import logging
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from app.core.database import get_db
from app.services.dashboard_service import DashboardService
from app.schemas.schemas import ProjectStatistics, GlobalStatistics

router = APIRouter()
logger = logging.getLogger(__name__)

@router.on_event("startup")
async def startup_event():
    logger.info("Dashboard API router initialized")

@router.get("/statistics", response_model=GlobalStatistics)
def get_global_statistics(db=Depends(get_db)):
    logger.info("Fetching global statistics")
    dashboard_service = DashboardService(lambda: db)
    try:
        result = dashboard_service.get_global_statistics()
        logger.info(f"Successfully fetched global statistics: {result}")
        return result
    except Exception as e:
        logger.error(f"Error fetching global statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/project-statistics", response_model=List[ProjectStatistics])
def get_project_statistics(db=Depends(get_db)):
    logger.info("Fetching project statistics")
    dashboard_service = DashboardService(lambda: db)
    try:
        result = dashboard_service.get_project_statistics()
        logger.info(f"Successfully fetched {len(result)} project statistics")
        return result
    except Exception as e:
        logger.error(f"Error fetching project statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")