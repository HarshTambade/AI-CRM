#!/usr/bin/env python3
"""
Start script for AI-Powered CRM System
This script starts both backend and frontend servers
"""

import os
import sys
import subprocess
import platform
import time
import threading
import signal
import atexit

# Global variables to track processes
backend_process = None
frontend_process = None

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print("\n🛑 Shutting down servers...")
    cleanup()
    sys.exit(0)

def cleanup():
    """Clean up processes"""
    global backend_process, frontend_process
    
    if backend_process:
        backend_process.terminate()
        backend_process.wait()
        print("✅ Backend server stopped")
    
    if frontend_process:
        frontend_process.terminate()
        frontend_process.wait()
        print("✅ Frontend server stopped")

def run_backend():
    """Run the backend server"""
    global backend_process
    
    print("🚀 Starting backend server...")
    
    # Activate virtual environment and start server
    if platform.system() == "Windows":
        cmd = "venv\\Scripts\\uvicorn main:app --reload --host 0.0.0.0 --port 8000"
    else:
        cmd = "venv/bin/uvicorn main:app --reload --host 0.0.0.0 --port 8000"
    
    backend_process = subprocess.Popen(
        cmd,
        shell=True,
        cwd="backend",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    
    # Wait for backend to start
    time.sleep(3)
    
    if backend_process.poll() is None:
        print("✅ Backend server started on http://localhost:8000")
    else:
        print("❌ Failed to start backend server")
        return False
    
    return True

def run_frontend():
    """Run the frontend server"""
    global frontend_process
    
    print("🚀 Starting frontend server...")
    
    frontend_process = subprocess.Popen(
        "npm run dev",
        shell=True,
        cwd="frontend",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    
    # Wait for frontend to start
    time.sleep(5)
    
    if frontend_process.poll() is None:
        print("✅ Frontend server started on http://localhost:3000")
    else:
        print("❌ Failed to start frontend server")
        return False
    
    return True

def check_dependencies():
    """Check if dependencies are installed"""
    print("📋 Checking dependencies...")
    
    # Check backend
    if not os.path.exists("backend/venv"):
        print("❌ Backend virtual environment not found. Run setup.py first.")
        return False
    
    # Check frontend
    if not os.path.exists("frontend/node_modules"):
        print("❌ Frontend dependencies not found. Run setup.py first.")
        return False
    
    print("✅ Dependencies found")
    return True

def main():
    """Main function"""
    print("🚀 AI-Powered CRM System")
    print("=" * 50)
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    atexit.register(cleanup)
    
    # Check dependencies
    if not check_dependencies():
        print("\n💡 Run 'python setup.py' to set up the environment first.")
        return
    
    # Start backend
    if not run_backend():
        return
    
    # Start frontend
    if not run_frontend():
        cleanup()
        return
    
    print("\n🎉 Both servers are running!")
    print("\n🌐 Access the application:")
    print("  Frontend: http://localhost:3000")
    print("  Backend API: http://localhost:8000")
    print("  API Docs: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop both servers")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if backend_process and backend_process.poll() is not None:
                print("❌ Backend server stopped unexpectedly")
                break
            
            if frontend_process and frontend_process.poll() is not None:
                print("❌ Frontend server stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Received interrupt signal")
    finally:
        cleanup()

if __name__ == "__main__":
    main() 