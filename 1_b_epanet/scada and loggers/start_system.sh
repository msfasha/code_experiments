#!/bin/bash

# Water Network Monitoring System Startup Script
# This script starts both the FastAPI backend and Streamlit frontend

echo "🚀 Starting Water Network Monitoring System..."

# Check if we're in the right directory
if [ ! -f "frontend/streamlit_app.py" ]; then
    echo "❌ Error: frontend/streamlit_app.py not found. Please run this script from the project root directory."
    exit 1
fi

# Check if backend directory exists
if [ ! -d "backend" ]; then
    echo "❌ Error: backend directory not found. Please run this script from the project root directory."
    exit 1
fi

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Check if ports are available
echo "🔍 Checking port availability..."

for port in 8000 8501; do
    if check_port $port; then
        echo "⚠️  Warning: Port $port is already in use."
        # Using fuser as it's more direct for this task
        PIDS=$(fuser $port/tcp 2>/dev/null)
        echo "   Processes on port $port: $PIDS"
        read -p "   Do you want to kill these processes? [y/N] " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "   Killing processes on port $port..."
            fuser -k $port/tcp
            sleep 1 # Give a moment for the port to be released
            echo "   Processes killed."
        else
            echo "   Skipping. The application might fail to start."
        fi
    fi
done


# Start backend
echo "🔧 Starting FastAPI backend..."
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Error: Virtual environment not found. Please run setup first:"
    echo "   cd backend"
    echo "   python -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment and start backend
source venv/bin/activate
echo "✅ Virtual environment activated"

# Start backend in background
echo "🚀 Starting FastAPI backend on port 8000..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Check if backend started successfully
if ! check_port 8000; then
    echo "❌ Error: Backend failed to start on port 8000"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo "✅ Backend started successfully (PID: $BACKEND_PID)"

# Go back to project root
cd ..

# Start frontend
echo "🎨 Starting Streamlit frontend..."
echo "🚀 Starting Streamlit frontend on port 8501..."

# Start Streamlit
streamlit run frontend/streamlit_app.py --server.port 8501 --server.headless true &
FRONTEND_PID=$!

# Wait a moment for frontend to start
sleep 3

# Check if frontend started successfully
if ! check_port 8501; then
    echo "❌ Error: Frontend failed to start on port 8501"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 1
fi

echo "✅ Frontend started successfully (PID: $FRONTEND_PID)"

# Display system information
echo ""
echo "🎉 Water Network Monitoring System is running!"
echo ""
echo "📊 System Information:"
echo "   Backend API:  http://localhost:8000"
echo "   Frontend UI:  http://localhost:8501"
echo "   API Docs:     http://localhost:8000/docs"
echo ""
echo "🔧 Process IDs:"
echo "   Backend PID:  $BACKEND_PID"
echo "   Frontend PID: $FRONTEND_PID"
echo ""
echo "🛑 To stop the system:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo "   or press Ctrl+C"
echo ""

# Function to handle cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping Water Network Monitoring System..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    echo "✅ System stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Keep script running
echo "⏳ System is running. Press Ctrl+C to stop..."
wait
