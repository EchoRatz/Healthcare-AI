#!/usr/bin/env python3
"""
Setup Program for Ultra Fast Llama 3.1
======================================

This setup program ensures everything is ready for the ultra-fast 
Thai healthcare Q&A system with Llama 3.1
"""

import os
import sys
import subprocess
import requests
import json
import time
from pathlib import Path

class UltraFastSetup:
    def __init__(self):
        self.success = True
        self.issues = []
        
    def print_header(self):
        """Print setup header"""
        print("⚡ Ultra Fast Llama 3.1 Setup")
        print("=" * 40)
        print("🎯 Setting up 10-minute healthcare Q&A system")
        print()
    
    def check_python_version(self):
        """Check Python version"""
        print("🐍 Checking Python version...")
        version = sys.version_info
        
        if version.major == 3 and version.minor >= 8:
            print(f"  ✅ Python {version.major}.{version.minor}.{version.micro}")
            return True
        else:
            print(f"  ❌ Python {version.major}.{version.minor}.{version.micro} (need 3.8+)")
            self.issues.append("Python 3.8+ required")
            return False
    
    def check_packages(self):
        """Check required Python packages"""
        print("📦 Checking Python packages...")
        
        required_packages = {
            'requests': 'requests>=2.25.0',
            'numpy': 'numpy>=1.20.0'
        }
        
        missing = []
        
        for package, install_name in required_packages.items():
            try:
                __import__(package)
                print(f"  ✅ {package}")
            except ImportError:
                print(f"  ❌ {package} (missing)")
                missing.append(install_name)
        
        if missing:
            print(f"\n💡 Installing missing packages...")
            try:
                cmd = [sys.executable, '-m', 'pip', 'install'] + missing
                subprocess.run(cmd, check=True, capture_output=True)
                print("  ✅ Packages installed successfully")
            except subprocess.CalledProcessError as e:
                print(f"  ❌ Failed to install packages: {e}")
                self.issues.append("Could not install required packages")
                return False
        
        return True
    
    def check_ollama_service(self):
        """Check if Ollama service is running"""
        print("🤖 Checking Ollama service...")
        
        try:
            response = requests.get('http://localhost:11434/api/version', timeout=3)
            if response.status_code == 200:
                version_info = response.json()
                print(f"  ✅ Ollama running (version: {version_info.get('version', 'unknown')})")
                return True
            else:
                print(f"  ❌ Ollama service error (status: {response.status_code})")
                self.issues.append("Ollama service not responding")
                return False
        except requests.exceptions.RequestException:
            print("  ❌ Ollama service not running")
            print("  💡 Start with: ollama serve")
            self.issues.append("Ollama service not running")
            return False
    
    def check_llama31_models(self):
        """Check available Llama 3.1 models"""
        print("🦙 Checking Llama 3.1 models...")
        
        try:
            response = requests.get('http://localhost:11434/api/tags', timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                llama31_models = []
                
                for model in models:
                    model_name = model.get('name', '')
                    if 'llama3.1' in model_name.lower():
                        size = model.get('size', 0)
                        size_gb = size / (1024**3) if size > 0 else 0
                        llama31_models.append((model_name, size_gb))
                
                if llama31_models:
                    print(f"  ✅ Found {len(llama31_models)} Llama 3.1 model(s):")
                    for name, size in llama31_models:
                        if '70b' in name.lower():
                            quality = "🏆 Excellent quality, slower"
                        elif '8b' in name.lower():
                            quality = "⚡ Good quality, faster"
                        else:
                            quality = "📊 Standard quality"
                        
                        print(f"    • {name} ({size:.1f}GB) - {quality}")
                    
                    # Recommend best model
                    best_model = max(llama31_models, key=lambda x: x[1])  # Largest model
                    print(f"  💡 Recommended: {best_model[0]}")
                    return True, best_model[0]
                else:
                    print("  ❌ No Llama 3.1 models found")
                    print("  💡 Install with: ollama pull llama3.1:8b")
                    self.issues.append("No Llama 3.1 models available")
                    return False, None
            else:
                print("  ❌ Could not check models")
                self.issues.append("Could not check available models")
                return False, None
                
        except requests.exceptions.RequestException:
            print("  ❌ Could not connect to Ollama")
            self.issues.append("Could not connect to Ollama service")
            return False, None
    
    def check_data_files(self):
        """Check required data files"""
        print("📁 Checking data files...")
        
        required_files = [
            'Healthcare-AI-Refactored/src/infrastructure/test.csv',
            'Healthcare-AI-Refactored/src/infrastructure/results_doc/direct_extraction_corrected.txt',
            'Healthcare-AI-Refactored/src/infrastructure/results_doc2/direct_extraction_corrected.txt',
            'Healthcare-AI-Refactored/src/infrastructure/results_doc3/direct_extraction_corrected.txt'
        ]
        
        all_found = True
        
        for file_path in required_files:
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                if 'test.csv' in file_path:
                    # Count lines in test.csv
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = sum(1 for _ in f) - 1  # Subtract header
                    print(f"  ✅ test.csv ({lines} questions)")
                else:
                    print(f"  ✅ {os.path.basename(file_path)} ({size//1024}KB)")
            else:
                print(f"  ❌ {file_path} (missing)")
                self.issues.append(f"Missing data file: {file_path}")
                all_found = False
        
        return all_found
    
    def check_main_script(self):
        """Check if main script exists"""
        print("🚀 Checking main script...")
        
        if os.path.exists('ultra_fast_llama31.py'):
            size = os.path.getsize('ultra_fast_llama31.py')
            print(f"  ✅ ultra_fast_llama31.py ({size//1024}KB)")
            return True
        else:
            print("  ❌ ultra_fast_llama31.py (missing)")
            self.issues.append("Main script missing")
            return False
    
    def test_system(self, recommended_model):
        """Test the system with a quick question"""
        if not recommended_model:
            return False
            
        print("🧪 Testing system...")
        
        try:
            # Quick test prompt
            test_prompt = """คุณเป็นผู้เชี่ยวชาญด้านสุขภาพไทย

คำถาม: ระบบประกันสุขภาพแห่งชาติคืออะไร?

ตอบสั้นๆ:"""

            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': recommended_model,
                    'prompt': test_prompt,
                    'stream': False,
                    'options': {
                        'temperature': 0.1,
                        'num_predict': 50
                    }
                },
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get('response', '').strip()
                if answer and len(answer) > 10:
                    print(f"  ✅ System test passed")
                    print(f"    Test response: {answer[:60]}...")
                    return True
                else:
                    print("  ❌ System test failed (empty response)")
                    return False
            else:
                print(f"  ❌ System test failed (HTTP {response.status_code})")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"  ❌ System test failed: {str(e)[:50]}...")
            return False
    
    def run_setup(self):
        """Run complete setup check"""
        self.print_header()
        
        # Run all checks
        checks = [
            ("Python Version", self.check_python_version),
            ("Python Packages", self.check_packages),
            ("Ollama Service", self.check_ollama_service),
            ("Data Files", self.check_data_files),
            ("Main Script", self.check_main_script),
        ]
        
        results = {}
        for name, check_func in checks:
            results[name] = check_func()
            print()
        
        # Special handling for model check
        model_ok, recommended_model = self.check_llama31_models()
        results["Llama 3.1 Models"] = model_ok
        print()
        
        # Test system if everything looks good
        if all(results.values()) and recommended_model:
            results["System Test"] = self.test_system(recommended_model)
            print()
        
        # Summary
        self.print_summary(results, recommended_model)
        
        return all(results.values())
    
    def print_summary(self, results, recommended_model):
        """Print setup summary"""
        print("📊 Setup Summary")
        print("-" * 20)
        
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        
        for name, status in results.items():
            status_icon = "✅" if status else "❌"
            print(f"  {status_icon} {name}")
        
        print(f"\n🎯 Status: {passed}/{total} checks passed")
        
        if passed == total:
            print("\n🎉 SETUP COMPLETE!")
            print("🚀 Ready to run: python ultra_fast_llama31.py")
            
            if recommended_model:
                if '70b' in recommended_model.lower():
                    print("⏱️  Expected time: 12-18 minutes (high quality)")
                    print("🎯 Expected accuracy: ~90-95%")
                else:
                    print("⏱️  Expected time: 8-12 minutes (good speed)")
                    print("🎯 Expected accuracy: ~85-90%")
                
                print(f"🤖 Using model: {recommended_model}")
        else:
            print("\n⚠️  SETUP INCOMPLETE")
            print("🔧 Issues to fix:")
            for issue in self.issues:
                print(f"  • {issue}")
            
            print("\n💡 Common solutions:")
            if "Ollama service not running" in str(self.issues):
                print("  • Start Ollama: ollama serve")
            if "No Llama 3.1 models" in str(self.issues):
                print("  • Install model: ollama pull llama3.1:8b")
            if "Missing data file" in str(self.issues):
                print("  • Check Healthcare-AI-Refactored directory structure")
    
    def print_installation_guide(self):
        """Print installation guide for missing components"""
        print("\n📋 Installation Guide")
        print("-" * 25)
        print("1. Install Ollama:")
        print("   • Visit: https://ollama.ai")
        print("   • Download and install for your OS")
        print("   • Run: ollama serve")
        print()
        print("2. Install Llama 3.1:")
        print("   • Fast version: ollama pull llama3.1:8b")
        print("   • High quality: ollama pull llama3.1:70b")
        print()
        print("3. Verify setup:")
        print("   • Run: python setup_ultra_fast.py")

def main():
    """Main setup function"""
    setup = UltraFastSetup()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--install-guide':
        setup.print_installation_guide()
        return
    
    success = setup.run_setup()
    
    if not success:
        print("\n💡 Run with --install-guide for detailed installation steps")
        sys.exit(1)
    else:
        print("\n🎯 System ready for ultra-fast processing!")

if __name__ == "__main__":
    main()