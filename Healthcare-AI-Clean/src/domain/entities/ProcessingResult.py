"""Processing result entities."""
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class ProcessingStats:
    """Statistics for batch processing."""
    total_questions: int
    successful: int
    errors: int
    start_time: datetime
    end_time: Optional[datetime] = None
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_questions == 0:
            return 0.0
        return (self.successful / self.total_questions) * 100
    
    @property
    def duration(self) -> float:
        """Calculate processing duration in seconds."""
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0


@dataclass
class BatchResult:
    """Result of batch processing."""
    results: List[dict]
    stats: ProcessingStats
    output_file: str
    
    def get_summary(self) -> str:
        """Get processing summary."""
        return f"Processed {self.stats.total_questions} questions, " \
               f"Success rate: {self.stats.success_rate:.1f}%, " \
               f"Duration: {self.stats.duration:.2f}s"