import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.schemas import DataSource, DataSourceCreate, DataSourceUpdate, ConnectionTest
from app.services.services import DataSourceService

router = APIRouter()
logger = logging.getLogger(__name__)

@router.on_event("startup")
async def startup_event():
    logger.info("Data sources API router initialized")

@router.post("/", response_model=DataSource)
def create_data_source(
    data_source: DataSourceCreate,
    db: Session = Depends(get_db)
):
    data_source_service = DataSourceService(db)
    # In a real app, you'd get the user_id from the token
    user_id = 1  # Placeholder
    created_data_source = data_source_service.create_data_source(data_source, created_by=user_id)
    # Add status field based on actual connection status
    data_source_dict = created_data_source.__dict__.copy()
    if created_data_source.is_active:
        # Test the actual connection to determine status
        connection_ok = data_source_service.test_connection(created_data_source.id)
        data_source_dict['status'] = 'active' if connection_ok else 'error'
    else:
        data_source_dict['status'] = 'inactive'
    return data_source_dict

@router.get("/", response_model=List[DataSource])
def read_data_sources(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    logger.info(f"Fetching data sources with skip={skip}, limit={limit}")
    data_source_service = DataSourceService(db)
    try:
        result = data_source_service.get_data_sources(skip=skip, limit=limit)
        logger.info(f"Successfully fetched {len(result)} data sources")
        # Add status field based on actual connection status
        enhanced_result = []
        for ds in result:
            ds_dict = ds.__dict__.copy()
            # Test actual connection to determine status
            if ds.is_active:
                connection_ok = data_source_service.test_connection(ds.id)
                ds_dict['status'] = 'active' if connection_ok else 'error'
            else:
                ds_dict['status'] = 'inactive'
            enhanced_result.append(ds_dict)
        return enhanced_result
    except Exception as e:
        logger.error(f"Error fetching data sources: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/{data_source_id}", response_model=DataSource)
def read_data_source(
    data_source_id: int,
    db: Session = Depends(get_db)
):
    data_source_service = DataSourceService(db)
    data_source = data_source_service.get_data_source(data_source_id)
    if data_source is None:
        raise HTTPException(status_code=404, detail="Data source not found")
    # Add status field based on actual connection status
    data_source_dict = data_source.__dict__.copy()
    if data_source.is_active:
        connection_ok = data_source_service.test_connection(data_source_id)
        data_source_dict['status'] = 'active' if connection_ok else 'error'
    else:
        data_source_dict['status'] = 'inactive'
    return data_source_dict

@router.post("/{data_source_id}/test")
def test_connection(
    data_source_id: int,
    db: Session = Depends(get_db)
):
    data_source_service = DataSourceService(db)
    data_source = data_source_service.get_data_source(data_source_id)
    if data_source is None:
        raise HTTPException(status_code=404, detail="Data source not found")
    result = data_source_service.test_connection(data_source_id)
    return {"connection_successful": result}

@router.post("/test-connection")
def test_connection_before_create(
    connection_data: ConnectionTest,
    db: Session = Depends(get_db)
):
    logger.info(f"收到测试连接请求 - 类型: {connection_data.type}, 主机: {connection_data.host}:{connection_data.port}")
    data_source_service = DataSourceService(db)
    result = data_source_service.test_connection_with_config(connection_data)
    logger.info(f"测试连接完成 - 结果: {result}")
    return {"connection_successful": result}

@router.post("/test-sql")
def test_sql_query(
    data: dict,
    db: Session = Depends(get_db)
):
    data_source_id = data.get("data_source_id")
    sql = data.get("sql")
    
    if not data_source_id or not sql:
        raise HTTPException(status_code=400, detail="data_source_id and sql are required")
    
    data_source_service = DataSourceService(db)
    data_source = data_source_service.get_data_source(data_source_id)
    if data_source is None:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    try:
        result = data_source_service.test_sql_query(data_source_id, sql)
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/{data_source_id}/schema")
def get_sql_schema(
    data_source_id: int,
    db: Session = Depends(get_db)
):
    data_source_service = DataSourceService(db)
    data_source = data_source_service.get_data_source(data_source_id)
    if data_source is None:
        raise HTTPException(status_code=404, detail="Data source not found")
    schema = data_source_service.get_sql_schema(data_source_id)
    return schema

@router.put("/{data_source_id}", response_model=DataSource)
def update_data_source(
    data_source_id: int,
    data_source_update: DataSourceUpdate,
    db: Session = Depends(get_db)
):
    """更新数据源"""
    logger.info(f"Attempting to update data source with ID: {data_source_id}")
    data_source_service = DataSourceService(db)
    
    try:
        # In a real app, you'd get the user_id from the token
        user_id = 1  # Placeholder
        
        updated_data_source = data_source_service.update_data_source(
            data_source_id, data_source_update, updated_by=user_id
        )
        
        # Add status field based on actual connection status
        data_source_dict = updated_data_source.__dict__.copy()
        if updated_data_source.is_active:
            # Test the actual connection to determine status
            connection_ok = data_source_service.test_connection(updated_data_source.id)
            data_source_dict['status'] = 'active' if connection_ok else 'error'
        else:
            data_source_dict['status'] = 'inactive'
            
        logger.info(f"Successfully updated data source with ID: {data_source_id}")
        return data_source_dict
        
    except ValueError as e:
        logger.error(f"Data source not found: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        logger.error(f"Permission denied: {str(e)}")
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating data source {data_source_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete("/{data_source_id}")
def delete_data_source(
    data_source_id: int,
    db: Session = Depends(get_db)
):
    logger.info(f"Attempting to delete data source with ID: {data_source_id}")
    data_source_service = DataSourceService(db)
    
    # Check if data source exists
    data_source = data_source_service.get_data_source(data_source_id)
    if data_source is None:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    try:
        # Check if there are any inspection tasks using this data source
        from app.models.models import InspectionTask
        tasks_using_ds = db.query(InspectionTask).filter(
            InspectionTask.data_source_id == data_source_id
        ).first()
        
        if tasks_using_ds:
            raise HTTPException(
                status_code=400, 
                detail="Cannot delete data source: it is being used by inspection tasks"
            )
        
        # Delete the data source
        success = data_source_service.delete_data_source(data_source_id)
        if success:
            logger.info(f"Successfully deleted data source with ID: {data_source_id}")
            return {"message": "Data source deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete data source")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting data source {data_source_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")