#!/usr/bin/env python3
"""
Product Retrieval System - Application Entry Point
"""

import os
import sys
from pathlib import Path

# Add backend to Python path
backend_dir = Path(__file__).resolve().parent / 'backend'
sys.path.insert(0, str(backend_dir))

# Import the Flask app
from app import app

if __name__ == '__main__':
    # Get configuration from environment
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    
    print("🚀 Starting Product Retrieval System...")
    print(f"   Debug: {debug}")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   URL: http://{host}:{port}")
    
    # Run the application
    app.run(debug=debug, host=host, port=port)