"""
File-Based Thread Example - Demonstrates persistent CSV processing with file-based state.
"""

import time
import pandas as pd
import numpy as np
from pathlib import Path
import shutil
from file_based_thread import FileBasedThreadManager


def create_test_files(num_files: int = 10, rows_per_file: int = 5000):
    """Create test CSV files for file-based processing."""
    
    csv_input_dir = Path("data/csv_input")
    csv_input_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Creating {num_files} test files with {rows_per_file} rows each...")
    
    for i in range(num_files):
        # Create different types of data
        if i % 4 == 0:
            # QA data
            data = {
                'question': [f'Question {j} for file {i}?' for j in range(rows_per_file)],
                'answer': [f'Answer {j} for file {i}.' for j in range(rows_per_file)]
            }
            filename = f"qa_file_{i:03d}.csv"
        elif i % 4 == 1:
            # Patient data
            data = {
                'patient_id': [f'P{i:03d}_{j:06d}' for j in range(rows_per_file)],
                'name': [f'Patient {j}' for j in range(rows_per_file)],
                'age': np.random.randint(18, 80, rows_per_file),
                'diagnosis': np.random.choice(['Hypertension', 'Diabetes', 'Asthma'], rows_per_file)
            }
            filename = f"patient_file_{i:03d}.csv"
        elif i % 4 == 2:
            # Medical data
            data = {
                'record_id': [f'M{i:03d}_{j:06d}' for j in range(rows_per_file)],
                'symptom': np.random.choice(['Fever', 'Cough', 'Headache', 'Fatigue'], rows_per_file),
                'severity': np.random.choice(['Mild', 'Moderate', 'Severe'], rows_per_file),
                'treatment': np.random.choice(['Rest', 'Medication', 'Surgery'], rows_per_file)
            }
            filename = f"medical_file_{i:03d}.csv"
        else:
            # Large data
            data = {}
            for col in range(15):
                if col < 5:
                    data[f'num_col_{col}'] = np.random.randn(rows_per_file)
                elif col < 10:
                    data[f'int_col_{col}'] = np.random.randint(0, 1000, rows_per_file)
                else:
                    data[f'str_col_{col}'] = [f'value_{j}_{col}' for j in range(rows_per_file)]
            filename = f"large_file_{i:03d}.csv"
        
        # Create DataFrame and save
        df = pd.DataFrame(data)
        file_path = csv_input_dir / filename
        df.to_csv(file_path, index=False)
        
        print(f"Created: {filename}")
    
    print(f"Created {num_files} test files successfully")
    return num_files


def demonstrate_persistence():
    """Demonstrate thread persistence across restarts."""
    
    print("\n=== Persistence Demonstration ===")
    
    # Create test files
    num_files = 8
    create_test_files(num_files, 3000)
    
    # Create file-based thread
    thread = FileBasedThreadManager(
        thread_id="persistent_thread_001",
        base_directory="thread_data",
        watch_directory="data/csv_input",
        processed_directory="data/csv_processed",
        error_directory="data/csv_errors",
        checkpoint_interval=5,  # Save checkpoint every 5 seconds
        use_cuda=True
    )
    
    print("Starting thread...")
    thread.start()
    
    # Let it process some files
    print("Processing files for 15 seconds...")
    start_time = time.time()
    while time.time() - start_time < 15:
        stats = thread.get_stats()
        task_stats = thread.get_task_stats()
        print(f"Time: {time.time() - start_time:.1f}s - "
              f"Processed: {stats['files_processed']}, "
              f"Failed: {stats['files_failed']}, "
              f"State: {stats['state']}")
        time.sleep(2)
    
    # Stop the thread
    print("Stopping thread...")
    thread.stop()
    
    # Show what was saved
    print("\nThread stopped. Checking saved state...")
    checkpoint_file = Path("thread_data/checkpoints/persistent_thread_001.json")
    if checkpoint_file.exists():
        import json
        with open(checkpoint_file, 'r') as f:
            checkpoint_data = json.load(f)
        print(f"Saved checkpoint: {checkpoint_data}")
    
    # Check database
    print("\nDatabase contents:")
    import sqlite3
    with sqlite3.connect("thread_data/tasks.db") as conn:
        cursor = conn.execute("SELECT file_path, status, thread_id FROM tasks")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]} (Thread: {row[2]})")
    
    # Restart the thread
    print("\nRestarting thread...")
    thread2 = FileBasedThreadManager(
        thread_id="persistent_thread_001",  # Same ID to resume
        base_directory="thread_data",
        watch_directory="data/csv_input",
        processed_directory="data/csv_processed",
        error_directory="data/csv_errors",
        use_cuda=True
    )
    
    thread2.start()
    
    # Monitor restart
    print("Monitoring restart for 10 seconds...")
    start_time = time.time()
    while time.time() - start_time < 10:
        stats = thread2.get_stats()
        task_stats = thread2.get_task_stats()
        print(f"Time: {time.time() - start_time:.1f}s - "
              f"Processed: {stats['files_processed']}, "
              f"Failed: {stats['files_failed']}, "
              f"State: {stats['state']}")
        time.sleep(2)
    
    thread2.stop()
    print("Restart demonstration completed.")


