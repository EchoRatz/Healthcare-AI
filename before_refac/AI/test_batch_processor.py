#!/usr/bin/env python3
"""
Test script to verify batch processor can find and validate test.csv
"""

import os
import sys
import csv


def test_find_csv():
    """Test finding test.csv file"""
    print("🔍 Testing CSV file detection...")
    
    # Check possible locations
    possible_paths = ["test.csv", "../test.csv", "AI/test.csv"]
    found_files = []
    
    for path in possible_paths:
        if os.path.exists(path):
            found_files.append(path)
            print(f"   ✅ Found: {path}")
        else:
            print(f"   ❌ Not found: {path}")
    
    if found_files:
        print(f"\n📁 Will use: {found_files[0]}")
        return found_files[0]
    else:
        print("\n❌ No test.csv file found!")
        return None


def test_csv_format(csv_path):
    """Test CSV format validation"""
    if not csv_path:
        return False
        
    print(f"\n📋 Testing CSV format: {csv_path}")
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            # Check headers
            if 'id' not in reader.fieldnames:
                print("   ❌ Missing 'id' column")
                return False
            
            if 'question' not in reader.fieldnames:
                print("   ❌ Missing 'question' column")
                return False
                
            print("   ✅ Headers OK")
            
            # Check first few rows
            row_count = 0
            for row in reader:
                if not row['id'] or not row['question']:
                    print(f"   ❌ Empty data in row {row_count + 1}")
                    return False
                
                row_count += 1
                if row_count >= 3:
                    break
            
            print(f"   ✅ Data OK (checked {row_count} rows)")
            
            # Count total rows
            file.seek(0)
            reader = csv.DictReader(file)
            total_rows = sum(1 for row in reader)
            print(f"   📊 Total questions: {total_rows}")
            
            return True
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_import():
    """Test importing the batch processor"""
    print("\n🔧 Testing module import...")
    
    try:
        from batch_test_processor import validate_csv_format, preview_csv
        print("   ✅ Import successful")
        return True
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False


def test_validation_function(csv_path):
    """Test the validation function from batch processor"""
    if not csv_path:
        return
        
    print(f"\n🧪 Testing validation function...")
    
    try:
        from batch_test_processor import validate_csv_format
        
        is_valid, message = validate_csv_format(csv_path)
        
        if is_valid:
            print(f"   ✅ {message}")
        else:
            print(f"   ❌ {message}")
            
    except Exception as e:
        print(f"   ❌ Validation test failed: {e}")


def main():
    """Run all tests"""
    print("🧪 Batch Processor Test Suite")
    print("=" * 50)
    
    # Test 1: Find CSV file
    csv_path = test_find_csv()
    
    # Test 2: Test CSV format
    format_ok = test_csv_format(csv_path)
    
    # Test 3: Test imports
    import_ok = test_import()
    
    # Test 4: Test validation function
    if import_ok and csv_path:
        test_validation_function(csv_path)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"   CSV File Found: {'✅' if csv_path else '❌'}")
    print(f"   CSV Format OK: {'✅' if format_ok else '❌'}")
    print(f"   Module Import: {'✅' if import_ok else '❌'}")
    
    if csv_path and format_ok and import_ok:
        print("\n🎉 All tests passed! Ready to process test.csv")
        print("\n💡 Next steps:")
        print("   python batch_test_processor.py --help")
        print("   python batch_test_processor.py --sample")
        print("   python batch_test_processor.py")
    else:
        print("\n⚠️  Some tests failed. Check the issues above.")


if __name__ == "__main__":
    main()