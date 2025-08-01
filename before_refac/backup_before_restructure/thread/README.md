# CSV File Handler Thread

A robust, thread-based CSV file processing system designed for the Healthcare AI project. This thread continuously monitors a directory for new CSV files and processes them according to configurable handlers.

## Features

- **Continuous Monitoring**: Automatically detects and processes new CSV files
- **Multiple Handler Types**: Different processing logic for various CSV formats
- **Error Handling**: Graceful error handling with file categorization
- **Statistics Tracking**: Real-time processing statistics
- **Extensible**: Easy to add custom handlers for specific file patterns
- **Thread-Safe**: Proper thread management and queue-based processing

## Quick Start

### Basic Usage

```python
from thread import CSVFileThread

# Create and start the thread
csv_thread = CSVFileThread(
    watch_directory="data/csv_input",
    processed_directory="data/csv_processed",
    error_directory="data/csv_errors"
)

csv_thread.start()

# Stop the thread when done
csv_thread.stop()
csv_thread.join()
```

### Run Example

```bash
cd thread
python example_usage.py
```

## Configuration

### Directory Structure

The thread creates and manages these directories:

```
data/
├── csv_input/          # Place CSV files here for processing
├── csv_processed/      # Successfully processed files
└── csv_errors/         # Files that failed processing
```

### Handler Types

The thread includes built-in handlers for different CSV types:

1. **Default Handler** (`*.csv`): General CSV processing
2. **QA Handler** (`qa_*.csv`): Question-Answer format
3. **Patient Handler** (`patient_*.csv`): Patient data format
4. **Medical Handler** (`medical_*.csv`): Medical records format

### CSV Format Examples

#### QA Format
```csv
question,answer
What is diabetes?,Diabetes is a chronic disease...
How to treat hypertension?,Hypertension can be treated with...
```

#### Patient Format
```csv
patient_id,name,age,diagnosis
P001,John Doe,45,Hypertension
P002,Jane Smith,32,Diabetes
```

#### Medical Format
```csv
record_id,symptom,severity,treatment
M001,Fever,Mild,Rest
M002,Cough,Moderate,Cough syrup
```

## Advanced Usage

### Custom Handlers

```python
def my_custom_handler(file_path):
    """Custom CSV processing logic."""
    # Your processing code here
    return True  # Return True for success, False for failure

# Add custom handler
csv_thread.add_csv_handler("custom_*.csv", my_custom_handler)
```

### Custom Configuration

```python
csv_thread = CSVFileThread(
    watch_directory="my_input_dir",
    processed_directory="my_processed_dir",
    error_directory="my_error_dir",
    polling_interval=2.0,  # Check every 2 seconds
    csv_handlers={
        "my_*.csv": my_custom_handler,
        "*.csv": default_handler
    }
)
```

### Monitoring Statistics

```python
# Get current statistics
stats = csv_thread.get_stats()
print(f"Files processed: {stats['files_processed']}")
print(f"Files failed: {stats['files_failed']}")
print(f"Queue size: {stats['queue_size']}")
print(f"Uptime: {stats['uptime']} seconds")
```

## API Reference

### CSVFileThread Class

#### Constructor Parameters

- `watch_directory` (str): Directory to monitor for CSV files
- `processed_directory` (str): Directory for successfully processed files
- `error_directory` (str): Directory for failed files
- `polling_interval` (float): How often to check for new files (seconds)
- `csv_handlers` (dict): Custom handlers mapping file patterns to functions

#### Methods

- `start()`: Start the monitoring thread
- `stop()`: Stop the thread gracefully
- `join(timeout=None)`: Wait for thread to finish
- `get_stats()`: Get current processing statistics
- `add_csv_handler(pattern, handler)`: Add custom handler

### Handler Functions

Handler functions should:
- Accept a `Path` object as the file path
- Return `True` for success, `False` for failure
- Handle their own exceptions

```python
def my_handler(file_path: Path) -> bool:
    try:
        # Process the CSV file
        return True
    except Exception as e:
        logger.error(f"Error processing {file_path}: {e}")
        return False
```

## Integration with Healthcare AI

This thread integrates seamlessly with the existing Healthcare AI architecture:

- Uses the project's logging system (`utils.logger`)
- Uses the project's file handling utilities (`utils.file_handler`)
- Follows the project's clean architecture principles
- Processes healthcare-specific data formats

### Integration Example

```python
from src.rag.rag_pipeline import RAGPipeline
from thread import CSVFileThread

# Initialize RAG pipeline
rag_pipeline = RAGPipeline()

def healthcare_csv_handler(file_path):
    """Process healthcare CSV and add to RAG pipeline."""
    # Process CSV data
    # Add to vector store
    # Update RAG pipeline
    return True

# Create CSV thread with healthcare handler
csv_thread = CSVFileThread(
    csv_handlers={"healthcare_*.csv": healthcare_csv_handler}
)
```

## Error Handling

The thread provides comprehensive error handling:

1. **File Processing Errors**: Failed files are moved to error directory
2. **Handler Errors**: Individual handler exceptions are logged
3. **Thread Errors**: Main thread loop errors are caught and logged
4. **File System Errors**: Directory creation and file movement errors are handled

## Logging

The thread uses the project's logging system:

- Info level: File processing events
- Warning level: Non-critical issues
- Error level: Processing failures
- Debug level: Detailed processing information

Logs are written to both console and `logs/app.log`.

## Performance Considerations

- **Polling Interval**: Adjust based on your needs (1-5 seconds recommended)
- **File Queue**: Large files are queued to prevent blocking
- **Memory Usage**: Files are processed one at a time
- **Thread Safety**: Proper synchronization for shared resources

## Testing

Run the example to test the thread:

```bash
python example_usage.py
```

This will:
1. Create sample CSV files
2. Start the thread
3. Monitor processing
4. Show results

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure `src` directory is in Python path
2. **Permission Errors**: Check directory write permissions
3. **File Locking**: Ensure CSV files aren't open in other applications
4. **Memory Issues**: Process large files in chunks if needed

### Debug Mode

Enable debug logging for detailed information:

```python
import logging
logging.getLogger('thread').setLevel(logging.DEBUG)
```

## Contributing

To add new handlers or modify existing ones:

1. Follow the existing handler pattern
2. Add proper error handling
3. Include logging statements
4. Update this documentation
5. Test with sample data 