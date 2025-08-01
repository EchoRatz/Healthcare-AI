"""
Multi-Threaded CSV Processing Example - Demonstrates 30-thread processing.
"""

import time
import pandas as pd
import numpy as np
from pathlib import Path
import threading
from multi_thread_csv_manager import MultiThreadCSVManager


def create_test_files(num_files: int = 50, rows_per_file: int = 10000):
    """Create multiple test CSV files for multi-threaded processing."""
    
    csv_input_dir = Path("data/csv_input")
    csv_input_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Creating {num_files} test files with {rows_per_file} rows each...")
    
    for i in range(num_files):
        # Create different types of data
        if i % 5 == 0:
            # QA data
            data = {
                'question': [f'Question {j} for file {i}?' for j in range(rows_per_file)],
                'answer': [f'Answer {j} for file {i}.' for j in range(rows_per_file)]
            }
            filename = f"qa_file_{i:03d}.csv"
        elif i % 5 == 1:
            # Patient data
            data = {
                'patient_id': [f'P{i:03d}_{j:06d}' for j in range(rows_per_file)],
                'name': [f'Patient {j}' for j in range(rows_per_file)],
                'age': np.random.randint(18, 80, rows_per_file),
                'diagnosis': np.random.choice(['Hypertension', 'Diabetes', 'Asthma'], rows_per_file)
            }
            filename = f"patient_file_{i:03d}.csv"
        elif i % 5 == 2:
            # Medical data
            data = {
                'record_id': [f'M{i:03d}_{j:06d}' for j in range(rows_per_file)],
                'symptom': np.random.choice(['Fever', 'Cough', 'Headache', 'Fatigue'], rows_per_file),
                'severity': np.random.choice(['Mild', 'Moderate', 'Severe'], rows_per_file),
                'treatment': np.random.choice(['Rest', 'Medication', 'Surgery'], rows_per_file)
            }
            filename = f"medical_file_{i:03d}.csv"
        elif i % 5 == 3:
            # Large data with many columns
            data = {}
            for col in range(20):
                if col < 5:
                    data[f'num_col_{col}'] = np.random.randn(rows_per_file)
                elif col < 10:
                    data[f'int_col_{col}'] = np.random.randint(0, 1000, rows_per_file)
                else:
                    data[f'str_col_{col}'] = [f'value_{j}_{col}' for j in range(rows_per_file)]
            filename = f"large_file_{i:03d}.csv"
        else:
            # ML data
            data = {
                'age': np.random.randint(18, 80, rows_per_file),
                'income': np.random.randint(20000, 150000, rows_per_file),
                'education': np.random.choice(['High School', 'Bachelor', 'Master', 'PhD'], rows_per_file),
                'health_score': np.random.randn(rows_per_file) * 10 + 70,
                'risk_factor': np.random.choice(['Low', 'Medium', 'High'], rows_per_file)
            }
            filename = f"ml_file_{i:03d}.csv"
        
        # Create DataFrame and save
        df = pd.DataFrame(data)
        file_path = csv_input_dir / filename
        df.to_csv(file_path, index=False)
        
        if (i + 1) % 10 == 0:
            print(f"Created {i + 1}/{num_files} files")
    
    print(f"Created {num_files} test files successfully")
    return num_files


def monitor_manager(manager: MultiThreadCSVManager, duration: int = 60):
    """Monitor the multi-threaded manager for a specified duration."""
    
    print(f"\nMonitoring manager for {duration} seconds...")
    print("=" * 80)
    
    start_time = time.time()
    last_stats = None
    
    while time.time() - start_time < duration and manager.running:
        stats = manager.get_stats()
        
        # Calculate rates
        if last_stats:
            time_diff = time.time() - start_time
            files_processed_diff = stats["total_files_processed"] - last_stats["total_files_processed"]
            files_failed_diff = stats["total_files_failed"] - last_stats["total_files_failed"]
            
            if time_diff > 0:
                processing_rate = files_processed_diff / time_diff
                failure_rate = files_failed_diff / time_diff
            else:
                processing_rate = failure_rate = 0
        else:
            processing_rate = failure_rate = 0
        
        # Display current status
        print(f"\nTime: {time.time() - start_time:.1f}s")
        print(f"Files Processed: {stats['total_files_processed']} (+{stats['total_files_processed'] - (last_stats['total_files_processed'] if last_stats else 0)})")
        print(f"Files Failed: {stats['total_files_failed']} (+{stats['total_files_failed'] - (last_stats['total_files_failed'] if last_stats else 0)})")
        print(f"Queue Size: {stats['queue_size']}")
        print(f"Processing Rate: {processing_rate:.2f} files/sec")
        print(f"Active Threads: {stats['active_threads']}/{stats['max_threads']}")
        print(f"Idle Threads: {stats['idle_threads']}")
        print(f"Error Threads: {stats['error_threads']}")
        
        if stats.get('gpu_memory_used_gb'):
            print(f"GPU Memory Used: {stats['gpu_memory_used_gb']:.2f} GB")
        
        last_stats = stats.copy()
        time.sleep(2)
    
    print("=" * 80)


