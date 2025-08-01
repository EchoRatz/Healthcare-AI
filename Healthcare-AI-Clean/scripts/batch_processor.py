"""Main entry point for batch processing."""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from infrastructure.repositories.CsvQuestionRepository import CsvQuestionRepository
from infrastructure.services.SimpleAnswerService import SimpleAnswerService
from infrastructure.config.Settings import settings
from core.use_cases.ProcessCsvBatch import ProcessCsvBatch


def find_input_file(args: list) -> str:
    """Find input CSV file."""
    if len(args) > 0:
        return args[0]
    
    # Look for default files
    possible_paths = [
        "data/input/test.csv",
        "test.csv", 
        "../test.csv",
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return "data/input/test.csv"


def main():
    """Main entry point for batch processing."""
    args = sys.argv[1:]
    
    # Parse arguments
    input_file = find_input_file(args)
    output_file = args[1] if len(args) > 1 else "data/output/batch_answers.csv"
    batch_size = int(args[2]) if len(args) > 2 else settings.default_batch_size
    
    print("🎯 Healthcare AI - Batch Processor")
    print("=" * 50)
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        print("Usage: python scripts/batch_processor.py [input.csv] [output.csv] [batch_size]")
        return
    
    # Initialize components
    question_repo = CsvQuestionRepository()
    answer_service = SimpleAnswerService()
    batch_processor = ProcessCsvBatch(question_repo, answer_service)
    
    # Validate input
    is_valid, message = question_repo.validate_csv_format(input_file)
    if not is_valid:
        print(f"❌ {message}")
        return
    
    print(f"✅ {message}")
    print(f"📝 Input: {input_file}")
    print(f"💾 Output: {output_file}")
    print(f"📦 Batch size: {batch_size}")
    
    # Confirm processing
    if "--auto" not in args and "-y" not in args:
        response = input("\nContinue? (y/n): ").lower()
        if response not in ['y', 'yes']:
            print("❌ Processing cancelled")
            return
    
    # Process questions
    try:
        result = batch_processor.execute(input_file, output_file, batch_size)
        
        print(f"\n🎉 Processing complete!")
        print(f"📊 {result.get_summary()}")
        
    except Exception as e:
        print(f"❌ Error during processing: {str(e)}")


if __name__ == "__main__":
    main()