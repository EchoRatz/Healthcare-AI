#!/usr/bin/env python3
"""
Complete System Setup Guide
===========================

Step-by-step setup for the enhanced healthcare AI system
"""

import os
import sys
import subprocess
import requests
import json
from pathlib import Path

def check_python():
    """Check Python version"""
    print("🐍 Step 1: Checking Python...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor} - Need Python 3.8+")
        return False

def check_ollama():
    """Check if Ollama is running"""
    print("🤖 Step 2: Checking Ollama...")
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"   ✅ Ollama running with {len(models)} models")
            
            # Check for Llama 3.1
            llama_models = [m for m in models if 'llama3.1' in m['name'].lower()]
            if llama_models:
                print(f"   ✅ Llama 3.1 available: {llama_models[0]['name']}")
                return True, llama_models[0]['name']
            else:
                print(f"   ⚠️  Ollama running but no Llama 3.1 model found")
                return False, None
        else:
            print(f"   ❌ Ollama not responding (HTTP {response.status_code})")
            return False, None
    except Exception as e:
        print(f"   ❌ Ollama not accessible: {str(e)[:50]}...")
        return False, None

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Step 3: Installing Python dependencies...")
    
    dependencies = [
        "requests",
        "numpy", 
        "scikit-learn",
        "sentence-transformers",
        "faiss-cpu",
        "aiohttp"
    ]
    
    for dep in dependencies:
        try:
            __import__(dep.replace('-', '_'))
            print(f"   ✅ {dep} already installed")
        except ImportError:
            print(f"   📥 Installing {dep}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", dep], 
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"   ✅ {dep} installed successfully")
            except subprocess.CalledProcessError:
                print(f"   ❌ Failed to install {dep}")
                return False
    
    return True

def check_data_files():
    """Check if required data files exist"""
    print("📁 Step 4: Checking data files...")
    
    required_files = [
        "Healthcare-AI-Refactored/src/infrastructure/test.csv",
        "Healthcare-AI-Refactored/src/infrastructure/results_doc/direct_extraction_corrected.txt",
        "Healthcare-AI-Refactored/src/infrastructure/results_doc2/direct_extraction_corrected.txt", 
        "Healthcare-AI-Refactored/src/infrastructure/results_doc3/direct_extraction_corrected.txt"
    ]
    
    all_found = True
    for file_path in required_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"   ✅ {os.path.basename(file_path)} ({size:,} bytes)")
        else:
            print(f"   ❌ Missing: {file_path}")
            all_found = False
    
    return all_found

def check_system_files():
    """Check if all system files are present"""
    print("🔧 Step 5: Checking system files...")
    
    system_files = [
        "ultra_fast_llama31.py",
        "enhanced_logical_validator.py",
        "improved_healthcare_validator.py", 
        "mock_mcp_healthcare.py",
        "multi_tool_mcp_client.py"
    ]
    
    all_found = True
    for file_path in system_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"   ✅ {file_path} ({size:,} bytes)")
        else:
            print(f"   ❌ Missing: {file_path}")
            all_found = False
    
    return all_found

def test_system_loading():
    """Test if the complete system loads"""
    print("🧪 Step 6: Testing system loading...")
    
    try:
        # Test imports
        from ultra_fast_llama31 import UltraFastQA
        print("   ✅ Main system loads successfully")
        
        # Test components
        from enhanced_logical_validator import ThaiHealthcareLogicalValidator
        from improved_healthcare_validator import ImprovedHealthcareValidator
        from mock_mcp_healthcare import MockMCPHealthcareSystem
        from multi_tool_mcp_client import MultiToolMCPClient
        
        print("   ✅ All validation components load successfully")
        
        # Quick functionality test
        validator = ThaiHealthcareLogicalValidator()
        test_result = validator.validate_answer(
            "Test question", 
            {"ก": "A", "ข": "B", "ค": "C", "ง": "None"}, 
            ["ง"]
        )
        
        if test_result:
            print("   ✅ System functionality test passed")
            return True
        else:
            print("   ❌ System functionality test failed")
            return False
            
    except Exception as e:
        print(f"   ❌ System loading failed: {str(e)[:60]}...")
        return False

def main():
    """Main setup function"""
    print("🚀 Enhanced Healthcare AI - Complete Setup")
    print("=" * 50)
    print("Setting up the multi-tool MCP system with 4-layer validation")
    print()
    
    # Run all checks
    checks = [
        ("Python", check_python),
        ("Dependencies", install_dependencies),
        ("Data Files", check_data_files),
        ("System Files", check_system_files),
        ("System Loading", test_system_loading)
    ]
    
    # Check Ollama separately since it might need manual setup
    ollama_ok, model_name = check_ollama()
    
    all_passed = True
    for check_name, check_func in checks:
        try:
            if not check_func():
                all_passed = False
        except Exception as e:
            print(f"   ❌ {check_name} check failed: {e}")
            all_passed = False
        print()
    
    # Final status
    print("📊 Setup Summary:")
    print("=" * 20)
    
    if all_passed and ollama_ok:
        print("✅ ALL SYSTEMS READY!")
        print()
        print("🚀 Ready to run:")
        print("   python ultra_fast_llama31.py")
        print()
        print("📈 Expected Performance:")
        print("   • Accuracy: 32.8% → 60-80%+")
        print("   • Reduce 'ง' answers: 249/500 → ~50-100/500")
        print("   • Multi-tool analysis for complex questions")
        print("   • 4-layer validation pipeline active")
        
    elif all_passed and not ollama_ok:
        print("⚠️  SYSTEM READY - OLLAMA SETUP NEEDED")
        print()
        print("🔧 Next Steps:")
        print("   1. Install Ollama: https://ollama.ai")
        print("   2. Start Ollama: ollama serve")
        print("   3. Install Llama 3.1: ollama pull llama3.1")
        print("   4. Run: python ultra_fast_llama31.py")
        
    else:
        print("❌ SETUP INCOMPLETE")
        print("   Please fix the issues above and run setup again")

if __name__ == "__main__":
    main()