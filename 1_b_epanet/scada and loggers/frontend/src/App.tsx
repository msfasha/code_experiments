import { useState, useEffect } from 'react';
import { Routes, Route, Link, useLocation } from 'react-router-dom';
import axios from 'axios';
import { scadaAPI } from './api/scada';

// Type definitions
interface SystemStatus {
  api: string;
  status: string;
  version: string;
  timestamp: string;
}

interface NetworkInfo {
  message: string;
  filename: string;
  file_size: number;
  uploaded_at: string;
  success: boolean;
  network_info?: {
    summary: {
      total_junctions: number;
      total_pipes: number;
      total_pumps: number;
      total_tanks: number;
      total_reservoirs: number;
      total_nodes: number;
      total_links: number;
    };
    junctions?: {
      ids: string[];
      count: number;
    };
    pipes?: {
      ids: string[];
      count: number;
    };
    pumps?: {
      ids: string[];
      count: number;
    };
    tanks?: {
      ids: string[];
      count: number;
    };
  };
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
  
  const navItems = [
    { path: '/', label: 'Dashboard', icon: '🏠' },
    { path: '/network', label: 'Network', icon: '🌐' },
    { path: '/scada', label: 'SCADA', icon: '📊' },
    { path: '/monitoring', label: 'Monitoring', icon: '🔍' }
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

// Dashboard page
const DashboardPage = () => {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/status');
        setStatus(response.data);
      } catch (error) {
        console.error('Failed to fetch status:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchStatus();
  }, []);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '2rem' }}>
        <p>Loading system status...</p>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 1rem' }}>
      <h1 style={{ fontSize: '2rem', marginBottom: '1rem', color: '#1f2937' }}>
        System Dashboard
      </h1>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
        <div style={{
          backgroundColor: 'white',
          padding: '2rem',
          borderRadius: '0.5rem',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          border: '1px solid #e5e7eb'
        }}>
          <h2 style={{ color: '#1f2937', marginBottom: '1rem' }}>System Status</h2>
          <p style={{ color: '#6b7280' }}>API: {status?.api || 'Unknown'}</p>
          <p style={{ color: '#6b7280' }}>Status: {status?.status || 'Unknown'}</p>
          <p style={{ color: '#6b7280' }}>Version: {status?.version || 'Unknown'}</p>
        </div>

        <div style={{
          backgroundColor: 'white',
          padding: '2rem',
          borderRadius: '0.5rem',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          border: '1px solid #e5e7eb'
        }}>
          <h2 style={{ color: '#1f2937', marginBottom: '1rem' }}>Quick Actions</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <Link to="/network" style={{ color: '#3b82f6', textDecoration: 'none' }}>
              📁 Upload Network File
            </Link>
            <Link to="/scada" style={{ color: '#3b82f6', textDecoration: 'none' }}>
              📊 Start SCADA Simulator
            </Link>
            <Link to="/monitoring" style={{ color: '#3b82f6', textDecoration: 'none' }}>
              🔍 View Monitoring
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

