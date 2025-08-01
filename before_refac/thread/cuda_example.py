"""
CUDA CSV Thread Example - Demonstrates GPU-accelerated CSV processing.
"""

import time
import pandas as pd
import numpy as np
from pathlib import Path
from cuda_csv_thread import CUDACSVThread


def create_large_sample_csv():
    """Create a large sample CSV file for testing GPU acceleration."""
    
    csv_input_dir = Path("data/csv_input")
    csv_input_dir.mkdir(parents=True, exist_ok=True)
    
    # Create large dataset for GPU testing
    print("Creating large sample CSV for GPU testing...")
    
    # Generate large dataset
    num_rows = 100000
    num_cols = 20
    
    # Create random data
    data = {}
    for i in range(num_cols):
        if i < 5:
            # Numeric columns
            data[f'num_col_{i}'] = np.random.randn(num_rows)
        elif i < 10:
            # Integer columns
            data[f'int_col_{i}'] = np.random.randint(0, 1000, num_rows)
        else:
            # String columns
            data[f'str_col_{i}'] = [f'value_{j}_{i}' for j in range(num_rows)]
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Save as CSV
    large_file = csv_input_dir / "large_sample.csv"
    df.to_csv(large_file, index=False)
    
    print(f"Created large CSV file: {large_file}")
    print(f"Size: {large_file.stat().st_size / 1024 / 1024:.2f} MB")
    print(f"Rows: {len(df)}, Columns: {len(df.columns)}")
    
    return large_file


def create_ml_sample_csv():
    """Create ML-ready sample CSV for preprocessing testing."""
    
    csv_input_dir = Path("data/csv_input")
    csv_input_dir.mkdir(parents=True, exist_ok=True)
    
    # Create ML dataset
    num_samples = 50000
    
    data = {
        'age': np.random.randint(18, 80, num_samples),
        'income': np.random.randint(20000, 150000, num_samples),
        'education': np.random.choice(['High School', 'Bachelor', 'Master', 'PhD'], num_samples),
        'occupation': np.random.choice(['Engineer', 'Doctor', 'Teacher', 'Manager', 'Student'], num_samples),
        'health_score': np.random.randn(num_samples) * 10 + 70,
        'risk_factor': np.random.choice(['Low', 'Medium', 'High'], num_samples),
        'symptoms_count': np.random.randint(0, 10, num_samples),
        'medication_count': np.random.randint(0, 5, num_samples)
    }
    
    # Add some missing values
    for col in ['income', 'health_score']:
        mask = np.random.random(num_samples) < 0.1  # 10% missing values
        data[col][mask] = np.nan
    
    df = pd.DataFrame(data)
    
    # Save as CSV
    ml_file = csv_input_dir / "ml_sample.csv"
    df.to_csv(ml_file, index=False)
    
    print(f"Created ML CSV file: {ml_file}")
    print(f"Rows: {len(df)}, Columns: {len(df.columns)}")
    
    return ml_file


def benchmark_cuda_vs_cpu():
    """Benchmark CUDA vs CPU processing."""
    
    print("\n=== CUDA vs CPU Benchmark ===")
    
    # Create test file
    test_file = create_large_sample_csv()
    
    # Test CPU processing
    print("\n1. Testing CPU processing...")
    cpu_thread = CUDACSVThread(
        watch_directory="data/csv_input",
        processed_directory="data/csv_processed",
        error_directory="data/csv_errors",
        use_cuda=False,
        polling_interval=0.1
    )
    
    start_time = time.time()
    cpu_thread.start()
    
    # Wait for processing
    time.sleep(5)
    
    cpu_time = time.time() - start_time
    cpu_stats = cpu_thread.get_stats()
    
    cpu_thread.stop()
    cpu_thread.join()
    
    # Test CUDA processing
    print("\n2. Testing CUDA processing...")
    cuda_thread = CUDACSVThread(
        watch_directory="data/csv_input",
        processed_directory="data/csv_processed",
        error_directory="data/csv_errors",
        use_cuda=True,
        polling_interval=0.1
    )
    
    start_time = time.time()
    cuda_thread.start()
    
    # Wait for processing
    time.sleep(5)
    
    cuda_time = time.time() - start_time
    cuda_stats = cuda_thread.get_stats()
    
    cuda_thread.stop()
    cuda_thread.join()
    cuda_thread.clear_gpu_memory()
    
    # Compare results
    print("\n=== Benchmark Results ===")
    print(f"CPU Processing Time: {cpu_time:.2f} seconds")
    print(f"CUDA Processing Time: {cuda_time:.2f} seconds")
    
    if cuda_time > 0:
        speedup = cpu_time / cuda_time
        print(f"Speedup: {speedup:.2f}x")
    
    print(f"CPU Files Processed: {cpu_stats.get('files_processed', 0)}")
    print(f"CUDA Files Processed: {cuda_stats.get('files_processed', 0)}")
    
    if 'gpu_memory_used_gb' in cuda_stats:
        print(f"GPU Memory Used: {cuda_stats['gpu_memory_used_gb']:.2f} GB")


