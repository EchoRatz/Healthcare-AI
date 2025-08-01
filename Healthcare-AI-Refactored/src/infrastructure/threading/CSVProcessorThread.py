"""CSV processor thread implementation."""

import threading
import time
import queue
from pathlib import Path
from typing import Optional, Callable, Dict
from ...shared.logging.LoggerMixin import get_logger


class CSVProcessorThread(threading.Thread):
    """Thread for processing CSV files."""
    
    def __init__(self,
                 watch_directory: str = "data/csv_input",
                 processed_directory: str = "data/csv_processed",
                 error_directory: str = "data/csv_errors",
                 polling_interval: float = 1.0,
                 csv_handler: Optional[Callable] = None):
        super().__init__(daemon=True)
        
        self.watch_directory = Path(watch_directory)
        self.processed_directory = Path(processed_directory)
        self.error_directory = Path(error_directory)
        self.polling_interval = polling_interval
        self.csv_handler = csv_handler or self._default_handler
        
        self.running = False
        self.file_queue = queue.Queue()
        self.logger = get_logger(__name__)
        self.stats = {
            'files_processed': 0,
            'files_failed': 0,
            'start_time': None
        }
        
        self._setup_directories()
    
    def run(self):
        """Main thread loop."""
        self.running = True
        self.stats['start_time'] = time.time()
        self.logger.info("CSV processor thread started")
        
        try:
            while self.running:
                self._scan_for_files()
                self._process_queue()
                time.sleep(self.polling_interval)
                
        except Exception as e:
            self.logger.error(f"CSV processor thread error: {e}")
        finally:
            self.logger.info("CSV processor thread stopped")
    
    def stop(self):
        """Stop the thread gracefully."""
        self.running = False
        self.logger.info("Stopping CSV processor thread...")
    
    def get_stats(self) -> Dict:
        """Get processing statistics."""
        uptime = time.time() - self.stats['start_time'] if self.stats['start_time'] else 0
        return {
            **self.stats,
            'uptime': uptime,
            'queue_size': self.file_queue.qsize()
        }
    
    def _setup_directories(self):
        """Create necessary directories."""
        for directory in [self.watch_directory, self.processed_directory, self.error_directory]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _scan_for_files(self):
        """Scan for new CSV files."""
        try:
            for file_path in self.watch_directory.glob("*.csv"):
                if file_path.is_file() and not self._is_being_processed(file_path):
                    self.file_queue.put(file_path)
                    self.logger.info(f"Queued file: {file_path.name}")
        except Exception as e:
            self.logger.error(f"Error scanning files: {e}")
    
    def _process_queue(self):
        """Process files in queue."""
        while not self.file_queue.empty() and self.running:
            try:
                file_path = self.file_queue.get_nowait()
                self._process_file(file_path)
                self.file_queue.task_done()
            except queue.Empty:
                break
            except Exception as e:
                self.logger.error(f"Error processing queue: {e}")
    
    def _process_file(self, file_path: Path):
        """Process a single CSV file."""
        try:
            success = self.csv_handler(file_path)
            
            if success:
                self._move_file(file_path, self.processed_directory)
                self.stats['files_processed'] += 1
                self.logger.info(f"Successfully processed: {file_path.name}")
            else:
                self._move_file(file_path, self.error_directory)
                self.stats['files_failed'] += 1
                self.logger.error(f"Failed to process: {file_path.name}")
                
        except Exception as e:
            self.logger.error(f"Error processing {file_path.name}: {e}")
            self._move_file(file_path, self.error_directory)
            self.stats['files_failed'] += 1
    
    def _move_file(self, file_path: Path, destination: Path):
        """Move file to destination."""
        try:
            destination_file = destination / file_path.name
            file_path.rename(destination_file)
        except Exception as e:
            self.logger.error(f"Failed to move {file_path.name}: {e}")
    
    def _is_being_processed(self, file_path: Path) -> bool:
        """Check if file is being processed."""
        processed_file = self.processed_directory / file_path.name
        error_file = self.error_directory / file_path.name
        return processed_file.exists() or error_file.exists()
    
    def _default_handler(self, file_path: Path) -> bool:
        """Default CSV handler."""
        try:
            # Simple validation - check if file can be read
            with open(file_path, 'r', encoding='utf-8') as f:
                f.readline()  # Try to read first line
            return True
        except Exception:
            return False