def demonstrate_pause_resume():
    """Demonstrate pause and resume functionality."""
    
    print("\n=== Pause/Resume Demonstration ===")
    
    # Create test files
    num_files = 5
    create_test_files(num_files, 2000)
    
    # Create thread
    thread = FileBasedThreadManager(
        thread_id="pause_resume_thread",
        base_directory="thread_data",
        watch_directory="data/csv_input",
        processed_directory="data/csv_processed",
        error_directory="data/csv_errors",
        use_cuda=True
    )
    
    print("Starting thread...")
    thread.start()
    
    # Let it process for a bit
    print("Processing for 5 seconds...")
    time.sleep(5)
    
    # Pause
    print("Pausing thread...")
    thread.pause()
    
    # Monitor paused state
    print("Monitoring paused state for 5 seconds...")
    start_time = time.time()
    while time.time() - start_time < 5:
        stats = thread.get_stats()
        print(f"Time: {time.time() - start_time:.1f}s - "
              f"State: {stats['state']}, "
              f"Paused: {stats['paused']}")
        time.sleep(1)
    
    # Resume
    print("Resuming thread...")
    thread.resume()
    
    # Monitor resumed state
    print("Monitoring resumed state for 5 seconds...")
    start_time = time.time()
    while time.time() - start_time < 5:
        stats = thread.get_stats()
        print(f"Time: {time.time() - start_time:.1f}s - "
              f"State: {stats['state']}, "
              f"Paused: {stats['paused']}")
        time.sleep(1)
    
    thread.stop()
    print("Pause/Resume demonstration completed.")


def demonstrate_file_deduplication():
    """Demonstrate file deduplication using hashes."""
    
    print("\n=== File Deduplication Demonstration ===")
    
    # Create a test file
    csv_input_dir = Path("data/csv_input")
    csv_input_dir.mkdir(parents=True, exist_ok=True)
    
    # Create original file
    data = {
        'id': range(1000),
        'name': [f'Item {i}' for i in range(1000)],
        'value': np.random.randn(1000)
    }
    df = pd.DataFrame(data)
    
    # Save as different filenames (same content)
    file1 = csv_input_dir / "original_file.csv"
    file2 = csv_input_dir / "duplicate_file.csv"
    file3 = csv_input_dir / "copy_file.csv"
    
    df.to_csv(file1, index=False)
    df.to_csv(file2, index=False)
    df.to_csv(file3, index=False)
    
    print("Created 3 files with identical content but different names")
    
    # Create thread
    thread = FileBasedThreadManager(
        thread_id="dedup_thread",
        base_directory="thread_data",
        watch_directory="data/csv_input",
        processed_directory="data/csv_processed",
        error_directory="data/csv_errors",
        use_cuda=True
    )
    
    print("Starting thread...")
    thread.start()
    
    # Monitor processing
    print("Monitoring for 10 seconds...")
    start_time = time.time()
    while time.time() - start_time < 10:
        stats = thread.get_stats()
        task_stats = thread.get_task_stats()
        print(f"Time: {time.time() - start_time:.1f}s - "
              f"Processed: {stats['files_processed']}, "
              f"Task stats: {task_stats}")
        time.sleep(2)
    
    thread.stop()
    
    # Check database for deduplication
    print("\nChecking database for deduplication:")
    import sqlite3
    with sqlite3.connect("thread_data/tasks.db") as conn:
        cursor = conn.execute("SELECT file_path, file_hash, status FROM tasks ORDER BY file_path")
        for row in cursor.fetchall():
            print(f"  {row[0]}: Hash={row[1][:8]}..., Status={row[2]}")
    
    print("Deduplication demonstration completed.")