def test_different_file_types():
    """Test processing different types of CSV files."""
    
    print("\n=== Testing Different File Types ===")
    
    # Create various test files
    files = []
    
    # QA file
    qa_data = {
        'question': [f'Question {i}?' for i in range(1000)],
        'answer': [f'Answer {i}.' for i in range(1000)]
    }
    qa_df = pd.DataFrame(qa_data)
    qa_file = Path("data/csv_input/qa_test.csv")
    qa_df.to_csv(qa_file, index=False)
    files.append(qa_file)
    
    # Patient file
    patient_data = {
        'patient_id': [f'P{i:04d}' for i in range(1000)],
        'name': [f'Patient {i}' for i in range(1000)],
        'age': np.random.randint(18, 80, 1000),
        'diagnosis': np.random.choice(['Hypertension', 'Diabetes', 'Asthma'], 1000)
    }
    patient_df = pd.DataFrame(patient_data)
    patient_file = Path("data/csv_input/patient_test.csv")
    patient_df.to_csv(patient_file, index=False)
    files.append(patient_file)
    
    # Medical file
    medical_data = {
        'record_id': [f'M{i:04d}' for i in range(1000)],
        'symptom': np.random.choice(['Fever', 'Cough', 'Headache', 'Fatigue'], 1000),
        'severity': np.random.choice(['Mild', 'Moderate', 'Severe'], 1000),
        'treatment': np.random.choice(['Rest', 'Medication', 'Surgery'], 1000)
    }
    medical_df = pd.DataFrame(medical_data)
    medical_file = Path("data/csv_input/medical_test.csv")
    medical_df.to_csv(medical_file, index=False)
    files.append(medical_file)
    
    # ML file
    ml_file = create_ml_sample_csv()
    files.append(ml_file)
    
    print(f"Created {len(files)} test files")
    
    # Process with CUDA
    cuda_thread = CUDACSVThread(
        watch_directory="data/csv_input",
        processed_directory="data/csv_processed",
        error_directory="data/csv_errors",
        use_cuda=True,
        polling_interval=0.5
    )
    
    cuda_thread.start()
    
    # Monitor processing
    print("\nMonitoring file processing...")
    for i in range(20):  # Monitor for 10 seconds
        stats = cuda_thread.get_stats()
        print(f"Time: {i*0.5}s - Processed: {stats['files_processed']}, "
              f"Failed: {stats['files_failed']}, Queue: {stats['queue_size']}")
        time.sleep(0.5)
        
        if stats['files_processed'] >= len(files):
            break
    
    cuda_thread.stop()
    cuda_thread.join()
    cuda_thread.clear_gpu_memory()
    
    # Show results
    print("\n=== Processing Results ===")
    processed_dir = Path("data/csv_processed")
    if processed_dir.exists():
        processed_files = list(processed_dir.glob("*"))
        print(f"Files processed: {len(processed_files)}")
        for file in processed_files:
            print(f"  - {file.name}")


def main():
    """Main example function."""
    
    print("=== CUDA CSV Thread Example ===\n")
    
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
        return
    except Exception as e:
        print(f"Error checking CUDA: {e}")
        return
    
    # Create directories
    for dir_name in ["data/csv_input", "data/csv_processed", "data/csv_errors"]:
        Path(dir_name).mkdir(parents=True, exist_ok=True)
    
    # Run tests
    try:
        # Test different file types
        test_different_file_types()
        
        # Benchmark CUDA vs CPU
        benchmark_cuda_vs_cpu()
        
        print("\n=== Example completed successfully ===")
        
    except Exception as e:
        print(f"Error during testing: {e}")
    
    finally:
        # Cleanup
        print("\nCleaning up...")
        import shutil
        for dir_name in ["data/csv_input", "data/csv_processed", "data/csv_errors"]:
            if Path(dir_name).exists():
                shutil.rmtree(dir_name)


if __name__ == "__main__":
    main() 