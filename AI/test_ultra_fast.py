from thai_qa_processor import ThaiHealthcareQA
import time

def test_ultra_fast():
    """Test ultra-fast processing"""
    qa_system = ThaiHealthcareQA()
    
    print("🚀 ULTRA-FAST TEST: First 50 questions")
    
    start_time = time.time()
    qa_system.process_csv_ultra_fast(
        'test.csv',
        'ultra_fast_test.csv',
        max_threads=20  # Moderate threading to avoid I/O issues
    )
    end_time = time.time()
    
    print(f"🏁 Total time: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    test_ultra_fast()