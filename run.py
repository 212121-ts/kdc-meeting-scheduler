#!/usr/bin/env python3
"""
Simple launcher script for the Meeting Poll App
Double-click this file to start the server!
"""

import sys
import subprocess
import webbrowser
import time
from threading import Timer

def install_requirements():
    """Install required packages"""
    try:
        import flask
        print("✅ Flask is already installed")
    except ImportError:
        print("📦 Installing Flask...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "flask"])
        print("✅ Flask installed successfully")

def open_browser():
    """Open browser after a short delay"""
    webbrowser.open('http://localhost:5000')

def main():
    print("=" * 50)
    print("🗳️  KDC MEETING SCHEDULER")
    print("=" * 50)
    
    # Install requirements
    install_requirements()
    
    # Import and run the main app
    try:
        # Set up browser opening
        Timer(2.0, open_browser).start()
        
        # Import and run the main application
        import app
        
        # Force recreate templates with KDC branding
        import os, shutil
        if os.path.exists('templates'):
            shutil.rmtree('templates')
            print("🔄 Updating to KDC branding...")
        
        app.create_templates()
        app.init_db()
        
        print("\n🚀 Starting KDC Meeting Scheduler...")
        print("🌐 Your branded app will open at: http://localhost:5000")
        print("🛑 Press Ctrl+C to stop the server")
        print("=" * 50)
        
        app.app.run(debug=False, host='127.0.0.1', port=5000)
        
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Thanks for using KDC Meeting Scheduler!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure 'app.py' is in the same folder as this script.")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()