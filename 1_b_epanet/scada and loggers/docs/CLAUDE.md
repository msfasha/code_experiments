# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Real-Time Dynamic Water Network Monitoring System (RTDWMS) - A production-ready digital twin for water distribution networks in Jordan. The system simulates SCADA behavior, runs real-time hydraulic computations using EPANET (via EPyT), detects anomalies, and provides an interactive React dashboard.

## Architecture

### Full-Stack Structure
- **Backend**: FastAPI (Python) - REST API + WebSockets, runs on port 8000
- **Frontend**: React 18 + TypeScript + Vite, runs on port 5173 (dev)
- **Database**: SQLite at `data/monitoring.db` (production will use PostgreSQL)
- **Hydraulics Engine**: EPyT (EPANET-Python Toolkit)
- **Network Files**: EPANET `.inp` files in `networks/` directory

### Backend Architecture (`backend/`)
```
backend/
├── main.py              # FastAPI app initialization, CORS, router registration
├── config.py            # System-wide configuration (paths, thresholds, settings)
├── init_db.py           # Database initialization utility
├── api/                 # REST API endpoints
│   ├── network.py       # Network upload, info, status endpoints
│   └── scada.py         # SCADA simulator control endpoints
├── models/              # Database layer
│   ├── database.py      # SQLAlchemy engine and session management
│   └── tables.py        # Database tables: SCADAReading, SCADASimulatorConfig,
│                        #                 MonitoringResult, NetworkComponent
└── services/            # Business logic
    ├── network_loader.py    # EPyT network loading and parsing (singleton)
    ├── network_state.py     # Global network state management
    └── scada_simulator.py   # Async SCADA data generator (singleton)
```

### Frontend Architecture (`frontend/`)
```
frontend/src/
├── main.tsx             # App entry point
├── App.tsx              # Main application with routing
├── api/                 # API client layer
│   ├── client.ts        # Axios HTTP client with baseURL
│   ├── network.ts       # Network API calls
│   └── scada.ts         # SCADA API calls
└── components/          # React components
    ├── Dashboard.tsx        # Main monitoring dashboard
    ├── NetworkUpload.tsx    # File upload interface
    ├── NetworkInfo.tsx      # Network summary display
    └── NetworkViewer.tsx    # Plotly.js network visualization
```

### Key Design Patterns

**Singleton Pattern**: Both `NetworkLoader` and `SCADASimulator` use singleton pattern via global module instances (`network_state.network_loader`, `scada_simulator`)

**Global State**: `network_state` module provides shared access to the loaded EPANET network across all services

**Async Background Tasks**: SCADA simulator runs as an asyncio background task generating sensor data at configurable intervals

**Database Session Management**: Uses SQLAlchemy with `SessionLocal()` context managers for thread-safe database access

## Common Development Commands

### Backend (Python)

**Environment Setup:**
```bash
cd backend
python -m venv venv  # or use existing venv in parent dir
source venv/bin/activate  # or: venv/bin/activate (Linux/Mac)
pip install -r requirements.txt
```

**Run Backend Server:**
```bash
cd backend
python main.py
# Server runs on http://localhost:8000
# API docs at http://localhost:8000/docs
```

**Initialize Database:**
```bash
cd backend
python init_db.py
```

**Database Location:**
- SQLite database: `data/monitoring.db`
- Created automatically on first run if missing
- Tables: scada_readings, scada_simulator_config, monitoring_results, network_components

### Frontend (React + TypeScript)

**Environment Setup:**
```bash
cd frontend
npm install
```

**Run Frontend Dev Server:**
```bash
cd frontend
npm run dev
# Server runs on http://localhost:5173
```

**Build for Production:**
```bash
cd frontend
npm run build
# Output in frontend/dist/
```

**Lint Frontend:**
```bash
cd frontend
npm run lint
```

**Preview Production Build:**
```bash
cd frontend
npm run preview
```

### Full Stack Development

**Start Both Services (in separate terminals):**
```bash
# Terminal 1 - Backend
cd backend && python main.py

# Terminal 2 - Frontend
cd frontend && npm run dev
```

## Critical Technical Details

