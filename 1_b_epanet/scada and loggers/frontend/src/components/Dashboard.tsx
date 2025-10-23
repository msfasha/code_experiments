import React from 'react';
import { Link } from 'react-router-dom';

interface DashboardProps {
  networkStatus: { network_loaded: boolean } | null;
}

const Dashboard: React.FC<DashboardProps> = ({ networkStatus }) => {
  const features = [
    {
      title: 'Network Configuration',
      description: 'Upload and configure EPANET network files',
      icon: '🌐',
      path: '/network',
      status: networkStatus?.network_loaded ? 'Ready' : 'Not Loaded',
      statusColor: networkStatus?.network_loaded ? 'text-green-600' : 'text-gray-500'
    },
    {
      title: 'SCADA Simulator',
      description: 'Generate synthetic sensor data for testing',
      icon: '📊',
      path: '/scada',
      status: 'Coming Soon',
      statusColor: 'text-gray-500'
    },
    {
      title: 'Live Monitoring',
      description: 'Real-time hydraulic analysis and anomaly detection',
      icon: '🔍',
      path: '/monitoring',
      status: 'Coming Soon',
      statusColor: 'text-gray-500'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Water Network Monitoring System
        </h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Real-time SCADA simulation and EPANET hydraulic analysis for water distribution networks
        </p>
      </div>

      {/* Status Card */}
      <div className="card">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">System Status</h2>
            <p className="text-gray-600">
              {networkStatus?.network_loaded 
                ? 'Network loaded and ready for analysis' 
                : 'No network loaded - upload a network file to begin'
              }
            </p>
          </div>
          <div className={`px-3 py-1 rounded-full text-sm font-medium ${
            networkStatus?.network_loaded 
              ? 'bg-green-100 text-green-800' 
              : 'bg-gray-100 text-gray-800'
          }`}>
            {networkStatus?.network_loaded ? 'Ready' : 'No Network'}
          </div>
        </div>
      </div>

      {/* Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {features.map((feature, index) => (
          <Link
            key={index}
            to={feature.path}
            className="card hover:shadow-lg transition-shadow duration-200 cursor-pointer"
          >
            <div className="flex items-start space-x-4">
              <div className="text-3xl">{feature.icon}</div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600 mb-3">
                  {feature.description}
                </p>
                <div className={`text-sm font-medium ${feature.statusColor}`}>
                  {feature.status}
                </div>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="flex flex-wrap gap-4">
          <Link
            to="/network"
            className="btn-primary"
          >
            Upload Network File
          </Link>
          {networkStatus?.network_loaded && (
            <>
              <Link
                to="/scada"
                className="btn-secondary"
              >
                Start SCADA Simulation
              </Link>
              <Link
                to="/monitoring"
                className="btn-secondary"
              >
                View Live Monitoring
              </Link>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

