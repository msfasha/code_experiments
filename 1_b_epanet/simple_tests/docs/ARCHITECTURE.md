# System Architecture Diagram

## Water Network Monitoring System - Component Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    YASMIN WATER NETWORK (Amman, Jordan)              │
│                         EPANET Model (.inp file)                     │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      CORE SIMULATION ENGINE                          │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  RealTimeSimulator (realtime_simulator.py)                  │   │
│  │  ─────────────────────────────────────────                  │   │
│  │  • Hydraulic Analysis (EPANET 2.2)                          │   │
│  │  • Step-by-step simulation                                  │   │
│  │  • State management                                         │   │
│  │  • Historical data collection                               │   │
│  │                                                              │   │
│  │  Methods:                                                    │   │
│  │  - initialize()      : Setup hydraulic engine               │   │
│  │  - step()           : Advance one time step                 │   │
│  │  - run_continuous() : Continuous simulation                 │   │
│  └─────────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    SCADA SENSOR SIMULATION                           │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  SCADASimulator (scada_simulator.py)                        │   │
│  │  ──────────────────────────────────────                     │   │
│  │  • Virtual sensor deployment                                │   │
│  │  • Realistic noise generation                               │   │
│  │  • Multi-sensor support                                     │   │
│  │                                                              │   │
│  │  Sensor Types:                                               │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │   │
│  │  │  Pressure   │  │    Flow     │  │ Tank Level  │        │   │
│  │  │   Sensors   │  │   Meters    │  │   Sensors   │        │   │
│  │  │  (at nodes) │  │  (at pipes) │  │  (at tanks) │        │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘        │   │
│  │                                                              │   │
│  │  Methods:                                                    │   │
│  │  - add_sensors()        : Deploy sensors                    │   │
│  │  - auto_deploy_sensors(): Auto placement                    │   │
│  │  - get_live_data()      : Get sensor readings               │   │
│  └─────────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       MAIN CONTROLLER                                │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  WaterNetworkMonitor (main_monitor.py)                      │   │
│  │  ────────────────────────────────────                       │   │
│  │  • Component integration                                    │   │
│  │  • Threading management                                     │   │
│  │  • Data flow orchestration                                  │   │
│  │                                                              │   │
│  │  Flow:                                                       │   │
│  │  1. Load EPANET network                                     │   │
│  │  2. Initialize simulator & SCADA                            │   │
│  │  3. Start simulation thread                                 │   │
│  │  4. Update dashboard continuously                           │   │
│  └─────────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    WEB DASHBOARD & VISUALIZATION                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  NetworkDashboard (network_dashboard.py)                    │   │
│  │  ────────────────────────────────────────                   │   │
│  │  • Plotly Dash web framework                                │   │
│  │  • Real-time data visualization                             │   │
│  │  • Interactive network map                                  │   │
│  │  • Alert system                                             │   │
│  │                                                              │   │
│  │  Components:                                                 │   │
│  │  ┌──────────────────────────────────────────────────┐      │   │
│  │  │         STATUS PANEL                             │      │   │
│  │  │  • System status  • Time  • Sensor count         │      │   │
│  │  └──────────────────────────────────────────────────┘      │   │
│  │                                                              │   │
│  │  ┌─────────────────────┐  ┌──────────────────────┐        │   │
│  │  │   NETWORK MAP       │  │   ALERTS PANEL       │        │   │
│  │  │   • Node markers    │  │   • Low pressure     │        │   │
│  │  │   • Link lines      │  │   • High pressure    │        │   │
│  │  │   • Color-coded     │  │   • Statistics       │        │   │
│  │  │   • Interactive     │  │                      │        │   │
│  │  └─────────────────────┘  └──────────────────────┘        │   │
│  │                                                              │   │
│  │  ┌─────────────────────┐  ┌──────────────────────┐        │   │
│  │  │  PRESSURE TRENDS    │  │   FLOW TRENDS        │        │   │
│  │  │  • Time series      │  │   • Time series      │        │   │
│  │  │  • Multi-node       │  │   • Multi-link       │        │   │
│  │  └─────────────────────┘  └──────────────────────┘        │   │
│  │                                                              │   │
│  │  Methods:                                                    │   │
│  │  - setup_layout()       : Create UI layout                  │   │
│  │  - setup_callbacks()    : Real-time updates                 │   │
│  │  - create_network_figure(): Generate map                    │   │
│  │  - check_alerts()       : Monitor anomalies                 │   │
│  └─────────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                               │
│                    Web Browser (localhost:8050)                      │
│                                                                       │
│  Operators can:                                                      │
│  • Monitor network status in real-time                               │
│  • View pressure/flow trends                                         │
│  • Receive alerts for anomalies                                      │
│  • Analyze network statistics                                        │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
EPANET Network (.inp)
        │
        ├─> Load Model ──> RealTimeSimulator
        │                      │
        │                      ├─> Run Hydraulic Step
        │                      │       │
        │                      │       ├─> Pressures
        │                      │       ├─> Flows
        │                      │       ├─> Demands
        │                      │       └─> Tank Levels
        │                      │
        └─────────────────────┬────────┘
                              │
                              ▼
                    SCADASimulator
                              │
                              ├─> Add Noise
                              ├─> Simulate Sensors
                              │
                              ▼
                    Sensor Data (with noise)
                              │
                              ▼
                    WaterNetworkMonitor
                              │
                              ├─> Merge Data
                              ├─> Update State
                              │
                              ▼
                    NetworkDashboard
                              │
                              ├─> Update Visualizations
                              ├─> Check Alerts
                              ├─> Store History
                              │
                              ▼
                    Web Interface (User)
