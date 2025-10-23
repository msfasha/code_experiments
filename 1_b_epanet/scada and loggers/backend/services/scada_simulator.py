import asyncio
import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from models.database import SessionLocal
from models.tables import SCADAReading, SCADASimulatorConfig, NetworkComponent
from services.network_loader import NetworkLoader
from services.network_state import network_state
import logging

logger = logging.getLogger(__name__)

class SCADASimulator:
    """SCADA data simulator that generates synthetic sensor readings"""
    
    def __init__(self):
        self._running = False
        self._task = None
        self._config = None
        # Use the global singleton instance
        self._network_loader = NetworkLoader()
        
    @property
    def is_running(self) -> bool:
        return self._running
    
    async def start(self, config: Dict[str, Any] = None) -> Dict[str, Anyr]:
        """Start the SCADA simulator"""
        if self._running:
            return {"message": "Simulator already running", "success": False}
        
        # Load or create configuration
        db = SessionLocal()
        try:
            self._config = db.query(SCADASimulatorConfig).first()
            if not self._config:
                self._config = SCADASimulatorConfig()
                db.add(self._config)
                db.commit()
            
            # Update config if provided
            if config:
                for key, value in config.items():
                    if hasattr(self._config, key):
                        setattr(self._config, key, value)
                self._config.updated_at = datetime.utcnow()
                db.commit()
            
            # Check if network is loaded using global state
            if not network_state.is_loaded:
                return {"message": "No network loaded. Please upload a network file first.", "success": False}
            
            # Start the simulation task
            self._running = True
            self._config.is_running = True
            self._config.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(self._config)
            
            self._task = asyncio.create_task(self._simulation_loop())
            
            return {
                "message": "SCADA simulator started successfully",
                "success": True,
                "config": {
                    "update_interval": self._config.update_interval,
                    "pressure_variation": self._config.pressure_variation,
                    "flow_variation": self._config.flow_variation,
                    "level_variation": self._config.level_variation
                }
            }
        except Exception as e:
            logger.error(f"Failed to start SCADA simulator: {str(e)}")
            return {"message": f"Failed to start simulator: {str(e)}", "success": False}
        finally:
            db.close()
    
    async def stop(self) -> Dict[str, Any]:
        """Stop the SCADA simulator"""
        # Check database state instead of just the _running flag
        db = SessionLocal()
        try:
            config = db.query(SCADASimulatorConfig).first()
            if not config or not config.is_running:
                return {"message": "Simulator not running", "success": False}
        finally:
            db.close()
        
        try:
            self._running = False
            if self._task:
                self._task.cancel()
                try:
                    await self._task
                except asyncio.CancelledError:
                    pass
            
            # Update database
            db = SessionLocal()
            try:
                config = db.query(SCADASimulatorConfig).first()
                if config:
                    config.is_running = False
                    config.updated_at = datetime.utcnow()
                    db.commit()
                    db.refresh(config)
            finally:
                db.close()
            
            return {"message": "SCADA simulator stopped successfully", "success": True}
        except Exception as e:
            logger.error(f"Failed to stop SCADA simulator: {str(e)}")
            return {"message": f"Failed to stop simulator: {str(e)}", "success": False}
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current simulator status"""
        db = SessionLocal()
        try:
            config = db.query(SCADASimulatorConfig).first()
            if not config:
                return {
                    "is_running": False,
                    "message": "No configuration found",
                    "success": False
                }
            
            return {
                "is_running": config.is_running,
                "config": {
                    "update_interval": config.update_interval,
                    "pressure_variation": config.pressure_variation,
                    "flow_variation": config.flow_variation,
                    "level_variation": config.level_variation,
                    "fault_injection": config.fault_injection
                },
                "success": True
            }
        except Exception as e:
            logger.error(f"Failed to get simulator status: {str(e)}")
            return {"message": f"Failed to get status: {str(e)}", "success": False}
        finally:
            db.close()
    
    async def get_latest_readings(self, limit: int = 100) -> Dict[str, Any]:
        """Get latest SCADA readings"""
        db = SessionLocal()
        try:
            readings = db.query(SCADAReading).order_by(SCADAReading.timestamp.desc()).limit(limit).all()
            
            # Group readings by node and sensor type
            grouped_readings = {}
            for reading in readings:
                node_id = reading.node_id
                if node_id not in grouped_readings:
                    grouped_readings[node_id] = {}
                grouped_readings[node_id][reading.sensor_type] = {
                    "value": reading.value,
                    "unit": reading.unit,
                    "timestamp": reading.timestamp.isoformat(),
                    "quality": reading.quality
                }
            
            return {
                "readings": grouped_readings,
                "count": len(readings),
                "success": True
            }
        except Exception as e:
            logger.error(f"Failed to get latest readings: {str(e)}")
            return {"message": f"Failed to get readings: {str(e)}", "success": False}
        finally:
            db.close()
    
    async def _simulation_loop(self):
        """Main simulation loop that generates SCADA data"""
        logger.info("SCADA simulation loop started")
        
        while self._running:
            try:
                await self._generate_scada_data()
                await asyncio.sleep(self._config.update_interval)
            except asyncio.CancelledError:
                logger.info("SCADA simulation loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in simulation loop: {str(e)}")
                await asyncio.sleep(5)  # Wait before retrying
        
        logger.info("SCADA simulation loop stopped")
    
    async def _generate_scada_data(self):
        """Generate synthetic SCADA data for all network components"""
        if not network_state.is_loaded:
            return
        
        db = SessionLocal()
        try:
            network = network_state.current_network
            
            # Get network components
            junction_ids = network.getNodeJunctionNameID()
            tank_ids = network.getNodeTankNameID()
            pump_ids = network.getLinkPumpNameID()
            
            # Generate pressure readings for junctions
            for i, junction_id in enumerate(junction_ids):
                # Base pressure (simulated)
                base_pressure = 50.0 + random.uniform(-10, 10)  # 40-60 psi
                
                # Add variation based on config
                variation = random.uniform(-self._config.pressure_variation, self._config.pressure_variation)
                pressure = base_pressure * (1 + variation)
                
                # Store reading
                reading = SCADAReading(
                    node_id=junction_id,
                    sensor_type="pressure",
                    value=pressure,
                    unit="psi",
                    quality="good"
                )
                db.add(reading)
            
            # Generate flow readings for pumps
            for i, pump_id in enumerate(pump_ids):
                # Base flow (simulated)
                base_flow = 100.0 + random.uniform(-20, 20)  # 80-120 gpm
                
                # Add variation based on config
                variation = random.uniform(-self._config.flow_variation, self._config.flow_variation)
                flow = base_flow * (1 + variation)
                
                # Store reading
                reading = SCADAReading(
                    node_id=pump_id,
                    sensor_type="flow",
                    value=flow,
                    unit="gpm",
                    quality="good"
                )
                db.add(reading)
            
            # Generate level readings for tanks
            for i, tank_id in enumerate(tank_ids):
                # Base level (simulated)
                base_level = 20.0 + random.uniform(-2, 2)  # 18-22 ft
                
                # Add variation based on config
                variation = random.uniform(-self._config.level_variation, self._config.level_variation)
                level = base_level * (1 + variation)
                
                # Store reading
                reading = SCADAReading(
                    node_id=tank_id,
                    sensor_type="level",
                    value=level,
                    unit="ft",
                    quality="good"
                )
                db.add(reading)
            
            db.commit()
            logger.debug(f"Generated SCADA data for {len(junction_ids)} junctions, {len(pump_ids)} pumps, {len(tank_ids)} tanks")
            
        except Exception as e:
            logger.error(f"Error generating SCADA data: {str(e)}")
            db.rollback()
        finally:
            db.close()

# Global simulator instance
scada_simulator = SCADASimulator()
