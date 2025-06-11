#!/usr/bin/env python3
"""
Startup script for HF DABBY system
Handles both development and production modes
"""

import os
import sys
import subprocess
import argparse
import signal
import time
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import redis
        import fastapi
        import uvicorn
        import celery
        print("✓ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def start_redis():
    """Start Redis server"""
    try:
        # Check if Redis is already running
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✓ Redis is already running")
        return True
    except:
        print("Starting Redis server...")
        # On Windows, you might need to adjust this command
        if os.name == 'nt':  # Windows
            print("Please start Redis manually on Windows")
            return False
        else:
            subprocess.Popen(['redis-server'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(2)
            return True

def start_fastapi(port=8000, workers=1):
    """Start FastAPI application"""
    print(f"Starting FastAPI application on port {port}...")
    cmd = [
        sys.executable, "-m", "uvicorn",
        "fastapi_app:app",
        "--host", "0.0.0.0",
        "--port", str(port),
        "--workers", str(workers),
        "--reload" if workers == 1 else ""
    ]
    cmd = [arg for arg in cmd if arg]  # Remove empty strings
    
    return subprocess.Popen(cmd)

def start_celery_worker():
    """Start Celery worker"""
    print("Starting Celery worker...")
    cmd = [
        sys.executable, "-m", "celery",
        "-A", "celery_config",
        "worker",
        "--loglevel=info",
        "--concurrency=2"
    ]
    return subprocess.Popen(cmd)

def start_celery_beat():
    """Start Celery beat scheduler"""
    print("Starting Celery beat scheduler...")
    cmd = [
        sys.executable, "-m", "celery",
        "-A", "celery_config",
        "beat",
        "--loglevel=info"
    ]
    return subprocess.Popen(cmd)

def start_gradio():
    """Start Gradio interface"""
    print("Starting Gradio interface...")
    return subprocess.Popen([sys.executable, "main.py"])

def main():
    parser = argparse.ArgumentParser(description="HF DABBY Startup Script")
    parser.add_argument("--mode", choices=["dev", "prod"], default="dev",
                       help="Run in development or production mode")
    parser.add_argument("--services", nargs="+", 
                       choices=["fastapi", "celery", "beat", "gradio", "all"],
                       default=["all"],
                       help="Services to start")
    parser.add_argument("--fastapi-port", type=int, default=8000,
                       help="Port for FastAPI application")
    parser.add_argument("--workers", type=int, default=1,
                       help="Number of FastAPI workers")
    
    args = parser.parse_args()
    
    print("🚀 Starting HF DABBY system...")
    print(f"Mode: {args.mode}")
    print(f"Services: {args.services}")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check if Redis is available
    if not start_redis():
        print("⚠️  Redis is not available. Some features may not work.")
    
    processes = []
    
    try:
        # Start services based on arguments
        if "all" in args.services or "fastapi" in args.services:
            workers = args.workers if args.mode == "prod" else 1
            process = start_fastapi(args.fastapi_port, workers)
            processes.append(("FastAPI", process))
        
        if "all" in args.services or "celery" in args.services:
            process = start_celery_worker()
            processes.append(("Celery Worker", process))
        
        if "all" in args.services or "beat" in args.services:
            process = start_celery_beat()
            processes.append(("Celery Beat", process))
        
        if "all" in args.services or "gradio" in args.services:
            process = start_gradio()
            processes.append(("Gradio", process))
        
        print("\n✅ All services started successfully!")
        print("\nService URLs:")
        if "all" in args.services or "fastapi" in args.services:
            print(f"  📡 FastAPI: http://localhost:{args.fastapi_port}")
            print(f"  📚 API Docs: http://localhost:{args.fastapi_port}/docs")
        if "all" in args.services or "gradio" in args.services:
            print(f"  🎨 Gradio UI: http://localhost:7860")
        
        print("\nPress Ctrl+C to stop all services...")
        
        # Wait for interrupt
        while True:
            time.sleep(1)
            # Check if any process has died
            for name, process in processes:
                if process.poll() is not None:
                    print(f"⚠️  {name} process has stopped")
    
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
        
        # Terminate all processes
        for name, process in processes:
            print(f"Stopping {name}...")
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print(f"Force killing {name}...")
                process.kill()
        
        print("✅ All services stopped")

if __name__ == "__main__":
    main()
