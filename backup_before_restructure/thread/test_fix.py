"""
Test script to verify the logger initialization fix.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_cuda_thread():
    """Test CUDA thread initialization."""
    print("Testing CUDA thread initialization...")
    
    try:
        from cuda_csv_thread import CUDACSVThread
        
        # Create CUDA thread
        thread = CUDACSVThread(
            watch_directory="data/csv_input",
            processed_directory="data/csv_processed",
            error_directory="data/csv_errors",
            use_cuda=True
        )
        
        print("✓ CUDA thread created successfully")
        
        # Test basic functionality
        stats = thread.get_stats()
        print(f"✓ Thread stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"✗ CUDA thread error: {e}")
        return False

def test_file_based_thread():
    """Test file-based thread initialization."""
    print("\nTesting file-based thread initialization...")
    
    try:
        from file_based_thread import FileBasedThreadManager
        
        # Create file-based thread
        thread = FileBasedThreadManager(
            thread_id="test_thread_001",
            base_directory="test_thread_data",
            watch_directory="data/csv_input",
            processed_directory="data/csv_processed",
            error_directory="data/csv_errors",
            use_cuda=True
        )
        
        print("✓ File-based thread created successfully")
        
        # Test basic functionality
        stats = thread.get_stats()
        print(f"✓ Thread stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"✗ File-based thread error: {e}")
        return False

def test_basic_thread():
    """Test basic thread initialization."""
    print("\nTesting basic thread initialization...")
    
    try:
        from thread import CSVFileThread
        
        # Create basic thread
        thread = CSVFileThread(
            watch_directory="data/csv_input",
            processed_directory="data/csv_processed",
            error_directory="data/csv_errors"
        )
        
        print("✓ Basic thread created successfully")
        
        # Test basic functionality
        stats = thread.get_stats()
        print(f"✓ Thread stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"✗ Basic thread error: {e}")
        return False

def main():
    """Main test function."""
    
    print("=== Testing Thread Initialization Fix ===\n")
    
    # Create test directories
    for dir_name in ["data/csv_input", "data/csv_processed", "data/csv_errors", "test_thread_data"]:
        Path(dir_name).mkdir(parents=True, exist_ok=True)
    
    # Run tests
    tests = [
        ("Basic Thread", test_basic_thread),
        ("CUDA Thread", test_cuda_thread),
        ("File-Based Thread", test_file_based_thread)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n=== Test Results ===")
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("✓ All tests passed! The logger initialization fix is working.")
    else:
        print("✗ Some tests failed. Please check the errors above.")
    
    # Cleanup
    import shutil
    for dir_name in ["data/csv_input", "data/csv_processed", "data/csv_errors", "test_thread_data"]:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)

if __name__ == "__main__":
    main() 