import React, { useState, useEffect } from 'react';
import { networkAPI } from '../api/network';
import { useNetwork } from '../contexts/NetworkContext';
import type { NetworkCoordinates } from '../api/network';

const NetworkViewer: React.FC = () => {
  const { networkInfo, isNetworkLoaded } = useNetwork();
  const [coordinates, setCoordinates] = useState<NetworkCoordinates | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCoordinates = async () => {
      console.log('NetworkViewer: isNetworkLoaded =', isNetworkLoaded);
      console.log('NetworkViewer: networkInfo =', networkInfo);
      
      if (!isNetworkLoaded) {
        console.log('NetworkViewer: No network loaded, clearing coordinates');
        setCoordinates(null);
        setLoading(false);
        return;
      }

      try {
        console.log('NetworkViewer: Fetching network coordinates...');
        setLoading(true);
        setError(null);
        const response = await networkAPI.getNetworkPlot();
        console.log('NetworkViewer: Coordinates response received');
        setCoordinates(response.coordinates);
      } catch (err: any) {
        console.error('NetworkViewer: Error fetching coordinates:', err);
        setError(err.response?.data?.detail || err.message || 'Failed to load network coordinates');
        setCoordinates(null);
      } finally {
        setLoading(false);
      }
    };

    fetchCoordinates();
  }, [isNetworkLoaded, networkInfo?.filename]); // Re-fetch when network changes

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

  if (!isNetworkLoaded) {
    return (
      <div className="card">
        <div className="text-center py-8">
          <div className="text-gray-400 text-4xl mb-4">📁</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Network Loaded</h3>
          <p className="text-gray-600">
            Please upload a network file to see the visualization.
          </p>
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

  // Enhanced SVG visualization with better scaling
  const minX = Math.min(...nodeData.map(n => n.x));
  const maxX = Math.max(...nodeData.map(n => n.x));
  const minY = Math.min(...nodeData.map(n => n.y));
  const maxY = Math.max(...nodeData.map(n => n.y));
  
  const width = 800;
  const height = 600;
  const padding = 60;
  
  // Calculate the aspect ratio of the data
  const dataWidth = maxX - minX;
  const dataHeight = maxY - minY;
  const dataAspectRatio = dataWidth / dataHeight;
  const canvasAspectRatio = (width - 2 * padding) / (height - 2 * padding);
  
  let scale;
  
  if (dataAspectRatio > canvasAspectRatio) {
    // Data is wider than canvas - scale based on width
    scale = (width - 2 * padding) / dataWidth;
  } else {
    // Data is taller than canvas - scale based on height
    scale = (height - 2 * padding) / dataHeight;
  }
  
  // Center the network in the canvas
  const scaledDataWidth = dataWidth * scale;
  const scaledDataHeight = dataHeight * scale;
  const offsetX = (width - scaledDataWidth) / 2;
  const offsetY = (height - scaledDataHeight) / 2;
  
  const transformX = (x: number) => offsetX + (x - minX) * scale;
  const transformY = (y: number) => offsetY + (y - minY) * scale;

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
              <pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse">
                <path d="M 30 0 L 0 0 0 30" fill="none" stroke="#f3f4f6" strokeWidth="1"/>
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid)" />
            
            {/* Node connections - show connections between nearby nodes */}
            {nodeData.map((node, i) => 
              nodeData.slice(i + 1).map((otherNode, _j) => {
                const distance = Math.sqrt(
                  Math.pow(node.x - otherNode.x, 2) + Math.pow(node.y - otherNode.y, 2)
                );
                const maxDistance = Math.max(dataWidth, dataHeight) * 0.3; // Only connect nearby nodes
                
                if (distance <= maxDistance) {
                  return (
                    <line
                      key={`${node.id}-${otherNode.id}`}
                      x1={transformX(node.x)}
                      y1={transformY(node.y)}
                      x2={transformX(otherNode.x)}
                      y2={transformY(otherNode.y)}
                      stroke="#4b5563"
                      strokeWidth="4"
                      opacity="0.9"
                    />
                  );
                }
                return null;
              }).filter(Boolean)
            ).flat()}
            
            {/* Nodes */}
            {nodeData.map((node) => (
              <g key={node.id}>
                <circle
                  cx={transformX(node.x)}
                  cy={transformY(node.y)}
                  r="12"
                  fill="#3b82f6"
                  stroke="#1d4ed8"
                  strokeWidth="3"
                />
                <text
                  x={transformX(node.x)}
                  y={transformY(node.y) + 5}
                  textAnchor="middle"
                  className="text-sm font-semibold fill-white"
                >
                  {node.id}
                </text>
              </g>
            ))}
          </svg>
        </div>
        
        <div className="mt-4 text-center">
          <p className="text-xs text-gray-500">
            Network visualization using EPANET coordinates
          </p>
        </div>
      </div>
    </div>
  );
};

export default NetworkViewer;

