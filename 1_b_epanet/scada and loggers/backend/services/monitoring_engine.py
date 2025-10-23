"""
Monitoring Engine Service
Compares current SCADA readings vs baseline to detect drifts and anomalies
This is the core value-add component of the system
"""
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models.database import SessionLocal
from models.tables import SCADAReading
from services.baseline_engine import baseline_engine
from services.network_state import network_state

logger = logging.getLogger(__name__)

class MonitoringEngine:
    """
    Monitors network by comparing current SCADA readings vs baseline
    This is the core monitoring logic that detects drifts from normal operation
    """
    
    def __init__(self):
        self.monitoring_active = False
        self.anomaly_thresholds = {
            'pressure_deviation': 10.0,  # 10% deviation from baseline
            'flow_deviation': 15.0,      # 15% deviation from baseline
            'level_deviation': 20.0      # 20% deviation from baseline
        }
        self.recent_anomalies = []
    
    def start_monitoring(self) -> Dict[str, Any]:
        """Start the monitoring engine"""
        if not baseline_engine.is_baseline_established():
            return {
                "success": False,
                "message": "Baseline not established. Cannot start monitoring."
            }
        
        if not network_state.is_loaded:
            return {
                "success": False,
                "message": "No network loaded. Cannot start monitoring."
            }
        
        self.monitoring_active = True
        logger.info("Monitoring engine started")
        
        return {
            "success": True,
            "message": "Monitoring engine started successfully",
            "baseline_established": True,
            "anomaly_thresholds": self.anomaly_thresholds
        }
    
    def stop_monitoring(self) -> Dict[str, Any]:
        """Stop the monitoring engine"""
        self.monitoring_active = False
        logger.info("Monitoring engine stopped")
        
        return {
            "success": True,
            "message": "Monitoring engine stopped successfully"
        }
    
    def analyze_current_readings(self) -> Dict[str, Any]:
        """
        Analyze current SCADA readings against baseline
        This is the core monitoring function
        """
        if not self.monitoring_active:
            return {
                "success": False,
                "message": "Monitoring not active"
            }
        
        if not baseline_engine.is_baseline_established():
            return {
                "success": False,
                "message": "Baseline not established"
            }
        
        try:
            # Get latest SCADA readings
            current_readings = self._get_latest_scada_readings()
            if not current_readings:
                return {
                    "success": False,
                    "message": "No current SCADA readings available"
                }
            
            # Get baseline values
            baseline_pressures = baseline_engine.get_baseline_pressures()
            baseline_flows = baseline_engine.get_baseline_flows()
            baseline_levels = baseline_engine.get_baseline_tank_levels()
            
            # Analyze deviations
            analysis_results = self._analyze_deviations(
                current_readings,
                baseline_pressures,
                baseline_flows,
                baseline_levels
            )
            
            # Detect anomalies
            anomalies = self._detect_anomalies(analysis_results)
            
            # Store analysis results
            self._store_analysis_results(analysis_results, anomalies)
            
            return {
                "success": True,
                "analysis_timestamp": datetime.now().isoformat(),
                "total_readings": len(current_readings),
                "deviations_analyzed": len(analysis_results['deviations']),
                "anomalies_detected": len(anomalies),
                "analysis_results": analysis_results,
                "anomalies": anomalies
            }
            
        except Exception as e:
            logger.error(f"Error analyzing current readings: {str(e)}")
            return {
                "success": False,
                "message": f"Analysis failed: {str(e)}",
                "error": str(e)
            }
    
    def _get_latest_scada_readings(self) -> Dict[str, Dict[str, Any]]:
        """Get latest SCADA readings from database"""
        db = SessionLocal()
        try:
            # Get readings from last 5 minutes
            cutoff_time = datetime.now() - timedelta(minutes=5)
            readings = db.query(SCADAReading).filter(
                SCADAReading.timestamp >= cutoff_time
            ).order_by(SCADAReading.timestamp.desc()).all()
            
            # Group by node and sensor type
            grouped_readings = {}
            for reading in readings:
                node_id = reading.node_id
                if node_id not in grouped_readings:
                    grouped_readings[node_id] = {}
                grouped_readings[node_id][reading.sensor_type] = {
                    "value": reading.value,
                    "unit": reading.unit,
                    "timestamp": reading.timestamp,
                    "quality": reading.quality
                }
            
            return grouped_readings
            
        except Exception as e:
            logger.error(f"Error getting SCADA readings: {str(e)}")
            return {}
        finally:
            db.close()
    
    def _analyze_deviations(self, current_readings: Dict, baseline_pressures: Dict, 
                          baseline_flows: Dict, baseline_levels: Dict) -> Dict[str, Any]:
        """Analyze deviations between current readings and baseline"""
        deviations = []
        analysis_summary = {
            'total_analyzed': 0,
            'pressure_deviations': 0,
            'flow_deviations': 0,
            'level_deviations': 0,
            'max_deviation': 0.0,
            'avg_deviation': 0.0
        }
        
        total_deviation = 0.0
        deviation_count = 0
        
        # Analyze pressure deviations
        for node_id, readings in current_readings.items():
            if 'pressure' in readings and node_id in baseline_pressures:
                current_pressure = readings['pressure']['value']
                baseline_pressure = baseline_pressures[node_id]
                
                if baseline_pressure > 0:  # Avoid division by zero
                    deviation_pct = ((current_pressure - baseline_pressure) / baseline_pressure) * 100
                    
                    deviations.append({
                        'node_id': node_id,
                        'sensor_type': 'pressure',
                        'current_value': current_pressure,
                        'baseline_value': baseline_pressure,
                        'deviation_pct': deviation_pct,
                        'unit': readings['pressure']['unit'],
                        'timestamp': readings['pressure']['timestamp']
                    })
                    
                    total_deviation += abs(deviation_pct)
                    deviation_count += 1
                    analysis_summary['pressure_deviations'] += 1
        
        # Analyze flow deviations
        for node_id, readings in current_readings.items():
            if 'flow' in readings and node_id in baseline_flows:
                current_flow = readings['flow']['value']
                baseline_flow = baseline_flows[node_id]
                
                if baseline_flow > 0:  # Avoid division by zero
                    deviation_pct = ((current_flow - baseline_flow) / baseline_flow) * 100
                    
                    deviations.append({
                        'node_id': node_id,
                        'sensor_type': 'flow',
                        'current_value': current_flow,
                        'baseline_value': baseline_flow,
                        'deviation_pct': deviation_pct,
                        'unit': readings['flow']['unit'],
                        'timestamp': readings['flow']['timestamp']
                    })
                    
                    total_deviation += abs(deviation_pct)
                    deviation_count += 1
                    analysis_summary['flow_deviations'] += 1
        
        # Analyze level deviations
        for node_id, readings in current_readings.items():
            if 'level' in readings and node_id in baseline_levels:
                current_level = readings['level']['value']
                baseline_level = baseline_levels[node_id]
                
                if baseline_level > 0:  # Avoid division by zero
                    deviation_pct = ((current_level - baseline_level) / baseline_level) * 100
                    
                    deviations.append({
                        'node_id': node_id,
                        'sensor_type': 'level',
                        'current_value': current_level,
                        'baseline_value': baseline_level,
                        'deviation_pct': deviation_pct,
                        'unit': readings['level']['unit'],
                        'timestamp': readings['level']['timestamp']
                    })
                    
                    total_deviation += abs(deviation_pct)
                    deviation_count += 1
                    analysis_summary['level_deviations'] += 1
        
        # Calculate summary statistics
        analysis_summary['total_analyzed'] = len(deviations)
        analysis_summary['max_deviation'] = max([abs(d['deviation_pct']) for d in deviations]) if deviations else 0.0
        analysis_summary['avg_deviation'] = total_deviation / deviation_count if deviation_count > 0 else 0.0
        
        return {
            'deviations': deviations,
            'summary': analysis_summary,
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def _detect_anomalies(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect anomalies based on deviation thresholds"""
        anomalies = []
        deviations = analysis_results['deviations']
        
        for deviation in deviations:
            sensor_type = deviation['sensor_type']
            deviation_pct = abs(deviation['deviation_pct'])
            
            # Check against thresholds
            threshold = self.anomaly_thresholds.get(f'{sensor_type}_deviation', 10.0)
            
            if deviation_pct > threshold:
                anomaly = {
                    'node_id': deviation['node_id'],
                    'sensor_type': sensor_type,
                    'deviation_pct': deviation['deviation_pct'],
                    'threshold': threshold,
                    'severity': self._calculate_severity(deviation_pct, threshold),
                    'current_value': deviation['current_value'],
                    'baseline_value': deviation['baseline_value'],
                    'unit': deviation['unit'],
                    'timestamp': deviation['timestamp'],
                    'detected_at': datetime.now().isoformat()
                }
                anomalies.append(anomaly)
        
        return anomalies
    
    def _calculate_severity(self, deviation_pct: float, threshold: float) -> str:
        """Calculate anomaly severity"""
        if deviation_pct > threshold * 3:
            return 'critical'
        elif deviation_pct > threshold * 2:
            return 'high'
        elif deviation_pct > threshold:
            return 'medium'
        else:
            return 'low'
    
    def _store_analysis_results(self, analysis_results: Dict[str, Any], anomalies: List[Dict[str, Any]]):
        """Store analysis results in database"""
        # This would store results in a monitoring_results table
        # For now, just log the results
        logger.info(f"Analysis completed: {len(analysis_results['deviations'])} deviations, {len(anomalies)} anomalies")
        
        if anomalies:
            for anomaly in anomalies:
                logger.warning(f"Anomaly detected: {anomaly['node_id']} {anomaly['sensor_type']} "
                             f"deviation {anomaly['deviation_pct']:.1f}% (threshold: {anomaly['threshold']}%)")
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        return {
            "monitoring_active": self.monitoring_active,
            "baseline_established": baseline_engine.is_baseline_established(),
            "anomaly_thresholds": self.anomaly_thresholds,
            "recent_anomalies_count": len(self.recent_anomalies)
        }
    
    def set_anomaly_thresholds(self, thresholds: Dict[str, float]) -> Dict[str, Any]:
        """Update anomaly detection thresholds"""
        try:
            for key, value in thresholds.items():
                if key in self.anomaly_thresholds:
                    self.anomaly_thresholds[key] = value
            
            return {
                "success": True,
                "message": "Thresholds updated successfully",
                "new_thresholds": self.anomaly_thresholds
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to update thresholds: {str(e)}"
            }

# Global monitoring engine instance
monitoring_engine = MonitoringEngine()

