# Real-Time Water Network Monitoring System - AI Coding Guide

## Project Overview
Digital twin for water distribution networks with real-time SCADA simulation, EPANET hydraulic analysis, and anomaly detection. Built for Jordanian water infrastructure with FastAPI backend + React frontend.

## Architecture

### Backend: FastAPI + EPyT (EPANET Python Toolkit)
- **Global Network State Pattern**: Use `services/network_state.py` singleton (`network_state`) for sharing loaded EPANET networks across services
- **Service Layer**: `services/` contains core business logic (network_loader, scada_simulator, network_state)
- **API Routes**: `api/` routers are mounted in `main.py` with `/api` prefix
- **Database**: SQLAlchemy with SQLite (`data/monitoring.db`), tables defined in `models/tables.py`
- **Async Operations**: SCADA simulator runs as background asyncio task

### Frontend: React + TypeScript + Vite
- **Port**: Dev server runs on `localhost:5173` (configured in CORS middleware)
- **API Client**: Centralized in `src/api/` with typed interfaces
- **Routing**: React Router with pages: Dashboard, Network, SCADA, Monitoring
- **Visualization**: Plotly.js for network graphs, standard React components for UI

## Critical Workflows

### Running the System
```bash
# Backend (port 8000)
cd backend
python main.py

# Frontend (port 5173)
cd frontend
npm run dev
```

### Network Loading Flow
1. Upload `.inp` file via `/api/network/upload`
2. `NetworkLoader.load_network()` parses with EPyT
3. Updates `network_state` singleton (accessed by all services)
4. Network must be loaded before starting SCADA simulator

### SCADA Simulation Lifecycle
- **Start**: `/api/scada/start` → creates asyncio background task
- **State**: Tracked in DB (`SCADASimulatorConfig.is_running`) AND in-memory (`_running` flag)
- **Stop**: Must check DB state first, then cancel task
- **Data**: Generated readings stored in `scada_readings` table with timestamps

## EPANET/EPyT Integration Patterns

### Network Access
```python
from services.network_state import network_state

# Always check if loaded
if not network_state.is_loaded:
    raise ValueError("No network loaded")

# Access the EPyT instance
network = network_state.current_network
num_junctions = network.getNodeJunctionCount()
```

### Temporary File Management
- EPyT creates `.inp` and `.txt` files in `temp/` with timestamp prefixes
- Pattern: `YYYYMMDD_HHMMSS_<network_name>.inp`
- Clean up using `UPLOAD_DIR` from `config.py`

### Common EPyT Methods
- `getNodeJunctionCount()`, `getLinkPipeCount()` - network statistics
- `getNodeJunctionNameID()` - get junction IDs
- `getNodeElevations()`, `getNodeBaseDemands()` - node properties
- See `docs/epyt_api.md` for complete reference (8447 lines)

## Database Schema Conventions

### Key Tables (models/tables.py)
- **SCADAReading**: sensor data with `node_id`, `sensor_type` (pressure/flow/level), `value`, `timestamp`
- **SCADASimulatorConfig**: singleton config with `is_running`, `update_interval`, variation params
- **MonitoringResult**: anomaly detection results with baseline vs current comparisons
- **NetworkComponent**: parsed network topology from .inp files

### Timestamp Pattern
All tables use `datetime.utcnow()` for UTC timestamps, indexed for time-series queries

## Configuration Constants

Defined in `backend/config.py`:
- `DEFAULT_SIMULATION_INTERVAL = 30` seconds
- `DEFAULT_TIME_WINDOW = 5` seconds tolerance
- `DEFAULT_PRESSURE_THRESHOLD = 10.0%` deviation
- `DEFAULT_FLOW_THRESHOLD = 15.0%` deviation
- `MAX_FILE_SIZE = 10MB` for network uploads

## Project-Specific Patterns

### Network Directory Structure
- `networks/` - sample .inp files (Net1.inp, Net2.inp, yasmin.inp)
- `temp/` - timestamped temporary files from EPyT operations
- `data/` - SQLite database and persistent storage
- `logs/` - application logs

### State Management Anti-Pattern
⚠️ **Don't create multiple NetworkLoader instances** - use the global singleton or the instance in API routers to maintain state consistency

### CORS Configuration
Frontend URL hardcoded: `http://localhost:5173` in `main.py` CORS middleware

### Frontend API Typing
Each API module (`api/scada.ts`, `api/network.ts`) exports TypeScript interfaces matching backend Pydantic models

## Development Context

### Testing Network Files
Use existing networks in `networks/` directory:
- `Net1.inp` - EPANET standard example (small)
- `Net2.inp`, `Net3.inp` - larger examples
- `yasmin.inp` - custom network

### Anomaly Detection Approach
System compares baseline EPANET predictions vs simulated SCADA readings to detect:
- Pressure deviations (>10%)
- Flow anomalies (>15%)
- Data quality issues (stale sensors >5min)

### Real-Time Data Synchronization
Uses time window tolerance (±30 seconds) to handle asynchronous SCADA data arrival with last-known values for missing sensors

## Documentation References
- `docs/project_description.md` - complete functional requirements and architecture
- `docs/epyt_api.md` - comprehensive EPyT API reference
- `docs/cursor_review_project_description_docum.md` - design decisions and alternatives discussion
- `backend/README.md`, `frontend/README.md` - quick start guides
