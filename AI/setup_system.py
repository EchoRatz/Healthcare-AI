#!/usr/bin/env python3
"""
Setup script to prepare the Thai Healthcare Q&A system
"""

import subprocess
import sys
import os
import requests
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"   ❌ Python {version.major}.{version.minor} detected")
        print("   ⚠️  Requires Python 3.8 or higher")
        return False
    else:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True


def install_python_packages():
    """Install required Python packages"""
    print("\n📦 Installing Python packages...")
    
    packages = [
        "langchain-ollama",
        "langchain-chroma", 
        "langchain-core"
    ]
    
    for package in packages:
        try:
            print(f"   📥 Installing {package}...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"   ✅ {package} installed successfully")
            
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to install {package}")
            print(f"   Error: {e.stderr}")
            return False
    
    return True


def check_ollama_installation():
    """Check if Ollama is installed"""
    print("\n🤖 Checking Ollama installation...")
    
    try:
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ Ollama found: {result.stdout.strip()}")
            return True
        else:
            print("   ❌ Ollama not found")
            return False
            
    except FileNotFoundError:
        print("   ❌ Ollama not installed")
        return False


def install_ollama():
    """Provide instructions to install Ollama"""
    print("\n🚀 Installing Ollama...")
    print("   Please follow these steps:")
    print()
    print("   1. Go to: https://ollama.ai/")
    print("   2. Download Ollama for your operating system")
    print("   3. Install and run Ollama")
    print("   4. Come back and run this script again")
    print()
    
    response = input("   📝 Have you installed Ollama? (y/n): ").lower().strip()
    return response in ['y', 'yes']


def check_ollama_running():
    """Check if Ollama service is running"""
    print("\n🔄 Checking if Ollama is running...")
    
    try:
        response = requests.get("http://localhost:11434/api/version", timeout=5)
        if response.status_code == 200:
            print("   ✅ Ollama service is running")
            return True
        else:
            print("   ❌ Ollama service not responding")
            return False
            
    except requests.exceptions.RequestException:
        print("   ❌ Cannot connect to Ollama service")
        print("   💡 Try running: ollama serve")
        return False


def install_ollama_models():
    """Install required Ollama models"""
    print("\n📚 Installing Ollama models...")
    
    models = ["llama3.2", "mxbai-embed-large"]
    
    for model in models:
        try:
            print(f"   📥 Installing {model}...")
            result = subprocess.run(
                ["ollama", "pull", model],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode == 0:
                print(f"   ✅ {model} installed successfully")
            else:
                print(f"   ❌ Failed to install {model}")
                print(f"   Error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"   ⏰ Timeout installing {model} (this is normal for large models)")
        except Exception as e:
            print(f"   ❌ Error installing {model}: {e}")
            return False
    
    return True


def test_system():
    """Test if the system is working"""
    print("\n🧪 Testing system...")
    
    try:
        # Try importing the main components
        print("   🔧 Testing imports...")
        
        try:
            from thai_qa_processor import ThaiHealthcareQA
            print("   ✅ ThaiHealthcareQA import successful")
        except ImportError as e:
            print(f"   ❌ Import failed: {e}")
            return False
        
        # Try initializing the system
        print("   🚀 Testing system initialization...")
        try:
            qa_system = ThaiHealthcareQA()
            print("   ✅ System initialization successful")
        except Exception as e:
            print(f"   ❌ Initialization failed: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ System test failed: {e}")
        return False


def check_test_csv():
    """Check if test.csv exists"""
    print("\n📄 Checking for test.csv...")
    
    possible_paths = ["test.csv", "../test.csv", "AI/test.csv"]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"   ✅ Found: {path}")
            
            # Check file size
            size = os.path.getsize(path)
            print(f"   📊 File size: {size:,} bytes")
            
            # Count lines
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    lines = sum(1 for line in f)
                print(f"   📝 Lines: {lines}")
                
                if lines > 500:
                    print("   ✅ Appears to contain all questions")
                else:
                    print("   ⚠️  Fewer questions than expected")
                    
            except Exception as e:
                print(f"   ⚠️  Could not analyze file: {e}")
            
            return path
    
    print("   ❌ test.csv not found")
    print("   💡 Make sure test.csv is in the current directory")
    return None


def main():
    """Main setup function"""
    
    print("🎯 Thai Healthcare Q&A System Setup")
    print("=" * 60)
    print("This script will help you set up the complete system")
    print("=" * 60)
    
    # Step 1: Check Python version
    if not check_python_version():
        print("\n❌ Setup failed: Python version incompatible")
        return
    
    # Step 2: Install Python packages
    if not install_python_packages():
        print("\n❌ Setup failed: Could not install Python packages")
        print("💡 Try: pip install langchain-ollama langchain-chroma langchain-core")
        return
    
    # Step 3: Check Ollama
    ollama_installed = check_ollama_installation()
    
    if not ollama_installed:
        if not install_ollama():
            print("\n⏸️  Setup paused: Install Ollama and run this script again")
            return
        
        # Recheck after user claims to have installed
        if not check_ollama_installation():
            print("\n❌ Ollama still not found")
            return
    
    # Step 4: Check if Ollama is running
    if not check_ollama_running():
        print("\n💡 Please start Ollama service:")
        print("   Windows: Run Ollama from Start Menu")
        print("   Mac/Linux: Run 'ollama serve' in terminal")
        
        input("\n📝 Press Enter when Ollama is running...")
        
        if not check_ollama_running():
            print("\n❌ Still cannot connect to Ollama")
            return
    
    # Step 5: Install models
    if not install_ollama_models():
        print("\n⚠️  Model installation had issues, but continuing...")
    
    # Step 6: Check test.csv
    csv_path = check_test_csv()
    
    # Step 7: Test system
    if test_system():
        print("\n🎉 Setup Complete!")
        print("=" * 60)
        print("✅ All components are ready")
        print()
        print("🚀 Ready to process your test.csv!")
        print()
        print("📝 Next steps:")
        print("   python batch_test_processor.py              # Process all questions")
        print("   python quick_batch_test.py                  # Test with 5 questions")
        print("   python simple_csv_processor.py              # Demo version")
        print()
        
        if csv_path:
            response = input("🤔 Would you like to run a quick test now? (y/n): ").lower().strip()
            if response in ['y', 'yes']:
                print("\n🧪 Running quick test...")
                try:
                    subprocess.run([sys.executable, "quick_batch_test.py"])
                except Exception as e:
                    print(f"❌ Test failed: {e}")
    
    else:
        print("\n⚠️  Setup completed with issues")
        print("💡 Try running the simple processor first:")
        print("   python simple_csv_processor.py")


if __name__ == "__main__":
    main()