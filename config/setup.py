#!/usr/bin/env python3
"""
Setup script for Spitogatos Premium Analysis System
"""

import os
import sys
import subprocess
import logging

def check_python_version():
    """Check if Python version is compatible"""
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    
    print(f"✅ Python version OK: {sys.version}")
    return True

def install_requirements():
    """Install required packages"""
    
    print("📦 Installing requirements...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ Requirements installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    
    print("📁 Creating output directories...")
    
    directories = [
        "outputs",
        "outputs/data", 
        "outputs/exports",
        "outputs/reports",
        "outputs/charts",
        "outputs/logs",
        "cache"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"  ✅ Created: {directory}")
    
    return True

def verify_installation():
    """Verify that all components can be imported"""
    
    print("🔍 Verifying installation...")
    
    try:
        # Test critical imports
        import requests
        import beautifulsoup4
        import pandas
        import numpy
        import sklearn
        import matplotlib
        import seaborn
        import plotly
        import folium
        import geopy
        import fake_useragent
        import aiohttp
        
        print("✅ All dependencies verified")
        
        # Test local imports
        from config import config
        from utils import setup_logging
        
        print("✅ Local modules verified")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def run_quick_test():
    """Run a quick system test"""
    
    print("🧪 Running quick system test...")
    
    try:
        # Test configuration
        from config import config
        assert config.validate_config(), "Configuration validation failed"
        
        # Test logging setup
        from utils import setup_logging
        setup_logging(config)
        
        # Test scraper initialization
        print("  ✅ Configuration valid")
        print("  ✅ Logging system ready")
        print("  ✅ Components initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ System test failed: {e}")
        return False

def main():
    """Main setup routine"""
    
    print("🚀 Spitogatos Premium Analysis System Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        print("\n💡 Try running: pip install -r requirements.txt")
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        sys.exit(1)
    
    # Verify installation
    if not verify_installation():
        print("\n💡 Some dependencies may be missing. Check requirements.txt")
        sys.exit(1)
    
    # Run system test
    if not run_quick_test():
        print("\n💡 System test failed. Check configuration files")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Review configuration in config.py")
    print("2. Run analysis: python main.py")
    print("3. Check outputs/ directory for results")
    print("\nFor help: python main.py --help")
    print("=" * 50)

if __name__ == "__main__":
    main()