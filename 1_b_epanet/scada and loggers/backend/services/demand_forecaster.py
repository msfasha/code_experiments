"""
Demand Forecaster Service
Provides realistic demand estimation based on time-of-day patterns and historical data
"""
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from services.network_state import network_state
import logging

logger = logging.getLogger(__name__)

class DemandForecaster:
    """
    Provides demand estimates based on time-of-day patterns and network characteristics
    """
    
    def __init__(self):
        self.demand_profiles = self._initialize_demand_profiles()
    
    def get_estimated_demands(self, timestamp: datetime) -> Dict[str, float]:
        """
        Get estimated demands for all junctions at given time
        Based on typical diurnal (24-hour) patterns and network characteristics
        """
        if not network_state.is_loaded:
            logger.warning("No network loaded for demand forecasting")
            return {}
        
        try:
            network = network_state.current_network
            junction_ids = network.getNodeJunctionNameID()
            base_demands = network.getNodeBaseDemands()
            
            # Get time-based multiplier
            hour = timestamp.hour
            day_of_week = timestamp.weekday()
            multiplier = self._get_demand_multiplier(hour, day_of_week)
            
            # Add some random variation (±10%)
            variation = random.uniform(0.9, 1.1)
            final_multiplier = multiplier * variation
            
            demands = {}
            for i, junction_id in enumerate(junction_ids):
                if i < len(base_demands) and base_demands[i] is not None:
                    # Use base demand from EPANET model
                    base_demand = base_demands[i]
                else:
                    # Fallback: estimate based on junction characteristics
                    base_demand = self._estimate_base_demand(junction_id, network)
                
                # Apply time-of-day multiplier
                estimated_demand = base_demand * final_multiplier
                demands[junction_id] = max(0, estimated_demand)  # Ensure non-negative
            
            logger.debug(f"Generated demands for {len(demands)} junctions with multiplier {final_multiplier:.2f}")
            return demands
            
        except Exception as e:
            logger.error(f"Error generating demand estimates: {str(e)}")
            return {}
    
    def _get_demand_multiplier(self, hour: int, day_of_week: int) -> float:
        """
        Get demand multiplier based on time of day and day of week
        Typical water demand pattern (higher in morning/evening, lower at night)
        """
        # Weekend patterns (Saturday=5, Sunday=6)
        is_weekend = day_of_week >= 5
        
        # Base diurnal pattern (24-hour cycle)
        if is_weekend:
            # Weekend pattern - more spread out, later peak
            pattern = {
                0: 0.4, 1: 0.3, 2: 0.3, 3: 0.3, 4: 0.3, 5: 0.4, 6: 0.5,
                7: 0.7, 8: 0.9, 9: 1.0, 10: 1.1, 11: 1.2, 12: 1.3, 13: 1.2,
                14: 1.1, 15: 1.0, 16: 1.1, 17: 1.3, 18: 1.4, 19: 1.3, 20: 1.2,
                21: 1.0, 22: 0.8, 23: 0.6
            }
        else:
            # Weekday pattern - morning and evening peaks
            pattern = {
                0: 0.3, 1: 0.2, 2: 0.2, 3: 0.2, 4: 0.3, 5: 0.5, 6: 0.8,
                7: 1.2, 8: 1.4, 9: 1.3, 10: 1.1, 11: 1.0, 12: 1.1, 13: 1.0,
                14: 0.9, 15: 0.9, 16: 1.0, 17: 1.3, 18: 1.5, 19: 1.4, 20: 1.2,
                21: 0.9, 22: 0.6, 23: 0.4
            }
        
        return pattern.get(hour, 1.0)
    
    def _estimate_base_demand(self, junction_id: str, network) -> float:
        """
        Estimate base demand for a junction when not available from EPANET model
        Based on typical residential/commercial patterns
        """
        try:
            # Get junction elevation to estimate if it's residential vs commercial
            elevations = network.getNodeElevations()
            junction_index = network.getNodeJunctionIndex(junction_id)
            
            if junction_index is not None and junction_index < len(elevations):
                elevation = elevations[junction_index]
                # Higher elevation might indicate commercial/industrial
                if elevation > 100:  # Arbitrary threshold
                    return random.uniform(50, 150)  # Commercial/industrial demand
                else:
                    return random.uniform(10, 50)   # Residential demand
            else:
                return random.uniform(20, 80)  # Default range
                
        except Exception as e:
            logger.warning(f"Could not estimate demand for {junction_id}: {str(e)}")
            return random.uniform(20, 80)  # Fallback
    
    def _initialize_demand_profiles(self) -> Dict[str, Any]:
        """
        Initialize demand profiles for different junction types
        """
        return {
            "residential": {
                "base_multiplier": 1.0,
                "peak_hours": [7, 8, 18, 19],
                "low_hours": [2, 3, 4]
            },
            "commercial": {
                "base_multiplier": 2.0,
                "peak_hours": [9, 10, 11, 14, 15, 16],
                "low_hours": [0, 1, 2, 3, 4, 5, 22, 23]
            },
            "industrial": {
                "base_multiplier": 3.0,
                "peak_hours": [8, 9, 10, 11, 12, 13, 14, 15, 16, 17],
                "low_hours": [0, 1, 2, 3, 4, 5, 22, 23]
            }
        }
    
    def get_demand_forecast(self, start_time: datetime, duration_hours: int = 24) -> Dict[str, List[float]]:
        """
        Get demand forecast for multiple time steps
        Useful for extended simulations
        """
        forecast = {}
        
        for i in range(duration_hours):
            current_time = start_time + timedelta(hours=i)
            demands = self.get_estimated_demands(current_time)
            
            for junction_id, demand in demands.items():
                if junction_id not in forecast:
                    forecast[junction_id] = []
                forecast[junction_id].append(demand)
        
        return forecast

