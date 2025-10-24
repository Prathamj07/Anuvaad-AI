#!/usr/bin/env python3
"""
Anuvaad AI Startup Script
Starts both backend and frontend servers with a single command
"""

import os
import sys
import subprocess
import signal
import time
from pathlib import Path

def check_env_file():
    """Check if .env file exists"""
    if not os.path.exists('.env'):
        print("❌ Error: .env file not found!")
        print("\n📝 Please create a .env file with your API keys.")
        print("   You can copy .env.example and fill in your keys:")
        print("   cp .env.example .env")
        print("\n   Then edit .env and add your API keys.")
        sys.exit(1)
    print("✅ .env file found")

def check_dependencies():
    """Check if required dependencies are installed"""
    print("\n🔍 Checking dependencies...")
    
    # Check Node.js
    try:
        subprocess.run(['node', '--version'], check=True, capture_output=True)
        print("✅ Node.js is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Node.js is not installed. Please install it from https://nodejs.org/")
        sys.exit(1)
    
    # Check if frontend dependencies are installed
    if not os.path.exists('frontend/node_modules'):
        print("\n📦 Installing frontend dependencies...")
        try:
            subprocess.run(['npm', 'install'], cwd='frontend', check=True)
            print("✅ Frontend dependencies installed")
        except subprocess.CalledProcessError:
            print("❌ Failed to install frontend dependencies")
            sys.exit(1)
    else:
        print("✅ Frontend dependencies are installed")

def start_servers():
    """Start both backend and frontend servers"""
    processes = []
    
    try:
        print("\n" + "="*60)
        print("🚀 Starting Anuvaad AI...")
        print("="*60)
        
        # Start backend
        print("\n📡 Starting Backend Server (Flask)...")
        backend_process = subprocess.Popen(
            [sys.executable, 'backend.py'],
            shell=True
        )
        processes.append(backend_process)
        time.sleep(2)  # Give backend time to start
        print("✅ Backend started on http://localhost:5001")
        
        # Start frontend
        print("\n🎨 Starting Frontend Server (Vite)...")
        frontend_process = subprocess.Popen(
            ['npm', 'run', 'dev', '--', '--host', '0.0.0.0', '--port', '5000'],
            cwd=os.path.join(os.getcwd(), 'frontend'),
            shell=True
        )

        processes.append(frontend_process)
        time.sleep(3)  # Give frontend time to start
        
        print("\n" + "="*60)
        print("✅ Anuvaad AI is now running!")
        print("="*60)
        print("\n🌐 Open your browser and go to:")
        print("   👉 http://localhost:5000")
        print("\n📊 Backend API running at:")
        print("   👉 http://localhost:5001")
        print("\n⏹️  Press Ctrl+C to stop both servers")
        print("="*60 + "\n")
        
        # Keep the script running and show output
        while True:
            time.sleep(1)
            
            # Check if any process has died
            for proc in processes:
                if proc.poll() is not None:
                    print(f"\n❌ A server process stopped unexpectedly")
                    raise KeyboardInterrupt
                    
    except KeyboardInterrupt:
        print("\n\n⏹️  Stopping servers...")
        for proc in processes:
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except:
                proc.kill()
        print("✅ All servers stopped")
        print("\nThank you for using Anuvaad AI! 👋\n")
        sys.exit(0)

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║              🎬 ANUVAAD AI STARTUP SCRIPT 🎬             ║
    ║                                                           ║
    ║           AI-Powered Video Dubbing Platform               ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    check_env_file()
    check_dependencies()
    start_servers()