```

## Technology Stack

```
┌─────────────────────────────────────┐
│         Application Layer            │
│  - Python 3.7+                       │
│  - Threading for concurrency         │
│  - Queue for data passing            │
└──────────────┬──────────────────────┘
               │
┌──────────────┴──────────────────────┐
│      Visualization Layer             │
│  - Dash 2.14+                        │
│  - Plotly 5.17+                      │
│  - HTML/CSS (auto-generated)         │
└──────────────┬──────────────────────┘
               │
┌──────────────┴──────────────────────┐
│      Computation Layer               │
│  - NumPy (numerical ops)             │
│  - Collections (data structures)     │
└──────────────┬──────────────────────┘
               │
┌──────────────┴──────────────────────┐
│      Simulation Engine               │
│  - EPyT 1.0.7+                       │
│  - EPANET 2.2                        │
└─────────────────────────────────────┘
```

## File Dependencies

```
main_monitor.py
    ├── imports: epyt.epanet
    ├── imports: scada_simulator.SCADASimulator
    ├── imports: realtime_simulator.RealTimeSimulator
    └── imports: network_dashboard.NetworkDashboard

scada_simulator.py
    ├── imports: numpy
    └── imports: datetime

realtime_simulator.py
    ├── imports: typing
    └── imports: time

network_dashboard.py
    ├── imports: dash
    ├── imports: plotly
    ├── imports: numpy
    └── imports: collections

test_system.py
    ├── imports: all modules (for testing)
    └── validates: installation
```

## Deployment Scenarios

### Current: Development & Testing
```
Developer Machine
    ├── Python environment
    ├── EPANET network files
    ├── Monitoring system
    └── Dashboard (localhost:8050)
```

### Future: Production Deployment
```
┌──────────────────────┐
│   Real SCADA System  │ ──┐
│   - OPC-UA           │   │
│   - Modbus           │   │
└──────────────────────┘   │
                           │
┌──────────────────────┐   │    ┌──────────────────────┐
│   Field Sensors      │ ──┼───▶│  Monitoring Server   │
│   - Pressure meters  │   │    │  - EPANET engine     │
│   - Flow meters      │   │    │  - State estimation  │
│   - Level sensors    │   │    │  - Data storage      │
└──────────────────────┘   │    └──────────┬───────────┘
                           │               │
┌──────────────────────┐   │               │
│   Actuators          │ ──┘               │
│   - Pumps            │                   │
│   - Valves           │                   │
└──────────────────────┘                   │
                                           ▼
                              ┌────────────────────────┐
                              │   Web Dashboard        │
                              │   - Real-time monitor  │
                              │   - Alerts             │
                              │   - Analytics          │
                              └────────────────────────┘
                                           │
                              ┌────────────┴────────────┐
                              │                         │
                         ┌────▼─────┐           ┌──────▼──────┐
                         │ Operators│           │  Management │
                         │ (Field)  │           │  (Office)   │
                         └──────────┘           └─────────────┘
```

## Key Features Summary

### ✅ Implemented (Current Version)
- ✓ Real-time hydraulic simulation
- ✓ SCADA sensor simulation with noise
- ✓ Interactive web dashboard
- ✓ Network visualization (color-coded)
- ✓ Pressure & flow trend charts
- ✓ Automated alert system
- ✓ Multi-threaded execution
- ✓ Configurable parameters

### 🔄 Planned (Future Enhancements)
- ⚙ Real SCADA integration (OPC-UA, Modbus)
- ⚙ Database storage (TimescaleDB, InfluxDB)
- ⚙ GIS map overlay (OpenStreetMap)
- ⚙ Machine learning anomaly detection
- ⚙ Water quality tracking (MSX)
- ⚙ Mobile app interface
- ⚙ SMS/Email alerts
- ⚙ User authentication
- ⚙ Multi-network support
- ⚙ Report generation
