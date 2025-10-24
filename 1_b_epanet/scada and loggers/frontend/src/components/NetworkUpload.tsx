import React, { useState, useRef } from 'react';
import { networkAPI } from '../api/network';
import type { UploadResponse } from '../api/network';

interface NetworkUploadProps {
  onUpload: () => void;
}

const NetworkUpload: React.FC<NetworkUploadProps> = ({ onUpload }) => {
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<UploadResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      handleUpload(file);
    }
  };

  const handleUpload = async (file: File) => {
    setUploading(true);
    setError(null);
    setUploadResult(null);

    try {
      // Validate file type
      if (!file.name.toLowerCase().endsWith('.inp')) {
        throw new Error('Please select a valid EPANET .inp file');
      }

      // Validate file size (10MB limit)
      if (file.size > 10 * 1024 * 1024) {
        throw new Error('File size must be less than 10MB');
      }

      const result = await networkAPI.uploadNetwork(file);
      setUploadResult(result);
      onUpload(); // Notify parent component
      
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    if (file) {
      handleUpload(file);
    }
  };

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
  };

  const clearUpload = () => {
    setUploadResult(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="card">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Upload Network File</h2>
      
      {/* Upload Area */}
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors duration-200 ${
          uploading
            ? 'border-primary-300 bg-primary-50'
            : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
        }`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
      >
        {uploading ? (
          <div className="space-y-4">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
            <p className="text-primary-600 font-medium">Uploading and parsing network file...</p>
            <p className="text-sm text-gray-500">This may take a few seconds</p>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="text-4xl">📁</div>
            <div>
              <p className="text-lg font-medium text-gray-900">
                Drop your EPANET .inp file here
              </p>
              <p className="text-gray-500">or</p>
              <button
                onClick={() => fileInputRef.current?.click()}
                className="btn-primary"
              >
                Browse Files
              </button>
            </div>
            <p className="text-sm text-gray-400">
              Supports .inp files up to 10MB
            </p>
          </div>
        )}
        
        <input
          ref={fileInputRef}
          type="file"
          accept=".inp"
          onChange={handleFileSelect}
          className="hidden"
        />
      </div>

      {/* Error Display */}
      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex">
            <div className="text-red-400 mr-3">❌</div>
            <div>
              <h3 className="text-sm font-medium text-red-800">Upload Failed</h3>
              <p className="text-sm text-red-700 mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Success Display */}
      {uploadResult && (
        <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex">
            <div className="text-green-400 mr-3">✅</div>
            <div className="flex-1">
              <h3 className="text-sm font-medium text-green-800">Network Loaded Successfully</h3>
              <div className="mt-2 text-sm text-green-700">
                <p><strong>File:</strong> {uploadResult.filename}</p>
                <p><strong>Size:</strong> {(uploadResult.file_size / 1024).toFixed(1)} KB</p>
                <p><strong>Uploaded:</strong> {new Date(uploadResult.uploaded_at).toLocaleString()}</p>
              </div>
              <div className="mt-3 flex space-x-2">
                <button
                  onClick={clearUpload}
                  className="btn-secondary text-sm"
                >
                  Upload Another
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default NetworkUpload;

