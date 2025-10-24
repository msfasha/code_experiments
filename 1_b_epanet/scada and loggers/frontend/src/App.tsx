import { useState, useEffect } from 'react';
import { Routes, Route, Link, useLocation } from 'react-router-dom';
import axios from 'axios';
import { scadaAPI } from './api/scada';
import { NetworkProvider, useNetwork } from './contexts/NetworkContext';
import NetworkViewer from './components/NetworkViewer';

// Type definitions
interface SystemStatus {
  api: string;
  status: string;
  version: string;
  timestamp: string;
}

interface SCADAReading {
  value: number;
  unit: string;
  timestamp: string;
  quality: string;
}

interface SCADAData {
  readings: { [nodeId: string]: { [sensorType: string]: SCADAReading } };
  count: number;
  success: boolean;
}

// Navigation component
const Navigation = () => {
  const location = useLocation();
  const { isNetworkLoaded, networkInfo } = useNetwork();
  
  const navItems = [
    { path: '/monitoring', label: 'Monitoring', icon: '🔍' },
    { path: '/scada', label: 'SCADA', icon: '📊' }
  ];

  return (
    <nav style={{
      backgroundColor: '#1f2937',
      padding: '1rem 0',
      borderBottom: '1px solid #374151'
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <h1 style={{ color: 'white', margin: 0, fontSize: '1.5rem' }}>
              🚀 Water Network Monitoring
            </h1>
            {isNetworkLoaded && (
              <div style={{ 
                marginLeft: '1rem', 
                padding: '0.25rem 0.75rem', 
                backgroundColor: '#10b981', 
                borderRadius: '0.375rem',
                fontSize: '0.875rem',
                color: 'white',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem'
              }}>
                <span>🌐</span>
                <span>{networkInfo?.filename || 'Network Loaded'}</span>
              </div>
            )}
          </div>
          <div style={{ display: 'flex', gap: '2rem' }}>
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                style={{
                  color: location.pathname === item.path ? '#60a5fa' : '#d1d5db',
                  textDecoration: 'none',
                  padding: '0.5rem 1rem',
                  borderRadius: '0.375rem',
                  backgroundColor: location.pathname === item.path ? '#1e40af' : 'transparent',
                  transition: 'all 0.2s',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem'
                }}
              >
                <span>{item.icon}</span>
                {item.label}
              </Link>
            ))}
          </div>
        </div>
      </div>
    </nav>
  );
};


