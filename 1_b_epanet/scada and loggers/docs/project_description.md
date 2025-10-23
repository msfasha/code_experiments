# Real-Time Dynamic Water Network Monitoring System (RTDWMS)
## Production-Ready Digital Twin for Jordanian Water Distribution Networks

---

## 🎯 System Objective

To develop a **production-ready digital twin** for a water distribution network in Jordan, capable of:

* Simulating live SCADA behavior (data generation),
* Running hydraulic computations in real time using **EPANET** (via **EPyT**),
* Detecting abnormal or faulty network conditions (pressures, flows),
* Providing a modern, interactive dashboard (via **React + FastAPI**) for visualization and control.

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

### Frontend (React/TypeScript)
- **React 18** - Modern UI framework
- **TypeScript** - Type safety
- **Vite** - Fast build tool
- **Plotly.js** - Interactive network visualization
- **Recharts** - Time-series charts
- **TanStack Query** - Data fetching/caching
- **Zustand** - State management
- **TailwindCSS** - Styling
- **Axios** - HTTP client

---

## 🧩 High-Level System Components

### 1. **React Frontend Application**
- Modern, responsive web interface
- Real-time network visualization with Plotly.js
- Interactive dashboards and controls
- Mobile-friendly design

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

### 4. **SCADA Simulator**
- Generates realistic sensor data (pressures, flows, tank levels, pump status)
- Configurable variation patterns
- Fault injection capabilities
- Synchronized data generation

### 5. **EPANET Monitoring Engine**
- Baseline simulation establishment
- Real-time hydraulic analysis
- Data quality assessment
- Time synchronization handling

### 6. **Anomaly Detection System**
- Pressure deviation analysis
- Flow anomaly detection
- Data quality monitoring
- Alert generation and prioritization

### 7. **Data Storage Layer**
- PostgreSQL for production data
- Time-series optimized storage
- Data retention policies
- Export capabilities

---

## ⚙️ Functional Requirements (FRs)

### **FR1 – Network File Management**
* The system shall allow users to upload EPANET `.inp` files via web interface
* The system shall parse and extract all network components:
  * Junctions with coordinates
  * Pipes/Links with properties
  * Pumps with characteristics
  * Tanks/Reservoirs with dimensions
* The system shall display network topology with interactive visualization
* The system shall provide network summary statistics

### **FR2 – Demand Forecasting System**
* The system shall implement time-of-day demand patterns
* The system shall support seasonal demand adjustments
* The system shall provide demand estimation based on historical patterns
* The system shall allow manual demand override capabilities
* The system shall track demand estimation accuracy

