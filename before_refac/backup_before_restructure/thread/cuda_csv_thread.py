"""
CUDA-Enhanced CSV File Handler Thread - GPU-accelerated CSV processing.
"""

import threading
import time
import queue
import csv
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Dict, List, Any, Callable
from datetime import datetime
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.logger import get_logger
from utils.file_handler import FileHandler

# CUDA imports
try:
    import cupy as cp
    import cudf
    CUDA_AVAILABLE = True
except ImportError:
    CUDA_AVAILABLE = False
    print("CUDA libraries not available. Install cupy and cudf for GPU acceleration.")

try:
    import torch
    TORCH_CUDA_AVAILABLE = torch.cuda.is_available()
except ImportError:
    TORCH_CUDA_AVAILABLE = False


class CUDACSVThread(threading.Thread):
    """
    CUDA-enhanced thread for receiving and processing CSV files with GPU acceleration.
    
    This thread provides GPU-accelerated processing for:
    - Large CSV file reading and parsing
    - Data transformations and filtering
    - Statistical computations
    - Vector operations
    - Machine learning preprocessing
    """
    
    def __init__(self, 
                 watch_directory: str = "data/csv_input",
                 processed_directory: str = "data/csv_processed",
                 error_directory: str = "data/csv_errors",
                 polling_interval: float = 1.0,
                 use_cuda: bool = True,
                 batch_size: int = 10000,
                 csv_handlers: Optional[Dict[str, Callable]] = None):
        """
        Initialize CUDA-enhanced CSV file handling thread.
        
        Args:
            watch_directory: Directory to monitor for new CSV files
            processed_directory: Directory to move successfully processed files
            error_directory: Directory to move files that failed processing
            polling_interval: How often to check for new files (seconds)
            use_cuda: Whether to use CUDA acceleration
            batch_size: Batch size for GPU processing
            csv_handlers: Dictionary mapping file patterns to handler functions
        """
        super().__init__()
        
        # Thread configuration
        self.watch_directory = Path(watch_directory)
        self.processed_directory = Path(processed_directory)
        self.error_directory = Path(error_directory)
        self.polling_interval = polling_interval
        self.use_cuda = use_cuda and CUDA_AVAILABLE
        self.batch_size = batch_size
        
        # Thread control
        self.running = False
        self.file_queue = queue.Queue()
        
        # Setup logging first
        self.logger = get_logger(__name__)
        
        # CUDA setup
        self._setup_cuda()
        
        # CSV handlers with CUDA support
        self.csv_handlers = csv_handlers or {
            "*.csv": self._default_cuda_csv_handler,
            "qa_*.csv": self._cuda_qa_csv_handler,
            "patient_*.csv": self._cuda_patient_csv_handler,
            "medical_*.csv": self._cuda_medical_csv_handler,
            "large_*.csv": self._cuda_large_csv_handler,
            "ml_*.csv": self._cuda_ml_preprocessing_handler
        }
        
        # Create directories if they don't exist
        self._setup_directories()
        
        # Statistics
        self.stats = {
            "files_processed": 0,
            "files_failed": 0,
            "start_time": None,
            "last_processed": None,
            "gpu_processing_time": 0.0,
            "cpu_processing_time": 0.0,
            "gpu_memory_used": 0.0
        }
    
    def _setup_cuda(self):
        """Setup CUDA environment and check availability."""
        if self.use_cuda:
            if CUDA_AVAILABLE:
                print("CUDA is available and enabled")
                # Get GPU info
                try:
                    gpu_memory = cp.cuda.runtime.memGetInfo()
                    print(f"GPU Memory: {gpu_memory[0] / 1024**3:.2f} GB free, "
                          f"{gpu_memory[1] / 1024**3:.2f} GB total")
                except Exception as e:
                    print(f"Could not get GPU memory info: {e}")
            else:
                print("CUDA libraries not available, falling back to CPU")
                self.use_cuda = False
        else:
            print("CUDA disabled, using CPU processing")
    
    def _setup_directories(self):
        """Create necessary directories."""
        for directory in [self.watch_directory, self.processed_directory, self.error_directory]:
            directory.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Ensured directory exists: {directory}")
    
    def run(self):
        """Main thread loop."""
        self.running = True
        self.stats["start_time"] = datetime.now()
        self.logger.info("CUDA CSV file handling thread started")
        
        try:
            while self.running:
                self._process_pending_files()
                self._scan_for_new_files()
                time.sleep(self.polling_interval)
                
        except Exception as e:
            self.logger.error(f"Error in CUDA CSV thread main loop: {e}")
        finally:
            self.logger.info("CUDA CSV file handling thread stopped")
    
    def stop(self):
        """Stop the thread gracefully."""
        self.running = False
        self.logger.info("Stopping CUDA CSV file handling thread...")
    
    def _scan_for_new_files(self):
        """Scan watch directory for new CSV files."""
        try:
            for file_path in self.watch_directory.glob("*.csv"):
                if file_path.is_file() and not self._is_file_being_processed(file_path):
                    self.logger.info(f"Found new CSV file: {file_path.name}")
                    self.file_queue.put(file_path)
                    
        except Exception as e:
            self.logger.error(f"Error scanning for new files: {e}")
    
    def _is_file_being_processed(self, file_path: Path) -> bool:
        """Check if file is currently being processed."""
        # Check if file is in queue
        for i in range(self.file_queue.qsize()):
            try:
                queued_file = self.file_queue.queue[i]
                if queued_file == file_path:
                    return True
            except IndexError:
                break
        
        # Check if file is in processed or error directories
        if (self.processed_directory / file_path.name).exists():
            return True
        if (self.error_directory / file_path.name).exists():
            return True
            
        return False
    
    def _process_pending_files(self):
        """Process files in the queue."""
        while not self.file_queue.empty() and self.running:
            try:
                file_path = self.file_queue.get_nowait()
                self._process_csv_file(file_path)
                self.file_queue.task_done()
                
            except queue.Empty:
                break
            except Exception as e:
                self.logger.error(f"Error processing file from queue: {e}")
    
    def _process_csv_file(self, file_path: Path):
        """Process a single CSV file with CUDA acceleration."""
        self.logger.info(f"Processing CSV file with CUDA: {file_path.name}")
        
        try:
            # Determine appropriate handler
            handler = self._get_handler_for_file(file_path)
            
            # Process the file
            start_time = time.time()
            result = handler(file_path)
            processing_time = time.time() - start_time
            
            if result:
                # Move to processed directory
                self._move_file(file_path, self.processed_directory)
                self.stats["files_processed"] += 1
                self.stats["last_processed"] = datetime.now()
                self.stats["gpu_processing_time"] += processing_time
                self.logger.info(f"Successfully processed: {file_path.name} in {processing_time:.2f}s")
            else:
                # Move to error directory
                self._move_file(file_path, self.error_directory)
                self.stats["files_failed"] += 1
                self.logger.error(f"Failed to process: {file_path.name}")
                
        except Exception as e:
            self.logger.error(f"Error processing {file_path.name}: {e}")
            self._move_file(file_path, self.error_directory)
            self.stats["files_failed"] += 1
    
    def _get_handler_for_file(self, file_path: Path) -> Callable:
        """Get the appropriate handler for a file based on its name."""
        for pattern, handler in self.csv_handlers.items():
            if file_path.match(pattern):
                return handler
        
        # Default handler if no pattern matches
        return self._default_cuda_csv_handler
    
    def _move_file(self, file_path: Path, destination: Path):
        """Move file to destination directory."""
        try:
            destination_file = destination / file_path.name
            file_path.rename(destination_file)
            self.logger.debug(f"Moved {file_path.name} to {destination}")
        except Exception as e:
            self.logger.error(f"Failed to move {file_path.name}: {e}")
    
    def _read_csv_with_cuda(self, file_path: Path) -> Optional[Any]:
        """Read CSV file using CUDA acceleration if available."""
        try:
            if self.use_cuda and CUDA_AVAILABLE:
                # Use cuDF for GPU-accelerated CSV reading
                self.logger.info(f"Reading {file_path.name} with GPU acceleration")
                df = cudf.read_csv(file_path)
                return df
            else:
                # Fallback to pandas
                self.logger.info(f"Reading {file_path.name} with CPU")
                df = pd.read_csv(file_path)
                return df
                
        except Exception as e:
            self.logger.error(f"Error reading CSV with CUDA: {e}")
            # Fallback to pandas
            try:
                df = pd.read_csv(file_path)
                return df
            except Exception as e2:
                self.logger.error(f"Error reading CSV with pandas: {e2}")
                return None
    
    def _default_cuda_csv_handler(self, file_path: Path) -> bool:
        """Default CUDA-accelerated CSV file handler."""
        try:
            # Read CSV with CUDA acceleration
            df = self._read_csv_with_cuda(file_path)
            
            if df is None:
                return False
            
            # Basic validation
            if len(df) == 0:
                self.logger.warning(f"CSV file is empty: {file_path.name}")
                return False
            
            # GPU-accelerated operations
            if self.use_cuda and hasattr(df, 'shape'):
                # cuDF operations
                row_count = len(df)
                col_count = len(df.columns)
                column_names = list(df.columns)
                
                # GPU-accelerated statistics
                numeric_columns = df.select_dtypes(include=[np.number]).columns
                if len(numeric_columns) > 0:
                    stats = df[numeric_columns].describe()
                    stats_dict = stats.to_dict()
                else:
                    stats_dict = {}
                    
            else:
                # Pandas operations
                row_count = len(df)
                col_count = len(df.columns)
                column_names = list(df.columns)
                
                # CPU statistics
                numeric_columns = df.select_dtypes(include=[np.number]).columns
                if len(numeric_columns) > 0:
                    stats_dict = df[numeric_columns].describe().to_dict()
                else:
                    stats_dict = {}
            
            # Log basic info
            self.logger.info(f"CSV file info - Rows: {row_count}, Columns: {col_count}")
            self.logger.info(f"Columns: {column_names}")
            
            # Save processed data summary
            summary = {
                "filename": file_path.name,
                "processed_at": datetime.now().isoformat(),
                "rows": row_count,
                "columns": col_count,
                "column_names": column_names,
                "processing_method": "CUDA" if self.use_cuda else "CPU",
                "statistics": stats_dict
            }
            
            summary_file = self.processed_directory / f"{file_path.stem}_summary.json"
            FileHandler.save_json(str(summary_file), summary)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error in default CUDA CSV handler: {e}")
            return False
    
    def _cuda_qa_csv_handler(self, file_path: Path) -> bool:
        """CUDA-accelerated handler for QA (Question-Answer) CSV files."""
        try:
            df = self._read_csv_with_cuda(file_path)
            
            if df is None:
                return False
            
            # Validate required columns for QA format
            required_columns = ['question', 'answer']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                self.logger.error(f"QA CSV missing required columns: {missing_columns}")
                return False
            
            # GPU-accelerated text processing
            if self.use_cuda and hasattr(df, 'str'):
                # cuDF string operations
                df['question_clean'] = df['question'].str.strip()
                df['answer_clean'] = df['answer'].str.strip()
                
                # Convert to CPU for JSON serialization
                qa_data = []
                for i in range(len(df)):
                    qa_data.append({
                        "question": str(df['question_clean'].iloc[i]),
                        "answer": str(df['answer_clean'].iloc[i]),
                        "source": file_path.name
                    })
            else:
                # Pandas operations
                qa_data = []
                for _, row in df.iterrows():
                    qa_data.append({
                        "question": str(row['question']).strip(),
                        "answer": str(row['answer']).strip(),
                        "source": file_path.name
                    })
            
            # Save processed QA data
            qa_file = self.processed_directory / f"{file_path.stem}_qa_processed.json"
            FileHandler.save_json(str(qa_file), {"qa_pairs": qa_data})
            
            self.logger.info(f"Processed {len(qa_data)} QA pairs from {file_path.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error in CUDA QA CSV handler: {e}")
            return False
    
    def _cuda_patient_csv_handler(self, file_path: Path) -> bool:
        """CUDA-accelerated handler for patient data CSV files."""
        try:
            df = self._read_csv_with_cuda(file_path)
            
            if df is None:
                return False
            
            # Basic patient data validation
            if 'patient_id' not in df.columns:
                self.logger.error("Patient CSV missing patient_id column")
                return False
            
            # GPU-accelerated data processing
            if self.use_cuda and hasattr(df, 'fillna'):
                # cuDF operations
                df = df.fillna('Unknown')
                
                # Convert to CPU for JSON serialization
                patient_data = []
                for i in range(len(df)):
                    patient_record = {
                        "patient_id": str(df['patient_id'].iloc[i]),
                        "source_file": file_path.name,
                        "data": {col: str(df[col].iloc[i]) for col in df.columns}
                    }
                    patient_data.append(patient_record)
            else:
                # Pandas operations
                df = df.fillna('Unknown')
                patient_data = []
                for _, row in df.iterrows():
                    patient_record = {
                        "patient_id": str(row['patient_id']),
                        "source_file": file_path.name,
                        "data": row.to_dict()
                    }
                    patient_data.append(patient_record)
            
            # Save processed patient data
            patient_file = self.processed_directory / f"{file_path.stem}_patients_processed.json"
            FileHandler.save_json(str(patient_file), {"patients": patient_data})
            
            self.logger.info(f"Processed {len(patient_data)} patient records from {file_path.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error in CUDA patient CSV handler: {e}")
            return False
    
    def _cuda_medical_csv_handler(self, file_path: Path) -> bool:
        """CUDA-accelerated handler for medical data CSV files."""
        try:
            df = self._read_csv_with_cuda(file_path)
            
            if df is None:
                return False
            
            # GPU-accelerated medical data processing
            if self.use_cuda and hasattr(df, 'groupby'):
                # cuDF operations
                total_records = len(df)
                columns = list(df.columns)
                
                # GPU-accelerated aggregations
                if 'severity' in df.columns:
                    severity_counts = df['severity'].value_counts().to_dict()
                else:
                    severity_counts = {}
                
                # Convert to CPU for JSON serialization
                medical_data = {
                    "filename": file_path.name,
                    "processed_at": datetime.now().isoformat(),
                    "total_records": total_records,
                    "columns": columns,
                    "severity_distribution": severity_counts,
                    "processing_method": "CUDA"
                }
            else:
                # Pandas operations
                total_records = len(df)
                columns = list(df.columns)
                
                severity_counts = {}
                if 'severity' in df.columns:
                    severity_counts = df['severity'].value_counts().to_dict()
                
                medical_data = {
                    "filename": file_path.name,
                    "processed_at": datetime.now().isoformat(),
                    "total_records": total_records,
                    "columns": columns,
                    "severity_distribution": severity_counts,
                    "processing_method": "CPU"
                }
            
            # Save processed medical data
            medical_file = self.processed_directory / f"{file_path.stem}_medical_processed.json"
            FileHandler.save_json(str(medical_file), medical_data)
            
            self.logger.info(f"Processed {total_records} medical records from {file_path.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error in CUDA medical CSV handler: {e}")
            return False
    
    def _cuda_large_csv_handler(self, file_path: Path) -> bool:
        """CUDA-accelerated handler for large CSV files with batch processing."""
        try:
            self.logger.info(f"Processing large CSV file: {file_path.name}")
            
            if not self.use_cuda:
                self.logger.warning("CUDA not available for large file processing")
                return self._default_cuda_csv_handler(file_path)
            
            # Process large files in batches
            batch_results = []
            total_rows = 0
            
            # Read in chunks for memory efficiency
            chunk_size = self.batch_size
            
            for chunk_num, chunk in enumerate(pd.read_csv(file_path, chunksize=chunk_size)):
                self.logger.info(f"Processing chunk {chunk_num + 1} with {len(chunk)} rows")
                
                # Convert chunk to GPU
                gpu_chunk = cudf.DataFrame(chunk)
                
                # GPU-accelerated processing
                processed_chunk = self._process_large_chunk(gpu_chunk)
                batch_results.append(processed_chunk)
                total_rows += len(chunk)
                
                # Clear GPU memory
                del gpu_chunk
                cp.get_default_memory_pool().free_all_blocks()
            
            # Combine results
            combined_results = {
                "filename": file_path.name,
                "processed_at": datetime.now().isoformat(),
                "total_rows": total_rows,
                "chunks_processed": len(batch_results),
                "processing_method": "CUDA_BATCH",
                "batch_size": chunk_size
            }
            
            # Save results
            large_file = self.processed_directory / f"{file_path.stem}_large_processed.json"
            FileHandler.save_json(str(large_file), combined_results)
            
            self.logger.info(f"Processed large file {file_path.name} with {total_rows} rows")
            return True
            
        except Exception as e:
            self.logger.error(f"Error in CUDA large CSV handler: {e}")
            return False
    
    def _process_large_chunk(self, gpu_chunk) -> dict:
        """Process a large chunk of data on GPU."""
        try:
            # GPU-accelerated operations
            chunk_stats = {
                "rows": len(gpu_chunk),
                "columns": len(gpu_chunk.columns),
                "memory_usage": gpu_chunk.memory_usage(deep=True).sum()
            }
            
            # GPU-accelerated statistics for numeric columns
            numeric_cols = gpu_chunk.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                chunk_stats["numeric_stats"] = gpu_chunk[numeric_cols].describe().to_dict()
            
            return chunk_stats
            
        except Exception as e:
            self.logger.error(f"Error processing large chunk: {e}")
            return {"error": str(e)}
    
    def _cuda_ml_preprocessing_handler(self, file_path: Path) -> bool:
        """CUDA-accelerated handler for machine learning preprocessing."""
        try:
            df = self._read_csv_with_cuda(file_path)
            
            if df is None:
                return False
            
            # GPU-accelerated ML preprocessing
            if self.use_cuda and hasattr(df, 'fillna'):
                # Handle missing values
                df = df.fillna(df.mean())
                
                # GPU-accelerated normalization for numeric columns
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    # Z-score normalization on GPU
                    for col in numeric_cols:
                        mean_val = df[col].mean()
                        std_val = df[col].std()
                        if std_val > 0:
                            df[col] = (df[col] - mean_val) / std_val
                
                # GPU-accelerated encoding for categorical columns
                categorical_cols = df.select_dtypes(include=['object']).columns
                encoding_map = {}
                
                for col in categorical_cols:
                    unique_vals = df[col].unique()
                    encoding_map[col] = {val: idx for idx, val in enumerate(unique_vals)}
                    df[col] = df[col].map(encoding_map[col])
                
                # Convert to CPU for saving
                processed_data = {
                    "filename": file_path.name,
                    "processed_at": datetime.now().isoformat(),
                    "preprocessing_method": "CUDA_ML",
                    "encoding_map": encoding_map,
                    "numeric_columns": list(numeric_cols),
                    "categorical_columns": list(categorical_cols)
                }
            else:
                # CPU preprocessing
                df = df.fillna(df.mean())
                
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    for col in numeric_cols:
                        mean_val = df[col].mean()
                        std_val = df[col].std()
                        if std_val > 0:
                            df[col] = (df[col] - mean_val) / std_val
                
                categorical_cols = df.select_dtypes(include=['object']).columns
                encoding_map = {}
                
                for col in categorical_cols:
                    unique_vals = df[col].unique()
                    encoding_map[col] = {val: idx for idx, val in enumerate(unique_vals)}
                    df[col] = df[col].map(encoding_map[col])
                
                processed_data = {
                    "filename": file_path.name,
                    "processed_at": datetime.now().isoformat(),
                    "preprocessing_method": "CPU_ML",
                    "encoding_map": encoding_map,
                    "numeric_columns": list(numeric_cols),
                    "categorical_columns": list(categorical_cols)
                }
            
            # Save processed ML data
            ml_file = self.processed_directory / f"{file_path.stem}_ml_processed.json"
            FileHandler.save_json(str(ml_file), processed_data)
            
            self.logger.info(f"ML preprocessing completed for {file_path.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error in CUDA ML preprocessing handler: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get thread statistics including GPU metrics."""
        stats = {
            **self.stats,
            "queue_size": self.file_queue.qsize(),
            "running": self.running,
            "cuda_available": self.use_cuda,
            "uptime": (datetime.now() - self.stats["start_time"]).total_seconds() if self.stats["start_time"] else 0
        }
        
        # Add GPU memory info if available
        if self.use_cuda and CUDA_AVAILABLE:
            try:
                gpu_memory = cp.cuda.runtime.memGetInfo()
                stats["gpu_memory_free_gb"] = gpu_memory[0] / 1024**3
                stats["gpu_memory_total_gb"] = gpu_memory[1] / 1024**3
                stats["gpu_memory_used_gb"] = (gpu_memory[1] - gpu_memory[0]) / 1024**3
            except Exception as e:
                stats["gpu_memory_error"] = str(e)
        
        return stats
    
    def add_csv_handler(self, pattern: str, handler: Callable):
        """Add a new CSV handler for a specific file pattern."""
        self.csv_handlers[pattern] = handler
        self.logger.info(f"Added CUDA CSV handler for pattern: {pattern}")
    
    def clear_gpu_memory(self):
        """Clear GPU memory cache."""
        if self.use_cuda and CUDA_AVAILABLE:
            try:
                cp.get_default_memory_pool().free_all_blocks()
                self.logger.info("GPU memory cleared")
            except Exception as e:
                self.logger.error(f"Error clearing GPU memory: {e}")


# Example usage and testing
if __name__ == "__main__":
    # Create and start the CUDA CSV thread
    cuda_csv_thread = CUDACSVThread(
        watch_directory="data/csv_input",
        processed_directory="data/csv_processed", 
        error_directory="data/csv_errors",
        polling_interval=2.0,
        use_cuda=True,
        batch_size=5000
    )
    
    try:
        cuda_csv_thread.start()
        print("CUDA CSV file handling thread started. Press Ctrl+C to stop.")
        
        # Monitor thread
        while cuda_csv_thread.is_alive():
            stats = cuda_csv_thread.get_stats()
            print(f"Stats: {stats}")
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\nStopping CUDA CSV thread...")
        cuda_csv_thread.stop()
        cuda_csv_thread.join(timeout=5)
        cuda_csv_thread.clear_gpu_memory()
        print("CUDA CSV thread stopped.") 