// Network page
const NetworkPage = () => {
  const [networkInfo, setNetworkInfo] = useState<NetworkInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch network info when component loads
  useEffect(() => {
    const fetchNetworkInfo = async () => {
      try {
        setLoading(true);
        const response = await axios.get('http://localhost:8000/api/network/info');
        if (response.data.success) {
          setNetworkInfo(response.data);
        }
      } catch (err: any) {
        console.log('No network loaded yet:', err.message);
        // Don't set error for this - it's normal if no network is loaded
      } finally {
        setLoading(false);
      }
    };

    fetchNetworkInfo();
  }, []);

  const refreshNetworkInfo = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get('http://localhost:8000/api/network/info');
      if (response.data.success) {
        setNetworkInfo(response.data);
      }
    } catch (err: any) {
      setError('Failed to load network information');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setLoading(true);
    setError(null);

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
      setError(err.response?.data?.detail || err.message || 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 1rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h1 style={{ fontSize: '2rem', color: '#1f2937', margin: 0 }}>
          Network Configuration
        </h1>
        <button
          onClick={refreshNetworkInfo}
          disabled={loading}
          style={{
            backgroundColor: '#3b82f6',
            color: 'white',
            padding: '0.5rem 1rem',
            border: 'none',
            borderRadius: '0.375rem',
            fontSize: '0.875rem',
            cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.5 : 1
          }}
        >
          {loading ? 'Loading...' : '🔄 Refresh'}
        </button>
      </div>

      <div style={{
        backgroundColor: 'white',
        padding: '2rem',
        borderRadius: '0.5rem',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        border: '1px solid #e5e7eb',
        marginBottom: '2rem'
      }}>
        <h2 style={{ color: '#1f2937', marginBottom: '1rem' }}>Upload Network File</h2>
        <input
          type="file"
          accept=".inp"
          onChange={handleFileUpload}
          disabled={loading}
          style={{
            padding: '0.5rem',
            border: '1px solid #d1d5db',
            borderRadius: '0.375rem',
            fontSize: '1rem',
            marginBottom: '1rem'
          }}
        />
        {loading && <p style={{ color: '#6b7280' }}>Uploading and processing...</p>}
        {error && (
          <div style={{ color: '#dc2626', backgroundColor: '#fef2f2', padding: '1rem', borderRadius: '0.375rem', marginTop: '1rem' }}>
            Error: {error}
          </div>
        )}
      </div>

      {networkInfo && (
        <div style={{
          backgroundColor: 'white',
          padding: '2rem',
          borderRadius: '0.5rem',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          border: '1px solid #e5e7eb'
        }}>
          <h2 style={{ color: '#1f2937', marginBottom: '1rem' }}>Network Information</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
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
    </div>
  );
};

// SCADA page with full functionality
const SCADAPage = () => {
  const [isRunning, setIsRunning] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [latestReadings, setLatestReadings] = useState<SCADAData | null>(null);
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

  const handleStartSimulator = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await scadaAPI.startSimulator(config);
      if (result.success) {
        setIsRunning(true);
        // Force refresh status to ensure synchronization
        await loadStatus();
        // Start polling for readings
        setInterval(loadLatestReadings, 5000);
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
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 1rem' }}>
      <h1 style={{ fontSize: '2rem', marginBottom: '1rem', color: '#1f2937' }}>
        SCADA Simulator
      </h1>

      {/* Status Card */}
      <div style={{
        backgroundColor: 'white',
        padding: '2rem',
        borderRadius: '0.5rem',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        border: '1px solid #e5e7eb',
        marginBottom: '2rem'
      }}>
        <h2 style={{ color: '#1f2937', marginBottom: '1rem' }}>Simulator Status</h2>
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

        <div style={{ display: 'flex', gap: '1rem' }}>
          <button
            onClick={handleStartSimulator}
            disabled={loading || isRunning}
            style={{
              backgroundColor: isRunning ? '#6b7280' : '#16a34a',
              color: 'white',
              padding: '0.75rem 1.5rem',
              border: 'none',
              borderRadius: '0.375rem',
              fontSize: '1rem',
              cursor: isRunning ? 'not-allowed' : 'pointer',
              opacity: isRunning ? 0.5 : 1
            }}
          >
            {loading ? 'Starting...' : 'Start Simulator'}
          </button>

          <button
            onClick={handleStopSimulator}
            disabled={loading || !isRunning}
            style={{
              backgroundColor: !isRunning ? '#6b7280' : '#dc2626',
              color: 'white',
              padding: '0.75rem 1.5rem',
              border: 'none',
              borderRadius: '0.375rem',
              fontSize: '1rem',
              cursor: !isRunning ? 'not-allowed' : 'pointer',
              opacity: !isRunning ? 0.5 : 1
            }}
          >
            {loading ? 'Stopping...' : 'Stop Simulator'}
          </button>
        </div>
      </div>

      {/* Configuration Card */}
      <div style={{
        backgroundColor: 'white',
        padding: '2rem',
        borderRadius: '0.5rem',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        border: '1px solid #e5e7eb',
        marginBottom: '2rem'
      }}>
        <h2 style={{ color: '#1f2937', marginBottom: '1rem' }}>Configuration</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
          <div>
            <label style={{ display: 'block', color: '#374151', fontWeight: '500', marginBottom: '0.5rem' }}>
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
                fontSize: '1rem'
              }}
            />
          </div>
          <div>
            <label style={{ display: 'block', color: '#374151', fontWeight: '500', marginBottom: '0.5rem' }}>
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
                fontSize: '1rem'
              }}
            />
          </div>
          <div>
            <label style={{ display: 'block', color: '#374151', fontWeight: '500', marginBottom: '0.5rem' }}>
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
                fontSize: '1rem'
              }}
            />
          </div>
          <div>
            <label style={{ display: 'block', color: '#374151', fontWeight: '500', marginBottom: '0.5rem' }}>
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
                fontSize: '1rem'
              }}
            />
          </div>
        </div>
        <button
          onClick={handleConfigUpdate}
          style={{
            backgroundColor: '#3b82f6',
            color: 'white',
            padding: '0.75rem 1.5rem',
            border: 'none',
            borderRadius: '0.375rem',
            fontSize: '1rem',
            cursor: 'pointer',
            marginTop: '1rem'
          }}
        >
          Update Configuration
        </button>
      </div>

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

      {/* Live Data Display */}
      {isRunning && latestReadings && (
        <div style={{
          backgroundColor: 'white',
          padding: '2rem',
          borderRadius: '0.5rem',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          border: '1px solid #e5e7eb'
        }}>
          <h2 style={{ color: '#1f2937', marginBottom: '1rem' }}>Live SCADA Data</h2>
          <p style={{ color: '#6b7280', marginBottom: '1rem' }}>
            Latest readings from {latestReadings?.count || 0} sensors
          </p>

          <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
            {latestReadings?.readings && Object.entries(latestReadings.readings).map(([nodeId, sensors]) => (
              <div key={nodeId} style={{
                border: '1px solid #e5e7eb',
                borderRadius: '0.375rem',
                padding: '1rem',
                marginBottom: '0.5rem',
                backgroundColor: '#f9fafb'
              }}>
                <h4 style={{ color: '#1f2937', marginBottom: '0.5rem' }}>Node: {nodeId}</h4>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '0.5rem' }}>
                  {Object.entries(sensors as { [key: string]: SCADAReading }).map(([sensorType, reading]) => (
                    <div key={sensorType} style={{
                      backgroundColor: 'white',
                      padding: '0.5rem',
                      borderRadius: '0.25rem',
                      border: '1px solid #e5e7eb'
                    }}>
                      <div style={{ fontSize: '0.875rem', color: '#6b7280', textTransform: 'capitalize' }}>
                        {sensorType}
                      </div>
                      <div style={{ fontSize: '1.25rem', fontWeight: '600', color: '#1f2937' }}>
                        {reading.value.toFixed(2)} {reading.unit}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>
                        {new Date(reading.timestamp).toLocaleTimeString()}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// Monitoring page
const MonitoringPage = () => {
  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 1rem' }}>
      <h1 style={{ fontSize: '2rem', marginBottom: '1rem', color: '#1f2937' }}>
        Monitoring Dashboard
      </h1>
      
      <div style={{
        backgroundColor: 'white',
        padding: '2rem',
        borderRadius: '0.5rem',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        border: '1px solid #e5e7eb'
      }}>
        <h2 style={{ color: '#1f2937', marginBottom: '1rem' }}>Real-time Monitoring</h2>
        <p style={{ color: '#6b7280' }}>
          This page will show real-time monitoring data, anomaly detection, and comparison charts.
          Coming soon in the next sprint!
        </p>
      </div>
    </div>
  );
};

// Main App component
const App = () => {
  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f9fafb' }}>
      <Navigation />
      
      <main style={{ maxWidth: '1200px', margin: '0 auto', padding: '1.5rem 1rem' }}>
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/network" element={<NetworkPage />} />
          <Route path="/scada" element={<SCADAPage />} />
          <Route path="/monitoring" element={<MonitoringPage />} />
        </Routes>
      </main>
    </div>
  );
};

export default App;