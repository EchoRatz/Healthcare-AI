#!/usr/bin/env python3
"""
Setup script for Enhanced Thai Healthcare Q&A System
Installs required packages and tests system capabilities
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def check_gpu():
    """Check if GPU is available for PyTorch"""
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False

def setup_enhanced_system():
    """Setup the enhanced system with all capabilities"""
    print("🚀 Setting up Enhanced Thai Healthcare Q&A System")
    print("=" * 60)
    
    # Core packages (always needed)
    core_packages = [
        "numpy>=1.21.0",
        "scikit-learn>=1.0.0", 
        "pandas>=1.3.0"
    ]
    
    # Enhanced AI packages
    enhanced_packages = [
        "sentence-transformers>=2.2.0",
        "faiss-cpu>=1.7.0",  # Use faiss-gpu if you have GPU
        "transformers>=4.20.0",
        "torch>=2.0.0"
    ]
    
    # Optional packages
    optional_packages = [
        "openai>=1.0.0",  # For GPT integration
        "langchain>=0.1.0",  # For advanced RAG
        "chromadb>=0.4.0"  # Alternative vector store
    ]
    
    print("📦 Installing core packages...")
    for package in core_packages:
        print(f"Installing {package}...", end=" ")
        if install_package(package):
            print("✅")
        else:
            print("❌")
    
    print("\n🧠 Installing AI enhancement packages...")
    for package in enhanced_packages:
        print(f"Installing {package}...", end=" ")
        if install_package(package):
            print("✅")
        else:
            print("❌ (will use fallback)")
    
    print("\n🔧 Installing optional packages...")
    for package in optional_packages:
        print(f"Installing {package}...", end=" ")
        if install_package(package):
            print("✅")
        else:
            print("❌ (skipped)")
    
    # Check capabilities
    print("\n🔍 Checking system capabilities...")
    
    capabilities = {
        "Basic TF-IDF": True,  # Always available
        "Sentence Transformers": False,
        "FAISS Vector Search": False,
        "OpenAI Integration": False,
        "GPU Acceleration": False
    }
    
    try:
        import sentence_transformers
        capabilities["Sentence Transformers"] = True
    except ImportError:
        pass
    
    try:
        import faiss
        capabilities["FAISS Vector Search"] = True
    except ImportError:
        pass
    
    try:
        import openai
        capabilities["OpenAI Integration"] = True
    except ImportError:
        pass
    
    capabilities["GPU Acceleration"] = check_gpu()
    
    print("\n📊 System Capabilities:")
    for capability, available in capabilities.items():
        status = "✅" if available else "❌"
        print(f"  {status} {capability}")
    
    # Recommendations
    print("\n💡 Recommendations:")
    
    if not capabilities["Sentence Transformers"]:
        print("  ⚠️  Install sentence-transformers for better accuracy")
        print("     pip install sentence-transformers")
    
    if not capabilities["FAISS Vector Search"]:
        print("  ⚠️  Install faiss-cpu for faster search")
        print("     pip install faiss-cpu")
    
    if capabilities["GPU Acceleration"]:
        print("  🚀 GPU detected! Consider installing faiss-gpu for better performance")
        print("     pip uninstall faiss-cpu && pip install faiss-gpu")
    
    if not capabilities["OpenAI Integration"]:
        print("  💡 For highest accuracy, set OPENAI_API_KEY environment variable")
        print("     export OPENAI_API_KEY='your-key-here'")
    
    # Test basic functionality
    print("\n🧪 Testing basic functionality...")
    try:
        from enhanced_thai_qa_system import EnhancedThaiHealthcareQA
        
        # Test with minimal files (if they exist)
        test_files = [
            'Healthcare-AI-Refactored/src/infrastructure/results_doc/direct_extraction_corrected.txt'
        ]
        
        if all(os.path.exists(f) for f in test_files):
            qa_system = EnhancedThaiHealthcareQA(test_files)
            print("✅ System initialized successfully")
            
            # Test question parsing
            test_question = "ทดสอบระบบ ก. ตัวเลือก 1 ข. ตัวเลือก 2 ค. ตัวเลือก 3 ง. ตัวเลือก 4"
            question, choices = qa_system.parse_question(test_question)
            if choices:
                print("✅ Question parsing works")
            else:
                print("❌ Question parsing failed")
        else:
            print("⚠️  Knowledge files not found - system ready but untested")
    
    except Exception as e:
        print(f"❌ System test failed: {e}")
    
    print("\n🎉 Setup completed!")
    print("\nNext steps:")
    print("1. Run: python enhanced_thai_qa_system.py")
    print("2. Or test with: python test_enhanced_system.py")

if __name__ == "__main__":
    setup_enhanced_system()