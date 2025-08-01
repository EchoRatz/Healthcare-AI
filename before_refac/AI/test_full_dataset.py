#!/usr/bin/env python3
"""
Test the intelligent knowledge caching system with the full test.csv dataset
"""

from thai_qa_processor import ThaiHealthcareQA
import time


def test_full_dataset():
    """Test with the complete test.csv dataset"""
    print("=" * 60)
    print("Testing Intelligent Knowledge Caching with Full Dataset")
    print("=" * 60)
    print("Processing 500 questions from test.csv...")
    print("This will show how the AI learns from real healthcare data!")

    # Initialize the system
    print("\nInitializing Thai Healthcare Q&A System...")
    qa_system = ThaiHealthcareQA()

    # Show initial cache stats
    print("\nCurrent cache before processing test.csv:")
    qa_system.show_cache_stats()

    print("\nStarting batch processing of test.csv...")
    qa_system.process_csv_questions("test.csv", "test_answers_with_cache.csv")

    print("\nFinal cache after processing test.csv:")
    qa_system.show_cache_stats()

    # Process the full dataset
    print("\nStarting batch processing of test.csv...")
    print("This may take several minutes...")

    start_time = time.time()

    try:
        qa_system.process_csv_questions("test.csv", "test_answers_with_cache.csv")

        end_time = time.time()
        processing_time = end_time - start_time

        print(f"\nProcessing completed in {processing_time:.1f} seconds")

        # Show final cache stats
        print("\nFinal cache after processing test.csv:")
        qa_system.show_cache_stats()

        # Export the massive knowledge gained
        print("\nExporting learned knowledge...")
        qa_system.export_cache_to_text("full_dataset_learned_knowledge.txt")

        print("\n" + "=" * 60)
        print("SUCCESS! The AI has processed 500 healthcare questions")
        print("and built a comprehensive knowledge base!")
        print("=" * 60)

        # Show some sample answers
        print("\nSample of generated answers:")
        try:
            with open("test_answers_with_cache.csv", "r", encoding="utf-8") as f:
                lines = f.readlines()
                for i in range(min(3, len(lines) - 1)):  # Show first 3 answers
                    parts = lines[i + 1].strip().split(",", 2)  # Skip header
                    if len(parts) >= 3:
                        print(f"Q{parts[0]}: {parts[2][:100]}...")
        except Exception as e:
            print(f"Could not display sample answers: {e}")

    except Exception as e:
        print(f"Error during processing: {e}")
        print("Make sure Ollama is running and models are available")


if __name__ == "__main__":
    test_full_dataset()
