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
from services.demand_forecaster import DemandForecaster
from services.baseline_engine import baseline_engine
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
        self._demand_forecaster = DemandForecaster()
        
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
        """Generate realistic SCADA data based on baseline + variations"""
        if not network_state.is_loaded:
            return
        
        db = SessionLocal()
        try:
            current_time = datetime.now()
            
            # Check if baseline is established
            if not baseline_engine.is_baseline_established():
                logger.warning("Baseline not established, using fallback data generation")
                await self._generate_fallback_data(db)
                return
            
            # Generate SCADA data based on baseline + realistic variations
            await self._generate_baseline_based_data(db, current_time)
            
            db.commit()
            logger.debug(f"Generated SCADA data based on baseline + variations")
            
        except Exception as e:
            logger.error(f"Error generating SCADA data: {str(e)}")
            db.rollback()
        finally:
            db.close()
    
    async def _generate_baseline_based_data(self, db, current_time: datetime):
        """Generate SCADA data based on baseline + realistic variations"""
        try:
            # Get baseline values
            baseline_pressures = baseline_engine.get_baseline_pressures()
            baseline_flows = baseline_engine.get_baseline_flows()
            baseline_levels = baseline_engine.get_baseline_tank_levels()
            
            # Generate pressure readings with realistic variations
            for junction_id, baseline_pressure in baseline_pressures.items():
                # Add time-of-day variation (±20% typical for water systems)
                time_variation = self._get_time_of_day_variation(current_time)
                variation_factor = 1.0 + (time_variation * 0.2)  # ±20% max variation
                
                # Add random noise (±2% typical sensor noise)
                noise_factor = 1.0 + random.gauss(0, 0.02)
                
                # Calculate final pressure
                final_pressure = baseline_pressure * variation_factor * noise_factor
                
                # Ensure reasonable pressure range (10-150 PSI)
                final_pressure = max(10, min(150, final_pressure))
                
                reading = SCADAReading(
                    node_id=junction_id,
                    sensor_type="pressure",
                    value=round(final_pressure, 2),
                    unit="psi",
                    quality="good"
                )
                db.add(reading)
            
            # Generate flow readings with realistic variations
            for pump_id, baseline_flow in baseline_flows.items():
                # Add time-of-day variation (±30% typical for pump flows)
                time_variation = self._get_time_of_day_variation(current_time)
                variation_factor = 1.0 + (time_variation * 0.3)  # ±30% max variation
                
                # Add random noise (±5% typical flow meter noise)
                noise_factor = 1.0 + random.gauss(0, 0.05)
                
                # Calculate final flow
                final_flow = baseline_flow * variation_factor * noise_factor
                
                # Ensure non-negative flow
                final_flow = max(0, final_flow)
                
                reading = SCADAReading(
                    node_id=pump_id,
                    sensor_type="flow",
                    value=round(final_flow, 2),
                    unit="gpm",
                    quality="good"
                )
                db.add(reading)
            
            # Generate tank level readings with realistic variations
            for tank_id, baseline_level in baseline_levels.items():
                # Add time-of-day variation (±15% typical for tank levels)
                time_variation = self._get_time_of_day_variation(current_time)
                variation_factor = 1.0 + (time_variation * 0.15)  # ±15% max variation
                
                # Add random noise (±1% typical level sensor noise)
                noise_factor = 1.0 + random.gauss(0, 0.01)
                
                # Calculate final level
                final_level = baseline_level * variation_factor * noise_factor
                
                # Ensure non-negative level
                final_level = max(0, final_level)
                
                reading = SCADAReading(
                    node_id=tank_id,
                    sensor_type="level",
                    value=round(final_level, 2),
                    unit="ft",
                    quality="good"
                )
                db.add(reading)
                
        except Exception as e:
            logger.error(f"Error generating baseline-based data: {str(e)}")
            raise
    
    def _get_time_of_day_variation(self, current_time: datetime) -> float:
        """Get time-of-day variation factor (-1 to +1)"""
        hour = current_time.hour
        
        # Typical water system variation pattern
        # Morning peak (7-9 AM): +0.5 to +1.0
        # Evening peak (6-8 PM): +0.3 to +0.8
        # Night low (2-5 AM): -0.5 to -0.8
        # Day normal (10 AM-5 PM): -0.2 to +0.2
        
        if 7 <= hour <= 9:  # Morning peak
            return random.uniform(0.5, 1.0)
        elif 18 <= hour <= 20:  # Evening peak
            return random.uniform(0.3, 0.8)
        elif 2 <= hour <= 5:  # Night low
            return random.uniform(-0.8, -0.5)
        else:  # Normal day
            return random.uniform(-0.2, 0.2)
    
    def _run_hydraulic_simulation(self, network, demands: Dict[str, float]) -> Optional[Dict[str, Any]]:
        """
        Run EPANET hydraulic simulation with estimated demands
        Returns simulation results or None if failed
        """
        try:
            # Set demands in the network
            junction_ids = network.getNodeJunctionNameID()
            for i, junction_id in enumerate(junction_ids):
                if junction_id in demands:
                    # Set demand for this junction
                    network.setNodeBaseDemands(i + 1, demands[junction_id])
            
            # Run hydraulic analysis
            network.openHydraulicAnalysis()
            network.initializeHydraulicAnalysis(0)
            
            # Run simulation
            t = network.runHydraulicAnalysis()
            if t <= 0:
                logger.warning("Hydraulic analysis failed to converge")
                network.closeHydraulicAnalysis()
                return None
            
            # Extract results
            pressures = network.getNodePressure()
            flows = network.getLinkFlows()
            tank_levels = network.getNodeTankLevel()
            
            network.closeHydraulicAnalysis()
            
            return {
                'pressures': pressures,
                'flows': flows,
                'tank_levels': tank_levels,
                'junction_ids': junction_ids,
                'pump_ids': network.getLinkPumpNameID(),
                'tank_ids': network.getNodeTankNameID()
            }
            
        except Exception as e:
            logger.error(f"Error running hydraulic simulation: {str(e)}")
            try:
                network.closeHydraulicAnalysis()
            except:
                pass
            return None
    
    async def _store_pressure_readings(self, db, results: Dict[str, Any]):
        """Store pressure readings with sensor noise"""
        junction_ids = results['junction_ids']
        pressures = results['pressures']
        
        for i, junction_id in enumerate(junction_ids):
            if i < len(pressures) and pressures[i] is not None:
                # Convert from meters to PSI (1 meter = 1.42 PSI)
                pressure_m = pressures[i]
                pressure_psi = pressure_m * 1.42
                
                # Add sensor noise (±2% typical for pressure sensors)
                noise = random.gauss(0, pressure_psi * 0.02)
                final_pressure = pressure_psi + noise
                
                # Ensure reasonable pressure range (10-150 PSI)
                final_pressure = max(10, min(150, final_pressure))
                
                reading = SCADAReading(
                    node_id=junction_id,
                    sensor_type="pressure",
                    value=round(final_pressure, 2),
                    unit="psi",
                    quality="good"
                )
                db.add(reading)
    
    async def _store_flow_readings(self, db, results: Dict[str, Any]):
        """Store flow readings for pumps and instrumented pipes"""
        pump_ids = results['pump_ids']
        flows = results['flows']
        
        # Get pump link indices
        for i, pump_id in enumerate(pump_ids):
            try:
                pump_index = network_state.current_network.getLinkPumpIndex(pump_id)
                if pump_index is not None and pump_index < len(flows):
                    flow_lps = flows[pump_index]  # Flow in L/s
                    flow_gpm = flow_lps * 15.85  # Convert to GPM
                    
                    # Add sensor noise (±5% typical for flow meters)
                    noise = random.gauss(0, flow_gpm * 0.05)
                    final_flow = flow_gpm + noise
                    
                    # Ensure non-negative flow
                    final_flow = max(0, final_flow)
                    
                    reading = SCADAReading(
                        node_id=pump_id,
                        sensor_type="flow",
                        value=round(final_flow, 2),
                        unit="gpm",
                        quality="good"
                    )
                    db.add(reading)
            except Exception as e:
                logger.warning(f"Could not get flow for pump {pump_id}: {str(e)}")
    
    async def _store_tank_levels(self, db, results: Dict[str, Any]):
        """Store tank level readings"""
        tank_ids = results['tank_ids']
        tank_levels = results['tank_levels']
        
        for i, tank_id in enumerate(tank_ids):
            if i < len(tank_levels) and tank_levels[i] is not None:
                level_m = tank_levels[i]
                level_ft = level_m * 3.28  # Convert to feet
                
                # Add sensor noise (±1% typical for level sensors)
                noise = random.gauss(0, level_ft * 0.01)
                final_level = level_ft + noise
                
                # Ensure non-negative level
                final_level = max(0, final_level)
                
                reading = SCADAReading(
                    node_id=tank_id,
                    sensor_type="level",
                    value=round(final_level, 2),
                    unit="ft",
                    quality="good"
                )
                db.add(reading)
    
    async def _generate_fallback_data(self, db):
        """Fallback to basic simulation if EPANET fails"""
        logger.warning("Using fallback data generation due to EPANET simulation failure")
        
        network = network_state.current_network
        junction_ids = network.getNodeJunctionNameID()
        pump_ids = network.getLinkPumpNameID()
        tank_ids = network.getNodeTankNameID()
        
        # Generate basic pressure readings (still better than completely random)
        for junction_id in junction_ids:
            # More realistic pressure range based on typical water systems
            base_pressure = 40.0 + random.uniform(-5, 15)  # 35-55 psi
            
            # Add variation based on config
            variation = random.uniform(-self._config.pressure_variation, self._config.pressure_variation)
            pressure = base_pressure * (1 + variation)
            
            reading = SCADAReading(
                node_id=junction_id,
                sensor_type="pressure",
                value=round(pressure, 2),
                unit="psi",
                quality="good"
            )
            db.add(reading)
        
        # Generate basic flow readings
        for pump_id in pump_ids:
            base_flow = 80.0 + random.uniform(-15, 25)  # 65-105 gpm
            variation = random.uniform(-self._config.flow_variation, self._config.flow_variation)
            flow = base_flow * (1 + variation)
            
            reading = SCADAReading(
                node_id=pump_id,
                sensor_type="flow",
                value=round(flow, 2),
                unit="gpm",
                quality="good"
            )
            db.add(reading)
        
        # Generate basic tank levels
        for tank_id in tank_ids:
            base_level = 15.0 + random.uniform(-3, 5)  # 12-20 ft
            variation = random.uniform(-self._config.level_variation, self._config.level_variation)
            level = base_level * (1 + variation)
            
            reading = SCADAReading(
                node_id=tank_id,
                sensor_type="level",
                value=round(level, 2),
                unit="ft",
                quality="good"
            )
            db.add(reading)

# Global simulator instance
scada_simulator = SCADASimulator()
