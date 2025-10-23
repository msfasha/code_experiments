import apiClient from './client';

// Types for network data
export interface NetworkInfo {
  summary: {
    total_junctions: number;
    total_pipes: number;
    total_pumps: number;
    total_tanks: number;
    total_reservoirs: number;
    total_nodes: number;
    total_links: number;
  };
  network_properties: {
    has_coordinates: boolean;
    total_demand: number;
    avg_pipe_length: number;
    avg_pipe_diameter: number;
  };
}

export interface NetworkCoordinates {
  x: Record<string, number>;
  y: Record<string, number>;
  x_vert: Record<string, number[]>;
  y_vert: Record<string, number[]>;
}

export interface UploadResponse {
  message: string;
  filename: string;
  file_size: number;
  uploaded_at: string;
  success: boolean;
  network_info: NetworkInfo;
}

// Network API functions
export const networkAPI = {
  // Upload network file
  uploadNetwork: async (file: File): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await apiClient.post('/network/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },

  // Get network information
  getNetworkInfo: async (): Promise<NetworkInfo> => {
    const response = await apiClient.get('/network/info');
    return response.data;
  },

  // Get network coordinates
  getNetworkCoordinates: async (): Promise<NetworkCoordinates> => {
    const response = await apiClient.get('/network/coordinates');
    return response.data.coordinates;
  },

  // Get network status
  getNetworkStatus: async (): Promise<{ network_loaded: boolean }> => {
    const response = await apiClient.get('/network/status');
    return response.data;
  },

  // Clear network
  clearNetwork: async (): Promise<void> => {
    await apiClient.delete('/network/clear');
  },

  // Test network API
  testNetworkAPI: async (): Promise<any> => {
    const response = await apiClient.get('/network/test');
    return response.data;
  }
};

