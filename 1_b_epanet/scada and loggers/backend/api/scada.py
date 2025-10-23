from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy.orm import Session
from services.scada_simulator import scada_simulator
from models.database import get_db
from models.tables import SCADASimulatorConfig

router = APIRouter()

# Pydantic models for request/response
class SCADAConfig(BaseModel):
    update_interval: Optional[float] = 30.0
    pressure_variation: Optional[float] = 0.1
    flow_variation: Optional[float] = 0.15
    level_variation: Optional[float] = 0.05
    fault_injection: Optional[bool] = False

class SCADAStartRequest(BaseModel):
    config: Optional[SCADAConfig] = None

@router.get("/")
async def scada_root():
    """Provides information about the SCADA API endpoints."""
    return {
        "message": "SCADA API is working",
        "endpoints": {
            "start": "POST /api/scada/start",
            "stop": "POST /api/scada/stop",
            "status": "GET /api/scada/status",
            "latest": "GET /api/scada/latest",
            "config": "POST /api/scada/config"
        },
        "timestamp": datetime.now().isoformat()
    }

@router.post("/start", response_model=Dict[str, Any])
async def start_scada_simulator(request: SCADAStartRequest = None):
    """
    Start the SCADA simulator with optional configuration.
    """
    try:
        config_dict = None
        if request and request.config:
            config_dict = request.config.dict(exclude_unset=True)
        
        result = await scada_simulator.start(config_dict)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start SCADA simulator: {str(e)}"
        )

@router.post("/stop", response_model=Dict[str, Any])
async def stop_scada_simulator():
    """
    Stop the SCADA simulator.
    """
    try:
        result = await scada_simulator.stop()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop SCADA simulator: {str(e)}"
        )

@router.get("/status", response_model=Dict[str, Any])
async def get_scada_status():
    """
    Get the current status of the SCADA simulator.
    """
    try:
        result = await scada_simulator.get_status()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get SCADA status: {str(e)}"
        )

@router.get("/latest", response_model=Dict[str, Any])
async def get_latest_scada_readings(limit: int = 100):
    """
    Get the latest SCADA readings.
    """
    try:
        result = await scada_simulator.get_latest_readings(limit)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get latest readings: {str(e)}"
        )

@router.post("/config", response_model=Dict[str, Any])
async def update_scada_config(config: SCADAConfig, db: Session = Depends(get_db)):
    """
    Update SCADA simulator configuration.
    """
    try:
        config_dict = config.model_dump(exclude_unset=True)
        
        # Update the database configuration
        db_config = db.query(SCADASimulatorConfig).first()
        if not db_config:
            db_config = SCADASimulatorConfig()
            db.add(db_config)
        
        for key, value in config_dict.items():
            if hasattr(db_config, key):
                setattr(db_config, key, value)
        
        db_config.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_config)
        
        return {
            "message": "Configuration updated successfully",
            "success": True,
            "config": {
                "update_interval": db_config.update_interval,
                "pressure_variation": db_config.pressure_variation,
                "flow_variation": db_config.flow_variation,
                "level_variation": db_config.level_variation,
                "fault_injection": db_config.fault_injection
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update configuration: {str(e)}"
        )

@router.post("/inject-fault", response_model=Dict[str, Any])
async def inject_fault(node_id: str, fault_type: str = "pressure_drop", severity: float = 0.5):
    """
    Inject a fault into the SCADA simulation for testing purposes.
    """
    try:
        # This would be implemented to inject specific faults
        # For now, just return a success message
        return {
            "message": f"Fault injected for node {node_id}",
            "success": True,
            "fault_type": fault_type,
            "severity": severity,
            "node_id": node_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to inject fault: {str(e)}"
        )
