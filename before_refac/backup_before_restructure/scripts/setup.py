#!/usr/bin/env python3
"""
Setup Script
Handles initial setup and dependency installation.
"""

import subprocess
import sys
from pathlib import Path


def install_dependencies():
    """Install required dependencies."""
    requirements = [
        "faiss-cpu",
        "sentence-transformers", 
        "numpy",
        "requests"
    ]
    
    print("Installing dependencies...")
    for req in requirements:
        print(f"Installing {req}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", req])
        except subprocess.CalledProcessError as e:
            print(f"Failed to install {req}: {e}")
            return False
    
    print("Dependencies installed successfully!")
    return True


def setup_directories():
    """Create necessary directories."""
    dirs = ["data", "logs"]
    
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"Created directory: {dir_name}")


def create_sample_data():
    """Create sample data file."""
    sample_data = """Learning is an important process for self-development
Good health comes from regular exercise and nutritious eating
Happiness is something that comes from having a peaceful mind
Education is an important foundation for national development
Technology helps make human life more convenient
Regular exercise helps strengthen physical and mental health
Reading books opens up perspectives and increases knowledge
A warm family is an important foundation of a good society"""
    
    data_file = Path("data/sample_data.txt")
    data_file.write_text(sample_data, encoding="utf-8")
    print(f"Created sample data: {data_file}")


def main():
    """Main setup function."""
    print("Healthcare-AI Setup")
    print("=" * 30)
    
    try:
        setup_directories()
        
        if install_dependencies():
            create_sample_data()
            
            print("\nSetup completed successfully!")
            print("\nTo run the application:")
            print("python scripts/run.py")
        else:
            print("Setup failed during dependency installation")
            
    except Exception as e:
        print(f"Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
