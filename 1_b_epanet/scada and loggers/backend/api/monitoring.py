"""
Monitoring API endpoints
Provides REST API for baseline establishment and monitoring operations
"""
from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any, Optional
from pydantic import BaseModel
from services.baseline_engine import baseline_engine
from services.monitoring_engine import monitoring_engine
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models for request/response
class ThresholdUpdate(BaseModel):
    pressure_deviation: Optional[float] = None
    flow_deviation: Optional[float] = None
    level_deviation: Optional[float] = None

class MonitoringStartRequest(BaseModel):
    thresholds: Optional[ThresholdUpdate] = None

# API endpoints
@router.post("/baseline/establish")
async def establish_baseline() -> Dict[str, Any]:
    """
    Establish baseline from original network design conditions
    This is the CRITICAL first step before any monitoring
    """
    try:
        result = baseline_engine.establish_baseline()
        return result
    except Exception as e:
        logger.error(f"Failed to establish baseline: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to establish baseline: {str(e)}"
        )

@router.get("/baseline/status")
async def get_baseline_status() -> Dict[str, Any]:
    """Get baseline establishment status"""
    try:
        if baseline_engine.is_baseline_established():
            summary = baseline_engine.get_baseline_summary()
            return summary
        else:
            return {
                "success": False,
                "baseline_established": False,
                "message": "Baseline not established"
            }
    except Exception as e:
        logger.error(f"Failed to get baseline status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get baseline status: {str(e)}"
        )

@router.get("/baseline/pressures")
async def get_baseline_pressures() -> Dict[str, Any]:
    """Get baseline pressure values"""
    try:
        if not baseline_engine.is_baseline_established():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Baseline not established"
            )
        
        pressures = baseline_engine.get_baseline_pressures()
        return {
            "success": True,
            "pressures": pressures,
            "count": len(pressures)
        }
    except Exception as e:
        logger.error(f"Failed to get baseline pressures: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get baseline pressures: {str(e)}"
        )

@router.get("/baseline/flows")
async def get_baseline_flows() -> Dict[str, Any]:
    """Get baseline flow values"""
    try:
        if not baseline_engine.is_baseline_established():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Baseline not established"
            )
        
        flows = baseline_engine.get_baseline_flows()
        return {
            "success": True,
            "flows": flows,
            "count": len(flows)
        }
    except Exception as e:
        logger.error(f"Failed to get baseline flows: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get baseline flows: {str(e)}"
        )

@router.get("/baseline/levels")
async def get_baseline_levels() -> Dict[str, Any]:
    """Get baseline tank level values"""
    try:
        if not baseline_engine.is_baseline_established():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Baseline not established"
            )
        
        levels = baseline_engine.get_baseline_tank_levels()
        return {
            "success": True,
            "levels": levels,
            "count": len(levels)
        }
    except Exception as e:
        logger.error(f"Failed to get baseline levels: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get baseline levels: {str(e)}"
        )

@router.post("/monitoring/start")
async def start_monitoring(request: Optional[MonitoringStartRequest] = None) -> Dict[str, Any]:
    """
    Start the monitoring engine
    Requires baseline to be established first
    """
    try:
        # Update thresholds if provided
        if request and request.thresholds:
            threshold_dict = request.thresholds.dict(exclude_unset=True)
            if threshold_dict:
                monitoring_engine.set_anomaly_thresholds(threshold_dict)
        
        result = monitoring_engine.start_monitoring()
        return result
    except Exception as e:
        logger.error(f"Failed to start monitoring: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start monitoring: {str(e)}"
        )

@router.post("/monitoring/stop")
async def stop_monitoring() -> Dict[str, Any]:
    """Stop the monitoring engine"""
    try:
        result = monitoring_engine.stop_monitoring()
        return result
    except Exception as e:
        logger.error(f"Failed to stop monitoring: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop monitoring: {str(e)}"
        )

@router.get("/monitoring/status")
async def get_monitoring_status() -> Dict[str, Any]:
    """Get current monitoring status"""
    try:
        status = monitoring_engine.get_monitoring_status()
        return {
            "success": True,
            "status": status
        }
    except Exception as e:
        logger.error(f"Failed to get monitoring status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get monitoring status: {str(e)}"
        )

@router.post("/monitoring/analyze")
async def analyze_current_readings() -> Dict[str, Any]:
    """
    Analyze current SCADA readings against baseline
    This is the core monitoring function
    """
    try:
        result = monitoring_engine.analyze_current_readings()
        return result
    except Exception as e:
        logger.error(f"Failed to analyze readings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze readings: {str(e)}"
        )

@router.put("/monitoring/thresholds")
async def update_anomaly_thresholds(thresholds: ThresholdUpdate) -> Dict[str, Any]:
    """Update anomaly detection thresholds"""
    try:
        threshold_dict = thresholds.dict(exclude_unset=True)
        result = monitoring_engine.set_anomaly_thresholds(threshold_dict)
        return result
    except Exception as e:
        logger.error(f"Failed to update thresholds: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update thresholds: {str(e)}"
        )

@router.get("/monitoring/health")
async def get_monitoring_health() -> Dict[str, Any]:
    """Get overall monitoring system health"""
    try:
        baseline_status = baseline_engine.is_baseline_established()
        monitoring_status = monitoring_engine.get_monitoring_status()
        
        health_score = 0
        if baseline_status:
            health_score += 50
        if monitoring_status['monitoring_active']:
            health_score += 50
        
        return {
            "success": True,
            "health_score": health_score,
            "baseline_established": baseline_status,
            "monitoring_active": monitoring_status['monitoring_active'],
            "anomaly_thresholds": monitoring_status['anomaly_thresholds'],
            "recent_anomalies": monitoring_status['recent_anomalies_count']
        }
    except Exception as e:
        logger.error(f"Failed to get monitoring health: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get monitoring health: {str(e)}"
        )

