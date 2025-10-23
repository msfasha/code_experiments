"""
Global network state manager
Provides a singleton pattern for sharing network state across the application
"""
import epyt
from typing import Optional, Dict, Any
from datetime import datetime

class NetworkState:
    """Global network state manager"""
    _instance = None
    _current_network: Optional[epyt.epanet] = None
    _network_path: Optional[str] = None
    _loaded_at: Optional[datetime] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NetworkState, cls).__new__(cls)
        return cls._instance
    
    @property
    def current_network(self) -> Optional[epyt.epanet]:
        return self._current_network
    
    @property
    def network_path(self) -> Optional[str]:
        return self._network_path
    
    @property
    def loaded_at(self) -> Optional[datetime]:
        return self._loaded_at
    
    @property
    def is_loaded(self) -> bool:
        return self._current_network is not None
    
    def set_network(self, network: epyt.epanet, path: str):
        """Set the current network"""
        self._current_network = network
        self._network_path = path
        self._loaded_at = datetime.utcnow()
    
    def clear_network(self):
        """Clear the current network"""
        if self._current_network:
            self._current_network.close()
        self._current_network = None
        self._network_path = None
        self._loaded_at = None
    
    def get_network_info(self) -> Dict[str, Any]:
        """Get network information if loaded"""
        if not self.is_loaded:
            raise ValueError("No network loaded")
        
        # Get basic network statistics
        num_junctions = self._current_network.getNodeJunctionCount()
        num_pipes = self._current_network.getLinkPipeCount()
        num_pumps = self._current_network.getLinkPumpCount()
        num_tanks = self._current_network.getNodeTankCount()
        num_reservoirs = self._current_network.getNodeReservoirCount()
        
        return {
            "summary": {
                "total_junctions": num_junctions,
                "total_pipes": num_pipes,
                "total_pumps": num_pumps,
                "total_tanks": num_tanks,
                "total_reservoirs": num_reservoirs,
                "total_nodes": self._current_network.getNodeCount(),
                "total_links": self._current_network.getLinkCount()
            }
        }

# Global instance
network_state = NetworkState()

