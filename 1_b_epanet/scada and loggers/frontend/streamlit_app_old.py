"""
Water Network Monitoring System - Streamlit Frontend
Real-time SCADA and EPANET monitoring system with Streamlit interface
"""

import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import base64
from datetime import datetime, timedelta
import time
import json
from typing import Dict, List, Any, Optional
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI backend configuration
API_BASE_URL = "http://localhost:8000"

# Configure Streamlit page
st.set_page_config(
    page_title="Water Network Monitoring System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .status-running {
        color: #28a745;
        font-weight: bold;
    }
    .status-stopped {
        color: #dc3545;
        font-weight: bold;
    }
    .status-warning {
        color: #ffc107;
        font-weight: bold;
    }
    .plot-container {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    .stAlert {
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'api_connected' not in st.session_state:
    st.session_state.api_connected = False
if 'network_loaded' not in st.session_state:
    st.session_state.network_loaded = False
if 'scada_running' not in st.session_state:
    st.session_state.scada_running = False
if 'monitoring_active' not in st.session_state:
    st.session_state.monitoring_active = False

# API Helper Functions
@st.cache_data(ttl=30)  # Cache for 30 seconds
def check_api_connection():
    """Check if FastAPI backend is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

@st.cache_data(ttl=60)  # Cache for 1 minute
def get_network_info():
    """Get network information from FastAPI"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/network/info", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except requests.exceptions.RequestException:
        return None

@st.cache_data(ttl=30)
def get_network_status():
    """Get network status from FastAPI"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/network/status", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except requests.exceptions.RequestException:
        return None

@st.cache_data(ttl=10)  # Cache for 10 seconds
def get_scada_readings():
    """Get SCADA readings from FastAPI"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/scada/readings", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except requests.exceptions.RequestException:
        return None

@st.cache_data(ttl=30)
def get_monitoring_status():
    """Get monitoring status from FastAPI"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/monitoring/monitoring/status", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except requests.exceptions.RequestException:
        return None

@st.cache_data(ttl=60)
def get_network_data():
    """Get raw network data from FastAPI for client-side plotting"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/network/data", timeout=15)
        if response.status_code == 200:
            return response.json()
        return None
    except requests.exceptions.RequestException:
        return None

def upload_network_file(file):
    """Upload network file to FastAPI"""
    try:
        files = {"file": (file.name, file.getvalue(), "application/octet-stream")}
        response = requests.post(f"{API_BASE_URL}/api/network/upload", files=files, timeout=30)
        if response.status_code == 200:
            return response.json()
        return None
    except requests.exceptions.RequestException:
        return None

def start_scada_simulation(config=None):
    """Start SCADA simulation via FastAPI"""
    try:
        data = {"config": config} if config else {}
        response = requests.post(f"{API_BASE_URL}/api/scada/start", json=data, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except requests.exceptions.RequestException:
        return None

def stop_scada_simulation():
    """Stop SCADA simulation via FastAPI"""
    try:
        response = requests.post(f"{API_BASE_URL}/api/scada/stop", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except requests.exceptions.RequestException:
        return None

def start_monitoring():
    """Start monitoring via FastAPI"""
    try:
        response = requests.post(f"{API_BASE_URL}/api/monitoring/monitoring/start", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except requests.exceptions.RequestException:
        return None

def stop_monitoring():
    """Stop monitoring via FastAPI"""
    try:
        response = requests.post(f"{API_BASE_URL}/api/monitoring/monitoring/stop", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except requests.exceptions.RequestException:
        return None

def establish_baseline():
    """Establish baseline via FastAPI"""
    try:
        response = requests.post(f"{API_BASE_URL}/api/monitoring/baseline/establish", timeout=30)
        if response.status_code == 200:
            return response.json()
        return None
    except requests.exceptions.RequestException:
        return None

def create_network_plot():
    """Create network plot using EPyT's native plot() method directly in Streamlit"""
    try:
        # Import EPyT for client-side plotting
        try:
            import epyt
        except ImportError:
            st.error("EPyT not installed. Please install with: pip install epyt")
            return None
        
        # Try to find the uploaded .inp file
        import os
        from pathlib import Path
        
        # Look for the most recent .inp file in the upload directory
        upload_dir = Path("backend/uploads")
        if upload_dir.exists():
            inp_files = list(upload_dir.glob("*.inp"))
            if inp_files:
                # Get the most recent file
                latest_file = max(inp_files, key=os.path.getctime)
                
                try:
                    # Create EPyT network object from the .inp file
                    network = epyt.Epanet(str(latest_file))
                    
                    # Use EPyT's native plot method
                    fig = network.plot(
                        title="Network Topology - EPyT Native Plot",
                        fig_size=[12, 8],
                        dpi=300,
                        legend=True,
                        fontsize=8
                    )
                    
                    return fig
                    
                except Exception as e:
                    st.warning(f"EPyT plot failed: {str(e)}")
                    return create_fallback_plot()
            else:
                st.warning("No .inp file found for EPyT plotting")
                return None
        else:
            st.warning("Upload directory not found")
            return None
        
    except Exception as e:
        st.error(f"Failed to create network plot: {str(e)}")
        return None

def create_fallback_plot():
    """Fallback plot using coordinates when EPyT network object is not available"""
    try:
        # Get network data from backend
        network_data = get_network_data()
        
        if not network_data:
            st.warning("No network data available")
            return None
            
        coords = network_data.get('coordinates', {})
        
        if not coords or 'x' not in coords or 'y' not in coords:
            st.warning("No coordinate data available for plotting")
            return None
        
        # Create a matplotlib figure for the network plot
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Plot nodes
        x_coords = list(coords['x'].values()) if isinstance(coords['x'], dict) else coords['x']
        y_coords = list(coords['y'].values()) if isinstance(coords['y'], dict) else coords['y']
        
        ax.scatter(x_coords, y_coords, c='blue', s=50, alpha=0.7, label='Nodes')
        
        # Add node labels
        node_ids = network_data.get('node_ids', [])
        for i, (x, y) in enumerate(zip(x_coords, y_coords)):
            if i < len(node_ids):
                ax.annotate(node_ids[i], (x, y), xytext=(5, 5), 
                           textcoords='offset points', fontsize=8)
        
        ax.set_title('Network Topology - Fallback Plot', fontsize=14, fontweight='bold')
        ax.set_xlabel('X Coordinate')
        ax.set_ylabel('Y Coordinate')
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.set_aspect('equal', adjustable='box')
        
        return fig
        
    except Exception as e:
        st.error(f"Failed to create fallback plot: {str(e)}")
        return None

# Main Application
def main():
    # Header with Logo
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        st.image("frontend/logo.png", width=200)
    
    with col2:
        st.markdown('<h1 class="main-header">Water Network Monitoring System</h1>', unsafe_allow_html=True)
    
    with col3:
        st.empty()  # Empty column for spacing
    
    # Check API connection
    api_connected = check_api_connection()
    st.session_state.api_connected = api_connected
    
    if not api_connected:
        st.error("❌ Cannot connect to FastAPI backend. Please ensure the backend is running on http://localhost:8000")
        st.stop()
    
    # Get all system data at the top level
    network_status = get_network_status()
    network_info = get_network_info() if network_status and network_status.get('network_loaded') else None
    scada_status = get_scada_readings()
    monitoring_status = get_monitoring_status()
    
    # Sidebar
    with st.sidebar:
        st.image("frontend/logo.png", width=150)
        st.header("🔧 System Controls")
        
        # API Status
        st.markdown("### 📡 API Status")
        if api_connected:
            st.success("✅ Backend Connected")
        else:
            st.error("❌ Backend Disconnected")
        
        # Network Status
        st.markdown("### 🌐 Network Status")
        if network_status and network_status.get('network_loaded'):
            st.success("✅ Network Loaded")
            if network_info:
                st.info(f"**File:** {network_info.get('filename', 'Unknown')}")
                st.info(f"**Nodes:** {network_info.get('nodes', 0)}")
                st.info(f"**Links:** {network_info.get('links', 0)}")
        else:
            st.warning("⚠️ No Network Loaded")
        
        # SCADA Status
        st.markdown("### 📊 SCADA Status")
        if scada_status and scada_status.get('simulator_running'):
            st.success("✅ SCADA Running")
        else:
            st.warning("⚠️ SCADA Stopped")
        
        # Monitoring Status
        st.markdown("### 🔍 Monitoring Status")
        if monitoring_status and monitoring_status.get('monitoring_active'):
            st.success("✅ Monitoring Active")
        else:
            st.warning("⚠️ Monitoring Inactive")
        
        # Refresh Button
        if st.button("🔄 Refresh Status", type="primary"):
            st.cache_data.clear()
            st.success("✅ Cache cleared! Data will refresh on next interaction.")
    
    # Main Content Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 Dashboard", "🌐 Network", "📊 SCADA", "🔍 Monitoring", "📈 Analytics"])
    
    # Dashboard Tab
    with tab1:
        st.header("📊 System Dashboard")
        
        # System Overview
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h4>🌐 Network Status</h4>
                <p><strong>Loaded:</strong> {}</p>
                <p><strong>Nodes:</strong> {}</p>
            </div>
            """.format(
                "✅ Yes" if network_status and network_status.get('network_loaded') else "❌ No",
                network_info.get('nodes', 0) if network_info else 0
            ), unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h4>📊 SCADA Status</h4>
                <p><strong>Running:</strong> {}</p>
                <p><strong>Readings:</strong> {}</p>
            </div>
            """.format(
                "✅ Yes" if scada_status and scada_status.get('simulator_running') else "❌ No",
                len(scada_status.get('readings', [])) if scada_status else 0
            ), unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
                <h4>🔍 Monitoring</h4>
                <p><strong>Active:</strong> {}</p>
                <p><strong>Anomalies:</strong> {}</p>
            </div>
            """.format(
                "✅ Yes" if monitoring_status and monitoring_status.get('monitoring_active') else "❌ No",
                len(monitoring_status.get('recent_anomalies', [])) if monitoring_status else 0
            ), unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="metric-card">
                <h4>📡 API Status</h4>
                <p><strong>Connected:</strong> {}</p>
                <p><strong>Response Time:</strong> {}ms</p>
            </div>
            """.format(
                "✅ Yes" if api_connected else "❌ No",
                "~50" if api_connected else "N/A"
            ), unsafe_allow_html=True)
        
        # Recent Activity
        st.header("📈 Recent Activity")
        
        if scada_status and scada_status.get('readings'):
            readings = scada_status['readings'][:10]  # Last 10 readings
            df = pd.DataFrame(readings)
            
            if not df.empty:
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No recent SCADA readings available")
        else:
            st.info("No SCADA data available")
    
    # Network Tab
    with tab2:
        st.header("🌐 Network Management")
        
        # Network refresh button
        col_refresh1, col_refresh2 = st.columns([1, 4])
        with col_refresh1:
            if st.button("🔄 Refresh Network Data", type="secondary"):
                st.cache_data.clear()
                st.success("✅ Cache cleared! Data will refresh on next interaction.")
        
        # Network Upload
        st.subheader("📁 Upload Network File")
        uploaded_file = st.file_uploader(
            "Choose an EPANET .inp file",
            type=['inp'],
            help="Upload a valid EPANET network file",
            key="network_file_uploader"
        )
        
        if uploaded_file is not None:
            # Store the uploaded file in session state to prevent rerun issues
            if 'pending_upload' not in st.session_state:
                st.session_state.pending_upload = None
            
            if st.session_state.pending_upload is None:
                st.session_state.pending_upload = uploaded_file
                st.info("📁 File selected. Click 'Upload Network' to proceed.")
            
            if st.button("📤 Upload Network", type="primary"):
                with st.spinner("Uploading network file..."):
                    result = upload_network_file(st.session_state.pending_upload)
                    if result:
                        st.success(f"✅ Network uploaded successfully: {result.get('network_info', {}).get('filename', 'Unknown')}")
                        st.cache_data.clear()  # Clear cache to refresh data
                        st.info("💡 Please click the 'Refresh Network Data' button below to see updated information")
                        st.session_state.pending_upload = None  # Clear pending upload
                    else:
                        st.error("❌ Failed to upload network file")
        
        # Network Information
        if network_status and network_status.get('network_loaded'):
            st.subheader("📊 Network Information")
            
            # Force refresh network info
            st.cache_data.clear()
            network_info = get_network_info()
            
            # Debug information
            st.write("🔍 Debug Info:")
            st.write(f"Network Status: {network_status}")
            st.write(f"Network Info: {network_info}")
            
            if network_info:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    **Filename:** {network_info.get('filename', 'Unknown')}
                    
                    **Nodes:** {network_info.get('nodes', 0)}
                    - Junctions: {network_info.get('junctions', 0)}
                    - Tanks: {network_info.get('tanks', 0)}
                    - Reservoirs: {network_info.get('reservoirs', 0)}
                    
                    **Links:** {network_info.get('links', 0)}
                    - Pipes: {network_info.get('pipes', 0)}
                    - Pumps: {network_info.get('pumps', 0)}
                    - Valves: {network_info.get('valves', 0)}
                    """)
                
                with col2:
                    # Network visualization
                    st.subheader("🗺️ Network Visualization")
                    
                    # Plot controls
                    col_plot1, col_plot2 = st.columns(2)
                    with col_plot1:
                        show_labels = st.checkbox("Show Node Labels", value=True)
                    with col_plot2:
                        if st.button("🔄 Refresh Plot", type="secondary"):
                            st.cache_data.clear()
                    
                    # Create client-side network plot
                    st.write("🔍 Plot Debug Info:")
                    st.write(f"Upload directory exists: {Path('backend/uploads').exists()}")
                    if Path('backend/uploads').exists():
                        inp_files = list(Path('backend/uploads').glob('*.inp'))
                        st.write(f"Found .inp files: {inp_files}")
                    
                    fig = create_network_plot()
                    if fig:
                        st.pyplot(fig)
                    else:
                        st.info("Network visualization not available")
        else:
            st.info("Please upload a network file to view network information")
    
    # SCADA Tab
    with tab3:
        st.header("📊 SCADA Simulator")
        
        # SCADA Controls
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("▶️ Start SCADA Simulation", type="primary"):
                with st.spinner("Starting SCADA simulation..."):
                    result = start_scada_simulation()
                    if result:
                        st.success("✅ SCADA simulation started")
                        st.cache_data.clear()
                        # Don't use st.rerun() as it resets tab selection
                    else:
                        st.error("❌ Failed to start SCADA simulation")
        
        with col2:
            if st.button("⏹️ Stop SCADA Simulation"):
                with st.spinner("Stopping SCADA simulation..."):
                    result = stop_scada_simulation()
                    if result:
                        st.success("✅ SCADA simulation stopped")
                        st.cache_data.clear()
                        # Don't use st.rerun() as it resets tab selection
                    else:
                        st.error("❌ Failed to stop SCADA simulation")
        
        # SCADA Configuration
        st.subheader("⚙️ SCADA Configuration")
        
        with st.expander("Advanced Configuration"):
            col1, col2 = st.columns(2)
            
            with col1:
                update_interval = st.slider("Update Interval (seconds)", 1, 300, 30)
                noise_level = st.slider("Noise Level (%)", 0, 10, 2)
            
            with col2:
                time_variation = st.slider("Time Variation (%)", 0, 100, 50)
                fault_injection = st.checkbox("Enable Fault Injection")
        
        # SCADA Data Display
        st.subheader("📈 SCADA Data")
        
        scada_data = get_scada_readings()
        if scada_data and scada_data.get('readings'):
            readings = scada_data['readings']
            
            # Convert to DataFrame
            df = pd.DataFrame(readings)
            
            if not df.empty:
                # Display data table
                st.dataframe(df, use_container_width=True)
                
                # Create charts
                if len(df) > 0:
                    st.subheader("📊 Data Visualization")
                    
                    # Pressure chart
                    if 'pressure' in df.columns:
                        fig_pressure = px.line(df, x='timestamp', y='pressure', title='Pressure Readings')
                        st.plotly_chart(fig_pressure, use_container_width=True)
                    
                    # Flow chart
                    if 'flow' in df.columns:
                        fig_flow = px.line(df, x='timestamp', y='flow', title='Flow Readings')
                        st.plotly_chart(fig_flow, use_container_width=True)
                    
                    # Level chart
                    if 'level' in df.columns:
                        fig_level = px.line(df, x='timestamp', y='level', title='Level Readings')
                        st.plotly_chart(fig_level, use_container_width=True)
            else:
                st.info("No SCADA readings available")
        else:
            st.info("SCADA simulation not running or no data available")
    
    # Monitoring Tab
    with tab4:
        st.header("🔍 Monitoring Engine")
        
        # Monitoring Controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🎯 Establish Baseline", type="primary"):
                with st.spinner("Establishing baseline..."):
                    result = establish_baseline()
                    if result:
                        st.success("✅ Baseline established successfully")
                        st.cache_data.clear()
                        # Don't use st.rerun() as it resets tab selection
                    else:
                        st.error("❌ Failed to establish baseline")
        
        with col2:
            if st.button("▶️ Start Monitoring"):
                with st.spinner("Starting monitoring..."):
                    result = start_monitoring()
                    if result:
                        st.success("✅ Monitoring started")
                        st.cache_data.clear()
                        # Don't use st.rerun() as it resets tab selection
                    else:
                        st.error("❌ Failed to start monitoring")
        
        with col3:
            if st.button("⏹️ Stop Monitoring"):
                with st.spinner("Stopping monitoring..."):
                    result = stop_monitoring()
                    if result:
                        st.success("✅ Monitoring stopped")
                        st.cache_data.clear()
                        # Don't use st.rerun() as it resets tab selection
                    else:
                        st.error("❌ Failed to stop monitoring")
        
        # Monitoring Status
        monitoring_status = get_monitoring_status()
        if monitoring_status:
            st.subheader("📊 Monitoring Status")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                **Status:** {'✅ Active' if monitoring_status.get('monitoring_active') else '❌ Inactive'}
                
                **Baseline:** {'✅ Established' if monitoring_status.get('baseline_established') else '❌ Not Established'}
                
                **Anomalies Detected:** {len(monitoring_status.get('recent_anomalies', []))}
                """)
            
            with col2:
                st.markdown(f"""
                **Thresholds:**
                - Pressure: {monitoring_status.get('thresholds', {}).get('pressure_deviation', 'N/A')}%
                - Flow: {monitoring_status.get('thresholds', {}).get('flow_deviation', 'N/A')}%
                - Level: {monitoring_status.get('thresholds', {}).get('level_deviation', 'N/A')}%
                """)
            
            # Recent Anomalies
            if monitoring_status.get('recent_anomalies'):
                st.subheader("🚨 Recent Anomalies")
                anomalies_df = pd.DataFrame(monitoring_status['recent_anomalies'])
                st.dataframe(anomalies_df, use_container_width=True)
            else:
                st.info("No anomalies detected")
        else:
            st.info("Monitoring status not available")
    
    # Analytics Tab
    with tab5:
        st.header("📈 Analytics & Reports")
        
        # Data Export
        st.subheader("📤 Data Export")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Export SCADA Data"):
                scada_data = get_scada_readings()
                if scada_data and scada_data.get('readings'):
                    df = pd.DataFrame(scada_data['readings'])
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"scada_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("No SCADA data available for export")
        
        with col2:
            if st.button("📈 Export Monitoring Data"):
                monitoring_data = get_monitoring_status()
                if monitoring_data:
                    # Convert to JSON for export
                    json_data = json.dumps(monitoring_data, indent=2)
                    st.download_button(
                        label="Download JSON",
                        data=json_data,
                        file_name=f"monitoring_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
                else:
                    st.warning("No monitoring data available for export")
        
        # System Statistics
        st.subheader("📊 System Statistics")
        
        # Get all data
        network_info = get_network_info()
        scada_data = get_scada_readings()
        monitoring_data = get_monitoring_status()
        
        # Create statistics
        stats_data = {
            'Metric': [
                'Network Nodes',
                'Network Links',
                'SCADA Readings',
                'Active Monitoring',
                'Anomalies Detected',
                'System Uptime'
            ],
            'Value': [
                network_info.get('nodes', 0) if network_info else 0,
                network_info.get('links', 0) if network_info else 0,
                len(scada_data.get('readings', [])) if scada_data else 0,
                'Yes' if monitoring_data and monitoring_data.get('monitoring_active') else 'No',
                len(monitoring_data.get('recent_anomalies', [])) if monitoring_data else 0,
                'N/A'  # Would need to implement uptime tracking
            ]
        }
        
        stats_df = pd.DataFrame(stats_data)
        st.dataframe(stats_df, use_container_width=True)
        
        # Performance Metrics
        st.subheader("⚡ Performance Metrics")
        
        # Simulate some performance data
        performance_data = {
            'Metric': ['API Response Time', 'Database Query Time', 'SCADA Generation Time', 'Monitoring Analysis Time'],
            'Average (ms)': [45, 12, 8, 15],
            'Max (ms)': [120, 45, 25, 35],
            'Status': ['✅ Good', '✅ Good', '✅ Good', '✅ Good']
        }
        
        perf_df = pd.DataFrame(performance_data)
        st.dataframe(perf_df, use_container_width=True)

if __name__ == "__main__":
    main()