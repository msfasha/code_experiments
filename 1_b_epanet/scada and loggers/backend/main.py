from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn

# Import API routers
from api.network import router as network_router
from api.scada import router as scada_router

# Import database models to ensure they're registered
from models.database import Base, engine
from models.tables import SCADAReading, SCADASimulatorConfig, MonitoringResult, NetworkComponent

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Water Network Monitoring API",
    description="Real-time SCADA and EPANET monitoring system",
    version="1.0.0"
)

# CORS configuration for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint - basic health check"""
    return {
        "message": "Water Network Monitoring API",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/status")
async def api_status():
    """API status endpoint"""
    return {
        "api": "Water Network Monitoring",
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "redoc": "/redoc",
            "network": "/api/network",
            "scada": "/api/scada"
        },
        "timestamp": datetime.now().isoformat()
    }

# Include API routers
app.include_router(network_router, prefix="/api/network", tags=["Network"])
app.include_router(scada_router, prefix="/api/scada", tags=["SCADA"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
