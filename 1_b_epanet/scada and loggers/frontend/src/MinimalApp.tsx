import React from 'react';

const MinimalApp: React.FC = () => {
  return (
    <div style={{ padding: '20px', backgroundColor: '#f0f9ff' }}>
      <h1 style={{ color: '#1e40af', fontSize: '2rem', marginBottom: '20px' }}>
        💧 Water Network Monitoring System
      </h1>
      
      <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
        <h2 style={{ color: '#374151', marginBottom: '16px' }}>System Status</h2>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '20px' }}>
          <div style={{ padding: '16px', backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '6px' }}>
            <h3 style={{ color: '#166534', margin: '0 0 8px 0' }}>🌐 Network</h3>
            <p style={{ color: '#166534', margin: '0' }}>Ready to upload</p>
          </div>
          
          <div style={{ padding: '16px', backgroundColor: '#fef3c7', border: '1px solid #fde68a', borderRadius: '6px' }}>
            <h3 style={{ color: '#92400e', margin: '0 0 8px 0' }}>📊 SCADA</h3>
            <p style={{ color: '#92400e', margin: '0' }}>Coming soon</p>
          </div>
          
          <div style={{ padding: '16px', backgroundColor: '#fef3c7', border: '1px solid #fde68a', borderRadius: '6px' }}>
            <h3 style={{ color: '#92400e', margin: '0 0 8px 0' }}>🔍 Monitoring</h3>
            <p style={{ color: '#92400e', margin: '0' }}>Coming soon</p>
          </div>
        </div>
        
        <div style={{ textAlign: 'center' }}>
          <button style={{ 
            backgroundColor: '#3b82f6', 
            color: 'white', 
            padding: '12px 24px', 
            border: 'none', 
            borderRadius: '6px', 
            fontSize: '16px',
            cursor: 'pointer'
          }}>
            Upload Network File
          </button>
        </div>
      </div>
    </div>
  );
};

export default MinimalApp;

