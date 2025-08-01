#!/usr/bin/env python3
"""
FastAPI Server Startup Script
"""

import sys
from pathlib import Path
import uvicorn

# Add paths
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "src"))
sys.path.append(str(project_root))

def main():
    """Start the FastAPI server."""
    print("Starting Healthcare-AI API Server...")
    print("=" * 50)
    print("API will be available at:")
    print("• http://localhost:8000")
    print("• API docs: http://localhost:8000/docs")
    print("• Health check: http://localhost:8000/health")
    print("=" * 50)
    
    try:
        uvicorn.run(
            "src.api.app:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except Exception as e:
        print(f"Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()