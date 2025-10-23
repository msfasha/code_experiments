"""
Network Loader Service
Handles EPANET .inp file parsing and network information extraction
"""
import epyt
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from services.network_state import network_state

class NetworkLoader:
    """
    Service for loading and parsing EPANET network files
    """
    
    def __init__(self):
        self.current_network = None
        self.network_file_path = None
    
    def load_network(self, file_path: str) -> Dict[str, Any]:
        """
        Load an EPANET .inp file and extract network information
        
        Args:
            file_path: Path to the .inp file
            
        Returns:
            Dictionary containing network information
        """
        try:
            # Load network with EPyT
            network = epyt.epanet(file_path)
            
            # Update global state
            network_state.set_network(network, file_path)
            
            # Update local state for backward compatibility
            self.current_network = network
            self.network_file_path = file_path
            
            # Extract network information
            network_info = self._extract_network_info()
            
            return {
                "success": True,
                "message": "Network loaded successfully",
                "network_info": network_info,
                "file_path": file_path,
                "loaded_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to load network: {str(e)}",
                "error": str(e),
                "file_path": file_path
            }
    
    def _extract_network_info(self) -> Dict[str, Any]:
        """
        Extract comprehensive network information from loaded EPANET model
        """
        if not self.current_network:
            raise ValueError("No network loaded")
        
        try:
            # Get basic network statistics
            num_junctions = self.current_network.getNodeJunctionCount()
            num_pipes = self.current_network.getLinkPipeCount()
            num_pumps = self.current_network.getLinkPumpCount()
            num_tanks = self.current_network.getNodeTankCount()
            num_reservoirs = self.current_network.getNodeReservoirCount()
            
            # Get junction information
            junction_ids = self.current_network.getNodeJunctionNameID()
            junction_elevations = self.current_network.getNodeElevations()
            junction_demands = self.current_network.getNodeBaseDemands()
            
            # Get pipe information
            pipe_ids = self.current_network.getLinkPipeNameID()
            pipe_lengths = self.current_network.getLinkLength()
            pipe_diameters = self.current_network.getLinkDiameter()
            
            # Get pump information
            pump_ids = self.current_network.getLinkPumpNameID()
            
            # Get tank information
            tank_ids = self.current_network.getNodeTankNameID()
            
            # Get coordinates for visualization
            coordinates = self._get_node_coordinates()
            
            # Get reservoir information
            reservoir_ids = self.current_network.getNodeReservoirNameID()
            
            return {
                "summary": {
                    "total_junctions": num_junctions,
                    "total_pipes": num_pipes,
                    "total_pumps": num_pumps,
                    "total_tanks": num_tanks,
                    "total_reservoirs": num_reservoirs,
                    "total_nodes": num_junctions + num_tanks + num_reservoirs,
                    "total_links": num_pipes + num_pumps
                },
                "junctions": {
                    "ids": junction_ids,
                    "count": num_junctions,
                    "elevations": dict(zip(junction_ids, junction_elevations)),
                    "base_demands": dict(zip(junction_ids, junction_demands))
                },
                "pipes": {
                    "ids": pipe_ids,
                    "count": num_pipes,
                    "lengths": dict(zip(pipe_ids, pipe_lengths)),
                    "diameters": dict(zip(pipe_ids, pipe_diameters))
                },
                "pumps": {
                    "ids": pump_ids,
                    "count": num_pumps
                },
                "tanks": {
                    "ids": tank_ids,
                    "count": num_tanks
                },
                "reservoirs": {
                    "ids": reservoir_ids,
                    "count": num_reservoirs
                },
                "coordinates": coordinates,
                "network_properties": {
                    "has_coordinates": len(coordinates) > 0,
                    "total_demand": sum(junction_demands) if junction_demands is not None and len(junction_demands) > 0 else 0,
                    "avg_pipe_length": sum(pipe_lengths) / len(pipe_lengths) if pipe_lengths is not None and len(pipe_lengths) > 0 else 0,
                    "avg_pipe_diameter": sum(pipe_diameters) / len(pipe_diameters) if pipe_diameters is not None and len(pipe_diameters) > 0 else 0
                }
            }
            
        except Exception as e:
            raise Exception(f"Failed to extract network information: {str(e)}")
    
    def _get_node_coordinates(self) -> Dict[str, Dict[str, float]]:
        """
        Get node coordinates for visualization
        Returns empty dict if coordinates not available
        """
        try:
            # Try to get coordinates
            coords = self.current_network.getNodeCoordinates()
            return coords
        except:
            # Coordinates not available in this network file
            return {}
    
    def get_network_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the currently loaded network
        """
        if not self.current_network:
            return {"error": "No network loaded"}
        
        try:
            info = self._extract_network_info()
            return {
                "success": True,
                "summary": info["summary"],
                "network_properties": info["network_properties"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_node_coordinates(self) -> Dict[str, Dict[str, float]]:
        """
        Get coordinates for all nodes
        """
        if not self.current_network:
            return {}
        
        return self._get_node_coordinates()
    
    def get_network_for_simulation(self):
        """
        Get the EPyT network object for running simulations
        """
        return self.current_network
    
    def is_network_loaded(self) -> bool:
        """
        Check if a network is currently loaded
        """
        return self.current_network is not None
    
    def clear_network(self):
        """
        Clear the currently loaded network
        """
        self.current_network = None
        self.network_file_path = None