### EPyT Network Loading
- **Network files**: Place `.inp` files in `networks/` directory (Net1.inp, Net2.inp, Net3.inp available)
- **Singleton instance**: `network_state.network_loader` is shared across all services
- **Loading process**: Upload via API → saved to `temp/` → loaded into EPyT → network data extracted
- **Global state check**: Always verify `network_state.is_loaded` before running simulations

### SCADA Simulator Behavior
- **Singleton instance**: `scada_simulator` (global in `scada_simulator.py`)
- **Data generation**: Generates synthetic pressures (junctions), flows (pumps), levels (tanks)
- **Update interval**: Configurable (default 30 seconds)
- **State persistence**: Simulator running state stored in database (`scada_simulator_config.is_running`)
- **Async loop**: Runs in background using `asyncio.create_task()`
- **Start requirement**: Network must be loaded before starting simulator

### Database Tables
1. **scada_readings**: Timestamped sensor data (pressure/flow/level readings)
2. **scada_simulator_config**: Simulator state and configuration (running status, intervals, variation %)
3. **monitoring_results**: Anomaly detection results (baseline vs current, deviations)
4. **network_components**: Parsed network topology (junctions, pipes, pumps, tanks)

### Time Synchronization
- **SCADA data**: Generated synchronously for all sensors at once
- **Tolerance window**: ±5 seconds (MVP), will be ±30 seconds in production
- **Missing data**: Last-known values used for missing sensors
- **Stale data**: Flagged if >5 minutes old

### API Endpoints Reference
- `POST /api/network/upload` - Upload .inp network file
- `GET /api/network/info` - Get loaded network summary
- `GET /api/network/status` - Check if network is loaded
- `POST /api/scada/start` - Start SCADA simulator
- `POST /api/scada/stop` - Stop SCADA simulator
- `GET /api/scada/status` - Get simulator status
- `GET /api/scada/readings` - Get latest SCADA readings

### Configuration Files
- **Backend config**: `backend/config.py` - Database path, upload directory, thresholds
- **Frontend API client**: `frontend/src/api/client.ts` - Backend base URL
- **CORS**: Configured in `backend/main.py` for localhost:5173

## Development Workflow

### Adding New Network Types
1. Add network parsing logic in `backend/services/network_loader.py`
2. Update database schema in `backend/models/tables.py` if needed
3. Add visualization support in `frontend/components/NetworkViewer.tsx`

### Adding New Sensor Types
1. Update `sensor_type` enum in `SCADAReading` model
2. Add generation logic in `scada_simulator._generate_scada_data()`
3. Update frontend display in Dashboard component

### Anomaly Detection (Future)
- Baseline values: From initial EPANET simulation
- Detection logic: Compare real-time SCADA vs predicted EPANET values
- Thresholds: Configurable in `config.py` (default: 10% pressure, 15% flow)
- Results stored in: `monitoring_results` table

## Data Flow

```
1. User uploads .inp file (Frontend → POST /api/network/upload)
2. Backend loads network with EPyT (network_loader.load_network())
3. Network topology stored in database (network_components table)
4. User starts SCADA simulator (Frontend → POST /api/scada/start)
5. Simulator generates data every 30s (scada_simulator._simulation_loop())
6. Data stored in database (scada_readings table)
7. Frontend polls for readings (GET /api/scada/readings)
8. Dashboard displays real-time data with Plotly.js
```

## Important Notes

- **Virtual Environment**: Use `venv/` in project root (already set up) or create new one
- **Network State**: Shared globally via `network_state` module - NOT thread-local
- **Async Safety**: SCADA simulator uses asyncio, ensure async/await patterns in new code
- **Database Sessions**: Always use try/finally with SessionLocal() to prevent connection leaks
- **EPANET Files**: Must be valid EPANET 2.2 format .inp files
- **Temporary Files**: Uploaded networks stored in `temp/`, EPANET creates temporary files with pattern `en*`

## MVP Phase Focus

Current development is in MVP phase focusing on:
- Basic network loading and visualization
- Simple SCADA simulation with synthetic data
- Fundamental anomaly detection (pressure deviations)
- Functional web interface
- Local development only (no authentication yet)

Production features planned for later:
- User authentication & authorization
- PostgreSQL database migration
- Advanced anomaly detection algorithms
- Real SCADA system integration
- Demand forecasting engine
- WebSocket real-time updates
- Multi-network support
- Scalability improvements
