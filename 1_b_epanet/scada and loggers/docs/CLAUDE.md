# Real-Time Dynamic Water Network Monitoring System (RTDWMS)
## Production-Ready Digital Twin for Jordanian Water Distribution Networks

---

## 🎯 System Objective

To develop a **production-ready digital twin** for a water distribution network in Jordan, capable of:

* **Monitoring network status** - Real-time monitoring of water network health
* **Detecting anomalies** - Identifying leaks, pressure drops, flow issues, and other problems
* **Providing forecasting** - Predicting future network behavior and demand patterns
* **Alerting operators** - Notifying when problems occur or are predicted
* **Simulating SCADA data** - Generating realistic sensor data for testing and development
* **Running hydraulic analysis** - Using EPANET for physics-based network modeling
* **Interactive dashboard** - Modern web interface for visualization and control

### **Core Value Proposition**
The system's main value is **anomaly detection and monitoring**, not just data generation. It compares what sensors measure vs what EPANET predicts to identify problems in the water network.

## 🎯 **Agreed System Logic (Critical for Implementation)**

### **The Correct Approach:**
1. **Upload network file** → Parse EPANET .inp file
2. **Establish baseline** → Run hydraulic analysis with **original network design conditions** (from .inp file)
3. **Get base pressure values** → Extract baseline pressures, flows, and tank levels
4. **Generate realistic SCADA data** → Simulate sensor readings based on baseline + time-of-day variations
5. **Monitor for major drifts** → Compare current SCADA readings vs baseline to detect anomalies

### **Key Implementation Requirements:**
- **True Baseline**: Use original network design conditions from .inp file, not estimated demands
- **Drift Detection**: Compare current readings against established baseline
- **Anomaly Thresholds**: Flag deviations >10% for pressure, >15% for flow
- **Real-time Monitoring**: Continuous comparison of measured vs baseline values
- **Alert System**: Notify operators when anomalies are detected

### **Critical Success Factors:**
- **Baseline Establishment**: Must use original network design, not estimated demands
- **Independent Monitoring**: SCADA data generation must be independent of monitoring logic
- **Accurate Comparison**: Monitoring engine must compare measured vs baseline, not predicted vs measured
- **Logical Flow**: Upload → Baseline → Generate Data → Monitor Drifts → Alert

---

## 🏗️ Technology Stack

### Backend (Python)
- **FastAPI** - Modern, high-performance web framework
- **EPyT** - EPANET hydraulic simulations
- **SQLAlchemy** - Database ORM
- **PostgreSQL/SQLite** - Time-series data storage
- **WebSockets** - Real-time data streaming
- **Pydantic** - Data validation
- **asyncio** - Asynchronous operations
- **Pandas** - Data processing and synchronization

### Frontend (Streamlit)
- **Streamlit** - Modern Python web framework
- **Matplotlib** - Network visualization and plotting
- **Plotly** - Interactive charts and graphs
- **Pandas** - Data processing and analysis
- **Requests** - HTTP client for API communication
- **Caching** - Built-in data caching with @st.cache_data

---

## 📁 Project Structure

The project is organized into dedicated folders for better maintainability:

```
├── backend/                 # FastAPI backend service
│   ├── api/                # REST API endpoints
│   ├── services/           # Business logic and engines
│   ├── models/             # Database models and schemas
│   └── main.py            # FastAPI application entry point
├── frontend/               # Streamlit frontend application
│   ├── streamlit_app.py   # Main Streamlit application
│   ├── requirements_streamlit.txt  # Frontend dependencies
│   └── logo.png           # Application logo
├── networks/              # Sample EPANET network files
├── docs/                  # Project documentation
└── start_system.sh        # System startup script
```

## 🧩 High-Level System Components

### 1. **Streamlit Frontend Application** (`frontend/`)
- Modern, responsive web interface
- Real-time network visualization with Matplotlib
- Interactive dashboards and controls
- Built-in caching and performance optimization

### 2. **FastAPI Backend Service**
- RESTful API endpoints
- WebSocket real-time communication
- Background task processing
- Database management

### 3. **Demand Forecasting Engine**
- Time-of-day demand patterns
- Historical data analysis
- Seasonal adjustments
- Weather-based corrections

### 4. **SCADA Simulator** (Data Source)
- Generates realistic sensor data (pressures, flows, tank levels, pump status)
- Configurable variation patterns
- Fault injection capabilities
- Synchronized data generation

### 5. **EPANET Monitoring Engine** (Core Analysis)
- **Baseline simulation establishment** - Creates expected network behavior
- **Real-time hydraulic analysis** - Runs EPANET with estimated demands
- **Predicted values generation** - What the network SHOULD be doing
- **Data quality assessment** - Validates sensor data quality

### 6. **Anomaly Detection System** (Core Value)
- **Pressure deviation analysis** - Compares measured vs predicted pressures
- **Flow anomaly detection** - Identifies unusual flow patterns
- **Data quality monitoring** - Flags sensor malfunctions
- **Alert generation and prioritization** - Notifies operators of problems

### 7. **Data Storage Layer**
- PostgreSQL for production data
- Time-series optimized storage
- Data retention policies
- Export capabilities

## 🔄 System Data Flow (Corrected Logic)

```
1. Network Upload → Parse EPANET .inp file
2. Baseline Establishment → Run EPANET with original design conditions
3. Baseline Storage → Store baseline pressures, flows, tank levels
4. SCADA Simulator → Generate realistic sensor data based on baseline + variations
5. Monitoring Engine → Compare current SCADA readings vs baseline
6. Anomaly Detector → Flag when deviations exceed thresholds (>10% pressure, >15% flow)
7. Alert System → Notify operators of detected anomalies
8. Dashboard → Show network status and alerts
```