def demonstrate_error_recovery():
    """Demonstrate error recovery and retry mechanisms."""
    
    print("\n=== Error Recovery Demonstration ===")
    
    # Create a problematic file (empty CSV)
    csv_input_dir = Path("data/csv_input")
    csv_input_dir.mkdir(parents=True, exist_ok=True)
    
    # Create empty file
    empty_file = csv_input_dir / "empty_file.csv"
    with open(empty_file, 'w') as f:
        f.write("")  # Empty file
    
    # Create normal file
    data = {
        'id': range(100),
        'name': [f'Item {i}' for i in range(100)]
    }
    df = pd.DataFrame(data)
    normal_file = csv_input_dir / "normal_file.csv"
    df.to_csv(normal_file, index=False)
    
    print("Created empty file and normal file")
    
    # Create thread
    thread = FileBasedThreadManager(
        thread_id="error_recovery_thread",
        base_directory="thread_data",
        watch_directory="data/csv_input",
        processed_directory="data/csv_processed",
        error_directory="data/csv_errors",
        use_cuda=True
    )
    
    print("Starting thread...")
    thread.start()
    
    # Monitor processing
    print("Monitoring for 10 seconds...")
    start_time = time.time()
    while time.time() - start_time < 10:
        stats = thread.get_stats()
        task_stats = thread.get_task_stats()
        print(f"Time: {time.time() - start_time:.1f}s - "
              f"Processed: {stats['files_processed']}, "
              f"Failed: {stats['files_failed']}, "
              f"Task stats: {task_stats}")
        time.sleep(2)
    
    thread.stop()
    
    # Check error directory
    error_dir = Path("data/csv_errors")
    if error_dir.exists():
        print(f"\nFiles in error directory:")
        for file in error_dir.glob("*"):
            print(f"  {file.name}")
    
    print("Error recovery demonstration completed.")


def main():
    """Main example function."""
    
    print("=== File-Based Thread Example ===\n")
    
    # Create base directories
    for dir_name in ["data/csv_input", "data/csv_processed", "data/csv_errors", "thread_data"]:
        Path(dir_name).mkdir(parents=True, exist_ok=True)
    
    try:
        # Run demonstrations
        print("1. Persistence Demonstration")
        demonstrate_persistence()
        
        print("\n2. Pause/Resume Demonstration")
        demonstrate_pause_resume()
        
        print("\n3. File Deduplication Demonstration")
        demonstrate_file_deduplication()
        
        print("\n4. Error Recovery Demonstration")
        demonstrate_error_recovery()
        
        print("\n=== All demonstrations completed successfully ===")
        
    except Exception as e:
        print(f"Error during demonstration: {e}")
    
    finally:
        # Cleanup
        print("\nCleaning up...")
        for dir_name in ["data/csv_input", "data/csv_processed", "data/csv_errors", "thread_data"]:
            if Path(dir_name).exists():
                shutil.rmtree(dir_name)


if __name__ == "__main__":
    main() 