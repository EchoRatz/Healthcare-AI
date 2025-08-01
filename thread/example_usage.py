"""
Example usage of CSV File Handler Thread.
"""

import time
import pandas as pd
from pathlib import Path
from thread import CSVFileThread


def create_sample_csv_files():
    """Create sample CSV files for testing."""
    
    # Create directories
    csv_input_dir = Path("data/csv_input")
    csv_input_dir.mkdir(parents=True, exist_ok=True)
    
    # Sample QA data
    qa_data = {
        'question': [
            'What is diabetes?',
            'How to treat hypertension?',
            'What are the symptoms of flu?'
        ],
        'answer': [
            'Diabetes is a chronic disease that affects how your body turns food into energy.',
            'Hypertension can be treated with lifestyle changes and medication.',
            'Flu symptoms include fever, cough, sore throat, and body aches.'
        ]
    }
    
    # Sample patient data
    patient_data = {
        'patient_id': ['P001', 'P002', 'P003'],
        'name': ['John Doe', 'Jane Smith', 'Bob Johnson'],
        'age': [45, 32, 58],
        'diagnosis': ['Hypertension', 'Diabetes', 'Asthma']
    }
    
    # Sample medical data
    medical_data = {
        'record_id': ['M001', 'M002', 'M003'],
        'symptom': ['Fever', 'Cough', 'Headache'],
        'severity': ['Mild', 'Moderate', 'Severe'],
        'treatment': ['Rest', 'Cough syrup', 'Pain reliever']
    }
    
    # Create CSV files
    pd.DataFrame(qa_data).to_csv(csv_input_dir / "qa_sample.csv", index=False)
    pd.DataFrame(patient_data).to_csv(csv_input_dir / "patient_sample.csv", index=False)
    pd.DataFrame(medical_data).to_csv(csv_input_dir / "medical_sample.csv", index=False)
    
    print("Created sample CSV files:")
    print("- qa_sample.csv")
    print("- patient_sample.csv") 
    print("- medical_sample.csv")


def custom_csv_handler(file_path):
    """Custom CSV handler example."""
    print(f"Custom handler processing: {file_path.name}")
    return True


def main():
    """Main example function."""
    
    print("=== CSV File Handler Thread Example ===\n")
    
    # Create sample files
    print("1. Creating sample CSV files...")
    create_sample_csv_files()
    
    # Create custom handlers
    custom_handlers = {
        "custom_*.csv": custom_csv_handler
    }
    
    # Initialize CSV thread
    print("\n2. Starting CSV file handling thread...")
    csv_thread = CSVFileThread(
        watch_directory="data/csv_input",
        processed_directory="data/csv_processed",
        error_directory="data/csv_errors",
        polling_interval=1.0,
        csv_handlers=custom_handlers
    )
    
    # Add custom handler
    csv_thread.add_csv_handler("test_*.csv", custom_csv_handler)
    
    try:
        # Start the thread
        csv_thread.start()
        
        # Monitor for 30 seconds
        print("3. Monitoring thread for 30 seconds...")
        for i in range(30):
            stats = csv_thread.get_stats()
            print(f"   Time: {i+1}s - Files processed: {stats['files_processed']}, "
                  f"Failed: {stats['files_failed']}, Queue: {stats['queue_size']}")
            time.sleep(1)
            
            # Create additional test file after 10 seconds
            if i == 10:
                print("\n4. Creating additional test file...")
                test_data = {'test_col': ['test_value']}
                pd.DataFrame(test_data).to_csv("data/csv_input/test_sample.csv", index=False)
        
        # Final stats
        print("\n5. Final statistics:")
        final_stats = csv_thread.get_stats()
        for key, value in final_stats.items():
            print(f"   {key}: {value}")
            
    except KeyboardInterrupt:
        print("\nStopping thread...")
    finally:
        # Stop the thread
        csv_thread.stop()
        csv_thread.join(timeout=5)
        print("Thread stopped.")
        
        # Show results
        print("\n6. Processing results:")
        processed_dir = Path("data/csv_processed")
        if processed_dir.exists():
            print("   Processed files:")
            for file in processed_dir.glob("*"):
                print(f"     - {file.name}")
        
        error_dir = Path("data/csv_errors")
        if error_dir.exists():
            print("   Error files:")
            for file in error_dir.glob("*"):
                print(f"     - {file.name}")


if __name__ == "__main__":
    main() 