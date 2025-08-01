"""
File-Based Thread System - Persistent CSV processing with file-based state management.
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
import json
import pickle
import sqlite3
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

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


class ThreadState(Enum):
    """Thread state enumeration."""
    IDLE = "idle"
    PROCESSING = "processing"
    ERROR = "error"
    STOPPED = "stopped"
    PAUSED = "paused"


@dataclass
class FileTask:
    """Represents a file processing task."""
    file_path: str
    file_hash: str
    priority: int = 0
    created_at: str = None
    started_at: str = None
    completed_at: str = None
    status: str = "pending"
    retry_count: int = 0
    max_retries: int = 3
    error_message: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


@dataclass
class ThreadCheckpoint:
    """Thread checkpoint for persistence."""
    thread_id: str
    state: ThreadState
    current_task: Optional[str] = None
    start_time: str = None
    files_processed: int = 0
    files_failed: int = 0
    total_processing_time: float = 0.0
    last_checkpoint: str = None
    
    def __post_init__(self):
        if self.start_time is None:
            self.start_time = datetime.now().isoformat()
        if self.last_checkpoint is None:
            self.last_checkpoint = datetime.now().isoformat()


class FileBasedThreadManager:
    """
    File-based thread manager with persistent state and checkpointing.
    
    Features:
    - Persistent task queue stored in files
    - Thread state checkpointing
    - Resume processing after restart
    - File-based progress tracking
    - SQLite database for task management
    - Hash-based file deduplication
    """
    
    def __init__(self,
                 thread_id: str,
                 base_directory: str = "thread_data",
                 watch_directory: str = "data/csv_input",
                 processed_directory: str = "data/csv_processed",
                 error_directory: str = "data/csv_errors",
                 checkpoint_interval: int = 30,
                 use_cuda: bool = True,
                 batch_size: int = 5000):
        """
        Initialize file-based thread manager.
        
        Args:
            thread_id: Unique identifier for this thread
            base_directory: Directory for storing thread data
            watch_directory: Directory to monitor for CSV files
            processed_directory: Directory for successfully processed files
            error_directory: Directory for failed files
            checkpoint_interval: How often to save checkpoints (seconds)
            use_cuda: Whether to use CUDA acceleration
            batch_size: Batch size for GPU processing
        """
        self.thread_id = thread_id
        self.base_directory = Path(base_directory)
        self.watch_directory = Path(watch_directory)
        self.processed_directory = Path(processed_directory)
        self.error_directory = Path(error_directory)
        self.checkpoint_interval = checkpoint_interval
        self.use_cuda = use_cuda and CUDA_AVAILABLE
        self.batch_size = batch_size
        
        # Thread control
        self.running = False
        self.paused = False
        
        # Setup logging first
        self.logger = get_logger(f"{__name__}.{thread_id}")
        
        # File-based storage
        self._setup_directories()
        self._setup_database()
        
        # Task management
        self.task_queue = queue.Queue()
        self.current_task: Optional[FileTask] = None
        self.processed_files = set()
        
        # State management
        self.checkpoint = ThreadCheckpoint(
            thread_id=thread_id,
            state=ThreadState.IDLE
        )
        
        # CSV handlers
        self.csv_handlers = {
            "*.csv": self._default_csv_handler,
            "qa_*.csv": self._qa_csv_handler,
            "patient_*.csv": self._patient_csv_handler,
            "medical_*.csv": self._medical_csv_handler,
            "large_*.csv": self._large_csv_handler,
            "ml_*.csv": self._ml_preprocessing_handler
        }
        
        # Load previous state if exists
        self._load_state()
    
    def _setup_directories(self):
        """Create necessary directories for file-based storage."""
        directories = [
            self.base_directory,
            self.base_directory / "checkpoints",
            self.base_directory / "tasks",
            self.base_directory / "logs",
            self.base_directory / "state",
            self.watch_directory,
            self.processed_directory,
            self.error_directory
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"Ensured directory exists: {directory}")
    
    def _setup_database(self):
        """Setup SQLite database for task management."""
        db_path = self.base_directory / "tasks.db"
        self.db_path = db_path
        
        with sqlite3.connect(db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE NOT NULL,
                    file_hash TEXT NOT NULL,
                    priority INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    started_at TEXT,
                    completed_at TEXT,
                    status TEXT DEFAULT 'pending',
                    retry_count INTEGER DEFAULT 0,
                    max_retries INTEGER DEFAULT 3,
                    error_message TEXT,
                    thread_id TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS checkpoints (
                    thread_id TEXT PRIMARY KEY,
                    state TEXT NOT NULL,
                    current_task TEXT,
                    start_time TEXT NOT NULL,
                    files_processed INTEGER DEFAULT 0,
                    files_failed INTEGER DEFAULT 0,
                    total_processing_time REAL DEFAULT 0.0,
                    last_checkpoint TEXT NOT NULL
                )
            """)
            
            conn.commit()
    
    def _load_state(self):
        """Load previous thread state from files."""
        checkpoint_file = self.base_directory / "checkpoints" / f"{self.thread_id}.json"
        
        if checkpoint_file.exists():
            try:
                with open(checkpoint_file, 'r') as f:
                    data = json.load(f)
                    self.checkpoint = ThreadCheckpoint(**data)
                    self.logger.info(f"Loaded previous state: {self.checkpoint.state}")
            except Exception as e:
                self.logger.error(f"Error loading checkpoint: {e}")
        
        # Load processed files list
        processed_file = self.base_directory / "state" / f"{self.thread_id}_processed.json"
        if processed_file.exists():
            try:
                with open(processed_file, 'r') as f:
                    self.processed_files = set(json.load(f))
                    self.logger.info(f"Loaded {len(self.processed_files)} processed files")
            except Exception as e:
                self.logger.error(f"Error loading processed files: {e}")
    
    def _save_checkpoint(self):
        """Save current thread state to file."""
        try:
            # Update checkpoint
            self.checkpoint.last_checkpoint = datetime.now().isoformat()
            
            # Save to JSON file
            checkpoint_file = self.base_directory / "checkpoints" / f"{self.thread_id}.json"
            with open(checkpoint_file, 'w') as f:
                json.dump(asdict(self.checkpoint), f, indent=2)
            
            # Save to database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO checkpoints 
                    (thread_id, state, current_task, start_time, files_processed, 
                     files_failed, total_processing_time, last_checkpoint)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.checkpoint.thread_id,
                    self.checkpoint.state.value,
                    self.checkpoint.current_task,
                    self.checkpoint.start_time,
                    self.checkpoint.files_processed,
                    self.checkpoint.files_failed,
                    self.checkpoint.total_processing_time,
                    self.checkpoint.last_checkpoint
                ))
                conn.commit()
            
            self.logger.debug(f"Checkpoint saved: {self.checkpoint.state}")
            
        except Exception as e:
            self.logger.error(f"Error saving checkpoint: {e}")
    
    def _save_processed_files(self):
        """Save list of processed files."""
        try:
            processed_file = self.base_directory / "state" / f"{self.thread_id}_processed.json"
            with open(processed_file, 'w') as f:
                json.dump(list(self.processed_files), f)
        except Exception as e:
            self.logger.error(f"Error saving processed files: {e}")
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file."""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            self.logger.error(f"Error calculating file hash: {e}")
            return ""
    
    def _add_task_to_database(self, file_path: Path) -> bool:
        """Add a new task to the database."""
        try:
            file_hash = self._calculate_file_hash(file_path)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR IGNORE INTO tasks 
                    (file_path, file_hash, created_at, status)
                    VALUES (?, ?, ?, ?)
                """, (
                    str(file_path),
                    file_hash,
                    datetime.now().isoformat(),
                    "pending"
                ))
                conn.commit()
            
            return True
        except Exception as e:
            self.logger.error(f"Error adding task to database: {e}")
            return False
    
    def _update_task_status(self, file_path: str, status: str, error_message: str = None):
        """Update task status in database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                if status == "processing":
                    conn.execute("""
                        UPDATE tasks SET status = ?, started_at = ?, thread_id = ?
                        WHERE file_path = ?
                    """, (status, datetime.now().isoformat(), self.thread_id, file_path))
                elif status in ["completed", "failed"]:
                    conn.execute("""
                        UPDATE tasks SET status = ?, completed_at = ?, error_message = ?
                        WHERE file_path = ?
                    """, (status, datetime.now().isoformat(), error_message, file_path))
                else:
                    conn.execute("""
                        UPDATE tasks SET status = ? WHERE file_path = ?
                    """, (status, file_path))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Error updating task status: {e}")
    
    def _get_pending_tasks(self) -> List[FileTask]:
        """Get pending tasks from database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT file_path, file_hash, priority, created_at, retry_count, max_retries
                    FROM tasks 
                    WHERE status = 'pending' AND retry_count < max_retries
                    ORDER BY priority DESC, created_at ASC
                """)
                
                tasks = []
                for row in cursor.fetchall():
                    task = FileTask(
                        file_path=row[0],
                        file_hash=row[1],
                        priority=row[2],
                        created_at=row[3],
                        retry_count=row[4],
                        max_retries=row[5]
                    )
                    tasks.append(task)
                
                return tasks
        except Exception as e:
            self.logger.error(f"Error getting pending tasks: {e}")
            return []
    
    def start(self):
        """Start the file-based thread."""
        self.running = True
        self.paused = False
        self.checkpoint.state = ThreadState.IDLE
        self.checkpoint.start_time = datetime.now().isoformat()
        
        self.logger.info(f"Starting file-based thread: {self.thread_id}")
        self._save_checkpoint()
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        # Start checkpoint thread
        self.checkpoint_thread = threading.Thread(target=self._checkpoint_loop, daemon=True)
        self.checkpoint_thread.start()
    
    def stop(self):
        """Stop the file-based thread."""
        self.running = False
        self.checkpoint.state = ThreadState.STOPPED
        self._save_checkpoint()
        self.logger.info(f"Stopped file-based thread: {self.thread_id}")
    
    def pause(self):
        """Pause the thread."""
        self.paused = True
        self.checkpoint.state = ThreadState.PAUSED
        self._save_checkpoint()
        self.logger.info(f"Paused file-based thread: {self.thread_id}")
    
    def resume(self):
        """Resume the thread."""
        self.paused = False
        self.checkpoint.state = ThreadState.IDLE
        self._save_checkpoint()
        self.logger.info(f"Resumed file-based thread: {self.thread_id}")
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.running:
            try:
                if not self.paused:
                    self._scan_for_new_files()
                    self._process_pending_tasks()
                
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Error in monitor loop: {e}")
                time.sleep(1)
    
    def _checkpoint_loop(self):
        """Checkpoint saving loop."""
        while self.running:
            try:
                self._save_checkpoint()
                self._save_processed_files()
                time.sleep(self.checkpoint_interval)
            except Exception as e:
                self.logger.error(f"Error in checkpoint loop: {e}")
                time.sleep(self.checkpoint_interval)
    
    def _scan_for_new_files(self):
        """Scan watch directory for new CSV files."""
        try:
            for file_path in self.watch_directory.glob("*.csv"):
                if (file_path.is_file() and 
                    file_path.name not in self.processed_files and
                    not self._is_file_processed(file_path)):
                    
                    # Add to database
                    if self._add_task_to_database(file_path):
                        self.logger.info(f"Added new task: {file_path.name}")
                        
        except Exception as e:
            self.logger.error(f"Error scanning for new files: {e}")
    
    def _is_file_processed(self, file_path: Path) -> bool:
        """Check if file has been processed."""
        return ((self.processed_directory / file_path.name).exists() or
                (self.error_directory / file_path.name).exists())
    
    def _process_pending_tasks(self):
        """Process pending tasks from database."""
        if self.current_task is not None:
            return  # Already processing a task
        
        tasks = self._get_pending_tasks()
        if not tasks:
            return
        
        # Get next task
        task = tasks[0]
        self.current_task = task
        
        # Update task status
        self._update_task_status(task.file_path, "processing")
        
        # Update checkpoint
        self.checkpoint.state = ThreadState.PROCESSING
        self.checkpoint.current_task = task.file_path
        self._save_checkpoint()
        
        try:
            self.logger.info(f"Processing task: {task.file_path}")
            
            # Process the file
            start_time = time.time()
            result = self._process_csv_file(Path(task.file_path))
            processing_time = time.time() - start_time
            
            # Update statistics
            self.checkpoint.total_processing_time += processing_time
            
            if result:
                self.checkpoint.files_processed += 1
                self._move_file(Path(task.file_path), self.processed_directory)
                self._update_task_status(task.file_path, "completed")
                self.processed_files.add(Path(task.file_path).name)
                self.logger.info(f"Successfully processed: {task.file_path}")
            else:
                self.checkpoint.files_failed += 1
                self._move_file(Path(task.file_path), self.error_directory)
                self._update_task_status(task.file_path, "failed", "Processing failed")
                self.logger.error(f"Failed to process: {task.file_path}")
            
        except Exception as e:
            self.logger.error(f"Error processing task {task.file_path}: {e}")
            self.checkpoint.files_failed += 1
            self._update_task_status(task.file_path, "failed", str(e))
            self._move_file(Path(task.file_path), self.error_directory)
        
        finally:
            # Clear current task
            self.current_task = None
            self.checkpoint.state = ThreadState.IDLE
            self.checkpoint.current_task = None
            self._save_checkpoint()
    
    def _process_csv_file(self, file_path: Path) -> bool:
        """Process a single CSV file."""
        try:
            handler = self._get_handler_for_file(file_path)
            return handler(file_path)
        except Exception as e:
            self.logger.error(f"Error in CSV handler: {e}")
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
                "thread_id": self.thread_id,
                "rows": row_count,
                "columns": col_count,
                "column_names": column_names,
                "processing_method": "CUDA" if self.use_cuda else "CPU",
                "statistics": stats_dict
            }
            
            summary_file = self.processed_directory / f"{file_path.stem}_{self.thread_id}_summary.json"
            FileHandler.save_json(str(summary_file), summary)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error in default CSV handler: {e}")
            return False
    
    # Additional handlers (simplified)
    def _qa_csv_handler(self, file_path: Path) -> bool:
        return self._default_csv_handler(file_path)
    
    def _patient_csv_handler(self, file_path: Path) -> bool:
        return self._default_csv_handler(file_path)
    
    def _medical_csv_handler(self, file_path: Path) -> bool:
        return self._default_csv_handler(file_path)
    
    def _large_csv_handler(self, file_path: Path) -> bool:
        return self._default_csv_handler(file_path)
    
    def _ml_preprocessing_handler(self, file_path: Path) -> bool:
        return self._default_csv_handler(file_path)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get thread statistics."""
        return {
            "thread_id": self.thread_id,
            "state": self.checkpoint.state.value,
            "current_task": self.checkpoint.current_task,
            "files_processed": self.checkpoint.files_processed,
            "files_failed": self.checkpoint.files_failed,
            "total_processing_time": self.checkpoint.total_processing_time,
            "uptime": (datetime.now() - datetime.fromisoformat(self.checkpoint.start_time)).total_seconds(),
            "last_checkpoint": self.checkpoint.last_checkpoint,
            "running": self.running,
            "paused": self.paused,
            "cuda_available": self.use_cuda
        }
    
    def get_task_stats(self) -> Dict[str, Any]:
        """Get task statistics from database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT status, COUNT(*) as count
                    FROM tasks
                    GROUP BY status
                """)
                
                stats = {}
                for row in cursor.fetchall():
                    stats[row[0]] = row[1]
                
                return stats
        except Exception as e:
            self.logger.error(f"Error getting task stats: {e}")
            return {}
    
    def add_csv_handler(self, pattern: str, handler: Callable):
        """Add a new CSV handler for a specific file pattern."""
        self.csv_handlers[pattern] = handler
        self.logger.info(f"Added CSV handler for pattern: {pattern}")


# Example usage
if __name__ == "__main__":
    # Create file-based thread
    thread = FileBasedThreadManager(
        thread_id="thread_001",
        base_directory="thread_data",
        watch_directory="data/csv_input",
        processed_directory="data/csv_processed",
        error_directory="data/csv_errors",
        use_cuda=True
    )
    
    try:
        thread.start()
        print("File-based thread started. Press Ctrl+C to stop.")
        
        # Monitor thread
        while thread.running:
            stats = thread.get_stats()
            task_stats = thread.get_task_stats()
            print(f"Stats: {stats}")
            print(f"Task Stats: {task_stats}")
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\nStopping file-based thread...")
        thread.stop()
        print("File-based thread stopped.") 