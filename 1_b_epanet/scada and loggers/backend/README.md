# Water Network Monitoring Backend

FastAPI backend for real-time water network monitoring with EPANET integration.

## Quick Start

1. **Install dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

2. **Run the server:**
```bash
python main.py
```

3. **Test the API:**
- Visit: http://localhost:8000
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## API Endpoints

- `GET /` - Root endpoint with basic info
- `GET /health` - Health check
- `GET /api/status` - API status and available endpoints
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

## Project Structure

```
backend/
├── main.py              # FastAPI application
├── config.py            # Configuration settings
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Next Steps

- Add network upload endpoints
- Integrate EPyT for EPANET processing
- Add database models
- Implement SCADA simulation
