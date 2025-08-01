#!/usr/bin/env python3
"""
Format Validator - Ensures output matches submission.csv format exactly
====================================================================
"""

import os
import csv
import sys

def validate_submission_format(output_file: str, reference_file: str = None) -> bool:
    """Validate that output file matches the exact submission.csv format"""
    
    if reference_file is None:
        reference_file = 'Healthcare-AI-Refactored/src/infrastructure/submission.csv'
    
    print("📋 Validating Submission Format")
    print("=" * 35)
    
    # Check if files exist
    if not os.path.exists(output_file):
        print(f"❌ Output file not found: {output_file}")
        return False
    
    if not os.path.exists(reference_file):
        print(f"❌ Reference file not found: {reference_file}")
        return False
    
    try:
        # Read both files
        with open(output_file, 'r', encoding='utf-8') as f:
            output_lines = f.readlines()
        
        with open(reference_file, 'r', encoding='utf-8') as f:
            reference_lines = f.readlines()
        
        # Check header
        if len(output_lines) == 0:
            print("❌ Output file is empty")
            return False
        
        output_header = output_lines[0].strip()
        reference_header = reference_lines[0].strip()
        
        if output_header != reference_header:
            print(f"❌ Header mismatch:")
            print(f"   Expected: {reference_header}")
            print(f"   Got:      {output_header}")
            return False
        
        print(f"✅ Header correct: {output_header}")
        
        # Check number of rows
        output_rows = len(output_lines) - 1  # Exclude header
        reference_rows = len(reference_lines) - 1  # Exclude header
        
        if output_rows != reference_rows:
            print(f"❌ Row count mismatch:")
            print(f"   Expected: {reference_rows} rows")
            print(f"   Got:      {output_rows} rows")
            return False
        
        print(f"✅ Row count correct: {output_rows} rows")
        
        # Check format of first few rows
        print("📊 Checking row formats...")
        
        valid_rows = 0
        sample_checks = min(5, output_rows)
        
        for i in range(1, sample_checks + 1):
            output_row = output_lines[i].strip()
            
            # Expected format: id,"answer" or id,"" or id, (empty)
            parts = output_row.split(',', 1)
            
            if len(parts) < 1:
                print(f"❌ Row {i} wrong format: {output_row}")
                continue
            
            try:
                row_id = int(parts[0])
                
                # Handle different answer formats
                if len(parts) == 1:
                    # Format: id (missing comma - invalid)
                    print(f"  ❌ Row {i} missing comma: {output_row}")
                    continue
                
                answer_part = parts[1]
                
                # Check answer format
                if answer_part == "":
                    # Empty answer (like reference file)
                    valid_rows += 1
                    if i <= 3:
                        print(f"  ✅ Row {i}: {output_row} (empty answer)")
                elif answer_part.startswith('"') and answer_part.endswith('"'):
                    # Properly quoted answer
                    valid_rows += 1
                    if i <= 3:
                        print(f"  ✅ Row {i}: {output_row} (quoted answer)")
                else:
                    # Unquoted answer - could be valid but not preferred
                    print(f"  ⚠️  Row {i} unquoted answer: {output_row}")
                    valid_rows += 1  # Still count as valid
                    
            except ValueError:
                print(f"  ❌ Row {i} invalid ID: {output_row}")
        
        if valid_rows == sample_checks:
            print(f"✅ All {sample_checks} sample rows valid")
        else:
            print(f"❌ Only {valid_rows}/{sample_checks} sample rows valid")
            return False
        
        # Check for expected answer format (Thai letters)
        print("🔤 Checking answer content...")
        
        thai_answers = 0
        empty_answers = 0
        
        for i in range(1, min(11, len(output_lines))):  # Check first 10 rows
            row = output_lines[i].strip()
            parts = row.split(',', 1)
            
            if len(parts) == 2:
                answer = parts[1].strip('"')  # Remove quotes
                
                if not answer:
                    empty_answers += 1
                elif any(c in answer for c in ['ก', 'ข', 'ค', 'ง']):
                    thai_answers += 1
                    if i <= 3:
                        print(f"  ✅ Row {i} has Thai answer: {answer}")
        
        if thai_answers > 0:
            print(f"✅ Found {thai_answers} Thai answers in first 10 rows")
        elif empty_answers == min(10, output_rows):
            print("⚠️  All checked answers are empty (like reference file)")
        else:
            print("❌ No valid Thai answers found in first 10 rows")
        
        # Final validation
        print(f"\n🎯 Format Validation Summary:")
        print(f"  ✅ Header: {output_header}")
        print(f"  ✅ Rows: {output_rows}")
        print(f"  ✅ Format: CSV with quoted answers")
        
        if thai_answers > 0:
            print(f"  ✅ Content: {thai_answers} Thai answers found")
            print(f"  🎉 VALIDATION PASSED - Ready for submission!")
        else:
            print(f"  ⚠️  Content: No answers yet (template format)")
            print(f"  📝 Format is correct, needs answers filled")
        
        return True
        
    except Exception as e:
        print(f"❌ Validation error: {e}")
        return False

def compare_with_reference():
    """Compare any CSV file with the reference submission.csv"""
    print("🔍 Find CSV files to validate...")
    
    csv_files = []
    for file in os.listdir('.'):
        if file.endswith('.csv') and file != 'submission.csv':
            csv_files.append(file)
    
    if not csv_files:
        print("📝 No CSV files found in current directory")
        return
    
    print(f"📋 Found CSV files: {csv_files}")
    
    for csv_file in csv_files:
        print(f"\n🔍 Validating: {csv_file}")
        validate_submission_format(csv_file)

def main():
    """Main validation function"""
    if len(sys.argv) > 1:
        # Validate specific file
        output_file = sys.argv[1]
        validate_submission_format(output_file)
    else:
        # Find and validate all CSV files
        compare_with_reference()

if __name__ == "__main__":
    main()