#!/usr/bin/env python3
"""
Integration Test Script for Water Network Monitoring System
Tests the connection between Streamlit frontend and FastAPI backend
"""

import requests
import time
import sys
import subprocess
import os
from typing import Dict, Any, Optional

# Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:8501"
TIMEOUT = 10

def test_backend_connection() -> bool:
    """Test if FastAPI backend is running and responding"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=TIMEOUT)
        if response.status_code == 200:
            print("✅ Backend connection successful")
            return True
        else:
            print(f"❌ Backend returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend connection failed: {e}")
        return False

def test_frontend_connection() -> bool:
    """Test if Streamlit frontend is running and responding"""
    try:
        response = requests.get(f"{FRONTEND_URL}", timeout=TIMEOUT)
        if response.status_code == 200:
            print("✅ Frontend connection successful")
            return True
        else:
            print(f"❌ Frontend returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Frontend connection failed: {e}")
        return False

def test_api_endpoints() -> bool:
    """Test key API endpoints"""
    endpoints = [
        "/health",
        "/api/status",
        "/api/network/status",
        "/api/scada/status",
        "/api/monitoring/monitoring/status"
    ]
    
    all_passed = True
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=TIMEOUT)
            if response.status_code == 200:
                print(f"✅ {endpoint} - OK")
            else:
                print(f"❌ {endpoint} - Status: {response.status_code}")
                all_passed = False
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint} - Error: {e}")
            all_passed = False
    
    return all_passed

def test_network_upload() -> bool:
    """Test network file upload functionality"""
    try:
        # Check if we have a sample network file
        sample_files = ["networks/Net1.inp", "networks/Net2.inp"]
        test_file = None
        
        for file_path in sample_files:
            if os.path.exists(file_path):
                test_file = file_path
                break
        
        if not test_file:
            print("⚠️  No sample network files found for upload test")
            return True
        
        # Test upload
        with open(test_file, 'rb') as f:
            files = {'file': (os.path.basename(test_file), f, 'application/octet-stream')}
            response = requests.post(f"{BACKEND_URL}/api/network/upload", files=files, timeout=TIMEOUT)
            
            if response.status_code == 200:
                print(f"✅ Network upload test successful: {os.path.basename(test_file)}")
                return True
            else:
                print(f"❌ Network upload failed: Status {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Network upload test failed: {e}")
        return False

def test_database_connection() -> bool:
    """Test database connectivity through API"""
    try:
        # Test by getting network status (requires database)
        response = requests.get(f"{BACKEND_URL}/api/network/status", timeout=TIMEOUT)
        if response.status_code == 200:
            print("✅ Database connection successful")
            return True
        else:
            print(f"❌ Database connection failed: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False

def run_integration_tests() -> bool:
    """Run all integration tests"""
    print("🧪 Running Water Network Monitoring System Integration Tests")
    print("=" * 60)
    
    tests = [
        ("Backend Connection", test_backend_connection),
        ("Frontend Connection", test_frontend_connection),
        ("API Endpoints", test_api_endpoints),
        ("Database Connection", test_database_connection),
        ("Network Upload", test_network_upload)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing: {test_name}")
        print("-" * 30)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n📈 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready for use.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the system configuration.")
        return False

def check_system_requirements() -> bool:
    """Check if system requirements are met"""
    print("🔍 Checking system requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    else:
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Check if required packages are available
    required_packages = ['requests', 'streamlit', 'fastapi', 'uvicorn']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} not found")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Please install missing packages:")
        print("pip install -r requirements.txt")
        print("pip install -r frontend/requirements_streamlit.txt")
        return False
    
    return True

def main():
    """Main test function"""
    print("🚀 Water Network Monitoring System - Integration Test")
    print("=" * 60)
    
    # Check requirements first
    if not check_system_requirements():
        print("\n❌ System requirements not met. Please fix issues and try again.")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("🧪 Starting Integration Tests")
    print("=" * 60)
    
    # Wait a moment for services to be ready
    print("⏳ Waiting for services to be ready...")
    time.sleep(2)
    
    # Run tests
    success = run_integration_tests()
    
    if success:
        print("\n🎉 Integration tests completed successfully!")
        print("\n📋 Next steps:")
        print("1. Open http://localhost:8501 in your browser")
        print("2. Upload a network file (networks/Net1.inp)")
        print("3. Start SCADA simulation")
        print("4. Begin monitoring")
        sys.exit(0)
    else:
        print("\n❌ Integration tests failed!")
        print("\n🔧 Troubleshooting:")
        print("1. Ensure backend is running: cd backend && uvicorn main:app --reload")
        print("2. Ensure frontend is running: streamlit run frontend/streamlit_app.py")
        print("3. Check port availability: lsof -i :8000 and lsof -i :8501")
        sys.exit(1)

if __name__ == "__main__":
    main()