### **FR3 – SCADA Data Simulation**
* The system shall generate realistic sensor data for:
  * **Pressure sensors** at junctions (not demands - SCADA doesn't measure demands)
  * **Flow meters** at instrumented pipe locations
  * **Tank level sensors** at storage facilities
  * **Pump status** and performance data
* The system shall apply configurable noise and variation patterns
* The system shall support fault injection for testing
* The system shall maintain data synchronization within time windows

### **FR4 – Real-Time Data Synchronization**
* The system shall handle asynchronous SCADA data arrival
* The system shall implement time window tolerance (±30 seconds for normal operation)
* The system shall assess data quality and coverage
* The system shall use last-known values for missing sensors
* The system shall flag stale data (>5 minutes old)

### **FR5 – EPANET Hydraulic Analysis**
* The system shall run baseline EPANET simulation on network load
* The system shall perform continuous hydraulic analysis with estimated demands
* The system shall compare predicted vs measured pressures and flows
* The system shall handle simulation failures gracefully
* The system shall provide simulation performance metrics

### **FR6 – Anomaly Detection & Analysis**
* The system shall detect pressure deviations (>10% from predicted)
* The system shall identify flow anomalies (>15% from predicted)
* The system shall flag data quality issues (stale sensors, missing data)
* The system shall prioritize anomalies by severity and location
* The system shall provide anomaly confidence scores

### **FR7 – Real-Time Monitoring Dashboard**
* The system shall display live network status with color-coded components
* The system shall show real-time pressure and flow charts
* The system shall provide anomaly alerts and notifications
* The system shall support multiple concurrent users
* The system shall offer mobile-responsive interface

### **FR8 – Data Management & Storage**
* The system shall store all data with precise timestamps
* The system shall implement data retention policies
* The system shall provide data export capabilities (CSV, Excel)
* The system shall support historical data queries
* The system shall maintain data integrity and backup

### **FR9 – Configuration Management**
* The system shall provide web-based configuration interface
* The system shall support configurable parameters:
  * Simulation intervals (30s to 5min)
  * Data quality thresholds
  * Anomaly detection sensitivity
  * Time synchronization windows
* The system shall persist configuration settings
* The system shall support configuration validation

### **FR10 – System Monitoring & Logging**
* The system shall log all major operations and errors
* The system shall provide system health monitoring
* The system shall track performance metrics
* The system shall support remote diagnostics
* The system shall implement graceful error recovery

### **FR11 – User Management & Security**
* The system shall support user authentication
* The system shall implement role-based access control
* The system shall provide audit trails
* The system shall support secure API access
* The system shall implement session management

### **FR12 – Integration Capabilities**
* The system shall provide RESTful API for external integration
* The system shall support WebSocket connections for real-time data
* The system shall offer data export APIs
* The system shall support third-party SCADA system integration
* The system shall provide webhook notifications

---

## ⚙️ Non-Functional Requirements (NFRs) - MVP Phase

### **Basic Performance**
* **Simulation Response Time**: <10 seconds (acceptable for pilot)
* **Data Processing**: Handle 1 network with 50-100 nodes
* **Concurrent Users**: 1-5 users (pilot demonstration)
* **Database**: SQLite for simplicity (upgrade to PostgreSQL later)

### **Basic Reliability**
* **Uptime**: System should run for 8+ hours without restart
* **Error Handling**: Graceful handling of EPANET failures
* **Data Persistence**: Basic data storage and retrieval
* **Recovery**: Manual restart capability

### **Basic Security**
* **No Authentication**: Open access for pilot (add later)
* **Local Network**: Run on localhost/private network
* **Basic Validation**: Input validation for file uploads

### **Basic Usability**
* **Simple Interface**: Clean, functional web interface
* **Desktop Focus**: Optimized for desktop browsers
* **Basic Documentation**: README and inline comments

---

## 🏗️ Production Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend (Port 3000)                │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐   │
│  │  Dashboard  │  Network   │   SCADA     │ Monitoring  │   │
│  │   Page      │   Config   │  Simulator  │   Page      │   │
│  └─────────────┴─────────────┴─────────────┴─────────────┘   │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP/REST + WebSocket
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                FastAPI Backend (Port 8000)                  │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐   │
│  │   Network   │   SCADA     │ Monitoring  │    Data     │   │
│  │    API      │    API      │    API      │    API      │   │
│  └─────────────┴─────────────┴─────────────┴─────────────┘   │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐   │
│  │  Demand     │   SCADA     │ Monitoring  │  Anomaly    │   │
│  │ Forecaster  │ Simulator   │   Engine    │  Detector   │   │
│  └─────────────┴─────────────┴─────────────┴─────────────┘   │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              PostgreSQL Database                            │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐   │
│  │   Network   │   SCADA     │ Monitoring  │  Anomalies  │   │
│  │   Data      │  Readings   │  Results    │    Log      │   │
│  └─────────────┴─────────────┴─────────────┴─────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Development Phases - MVP Focus

### **Phase 1: Core Backend (Week 1)**
- FastAPI project setup
- SQLite database with basic models
- EPyT network loader
- Basic API endpoints (upload, info, status)
- Simple demand forecasting

### **Phase 2: Basic Frontend (Week 1-2)**
- React + TypeScript setup
- Basic layout and routing
- Network file upload
- Simple network visualization
- API client integration

### **Phase 3: SCADA Simulation (Week 2)**
- Basic SCADA data generator
- Simple time-of-day demand patterns
- CSV data storage
- Frontend controls (start/stop)

### **Phase 4: Monitoring Engine (Week 2-3)**
- EPANET baseline simulation
- Basic anomaly detection (pressure deviations)
- Simple comparison logic
- Frontend monitoring display

### **Phase 5: Polish & Demo (Week 3)**
- Error handling and logging
- Basic data export
- Testing with sample networks
- Documentation and demo preparation

---

## 🔧 Key Technical Considerations - MVP

### **Simplified Data Flow**
- **Synchronized Generation**: SCADA simulator generates all data at once
- **Basic Time Windows**: ±5 seconds tolerance (simulator controls timing)
- **Simple Storage**: CSV files for data, SQLite for metadata
- **Last-Known Values**: Basic caching for missing data

### **SCADA Data Reality (Simplified)**
- **Simulated SCADA**: Pressures, flows, tank levels, pump status
- **Demand Estimation**: Simple time-of-day patterns (morning/evening peaks)
- **Basic Comparison**: Predicted vs measured pressure differences
- **Simple Alerts**: Flag deviations >10% from predicted values

### **MVP Performance**
- **Single Network**: Focus on one network file (Net1.inp)
- **Basic Database**: SQLite with simple tables
- **Local Development**: Run on localhost for simplicity
- **Manual Controls**: Start/stop buttons for simulation

---

## 📊 MVP Success Metrics

### **Technical Metrics**
- **System Stability**: Runs for 8+ hours without crashes
- **Response Time**: <10 seconds for hydraulic simulations
- **Data Accuracy**: Basic anomaly detection works
- **User Experience**: Functional web interface

### **Demo Metrics**
- **Network Loading**: Successfully load and visualize Net1.inp
- **SCADA Simulation**: Generate realistic sensor data
- **Anomaly Detection**: Detect pressure deviations
- **Real-time Updates**: Show live data in dashboard

---

## 🎯 MVP Readiness Checklist

- [ ] **Basic Functionality**: Upload network, run simulation, detect anomalies
- [ ] **User Interface**: Clean, functional web interface
- [ ] **Data Flow**: SCADA → EPANET → Comparison → Alerts
- [ ] **Error Handling**: Graceful handling of common errors
- [ ] **Documentation**: Basic README and setup instructions
- [ ] **Testing**: Works with sample network files
- [ ] **Demo Ready**: Can demonstrate core functionality

---

## 🚀 Next Steps - MVP Focus

1. **Setup Development Environment**: Python venv, Node.js, basic tools
2. **Backend MVP**: FastAPI + SQLite + EPyT integration
3. **Frontend MVP**: React + basic components + API integration
4. **Core Features**: Network upload, SCADA simulation, basic monitoring
5. **Testing**: Test with Net1.inp and other sample networks
6. **Demo Preparation**: Polish interface, add basic documentation
7. **Future Growth**: Plan for production features (authentication, scaling, etc.)