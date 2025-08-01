from thai_qa_processor import ThaiHealthcareQA
import time

def test_speed():
    """Test actual multithreading speed"""
    qa_system = ThaiHealthcareQA()
    
    print("🧪 Speed Test: Processing first 50 questions")
    
    # Test with smaller batch first
    start_time = time.time()
    qa_system.process_csv_multithreaded(
        'test.csv',
        'speed_test_50.csv',
        max_threads=4,  # Start with fewer threads
        clean_format=True
    )
    end_time = time.time()
    
    print(f"⚡ 50 questions in {end_time - start_time:.2f} seconds")
    print(f"📈 Rate: {50/(end_time - start_time):.2f} questions/second")

if __name__ == "__main__":
    test_speed()