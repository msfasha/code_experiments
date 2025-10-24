import React, { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import axios from 'axios';

// Types
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

interface NetworkContextType {
  networkInfo: NetworkInfo | null;
  isNetworkLoaded: boolean;
  loading: boolean;
  error: string | null;
  refreshNetworkInfo: () => Promise<void>;
  setNetworkInfo: (info: NetworkInfo | null) => void;
  clearNetwork: () => void;
}

// Create context
const NetworkContext = createContext<NetworkContextType | undefined>(undefined);

// Provider component
export const NetworkProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [networkInfo, setNetworkInfo] = useState<NetworkInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isNetworkLoaded = networkInfo !== null && (networkInfo.success || networkInfo.network_info);

  // Fetch network info from backend
  const refreshNetworkInfo = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get('http://localhost:8000/api/network/info');
      if (response.data.success) {
        setNetworkInfo(response.data);
      } else {
        setNetworkInfo(null);
      }
    } catch (err: any) {
      console.log('No network loaded:', err.message);
      setNetworkInfo(null);
      setError(null); // Don't set error for this - it's normal if no network is loaded
    } finally {
      setLoading(false);
    }
  };

  // Clear network
  const clearNetwork = () => {
    setNetworkInfo(null);
    setError(null);
  };

  // Load network info on mount
  useEffect(() => {
    refreshNetworkInfo();
  }, []);

  const value: NetworkContextType = {
    networkInfo,
    isNetworkLoaded,
    loading,
    error,
    refreshNetworkInfo,
    setNetworkInfo,
    clearNetwork
  };

  return (
    <NetworkContext.Provider value={value}>
      {children}
    </NetworkContext.Provider>
  );
};

// Hook to use network context
export const useNetwork = (): NetworkContextType => {
  const context = useContext(NetworkContext);
  if (context === undefined) {
    throw new Error('useNetwork must be used within a NetworkProvider');
  }
  return context;
};
