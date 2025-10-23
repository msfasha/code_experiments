import React, { useState, useEffect } from 'react';
import { networkAPI, NetworkInfo as NetworkInfoType } from '../api/network';

const NetworkInfo: React.FC = () => {
  const [networkInfo, setNetworkInfo] = useState<NetworkInfoType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchNetworkInfo = async () => {
      try {
        setLoading(true);
        const info = await networkAPI.getNetworkInfo();
        setNetworkInfo(info);
        setError(null);
      } catch (err: any) {
        setError(err.response?.data?.detail || err.message || 'Failed to load network info');
      } finally {
        setLoading(false);
      }
    };

    fetchNetworkInfo();
  }, []);

  if (loading) {
    return (
      <div className="card">
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mr-3"></div>
          <span className="text-gray-600">Loading network information...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <div className="text-center py-8">
          <div className="text-red-400 text-4xl mb-4">❌</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Error Loading Network</h3>
          <p className="text-red-600">{error}</p>
        </div>
      </div>
    );
  }

  if (!networkInfo) {
    return (
      <div className="card">
        <div className="text-center py-8">
          <div className="text-gray-400 text-4xl mb-4">📊</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Network Information</h3>
          <p className="text-gray-600">Upload a network file to see information here</p>
        </div>
      </div>
    );
  }

  const { summary, network_properties } = networkInfo;

  return (
    <div className="card">
      <h2 className="text-xl font-semibold text-gray-900 mb-6">Network Information</h2>
      
      {/* Summary Statistics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-blue-600">{summary.total_junctions}</div>
          <div className="text-sm text-blue-800">Junctions</div>
        </div>
        <div className="bg-green-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-green-600">{summary.total_pipes}</div>
          <div className="text-sm text-green-800">Pipes</div>
        </div>
        <div className="bg-yellow-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-yellow-600">{summary.total_pumps}</div>
          <div className="text-sm text-yellow-800">Pumps</div>
        </div>
        <div className="bg-purple-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-purple-600">{summary.total_tanks}</div>
          <div className="text-sm text-purple-800">Tanks</div>
        </div>
      </div>

      {/* Network Properties */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-3">Network Properties</h3>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600">Coordinates Available:</span>
              <span className={`font-medium ${network_properties.has_coordinates ? 'text-green-600' : 'text-red-600'}`}>
                {network_properties.has_coordinates ? 'Yes' : 'No'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Total Demand:</span>
              <span className="font-medium">{network_properties.total_demand.toFixed(2)} L/s</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Avg Pipe Length:</span>
              <span className="font-medium">{network_properties.avg_pipe_length.toFixed(1)} m</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Avg Pipe Diameter:</span>
              <span className="font-medium">{network_properties.avg_pipe_diameter.toFixed(1)} mm</span>
            </div>
          </div>
        </div>

        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-3">Component Summary</h3>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600">Total Nodes:</span>
              <span className="font-medium">{summary.total_nodes}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Total Links:</span>
              <span className="font-medium">{summary.total_links}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Reservoirs:</span>
              <span className="font-medium">{summary.total_reservoirs}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Status Indicator */}
      <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
        <div className="flex items-center">
          <div className="text-green-400 mr-3">✅</div>
          <div>
            <h4 className="text-sm font-medium text-green-800">Network Ready</h4>
            <p className="text-sm text-green-700">
              Network has been successfully loaded and is ready for SCADA simulation and monitoring.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NetworkInfo;
