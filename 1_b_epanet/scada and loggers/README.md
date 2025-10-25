# 💧 Water Network Monitoring System

## Real-Time SCADA and EPANET Monitoring with Streamlit + FastAPI

A production-ready digital twin for water distribution networks, featuring real-time monitoring, anomaly detection, and SCADA simulation capabilities.

---

## 🎯 System Overview

This system provides **real-time monitoring** of water distribution networks by:

- **Monitoring network status** - Real-time monitoring of water network health
- **Detecting anomalies** - Identifying leaks, pressure drops, flow issues, and other problems
- **Providing forecasting** - Predicting future network behavior and demand patterns
- **Alerting operators** - Notifying when problems occur or are predicted
- **Simulating SCADA data** - Generating realistic sensor data for testing and development
- **Running hydraulic analysis** - Using EPANET for physics-based network modeling

### **Core Value Proposition**
The system's main value is **anomaly detection and monitoring**. It compares what sensors measure vs what EPANET predicts to identify problems in the water network.

---

## 🏗️ Architecture

### **Hybrid Streamlit + FastAPI Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                Streamlit Frontend (Port 8501)               │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐   │
│  │  Dashboard  │  Network    │   SCADA     │ Monitoring  │   │
│  │   Tab       │   Tab       │    Tab      │    Tab      │   │
│  └─────────────┴─────────────┴─────────────┴─────────────┘   │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP/REST API Calls
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
│              SQLite/PostgreSQL Database                     │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐   │
│  │   Network    │   SCADA     │ Monitoring  │  Anomalies  │   │
│  │   Data       │  Readings   │  Results    │    Log      │   │
│  └─────────────┴─────────────┴─────────────┴─────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### **Technology Stack**

#### **Frontend (Streamlit)**
- **Streamlit** - Modern Python web framework
- **Matplotlib** - Network visualization and plotting
- **Plotly** - Interactive charts and graphs
- **Pandas** - Data processing and analysis
- **Requests** - HTTP client for API communication
- **Caching** - Built-in data caching with @st.cache_data

#### **Backend (FastAPI)**
- **FastAPI** - Modern, high-performance web framework
- **EPyT** - EPANET hydraulic simulations
- **SQLAlchemy** - Database ORM
- **PostgreSQL/SQLite** - Time-series data storage
- **WebSockets** - Real-time data streaming
- **Pydantic** - Data validation
- **asyncio** - Asynchronous operations

---

## 🚀 Quick Start

### **Prerequisites**
- Python 3.8+
- Node.js (for development tools)
- Git

### **Installation**

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd water-network-monitoring
   ```

2. **Setup Backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Setup Frontend**
   ```bash
   # Install Streamlit requirements
   pip install -r frontend/requirements_streamlit.txt
   ```

4. **Initialize Database**
   ```bash
   cd backend
   python init_db.py
   ```

### **Running the System**

1. **Start Backend**
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Start Frontend**
   ```bash
   streamlit run frontend/streamlit_app.py --server.port 8501
   ```

3. **Access the System**
   - **Frontend**: http://localhost:8501
   - **Backend API**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs

---

## 📊 System Features

### **🌐 Network Management**
- Upload EPANET .inp files
- Network topology visualization
- Component statistics and information
- Interactive network plots

### **📊 SCADA Simulation**
- Realistic sensor data generation
- Time-of-day demand patterns
- Configurable noise and variation
- Real-time data streaming

### **🔍 Monitoring Engine**
- Baseline establishment from original design
- Real-time anomaly detection
- Pressure, flow, and level monitoring
- Configurable thresholds

### **📈 Analytics & Reporting**
- Data export (CSV, JSON)
- Performance metrics
- System statistics
- Historical data analysis

---

## 🔧 Configuration

### **Environment Variables**
```bash
# Database
DATABASE_URL=sqlite:///./water_network_monitoring.db

# API Settings
API_HOST=0.0.0.0
API_PORT=8000

# Streamlit Settings
STREAMLIT_PORT=8501
STREAMLIT_HOST=localhost
```

### **Network Files**
Place your EPANET .inp files in the `networks/` directory:
```
networks/
├── Net1.inp
├── Net2.inp
└── your_network.inp
```

---

## 🧪 Testing

### **Test with Sample Networks**
1. Upload `networks/Net1.inp` (included)
2. Establish baseline
3. Start SCADA simulation
4. Monitor for anomalies

### **API Testing**
```bash
# Health check
curl http://localhost:8000/health

# Network status
curl http://localhost:8000/api/network/status

# SCADA readings
curl http://localhost:8000/api/scada/readings
```

---

## 📚 Documentation

- **Technical Documentation**: `docs/CLAUDE.md`
- **Streamlit Analysis**: `docs/Streamlit_Conversion_Analysis.md`
- **Architecture Analysis**: `docs/FastAPI_vs_Streamlit_Architecture_Analysis.md`
- **API Documentation**: http://localhost:8000/docs

---

## 🛠️ Development

### **Project Structure**
```
├── backend/                 # FastAPI backend
│   ├── api/                 # API endpoints
│   ├── services/            # Business logic
│   ├── models/              # Database models
│   └── main.py              # FastAPI application
├── frontend/
│   ├── streamlit_app.py     # Streamlit frontend
│   ├── requirements_streamlit.txt
│   └── logo.png
├── networks/                # Sample network files
├── docs/                    # Documentation
└── requirements*.txt       # Dependencies
```

### **Adding New Features**
1. **Backend**: Add API endpoints in `backend/api/`
2. **Frontend**: Add new tabs or functionality in `frontend/streamlit_app.py`
3. **Database**: Update models in `backend/models/`

---

## 🚨 Troubleshooting

### **Common Issues**

1. **Backend not starting**
   ```bash
   # Check if port 8000 is available
   lsof -i :8000
   ```

2. **Frontend not connecting**
   ```bash
   # Verify backend is running
   curl http://localhost:8000/health
   ```

3. **Database errors**
   ```bash
   # Reinitialize database
   cd backend
   python init_db.py
   ```

### **Performance Issues**
- **Large networks**: Use smaller networks for testing
- **Memory usage**: Monitor with `htop` or `top`
- **API timeouts**: Increase timeout values in Streamlit app

---

## 📈 Performance

### **System Requirements**
- **CPU**: 2+ cores recommended
- **RAM**: 4GB+ recommended
- **Storage**: 1GB+ for database and logs
- **Network**: Local network for development

### **Optimization**
- **Caching**: Streamlit automatically caches API responses
- **Database**: Use PostgreSQL for production
- **Monitoring**: Monitor system resources during operation

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🆘 Support

For support and questions:
- **Documentation**: Check `docs/` directory
- **Issues**: Create GitHub issues
- **API Docs**: http://localhost:8000/docs

---

## 🎯 Roadmap

### **Phase 1: Core Features** ✅
- [x] Network file upload and visualization
- [x] SCADA simulation
- [x] Monitoring engine
- [x] Streamlit frontend

### **Phase 2: Enhanced Features** 🔄
- [ ] Real-time WebSocket updates
- [ ] Advanced analytics
- [ ] Mobile responsiveness
- [ ] User authentication

### **Phase 3: Production Features** ⏳
- [ ] Docker containerization
- [ ] Kubernetes deployment
- [ ] Advanced security
- [ ] Multi-tenant support

---

**Built with ❤️ for water network monitoring and analysis**