def benchmark_thread_counts():
    """Benchmark different thread counts."""
    
    print("\n=== Thread Count Benchmark ===")
    
    thread_counts = [5, 10, 20, 30]
    results = {}
    
    for thread_count in thread_counts:
        print(f"\nTesting with {thread_count} threads...")
        
        # Create test files
        num_files = 20
        create_test_files(num_files, 5000)
        
        # Create manager
        manager = MultiThreadCSVManager(
            max_threads=thread_count,
            watch_directory="data/csv_input",
            processed_directory="data/csv_processed",
            error_directory="data/csv_errors",
            use_cuda=True,
            batch_size=5000
        )
        
        # Start processing
        start_time = time.time()
        manager.start()
        
        # Monitor until all files processed
        while manager.running:
            stats = manager.get_stats()
            if stats["total_files_processed"] + stats["total_files_failed"] >= num_files:
                break
            time.sleep(1)
        
        # Stop and calculate results
        processing_time = time.time() - start_time
        manager.stop()
        
        results[thread_count] = {
            "processing_time": processing_time,
            "files_processed": stats["total_files_processed"],
            "files_failed": stats["total_files_failed"],
            "processing_rate": stats["total_files_processed"] / processing_time if processing_time > 0 else 0
        }
        
        print(f"  Processing time: {processing_time:.2f}s")
        print(f"  Processing rate: {results[thread_count]['processing_rate']:.2f} files/sec")
        
        # Cleanup
        import shutil
        for dir_name in ["data/csv_input", "data/csv_processed", "data/csv_errors"]:
            if Path(dir_name).exists():
                shutil.rmtree(dir_name)
    
    # Display benchmark results
    print("\n=== Benchmark Results ===")
    print("Threads | Time (s) | Rate (files/sec) | Efficiency")
    print("-" * 50)
    
    for thread_count in thread_counts:
        result = results[thread_count]
        efficiency = result["processing_rate"] / thread_count
        print(f"{thread_count:7d} | {result['processing_time']:8.2f} | {result['processing_rate']:14.2f} | {efficiency:9.2f}")


def stress_test():
    """Stress test with many files and high load."""
    
    print("\n=== Stress Test ===")
    
    # Create many small files
    num_files = 100
    create_test_files(num_files, 1000)
    
    # Create manager with 30 threads
    manager = MultiThreadCSVManager(
        max_threads=30,
        watch_directory="data/csv_input",
        processed_directory="data/csv_processed",
        error_directory="data/csv_errors",
        use_cuda=True,
        batch_size=1000,
        max_queue_size=200
    )
    
    # Start processing
    manager.start()
    
    # Monitor for 30 seconds
    monitor_manager(manager, 30)
    
    # Get final stats
    final_stats = manager.get_stats()
    manager.stop()
    
    print(f"\nStress Test Results:")
    print(f"Total files processed: {final_stats['total_files_processed']}")
    print(f"Total files failed: {final_stats['total_files_failed']}")
    print(f"Peak thread count: {final_stats['peak_thread_count']}")
    print(f"Average processing time: {final_stats.get('average_processing_time', 0):.2f}s")


def main():
    """Main example function."""
    
    print("=== Multi-Threaded CSV Processing Example ===\n")
    
    # Check CUDA availability
    try:
        import cupy as cp
        gpu_count = cp.cuda.runtime.getDeviceCount()
        print(f"CUDA GPUs available: {gpu_count}")
        
        if gpu_count > 0:
            gpu_memory = cp.cuda.runtime.memGetInfo()
            print(f"GPU Memory: {gpu_memory[0] / 1024**3:.2f} GB free, "
                  f"{gpu_memory[1] / 1024**3:.2f} GB total")
        else:
            print("No CUDA GPUs found")
            
    except ImportError:
        print("CUDA libraries not available")
    except Exception as e:
        print(f"Error checking CUDA: {e}")
    
    # Create directories
    for dir_name in ["data/csv_input", "data/csv_processed", "data/csv_errors"]:
        Path(dir_name).mkdir(parents=True, exist_ok=True)
    
    try:
        # Run different tests
        print("\n1. Basic Multi-Threaded Test")
        basic_test()
        
        print("\n2. Thread Count Benchmark")
        benchmark_thread_counts()
        
        print("\n3. Stress Test")
        stress_test()
        
        print("\n=== All tests completed successfully ===")
        
    except Exception as e:
        print(f"Error during testing: {e}")
    
    finally:
        # Cleanup
        print("\nCleaning up...")
        import shutil
        for dir_name in ["data/csv_input", "data/csv_processed", "data/csv_errors"]:
            if Path(dir_name).exists():
                shutil.rmtree(dir_name)


def basic_test():
    """Basic multi-threaded test."""
    
    print("Creating test files...")
    num_files = 30
    create_test_files(num_files, 5000)
    
    print("Starting 30-thread manager...")
    manager = MultiThreadCSVManager(
        max_threads=30,
        watch_directory="data/csv_input",
        processed_directory="data/csv_processed",
        error_directory="data/csv_errors",
        use_cuda=True,
        batch_size=5000
    )
    
    manager.start()
    
    # Monitor until all files processed
    while manager.running:
        stats = manager.get_stats()
        if stats["total_files_processed"] + stats["total_files_failed"] >= num_files:
            break
        time.sleep(1)
    
    manager.stop()
    
    print(f"Basic test completed:")
    print(f"Files processed: {stats['total_files_processed']}")
    print(f"Files failed: {stats['total_files_failed']}")
    
    # Cleanup
    import shutil
    for dir_name in ["data/csv_input", "data/csv_processed", "data/csv_errors"]:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)


if __name__ == "__main__":
    main() 