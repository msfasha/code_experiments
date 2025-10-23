#!/usr/bin/env python3
"""
Database initialization script
Creates all tables defined in the models
"""

from models.database import engine, Base
from models.tables import SCADAReading, SCADASimulatorConfig, MonitoringResult, NetworkComponent
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize the database by creating all tables"""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Create initial SCADA config if it doesn't exist
        from models.database import SessionLocal
        from models.tables import SCADASimulatorConfig
        
        db = SessionLocal()
        try:
            config = db.query(SCADASimulatorConfig).first()
            if not config:
                config = SCADASimulatorConfig()
                db.add(config)
                db.commit()
                logger.info("Initial SCADA configuration created")
            else:
                logger.info("SCADA configuration already exists")
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise

if __name__ == "__main__":
    init_database()
