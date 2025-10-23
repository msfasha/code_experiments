"""
Baseline Engine Service
Establishes baseline network conditions from original EPANET design
This is the foundation for all monitoring and anomaly detection
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from services.network_state import network_state
import epyt

logger = logging.getLogger(__name__)

class BaselineEngine:
    """
    Establishes baseline network conditions from original EPANET design
    This baseline serves as the reference point for all monitoring
    """
    
    def __init__(self):
        self.baseline_data = None
        self.baseline_established = False
        self.baseline_timestamp = None
    
    def establish_baseline(self) -> Dict[str, Any]:
        """
        Establish baseline from original network design conditions
        This is the CRITICAL first step - must be done before any monitoring
        """
        if not network_state.is_loaded:
            raise ValueError("No network loaded. Cannot establish baseline.")
        
        try:
            network = network_state.current_network
            logger.info("Establishing baseline from original network design conditions")
            
            # Run EPANET with ORIGINAL design conditions (from .inp file)
            baseline_results = self._run_baseline_simulation(network)
            
            if not baseline_results:
                raise Exception("Failed to establish baseline - EPANET simulation failed")
            
            # Store baseline data
            self.baseline_data = baseline_results
            self.baseline_established = True
            self.baseline_timestamp = datetime.now()
            
            logger.info(f"Baseline established successfully with {len(baseline_results['pressures'])} pressure points")
            
            return {
                "success": True,
                "message": "Baseline established successfully",
                "baseline_data": baseline_results,
                "established_at": self.baseline_timestamp.isoformat(),
                "network_file": network_state.network_path
            }
            
        except Exception as e:
            logger.error(f"Failed to establish baseline: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to establish baseline: {str(e)}",
                "error": str(e)
            }
    
    def _run_baseline_simulation(self, network) -> Optional[Dict[str, Any]]:
        """
        Run EPANET with ORIGINAL design conditions from .inp file
        This is the true baseline - not estimated demands
        """
        try:
            # Use ORIGINAL demands from the .inp file (not estimated)
            original_demands = network.getNodeBaseDemands()
            
            # Run hydraulic analysis with original conditions
            network.openHydraulicAnalysis()
            network.initializeHydraulicAnalysis(0)
            
            # Run simulation
            t = network.runHydraulicAnalysis()
            if t <= 0:
                logger.warning("Baseline hydraulic analysis failed to converge")
                network.closeHydraulicAnalysis()
                return None
            
            # Extract baseline results
            baseline_pressures = network.getNodePressure()
            baseline_flows = network.getLinkFlows()
            baseline_tank_levels = network.getNodeTankLevel()
            baseline_pump_status = network.getLinkPumpState()
            
            network.closeHydraulicAnalysis()
            
            # Get network component IDs
            junction_ids = network.getNodeJunctionNameID()
            pump_ids = network.getLinkPumpNameID()
            tank_ids = network.getNodeTankNameID()
            pipe_ids = network.getLinkPipeNameID()
            
            return {
                'pressures': baseline_pressures,
                'flows': baseline_flows,
                'tank_levels': baseline_tank_levels,
                'pump_status': baseline_pump_status,
                'junction_ids': junction_ids,
                'pump_ids': pump_ids,
                'tank_ids': tank_ids,
                'pipe_ids': pipe_ids,
                'original_demands': original_demands,
                'network_info': {
                    'total_junctions': len(junction_ids),
                    'total_pumps': len(pump_ids),
                    'total_tanks': len(tank_ids),
                    'total_pipes': len(pipe_ids)
                }
            }
            
        except Exception as e:
            logger.error(f"Error running baseline simulation: {str(e)}")
            try:
                network.closeHydraulicAnalysis()
            except:
                pass
            return None
    
    def get_baseline_pressures(self) -> Dict[str, float]:
        """
        Get baseline pressures for all junctions
        Returns dict of {junction_id: pressure_value}
        """
        if not self.baseline_established or not self.baseline_data:
            raise ValueError("Baseline not established. Call establish_baseline() first.")
        
        pressures = {}
        junction_ids = self.baseline_data['junction_ids']
        baseline_pressures = self.baseline_data['pressures']
        
        for i, junction_id in enumerate(junction_ids):
            if i < len(baseline_pressures) and baseline_pressures[i] is not None:
                # Convert from meters to PSI (1 meter = 1.42 PSI)
                pressure_m = baseline_pressures[i]
                pressure_psi = pressure_m * 1.42
                pressures[junction_id] = pressure_psi
        
        return pressures
    
    def get_baseline_flows(self) -> Dict[str, float]:
        """
        Get baseline flows for all pumps
        Returns dict of {pump_id: flow_value}
        """
        if not self.baseline_established or not self.baseline_data:
            raise ValueError("Baseline not established. Call establish_baseline() first.")
        
        flows = {}
        pump_ids = self.baseline_data['pump_ids']
        baseline_flows = self.baseline_data['flows']
        
        for i, pump_id in enumerate(pump_ids):
            try:
                pump_index = network_state.current_network.getLinkPumpIndex(pump_id)
                if pump_index is not None and pump_index < len(baseline_flows):
                    flow_lps = baseline_flows[pump_index]  # Flow in L/s
                    flow_gpm = flow_lps * 15.85  # Convert to GPM
                    flows[pump_id] = flow_gpm
            except Exception as e:
                logger.warning(f"Could not get baseline flow for pump {pump_id}: {str(e)}")
        
        return flows
    
    def get_baseline_tank_levels(self) -> Dict[str, float]:
        """
        Get baseline tank levels
        Returns dict of {tank_id: level_value}
        """
        if not self.baseline_established or not self.baseline_data:
            raise ValueError("Baseline not established. Call establish_baseline() first.")
        
        levels = {}
        tank_ids = self.baseline_data['tank_ids']
        baseline_levels = self.baseline_data['tank_levels']
        
        for i, tank_id in enumerate(tank_ids):
            if i < len(baseline_levels) and baseline_levels[i] is not None:
                level_m = baseline_levels[i]
                level_ft = level_m * 3.28  # Convert to feet
                levels[tank_id] = level_ft
        
        return levels
    
    def get_baseline_summary(self) -> Dict[str, Any]:
        """
        Get summary of baseline data
        """
        if not self.baseline_established:
            return {"error": "Baseline not established"}
        
        try:
            pressures = self.get_baseline_pressures()
            flows = self.get_baseline_flows()
            levels = self.get_baseline_tank_levels()
            
            return {
                "success": True,
                "baseline_established": True,
                "established_at": self.baseline_timestamp.isoformat(),
                "network_file": network_state.network_path,
                "summary": {
                    "total_junctions": len(pressures),
                    "total_pumps": len(flows),
                    "total_tanks": len(levels),
                    "pressure_range": {
                        "min": min(pressures.values()) if pressures else 0,
                        "max": max(pressures.values()) if pressures else 0,
                        "avg": sum(pressures.values()) / len(pressures) if pressures else 0
                    },
                    "flow_range": {
                        "min": min(flows.values()) if flows else 0,
                        "max": max(flows.values()) if flows else 0,
                        "avg": sum(flows.values()) / len(flows) if flows else 0
                    },
                    "level_range": {
                        "min": min(levels.values()) if levels else 0,
                        "max": max(levels.values()) if levels else 0,
                        "avg": sum(levels.values()) / len(levels) if levels else 0
                    }
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def is_baseline_established(self) -> bool:
        """Check if baseline is established"""
        return self.baseline_established and self.baseline_data is not None
    
    def clear_baseline(self):
        """Clear baseline data"""
        self.baseline_data = None
        self.baseline_established = False
        self.baseline_timestamp = None
        logger.info("Baseline data cleared")

# Global baseline engine instance
baseline_engine = BaselineEngine()

