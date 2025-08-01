#!/usr/bin/env python3
"""
Install MCP Dependencies
========================

Installs required packages for MCP healthcare client integration
"""

import subprocess
import sys

def install_package(package):
    """Install a Python package"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    """Install MCP dependencies"""
    print("🔧 Installing MCP Healthcare Client Dependencies")
    print("=" * 50)
    
    required_packages = [
        "aiohttp>=3.8.0",
        "asyncio",
    ]
    
    success_count = 0
    for package in required_packages:
        print(f"📦 Installing {package}...")
        if install_package(package):
            print(f"  ✅ {package} installed successfully")
            success_count += 1
        else:
            print(f"  ❌ Failed to install {package}")
    
    print(f"\n📊 Installation Summary:")
    print(f"  ✅ Successful: {success_count}/{len(required_packages)}")
    
    if success_count == len(required_packages):
        print(f"\n🎉 All dependencies installed!")
        print(f"🚀 Ready to use MCP healthcare validation")
        print(f"💡 Run: python ultra_fast_llama31.py")
    else:
        print(f"\n⚠️  Some packages failed to install")
        print(f"💡 Try running: pip install aiohttp")

if __name__ == "__main__":
    main()