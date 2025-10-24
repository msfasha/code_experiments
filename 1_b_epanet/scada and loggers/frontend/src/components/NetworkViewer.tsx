import React, { useState, useEffect } from 'react';
import { networkAPI } from '../api/network';
import type { NetworkCoordinates } from '../api/network';

const NetworkViewer: React.FC = () => {
  const [coordinates, setCoordinates] = useState<NetworkCoordinates | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCoordinates = async () => {
      try {
        setLoading(true);
        const coords = await networkAPI.getNetworkCoordinates();
        setCoordinates(coords);
        setError(null);
      } catch (err: any) {
        setError(err.response?.data?.detail || err.message || 'Failed to load coordinates');
      } finally {
        setLoading(false);
      }
    };

    fetchCoordinates();
  }, []);

  if (loading) {
    return (
      <div className="card">
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mr-3"></div>
          <span className="text-gray-600">Loading network visualization...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <div className="text-center py-8">
          <div className="text-red-400 text-4xl mb-4">❌</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Error Loading Visualization</h3>
          <p className="text-red-600">{error}</p>
        </div>
      </div>
    );
  }

  if (!coordinates || Object.keys(coordinates.x).length === 0) {
    return (
      <div className="card">
        <div className="text-center py-8">
          <div className="text-gray-400 text-4xl mb-4">🗺️</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Coordinates Available</h3>
          <p className="text-gray-600">
            This network file doesn't contain coordinate information for visualization.
            The network can still be used for hydraulic analysis.
          </p>
        </div>
      </div>
    );
  }

  // Convert coordinates to array format for plotting
  const nodeData = Object.keys(coordinates.x).map(nodeId => ({
    id: nodeId,
    x: coordinates.x[nodeId],
    y: coordinates.y[nodeId]
  }));

  // Simple SVG visualization
  const minX = Math.min(...nodeData.map(n => n.x));
  const maxX = Math.max(...nodeData.map(n => n.x));
  const minY = Math.min(...nodeData.map(n => n.y));
  const maxY = Math.max(...nodeData.map(n => n.y));
  
  const width = 600;
  const height = 400;
  const padding = 40;
  
  const scaleX = (width - 2 * padding) / (maxX - minX);
  const scaleY = (height - 2 * padding) / (maxY - minY);
  
  const scale = Math.min(scaleX, scaleY);
  
  const transformX = (x: number) => padding + (x - minX) * scale;
  const transformY = (y: number) => height - padding - (y - minY) * scale;

  return (
    <div className="card">
      <h2 className="text-xl font-semibold text-gray-900 mb-6">Network Visualization</h2>
      
      <div className="bg-gray-50 rounded-lg p-4">
        <div className="text-center mb-4">
          <p className="text-sm text-gray-600">
            Network topology with {nodeData.length} nodes
          </p>
        </div>
        
        <div className="flex justify-center">
          <svg
            width={width}
            height={height}
            className="border border-gray-300 rounded-lg bg-white"
            viewBox={`0 0 ${width} ${height}`}
          >
            {/* Grid lines */}
            <defs>
              <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#f3f4f6" strokeWidth="1"/>
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid)" />
            
            {/* Node connections (simplified - just show all possible connections) */}
            {nodeData.map((node, i) => 
              nodeData.slice(i + 1).map((otherNode, _j) => (
                <line
                  key={`${node.id}-${otherNode.id}`}
                  x1={transformX(node.x)}
                  y1={transformY(node.y)}
                  x2={transformX(otherNode.x)}
                  y2={transformY(otherNode.y)}
                  stroke="#d1d5db"
                  strokeWidth="1"
                  opacity="0.3"
                />
              ))
            )}
            
            {/* Nodes */}
            {nodeData.map((node) => (
              <g key={node.id}>
                <circle
                  cx={transformX(node.x)}
                  cy={transformY(node.y)}
                  r="8"
                  fill="#3b82f6"
                  stroke="#1d4ed8"
                  strokeWidth="2"
                />
                <text
                  x={transformX(node.x)}
                  y={transformY(node.y) + 4}
                  textAnchor="middle"
                  className="text-xs font-medium fill-white"
                >
                  {node.id}
                </text>
              </g>
            ))}
          </svg>
        </div>
        
        <div className="mt-4 text-center">
          <p className="text-xs text-gray-500">
            Simple network topology view. Full interactive visualization coming in Sprint 5.
          </p>
        </div>
      </div>
    </div>
  );
};

export default NetworkViewer;