// SCADA page with enhanced continuous data flow
const SCADAPage = () => {
  const { isNetworkLoaded } = useNetwork();
  const [isRunning, setIsRunning] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [latestReadings, setLatestReadings] = useState<SCADAData | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(5000); // 5 seconds
  const [config, setConfig] = useState({
    update_interval: 30,
    pressure_variation: 0.1,
    flow_variation: 0.15,
    level_variation: 0.05
  });

  const loadStatus = async () => {
    try {
      const status = await scadaAPI.getStatus();
      setIsRunning(status.is_running);
      setError(null); // Clear any previous errors
      if (status.config) {
        setConfig({
          update_interval: status.config.update_interval,
          pressure_variation: status.config.pressure_variation,
          flow_variation: status.config.flow_variation,
          level_variation: status.config.level_variation,
        });
      }
    } catch (err: any) {
      setError(err.message);
    }
  };

  const loadLatestReadings = async () => {
    try {
      const readings = await scadaAPI.getLatestReadings(50);
      setLatestReadings(readings);
    } catch (err: any) {
      console.error('Failed to load readings:', err);
    }
  };

  // Auto-refresh functionality
  useEffect(() => {
    let interval: number;
    
    if (isRunning && autoRefresh) {
      interval = setInterval(loadLatestReadings, refreshInterval);
    }
    
    return () => {
      if (interval) {
        clearInterval(interval);
      }
    };
  }, [isRunning, autoRefresh, refreshInterval]);


  const handleStartSimulator = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await scadaAPI.startSimulator(config);
      if (result.success) {
        setIsRunning(true);
        // Force refresh status to ensure synchronization
        await loadStatus();
        // Load initial readings
        await loadLatestReadings();
      } else {
        setError(result.message);
        // Still refresh status to get current state
        await loadStatus();
      }
    } catch (err: any) {
      setError(err.message);
      // Refresh status even on error to get current state
      await loadStatus();
    } finally {
      setLoading(false);
    }
  };

  const handleStopSimulator = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await scadaAPI.stopSimulator();
      if (result.success) {
        setIsRunning(false);
        // Force refresh status to ensure synchronization
        await loadStatus();
      } else {
        setError(result.message);
        // Still refresh status to get current state
        await loadStatus();
      }
    } catch (err: any) {
      setError(err.message);
      // Refresh status even on error to get current state
      await loadStatus();
    } finally {
      setLoading(false);
    }
  };

  const handleConfigUpdate = async () => {
    try {
      const result = await scadaAPI.updateConfig(config);
      if (result.success && result.config) {
        // Update local config with the response from server
        setConfig({
          update_interval: result.config.update_interval,
          pressure_variation: result.config.pressure_variation,
          flow_variation: result.config.flow_variation,
          level_variation: result.config.level_variation,
        });
        setError(null);
      } else {
        setError(result.message || 'Failed to update configuration');
      }
    } catch (err: any) {
      setError(err.message);
    }
  };

  // Load initial status
  useEffect(() => {
    loadStatus();
  }, []);

  return (
    <div style={{ maxWidth: '1600px', margin: '0 auto', padding: '0 2rem' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h1 style={{ fontSize: '2.5rem', color: '#1f2937', margin: 0 }}>
          SCADA Simulator
        </h1>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <span style={{ 
            padding: '0.5rem 1rem', 
            backgroundColor: isRunning ? '#dcfce7' : '#fef2f2', 
            color: isRunning ? '#166534' : '#dc2626',
            borderRadius: '0.375rem',
            fontSize: '0.875rem',
            fontWeight: '500'
          }}>
            {isRunning ? '🟢 Running' : '🔴 Stopped'}
          </span>
          {!isNetworkLoaded && (
            <span style={{ 
              padding: '0.5rem 1rem', 
              backgroundColor: '#fef3c7', 
              color: '#d97706',
              borderRadius: '0.375rem',
              fontSize: '0.875rem',
              fontWeight: '500'
            }}>
              ⚠️ No Network Loaded
            </span>
          )}
        </div>
      </div>

      {/* Network Requirement Warning */}
      {!isNetworkLoaded && (
        <div style={{
          backgroundColor: '#fef3c7',
          border: '1px solid #f59e0b',
          borderRadius: '0.5rem',
          padding: '1rem',
          marginBottom: '2rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem'
        }}>
          <span style={{ fontSize: '1.5rem' }}>⚠️</span>
          <div>
            <h3 style={{ color: '#92400e', margin: 0, fontSize: '1rem', fontWeight: '600' }}>
              Network Required
            </h3>
            <p style={{ color: '#92400e', margin: '0.25rem 0 0 0', fontSize: '0.875rem' }}>
              Please upload a network file first before starting the SCADA simulator.
            </p>
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div style={{
          backgroundColor: '#fef2f2',
          border: '1px solid #fecaca',
          borderRadius: '0.5rem',
          padding: '1rem',
          marginBottom: '2rem'
        }}>
          <h3 style={{ color: '#dc2626', marginBottom: '0.5rem' }}>Error</h3>
          <p style={{ color: '#dc2626' }}>{error}</p>
        </div>
      )}

      {/* Two-Column Layout */}
      <div style={{ display: 'grid', gridTemplateColumns: '500px 1fr', gap: '2rem', alignItems: 'start' }}>
        
        {/* Left Column - Configuration */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          
          {/* Status Card */}
          <div style={{
            backgroundColor: 'white',
            padding: '1.5rem',
            borderRadius: '0.5rem',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
            border: '1px solid #e5e7eb'
          }}>
            <h2 style={{ color: '#1f2937', marginBottom: '1rem', fontSize: '1.25rem' }}>Simulator Status</h2>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem' }}>
              <span style={{
                display: 'inline-block',
                width: '0.75rem',
                height: '0.75rem',
                borderRadius: '9999px',
                backgroundColor: isRunning ? '#16a34a' : '#dc2626',
                marginRight: '0.5rem'
              }}></span>
              <span style={{ color: '#4b5563', fontWeight: '600' }}>
                {isRunning ? 'Running' : 'Stopped'}
              </span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <button
                onClick={handleStartSimulator}
                disabled={loading || isRunning || !isNetworkLoaded}
                style={{
                  backgroundColor: (isRunning || !isNetworkLoaded) ? '#6b7280' : '#16a34a',
                  color: 'white',
                  padding: '0.75rem 1rem',
                  border: 'none',
                  borderRadius: '0.375rem',
                  fontSize: '0.95rem',
                  cursor: (isRunning || !isNetworkLoaded) ? 'not-allowed' : 'pointer',
                  opacity: (isRunning || !isNetworkLoaded) ? 0.5 : 1,
                  width: '100%'
                }}
                title={!isNetworkLoaded ? 'Please upload a network file first' : ''}
              >
                {loading ? 'Starting...' : 'Start Simulator'}
              </button>

              <button
                onClick={handleStopSimulator}
                disabled={loading || !isRunning}
                style={{
                  backgroundColor: !isRunning ? '#6b7280' : '#dc2626',
                  color: 'white',
                  padding: '0.75rem 1rem',
                  border: 'none',
                  borderRadius: '0.375rem',
                  fontSize: '0.95rem',
                  cursor: !isRunning ? 'not-allowed' : 'pointer',
                  opacity: !isRunning ? 0.5 : 1,
                  width: '100%'
                }}
              >
                {loading ? 'Stopping...' : 'Stop Simulator'}
              </button>
            </div>
          </div>

          {/* Configuration Card */}
          <div style={{
            backgroundColor: 'white',
            padding: '1.5rem',
            borderRadius: '0.5rem',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
            border: '1px solid #e5e7eb'
          }}>
            <h2 style={{ color: '#1f2937', marginBottom: '1rem', fontSize: '1.25rem' }}>Configuration</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', color: '#374151', fontWeight: '500', marginBottom: '0.5rem', fontSize: '0.875rem' }}>
                  Update Interval (seconds)
                </label>
                <input
                  type="number"
                  value={config.update_interval}
                  onChange={(e) => setConfig({...config, update_interval: parseFloat(e.target.value)})}
                  style={{
                    width: '100%',
                    padding: '0.5rem',
                    border: '1px solid #d1d5db',
                    borderRadius: '0.375rem',
                    fontSize: '0.95rem'
                  }}
                />
              </div>
              <div>
                <label style={{ display: 'block', color: '#374151', fontWeight: '500', marginBottom: '0.5rem', fontSize: '0.875rem' }}>
                  Pressure Variation (%)
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={config.pressure_variation}
                  onChange={(e) => setConfig({...config, pressure_variation: parseFloat(e.target.value)})}
                  style={{
                    width: '100%',
                    padding: '0.5rem',
                    border: '1px solid #d1d5db',
                    borderRadius: '0.375rem',
                    fontSize: '0.95rem'
                  }}
                />
              </div>
              <div>
                <label style={{ display: 'block', color: '#374151', fontWeight: '500', marginBottom: '0.5rem', fontSize: '0.875rem' }}>
                  Flow Variation (%)
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={config.flow_variation}
                  onChange={(e) => setConfig({...config, flow_variation: parseFloat(e.target.value)})}
                  style={{
                    width: '100%',
                    padding: '0.5rem',
                    border: '1px solid #d1d5db',
                    borderRadius: '0.375rem',
                    fontSize: '0.95rem'
                  }}
                />
              </div>
              <div>
                <label style={{ display: 'block', color: '#374151', fontWeight: '500', marginBottom: '0.5rem', fontSize: '0.875rem' }}>
                  Level Variation (%)
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={config.level_variation}
                  onChange={(e) => setConfig({...config, level_variation: parseFloat(e.target.value)})}
                  style={{
                    width: '100%',
                    padding: '0.5rem',
                    border: '1px solid #d1d5db',
                    borderRadius: '0.375rem',
                    fontSize: '0.95rem'
                  }}
                />
              </div>
            </div>
            <button
              onClick={handleConfigUpdate}
              style={{
                backgroundColor: '#3b82f6',
                color: 'white',
                padding: '0.75rem 1rem',
                border: 'none',
                borderRadius: '0.375rem',
                fontSize: '0.95rem',
                cursor: 'pointer',
                marginTop: '1rem',
                width: '100%'
              }}
            >
              Update Configuration
            </button>
          </div>

          {/* Data Flow Controls */}
          {isRunning && (
            <div style={{
              backgroundColor: 'white',
              padding: '1.5rem',
              borderRadius: '0.5rem',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
              border: '1px solid #e5e7eb'
            }}>
              <h2 style={{ color: '#1f2937', marginBottom: '1rem', fontSize: '1.25rem' }}>Data Flow Controls</h2>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '1rem' }}>
                <div>
                  <label style={{ display: 'block', color: '#374151', fontWeight: '500', marginBottom: '0.5rem', fontSize: '0.875rem' }}>
                    Auto Refresh
                  </label>
                  <div style={{ display: 'flex', alignItems: 'center' }}>
                    <input
                      type="checkbox"
                      checked={autoRefresh}
                      onChange={(e) => setAutoRefresh(e.target.checked)}
                      style={{ marginRight: '0.5rem' }}
                    />
                    <span style={{ color: '#6b7280', fontSize: '0.875rem' }}>Enable continuous updates</span>
                  </div>
                </div>
                <div>
                  <label style={{ display: 'block', color: '#374151', fontWeight: '500', marginBottom: '0.5rem', fontSize: '0.875rem' }}>
                    Refresh Interval (ms)
                  </label>
                  <input
                    type="number"
                    value={refreshInterval}
                    onChange={(e) => setRefreshInterval(parseInt(e.target.value))}
                    min="1000"
                    max="30000"
                    step="1000"
                    style={{
                      width: '100%',
                      padding: '0.5rem',
                      border: '1px solid #d1d5db',
                      borderRadius: '0.375rem',
                      fontSize: '0.95rem'
                    }}
                  />
                </div>
              </div>
              <button
                onClick={loadLatestReadings}
                style={{
                  backgroundColor: '#10b981',
                  color: 'white',
                  padding: '0.75rem 1rem',
                  border: 'none',
                  borderRadius: '0.375rem',
                  fontSize: '0.875rem',
                  cursor: 'pointer',
                  width: '100%'
                }}
              >
                🔄 Manual Refresh
              </button>
              <p style={{ color: '#6b7280', fontSize: '0.75rem', marginTop: '0.5rem', textAlign: 'center' }}>
                Auto-refresh every {refreshInterval/1000}s
              </p>
            </div>
          )}
        </div>

        {/* Right Column - Live Data Table */}
        <div style={{
          backgroundColor: 'white',
          padding: '1.5rem',
          borderRadius: '0.5rem',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          border: '1px solid #e5e7eb',
          minHeight: '600px'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h2 style={{ color: '#1f2937', margin: 0, fontSize: '1.25rem' }}>Live SCADA Data</h2>
            {isRunning && latestReadings && (
              <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                <span style={{ color: '#6b7280', fontSize: '0.875rem' }}>
                  {latestReadings?.count || 0} sensors
                </span>
                {autoRefresh && (
                  <span style={{ color: '#10b981', fontSize: '0.875rem', fontWeight: '500' }}>
                    🔄 Auto-updating
                  </span>
                )}
              </div>
            )}
          </div>

          {isRunning && latestReadings ? (
            <div style={{ maxHeight: '700px', overflowY: 'auto' }}>
              {latestReadings?.readings && Object.keys(latestReadings.readings).length > 0 ? (
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ 
                    width: '100%', 
                    borderCollapse: 'collapse',
                    border: '1px solid #000'
                  }}>
                    <thead style={{ position: 'sticky', top: 0, backgroundColor: '#f0f0f0', zIndex: 1 }}>
                      <tr>
                        <th style={{ padding: '8px', textAlign: 'left', border: '1px solid #000', fontWeight: 'bold' }}>Node ID</th>
                        <th style={{ padding: '8px', textAlign: 'left', border: '1px solid #000', fontWeight: 'bold' }}>Sensor Type</th>
                        <th style={{ padding: '8px', textAlign: 'right', border: '1px solid #000', fontWeight: 'bold' }}>Value</th>
                        <th style={{ padding: '8px', textAlign: 'left', border: '1px solid #000', fontWeight: 'bold' }}>Unit</th>
                        <th style={{ padding: '8px', textAlign: 'left', border: '1px solid #000', fontWeight: 'bold' }}>Quality</th>
                        <th style={{ padding: '8px', textAlign: 'left', border: '1px solid #000', fontWeight: 'bold' }}>Timestamp</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(latestReadings.readings).map(([nodeId, sensors]) => 
                        Object.entries(sensors as { [key: string]: SCADAReading }).map(([sensorType, reading], sensorIndex) => (
                          <tr key={`${nodeId}-${sensorType}-${sensorIndex}`}>
                            <td style={{ padding: '8px', border: '1px solid #000' }}>{nodeId}</td>
                            <td style={{ padding: '8px', border: '1px solid #000' }}>{sensorType}</td>
                            <td style={{ padding: '8px', textAlign: 'right', border: '1px solid #000' }}>{reading.value.toFixed(2)}</td>
                            <td style={{ padding: '8px', border: '1px solid #000' }}>{reading.unit}</td>
                            <td style={{ padding: '8px', border: '1px solid #000' }}>{reading.quality}</td>
                            <td style={{ padding: '8px', border: '1px solid #000' }}>{new Date(reading.timestamp).toLocaleTimeString()}</td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div style={{ 
                  padding: '3rem', 
                  textAlign: 'center', 
                  color: '#6b7280',
                  backgroundColor: '#f9fafb',
                  border: '1px solid #e5e7eb',
                  borderRadius: '0.5rem'
                }}>
                  <p style={{ margin: 0, fontSize: '1.1rem' }}>No SCADA readings available</p>
                  <p style={{ margin: '0.5rem 0 0 0', fontSize: '0.9rem' }}>
                    Make sure the SCADA simulator is running and a network is loaded
                  </p>
                </div>
              )}
            </div>
          ) : (
            <div style={{ 
              padding: '3rem', 
              textAlign: 'center', 
              color: '#6b7280',
              backgroundColor: '#f9fafb',
              border: '1px solid #e5e7eb',
              borderRadius: '0.5rem',
              minHeight: '500px',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              alignItems: 'center'
            }}>
              <p style={{ margin: 0, fontSize: '1.5rem', marginBottom: '0.5rem' }}>📊</p>
              <p style={{ margin: 0, fontSize: '1.1rem', fontWeight: '500' }}>
                {isRunning ? 'Waiting for data...' : 'Start the simulator to see live data'}
              </p>
              <p style={{ margin: '0.5rem 0 0 0', fontSize: '0.9rem' }}>
                {isRunning 
                  ? 'Data will appear here once the simulator generates readings'
                  : 'Click "Start Simulator" in the left panel to begin'
                }
              </p>
            </div>
          )}
        </div>

      </div>

    </div>
  );
};

// Monitoring page with network upload functionality
const MonitoringPage = () => {
  const { networkInfo, setNetworkInfo } = useNetwork();
  const [uploadLoading, setUploadLoading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploadLoading(true);
    setUploadError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:8000/api/network/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      console.log('Network upload response:', response.data);
      setNetworkInfo(response.data);
    } catch (err: any) {
      console.error('Network upload error:', err);
      setUploadError(err.response?.data?.detail || err.message || 'Upload failed');
    } finally {
      setUploadLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '1600px', margin: '0 auto', padding: '0 2rem' }}>
      <div style={{ marginBottom: '1.5rem' }}>
        <h1 style={{ fontSize: '2.5rem', color: '#1f2937', margin: 0 }}>
          Monitoring Dashboard
        </h1>
      </div>

      {/* Two-Column Layout */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '3rem', alignItems: 'start' }}>
        
        {/* Left Column - Network Section */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          
          {/* Network Upload Section */}
          <div style={{
            backgroundColor: 'white',
            padding: '2rem',
            borderRadius: '0.5rem',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
            border: '1px solid #e5e7eb'
          }}>
            <h2 style={{ color: '#1f2937', marginBottom: '1rem' }}>Network Configuration</h2>
            <input
              type="file"
              accept=".inp"
              onChange={handleFileUpload}
              disabled={uploadLoading}
              style={{
                padding: '0.5rem',
                border: '1px solid #d1d5db',
                borderRadius: '0.375rem',
                fontSize: '1rem',
                marginBottom: '1rem',
                width: '100%'
              }}
            />
            {uploadLoading && <p style={{ color: '#6b7280' }}>Uploading and processing...</p>}
            {uploadError && (
              <div style={{ color: '#dc2626', backgroundColor: '#fef2f2', padding: '1rem', borderRadius: '0.375rem', marginTop: '1rem' }}>
                Error: {uploadError}
              </div>
            )}
          </div>

          {/* Network Information */}
          {networkInfo && (
            <div style={{
              backgroundColor: 'white',
              padding: '2rem',
              borderRadius: '0.5rem',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
              border: '1px solid #e5e7eb'
            }}>
              <h2 style={{ color: '#1f2937', marginBottom: '1rem' }}>Network Information</h2>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1rem' }}>
                <div>
                  <strong>Filename:</strong> {networkInfo.filename}
                </div>
                <div>
                  <strong>File Size:</strong> {networkInfo.file_size} bytes
                </div>
                <div>
                  <strong>Uploaded:</strong> {new Date(networkInfo.uploaded_at).toLocaleString()}
                </div>
                {networkInfo.network_info && (
                  <>
                    <div>
                      <strong>Junctions:</strong> {networkInfo.network_info.summary.total_junctions}
                    </div>
                    <div>
                      <strong>Pipes:</strong> {networkInfo.network_info.summary.total_pipes}
                    </div>
                    <div>
                      <strong>Tanks:</strong> {networkInfo.network_info.summary.total_tanks}
                    </div>
                    <div>
                      <strong>Pumps:</strong> {networkInfo.network_info.summary.total_pumps}
                    </div>
                    <div>
                      <strong>Reservoirs:</strong> {networkInfo.network_info.summary.total_reservoirs}
                    </div>
                    <div>
                      <strong>Total Nodes:</strong> {networkInfo.network_info.summary.total_nodes}
                    </div>
                    <div>
                      <strong>Total Links:</strong> {networkInfo.network_info.summary.total_links}
                    </div>
                  </>
                )}
              </div>
            </div>
          )}

          {/* Network Visualization */}
          {networkInfo && (
            <div style={{
              backgroundColor: 'white',
              padding: '2rem',
              borderRadius: '0.5rem',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
              border: '1px solid #e5e7eb'
            }}>
              <h2 style={{ color: '#1f2937', marginBottom: '1rem' }}>Network Visualization</h2>
              <NetworkViewer />
            </div>
          )}
        </div>

        {/* Right Column - Real-time Monitoring Section */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          
          {/* Real-time Monitoring */}
          <div style={{
            backgroundColor: 'white',
            padding: '2rem',
            borderRadius: '0.5rem',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
            border: '1px solid #e5e7eb',
            minHeight: '400px'
          }}>
            <h2 style={{ color: '#1f2937', marginBottom: '1rem' }}>Real-time Monitoring</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{
                padding: '1rem',
                backgroundColor: '#f8fafc',
                borderRadius: '0.375rem',
                border: '1px solid #e2e8f0'
              }}>
                <h3 style={{ color: '#1f2937', marginBottom: '0.5rem', fontSize: '1rem' }}>📊 Live Data Monitoring</h3>
                <p style={{ color: '#6b7280', fontSize: '0.875rem', margin: 0 }}>
                  Real-time SCADA data visualization with pressure, flow, and level monitoring
                </p>
              </div>
              
              <div style={{
                padding: '1rem',
                backgroundColor: '#f8fafc',
                borderRadius: '0.375rem',
                border: '1px solid #e2e8f0'
              }}>
                <h3 style={{ color: '#1f2937', marginBottom: '0.5rem', fontSize: '1rem' }}>🚨 Anomaly Detection</h3>
                <p style={{ color: '#6b7280', fontSize: '0.875rem', margin: 0 }}>
                  Automatic detection of pressure drops, flow anomalies, and system deviations
                </p>
              </div>
              
              <div style={{
                padding: '1rem',
                backgroundColor: '#f8fafc',
                borderRadius: '0.375rem',
                border: '1px solid #e2e8f0'
              }}>
                <h3 style={{ color: '#1f2937', marginBottom: '0.5rem', fontSize: '1rem' }}>📈 Trend Analysis</h3>
                <p style={{ color: '#6b7280', fontSize: '0.875rem', margin: 0 }}>
                  Historical data analysis and predictive monitoring capabilities
                </p>
              </div>
              
              <div style={{
                padding: '1rem',
                backgroundColor: '#f8fafc',
                borderRadius: '0.375rem',
                border: '1px solid #e2e8f0'
              }}>
                <h3 style={{ color: '#1f2937', marginBottom: '0.5rem', fontSize: '1rem' }}>🔔 Alert System</h3>
                <p style={{ color: '#6b7280', fontSize: '0.875rem', margin: 0 }}>
                  Automated notifications for critical system events and maintenance alerts
                </p>
              </div>
            </div>
            
            <div style={{
              marginTop: '1.5rem',
              padding: '1rem',
              backgroundColor: '#fef3c7',
              borderRadius: '0.375rem',
              border: '1px solid #f59e0b'
            }}>
              <p style={{ color: '#92400e', fontSize: '0.875rem', margin: 0, textAlign: 'center' }}>
                🚧 <strong>Coming Soon:</strong> Advanced monitoring features will be available in the next development sprint
              </p>
            </div>
          </div>

          {/* System Status */}
          <div style={{
            backgroundColor: 'white',
            padding: '2rem',
            borderRadius: '0.5rem',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
            border: '1px solid #e5e7eb'
          }}>
            <h2 style={{ color: '#1f2937', marginBottom: '1rem' }}>System Status</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ color: '#6b7280' }}>Network Status:</span>
                <span style={{ 
                  color: networkInfo ? '#16a34a' : '#dc2626',
                  fontWeight: '500'
                }}>
                  {networkInfo ? '✅ Loaded' : '❌ Not Loaded'}
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ color: '#6b7280' }}>Baseline Status:</span>
                <span style={{ color: '#6b7280', fontWeight: '500' }}>⏳ Pending</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ color: '#6b7280' }}>Monitoring Status:</span>
                <span style={{ color: '#6b7280', fontWeight: '500' }}>⏳ Pending</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Main App component
const App = () => {
  return (
    <NetworkProvider>
      <div style={{ minHeight: '100vh', backgroundColor: '#f9fafb' }}>
        <Navigation />
        
        <main style={{ maxWidth: '1600px', margin: '0 auto', padding: '2rem' }}>
          <Routes>
            <Route path="/" element={<MonitoringPage />} />
            <Route path="/monitoring" element={<MonitoringPage />} />
            <Route path="/scada" element={<SCADAPage />} />
          </Routes>
        </main>
      </div>
    </NetworkProvider>
  );
};

export default App;