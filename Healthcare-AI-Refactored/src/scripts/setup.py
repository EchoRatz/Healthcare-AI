"""Setup script for Healthcare AI."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.config.Config import AppConfig
from shared.logging.LoggerMixin import get_logger


def main():
    """Setup the Healthcare AI system."""
    print("🏥 Healthcare-AI Setup")
    print("=" * 50)
    
    logger = get_logger(__name__)
    
    try:
        # Create default configuration
        config = AppConfig.from_file("config/app.json")
        
        # Create necessary directories
        directories = [
            "data/documents",
            "data/vectors", 
            "data/csv_input",
            "data/csv_processed",
            "data/csv_errors",
            "logs"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            print(f"✅ Created directory: {directory}")
        
        # Save configuration
        config.save_to_file("config/app.json")
        print(f"✅ Saved configuration: config/app.json")
        
        print("\n🎉 Setup completed successfully!")
        print("\n📝 Next steps:")
        print("1. Start Ollama: ollama serve")
        print("2. Pull model: ollama pull llama2")
        print("3. Run system: python src/scripts/run.py")
        
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        print(f"❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()