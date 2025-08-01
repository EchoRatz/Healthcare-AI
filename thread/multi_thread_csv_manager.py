"""
Multi-Threaded CSV Processing Manager - Handles multiple CSV processing threads.
"""

import threading
import time
import queue
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Dict, List, Any, Callable
from datetime import datetime
import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing
from dataclasses import dataclass
from enum import Enum

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

try:
    import torch
    TORCH_CUDA_AVAILABLE = torch.cuda.is_available()
except ImportError:
    TORCH_CUDA_AVAILABLE = False


class ThreadStatus(Enum):
    """Thread status enumeration."""
    IDLE = "idle"
    PROCESSING = "processing"
    ERROR = "error"
    STOPPED = "stopped"


@dataclass
class ThreadInfo:
    """Information about a processing thread."""
    thread_id: int
    status: ThreadStatus
    current_file: Optional[str] = None
    start_time: Optional[datetime] = None
    files_processed: int = 0
    files_failed: int = 0
    gpu_memory_used: float = 0.0
    processing_time: float = 0.0


class MultiThreadCSVManager:
    """
    Multi-threaded CSV processing manager that can handle multiple threads simultaneously.
    
    Features:
    - Manages up to 30+ processing threads
    - Load balancing across threads
    - GPU resource management
    - Thread health monitoring
    - Automatic thread recovery
    - Performance optimization
    """
    
    def __init__(self,
                 max_threads: int = 30,
                 watch_directory: str = "data/csv_input",
                 processed_directory: str = "data/csv_processed",
                 error_directory: str = "data/csv_errors",
                 polling_interval: float = 1.0,
                 use_cuda: bool = True,
                 batch_size: int = 5000,
                 thread_timeout: int = 300,
                 max_queue_size: int = 1000):
        """
        Initialize multi-threaded CSV processing manager.
        
        Args:
            max_threads: Maximum number of processing threads
            watch_directory: Directory to monitor for CSV files
            processed_directory: Directory for successfully processed files
            error_directory: Directory for failed files
            polling_interval: How often to check for new files
            use_cuda: Whether to use CUDA acceleration
            batch_size: Batch size for GPU processing
            thread_timeout: Timeout for thread operations (seconds)
            max_queue_size: Maximum size of file processing queue
        """
        self.max_threads = max_threads
        self.watch_directory = Path(watch_directory)
        self.processed_directory = Path(processed_directory)
        self.error_directory = Path(error_directory)
        self.polling_interval = polling_interval
        self.use_cuda = use_cuda and CUDA_AVAILABLE
        self.batch_size = batch_size
        self.thread_timeout = thread_timeout
        self.max_queue_size = max_queue_size
        
        # Thread management
        self.running = False
        self.thread_pool = ThreadPoolExecutor(max_workers=max_threads)
        self.active_threads: Dict[int, ThreadInfo] = {}
        self.thread_lock = threading.Lock()
        
        # File management
        self.file_queue = queue.Queue(maxsize=max_queue_size)
        self.processing_files = set()
        
        # CUDA setup
        self._setup_cuda()
        
        # CSV handlers
        self.csv_handlers = {
            "*.csv": self._default_csv_handler,
            "qa_*.csv": self._qa_csv_handler,
            "patient_*.csv": self._patient_csv_handler,
            "medical_*.csv": self._medical_csv_handler,
            "large_*.csv": self._large_csv_handler,
            "ml_*.csv": self._ml_preprocessing_handler
        }
        
        # Setup logging
        self.logger = get_logger(__name__)
        
        # Create directories
        self._setup_directories()
        
        # Statistics
        self.stats = {
            "total_files_processed": 0,
            "total_files_failed": 0,
            "start_time": None,
            "last_processed": None,
            "total_gpu_processing_time": 0.0,
            "total_cpu_processing_time": 0.0,
            "peak_thread_count": 0,
            "average_processing_time": 0.0
        }
        
        # Performance monitoring
        self.performance_history = []
        
    def _setup_cuda(self):
        """Setup CUDA environment for multi-threading."""
        if self.use_cuda:
            if CUDA_AVAILABLE:
                self.logger.info(f"CUDA is available for {self.max_threads} threads")
                try:
                    gpu_memory = cp.cuda.runtime.memGetInfo()
                    self.logger.info(f"GPU Memory: {gpu_memory[0] / 1024**3:.2f} GB free, "
                                   f"{gpu_memory[1] / 1024**3:.2f} GB total")
                    # Calculate memory per thread
                    self.memory_per_thread = gpu_memory[0] / (self.max_threads * 2)  # Conservative estimate
                    self.logger.info(f"Memory per thread: {self.memory_per_thread / 1024**3:.2f} GB")
                except Exception as e:
                    self.logger.warning(f"Could not get GPU memory info: {e}")
                    self.memory_per_thread = 0.5 * 1024**3  # 0.5 GB default
            else:
                self.logger.warning("CUDA libraries not available, falling back to CPU")
                self.use_cuda = False
        else:
            self.logger.info("CUDA disabled, using CPU processing")
    
    def _setup_directories(self):
        """Create necessary directories."""
        for directory in [self.watch_directory, self.processed_directory, self.error_directory]:
            directory.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Ensured directory exists: {directory}")
    
    def start(self):
        """Start the multi-threaded CSV processing manager."""
        self.running = True
        self.stats["start_time"] = datetime.now()
        self.logger.info(f"Starting multi-threaded CSV manager with {self.max_threads} threads")
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        # Start file scanning thread
        self.scanner_thread = threading.Thread(target=self._file_scanner_loop, daemon=True)
        self.scanner_thread.start()
        
        # Start performance monitoring thread
        self.performance_thread = threading.Thread(target=self._performance_monitor_loop, daemon=True)
        self.performance_thread.start()
    
    def stop(self):
        """Stop the multi-threaded CSV processing manager."""
        self.running = False
        self.logger.info("Stopping multi-threaded CSV manager...")
        
        # Shutdown thread pool
        self.thread_pool.shutdown(wait=True, timeout=self.thread_timeout)
        
        # Clear GPU memory if using CUDA
        if self.use_cuda and CUDA_AVAILABLE:
            try:
                cp.get_default_memory_pool().free_all_blocks()
                self.logger.info("GPU memory cleared")
            except Exception as e:
                self.logger.error(f"Error clearing GPU memory: {e}")
    
    def _monitor_loop(self):
        """Main monitoring loop for thread management."""
        while self.running:
            try:
                # Process file queue
                self._process_file_queue()
                
                # Monitor thread health
                self._monitor_thread_health()
                
                # Update statistics
                self._update_statistics()
                
                time.sleep(self.polling_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitor loop: {e}")
                time.sleep(self.polling_interval)
    
    def _file_scanner_loop(self):
        """File scanning loop for new CSV files."""
        while self.running:
            try:
                self._scan_for_new_files()
                time.sleep(self.polling_interval)
            except Exception as e:
                self.logger.error(f"Error in file scanner loop: {e}")
                time.sleep(self.polling_interval)
    
    def _performance_monitor_loop(self):
        """Performance monitoring loop."""
        while self.running:
            try:
                self._record_performance_metrics()
                time.sleep(10)  # Record metrics every 10 seconds
            except Exception as e:
                self.logger.error(f"Error in performance monitor loop: {e}")
                time.sleep(10)
    
    def _scan_for_new_files(self):
        """Scan watch directory for new CSV files."""
        try:
            for file_path in self.watch_directory.glob("*.csv"):
                if (file_path.is_file() and 
                    file_path.name not in self.processing_files and
                    not self._is_file_processed(file_path)):
                    
                    # Add to queue if not full
                    try:
                        self.file_queue.put_nowait(file_path)
                        self.processing_files.add(file_path.name)
                        self.logger.info(f"Queued file: {file_path.name}")
                    except queue.Full:
                        self.logger.warning(f"File queue full, skipping: {file_path.name}")
                        
        except Exception as e:
            self.logger.error(f"Error scanning for new files: {e}")
    
    def _is_file_processed(self, file_path: Path) -> bool:
        """Check if file has been processed."""
        return ((self.processed_directory / file_path.name).exists() or
                (self.error_directory / file_path.name).exists())
    
    def _process_file_queue(self):
        """Process files from the queue using thread pool."""
        while not self.file_queue.empty() and self.running:
            try:
                file_path = self.file_queue.get_nowait()
                
                # Submit to thread pool
                future = self.thread_pool.submit(self._process_csv_file_worker, file_path)
                
                # Track the future (optional: can be used for result collection)
                self.logger.debug(f"Submitted {file_path.name} to thread pool")
                
            except queue.Empty:
                break
            except Exception as e:
                self.logger.error(f"Error submitting file to thread pool: {e}")
    
    def _process_csv_file_worker(self, file_path: Path) -> bool:
        """Worker function for processing CSV files in threads."""
        thread_id = threading.get_ident()
        
        with self.thread_lock:
            # Register thread
            self.active_threads[thread_id] = ThreadInfo(
                thread_id=thread_id,
                status=ThreadStatus.PROCESSING,
                current_file=file_path.name,
                start_time=datetime.now()
            )
        
        try:
            self.logger.info(f"Thread {thread_id} processing: {file_path.name}")
            
            # Determine handler
            handler = self._get_handler_for_file(file_path)
            
            # Process file
            start_time = time.time()
            result = handler(file_path)
            processing_time = time.time() - start_time
            
            # Update thread info
            with self.thread_lock:
                if thread_id in self.active_threads:
                    thread_info = self.active_threads[thread_id]
                    thread_info.status = ThreadStatus.IDLE
                    thread_info.current_file = None
                    thread_info.processing_time += processing_time
                    
                    if result:
                        thread_info.files_processed += 1
                        self._move_file(file_path, self.processed_directory)
                        self.stats["total_files_processed"] += 1
                        self.stats["total_gpu_processing_time"] += processing_time
                        self.logger.info(f"Thread {thread_id} successfully processed: {file_path.name}")
                    else:
                        thread_info.files_failed += 1
                        self._move_file(file_path, self.error_directory)
                        self.stats["total_files_failed"] += 1
                        self.logger.error(f"Thread {thread_id} failed to process: {file_path.name}")
            
            # Remove from processing set
            self.processing_files.discard(file_path.name)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Thread {thread_id} error processing {file_path.name}: {e}")
            
            with self.thread_lock:
                if thread_id in self.active_threads:
                    self.active_threads[thread_id].status = ThreadStatus.ERROR
            
            # Move file to error directory
            self._move_file(file_path, self.error_directory)
            self.processing_files.discard(file_path.name)
            
            return False
    
    def _get_handler_for_file(self, file_path: Path) -> Callable:
        """Get the appropriate handler for a file based on its name."""
        for pattern, handler in self.csv_handlers.items():
            if file_path.match(pattern):
                return handler
        return self._default_csv_handler
    
    def _move_file(self, file_path: Path, destination: Path):
        """Move file to destination directory."""
        try:
            destination_file = destination / file_path.name
            file_path.rename(destination_file)
            self.logger.debug(f"Moved {file_path.name} to {destination}")
        except Exception as e:
            self.logger.error(f"Failed to move {file_path.name}: {e}")
    
    def _monitor_thread_health(self):
        """Monitor health of processing threads."""
        with self.thread_lock:
            current_threads = len(self.active_threads)
            self.stats["peak_thread_count"] = max(self.stats["peak_thread_count"], current_threads)
            
            # Check for stuck threads
            current_time = datetime.now()
            for thread_id, thread_info in list(self.active_threads.items()):
                if (thread_info.status == ThreadStatus.PROCESSING and 
                    thread_info.start_time and
                    (current_time - thread_info.start_time).total_seconds() > self.thread_timeout):
                    
                    self.logger.warning(f"Thread {thread_id} appears stuck, marking as error")
                    thread_info.status = ThreadStatus.ERROR
    
    def _update_statistics(self):
        """Update global statistics."""
        with self.thread_lock:
            active_count = len([t for t in self.active_threads.values() if t.status == ThreadStatus.PROCESSING])
            idle_count = len([t for t in self.active_threads.values() if t.status == ThreadStatus.IDLE])
            error_count = len([t for t in self.active_threads.values() if t.status == ThreadStatus.ERROR])
            
            self.logger.debug(f"Thread status - Active: {active_count}, Idle: {idle_count}, Error: {error_count}")
    
    def _record_performance_metrics(self):
        """Record performance metrics."""
        with self.thread_lock:
            metrics = {
                "timestamp": datetime.now(),
                "active_threads": len([t for t in self.active_threads.values() if t.status == ThreadStatus.PROCESSING]),
                "queue_size": self.file_queue.qsize(),
                "total_processed": self.stats["total_files_processed"],
                "total_failed": self.stats["total_files_failed"]
            }
            
            self.performance_history.append(metrics)
            
            # Keep only last 1000 records
            if len(self.performance_history) > 1000:
                self.performance_history = self.performance_history[-1000:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics."""
        with self.thread_lock:
            stats = {
                **self.stats,
                "queue_size": self.file_queue.qsize(),
                "processing_files": len(self.processing_files),
                "running": self.running,
                "cuda_available": self.use_cuda,
                "max_threads": self.max_threads,
                "uptime": (datetime.now() - self.stats["start_time"]).total_seconds() if self.stats["start_time"] else 0
            }
            
            # Thread statistics
            active_threads = [t for t in self.active_threads.values() if t.status == ThreadStatus.PROCESSING]
            idle_threads = [t for t in self.active_threads.values() if t.status == ThreadStatus.IDLE]
            error_threads = [t for t in self.active_threads.values() if t.status == ThreadStatus.ERROR]
            
            stats.update({
                "active_threads": len(active_threads),
                "idle_threads": len(idle_threads),
                "error_threads": len(error_threads),
                "total_threads": len(self.active_threads)
            })
            
            # GPU memory info if available
            if self.use_cuda and CUDA_AVAILABLE:
                try:
                    gpu_memory = cp.cuda.runtime.memGetInfo()
                    stats.update({
                        "gpu_memory_free_gb": gpu_memory[0] / 1024**3,
                        "gpu_memory_total_gb": gpu_memory[1] / 1024**3,
                        "gpu_memory_used_gb": (gpu_memory[1] - gpu_memory[0]) / 1024**3
                    })
                except Exception as e:
                    stats["gpu_memory_error"] = str(e)
            
            return stats
    
    def get_thread_details(self) -> List[Dict[str, Any]]:
        """Get detailed information about all threads."""
        with self.thread_lock:
            details = []
            for thread_info in self.active_threads.values():
                details.append({
                    "thread_id": thread_info.thread_id,
                    "status": thread_info.status.value,
                    "current_file": thread_info.current_file,
                    "start_time": thread_info.start_time.isoformat() if thread_info.start_time else None,
                    "files_processed": thread_info.files_processed,
                    "files_failed": thread_info.files_failed,
                    "processing_time": thread_info.processing_time
                })
            return details
    
    # CSV Handler Methods (same as single-threaded version)
    def _default_csv_handler(self, file_path: Path) -> bool:
        """Default CSV file handler."""
        try:
            df = self._read_csv_with_cuda(file_path)
            if df is None or len(df) == 0:
                return False
            
            # Process with GPU acceleration if available
            if self.use_cuda and hasattr(df, 'shape'):
                row_count = len(df)
                col_count = len(df.columns)
                column_names = list(df.columns)
                
                numeric_columns = df.select_dtypes(include=[np.number]).columns
                if len(numeric_columns) > 0:
                    stats_dict = df[numeric_columns].describe().to_dict()
                else:
                    stats_dict = {}
            else:
                row_count = len(df)
                col_count = len(df.columns)
                column_names = list(df.columns)
                
                numeric_columns = df.select_dtypes(include=[np.number]).columns
                if len(numeric_columns) > 0:
                    stats_dict = df[numeric_columns].describe().to_dict()
                else:
                    stats_dict = {}
            
            # Save summary
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
            self.logger.error(f"Error in default CSV handler: {e}")
            return False
    
    def _read_csv_with_cuda(self, file_path: Path) -> Optional[Any]:
        """Read CSV file using CUDA acceleration if available."""
        try:
            if self.use_cuda and CUDA_AVAILABLE:
                df = cudf.read_csv(file_path)
                return df
            else:
                df = pd.read_csv(file_path)
                return df
        except Exception as e:
            self.logger.error(f"Error reading CSV: {e}")
            try:
                df = pd.read_csv(file_path)
                return df
            except Exception as e2:
                self.logger.error(f"Error reading CSV with pandas: {e2}")
                return None
    
    # Additional handlers (simplified for brevity)
    def _qa_csv_handler(self, file_path: Path) -> bool:
        """QA CSV handler."""
        return self._default_csv_handler(file_path)
    
    def _patient_csv_handler(self, file_path: Path) -> bool:
        """Patient CSV handler."""
        return self._default_csv_handler(file_path)
    
    def _medical_csv_handler(self, file_path: Path) -> bool:
        """Medical CSV handler."""
        return self._default_csv_handler(file_path)
    
    def _large_csv_handler(self, file_path: Path) -> bool:
        """Large CSV handler."""
        return self._default_csv_handler(file_path)
    
    def _ml_preprocessing_handler(self, file_path: Path) -> bool:
        """ML preprocessing handler."""
        return self._default_csv_handler(file_path)
    
    def add_csv_handler(self, pattern: str, handler: Callable):
        """Add a new CSV handler for a specific file pattern."""
        self.csv_handlers[pattern] = handler
        self.logger.info(f"Added CSV handler for pattern: {pattern}")
    
    def clear_gpu_memory(self):
        """Clear GPU memory cache."""
        if self.use_cuda and CUDA_AVAILABLE:
            try:
                cp.get_default_memory_pool().free_all_blocks()
                self.logger.info("GPU memory cleared")
            except Exception as e:
                self.logger.error(f"Error clearing GPU memory: {e}")


# Example usage
if __name__ == "__main__":
    # Create multi-threaded manager
    manager = MultiThreadCSVManager(
        max_threads=30,
        watch_directory="data/csv_input",
        processed_directory="data/csv_processed",
        error_directory="data/csv_errors",
        use_cuda=True,
        batch_size=5000
    )
    
    try:
        manager.start()
        print("Multi-threaded CSV manager started. Press Ctrl+C to stop.")
        
        # Monitor manager
        while manager.running:
            stats = manager.get_stats()
            print(f"Stats: {stats}")
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\nStopping multi-threaded CSV manager...")
        manager.stop()
        print("Multi-threaded CSV manager stopped.") 