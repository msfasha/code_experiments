import apiClient from './client';

// Define types for SCADA data
export interface SCADAConfig {
  update_interval?: number;
  pressure_variation?: number;
  flow_variation?: number;
  level_variation?: number;
  fault_injection?: boolean;
}

export interface SCADAStatus {
  is_running: boolean;
  config: {
    update_interval: number;
    pressure_variation: number;
    flow_variation: number;
    level_variation: number;
    fault_injection: boolean;
  };
  success: boolean;
}

export interface SCADAReading {
  value: number;
  unit: string;
  timestamp: string;
  quality: string;
}

export interface SCADAData {
  readings: { [nodeId: string]: { [sensorType: string]: SCADAReading } };
  count: number;
  success: boolean;
}

export const scadaAPI = {
  startSimulator: async (config?: SCADAConfig): Promise<any> => {
    const response = await apiClient.post('/scada/start', {
      config: config || {}
    });
    return response.data;
  },

  stopSimulator: async (): Promise<any> => {
    const response = await apiClient.post('/scada/stop');
    return response.data;
  },

  getStatus: async (): Promise<SCADAStatus> => {
    const response = await apiClient.get<SCADAStatus>('/scada/status');
    return response.data;
  },

  getLatestReadings: async (limit: number = 100): Promise<SCADAData> => {
    const response = await apiClient.get<SCADAData>(`/scada/latest?limit=${limit}`);
    return response.data;
  },

  updateConfig: async (config: SCADAConfig): Promise<any> => {
    const response = await apiClient.post('/scada/config', config);
    return response.data;
  },

  injectFault: async (nodeId: string, faultType: string = 'pressure_drop', severity: number = 0.5): Promise<any> => {
    const response = await apiClient.post(`/scada/inject-fault?node_id=${nodeId}&fault_type=${faultType}&severity=${severity}`);
    return response.data;
  },
};

