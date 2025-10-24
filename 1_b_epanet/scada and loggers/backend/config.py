"""
Configuration settings for the Water Network Monitoring System
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Database settings
DATABASE_URL = f"sqlite:///{BASE_DIR}/data/monitoring.db"

# API settings
API_V1_STR = "/api"
PROJECT_NAME = "Water Network Monitoring API"

# File upload settings
UPLOAD_DIR = BASE_DIR / "temp"
UPLOAD_DIR.mkdir(exist_ok=True)

# Data directories
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# SCADA simulation settings
DEFAULT_SIMULATION_INTERVAL = 2  # seconds
DEFAULT_TIME_WINDOW = 5  # seconds tolerance

# Anomaly detection settings
DEFAULT_PRESSURE_THRESHOLD = 10.0  # percentage deviation
DEFAULT_FLOW_THRESHOLD = 15.0  # percentage deviation

# Network file settings
ALLOWED_EXTENSIONS = [".inp"]
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Development settings
DEBUG = True
RELOAD = True
