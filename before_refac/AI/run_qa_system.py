#!/usr/bin/env python3
"""
Master script to run the Thai Healthcare Q&A System
Provides multiple options for processing test.csv
"""

import os
import sys
import subprocess
from pathlib import Path


def show_banner():
    """Show system banner"""
    print("🎯 Thai Healthcare Q&A System")
    print("=" * 60)
    print("✅ Ready to process your test.csv with 500 questions")
    print("✅ Outputs only choice letters (ก, ข, ค, ง)")
    print("=" * 60)


def check_test_csv():
    """Check if test.csv exists"""
    if os.path.exists("test.csv"):
        print("📁 Found: test.csv")
        
        # Count lines
        with open("test.csv", 'r', encoding='utf-8') as f:
            lines = sum(1 for line in f)
        print(f"📊 Questions: {lines - 1}")  # -1 for header
        return True
    else:
        print("❌ test.csv not found in current directory")
        return False


def show_options():
    """Show available processing options"""
    print("\n🚀 Processing Options:")
    print()
    
    print("1️⃣  Demo Version (Working Now)")
    print("   python simple_csv_processor.py")
    print("   ✅ No setup required")
    print("   ✅ Processes all 500 questions")
    print("   ✅ Rule-based logic")
    print()
    
    print("2️⃣  AI-Powered Version (Full System)")
    print("   python batch_test_processor.py")
    print("   🤖 Uses AI reasoning")
    print("   📚 Healthcare knowledge base")
    print("   ⚠️  Requires setup (Ollama + models)")
    print()
    
    print("3️⃣  Quick Test (5 questions)")
    print("   python quick_batch_test.py")
    print("   🧪 Test with sample questions")
    print()
    
    print("4️⃣  Setup Full System")
    print("   python setup_system.py")
    print("   🔧 Install dependencies")
    print("   📦 Download AI models")
    print()
    
    print("5️⃣  Help & Documentation")
    print("   python batch_test_processor.py --help")
    print("   📖 Detailed usage guide")


def run_option(choice):
    """Run the selected option"""
    
    if choice == "1":
        print("\n🎯 Running Demo Version...")
        print("=" * 40)
        try:
            result = subprocess.run([sys.executable, "simple_csv_processor.py"], 
                                  capture_output=False)
            if result.returncode == 0:
                print("\n✅ Demo completed successfully!")
                if os.path.exists("simple_test_answers.csv"):
                    print("📁 Results saved to: simple_test_answers.csv")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    elif choice == "2":
        print("\n🤖 Running AI-Powered Version...")
        print("=" * 40)
        try:
            result = subprocess.run([sys.executable, "batch_test_processor.py"], 
                                  capture_output=False)
        except Exception as e:
            print(f"❌ Error: {e}")
            print("💡 Try running setup first: python setup_system.py")
    
    elif choice == "3":
        print("\n🧪 Running Quick Test...")
        print("=" * 40)
        try:
            result = subprocess.run([sys.executable, "quick_batch_test.py"], 
                                  capture_output=False)
        except Exception as e:
            print(f"❌ Error: {e}")
    
    elif choice == "4":
        print("\n🔧 Running System Setup...")
        print("=" * 40)
        try:
            result = subprocess.run([sys.executable, "setup_system.py"], 
                                  capture_output=False)
        except Exception as e:
            print(f"❌ Error: {e}")
    
    elif choice == "5":
        print("\n📖 Showing Help...")
        print("=" * 40)
        try:
            result = subprocess.run([sys.executable, "batch_test_processor.py", "--help"], 
                                  capture_output=False)
        except Exception as e:
            print(f"❌ Error: {e}")
    
    else:
        print("❌ Invalid choice")


def show_results_info():
    """Show information about available results"""
    print("\n📊 Available Results:")
    
    results_files = [
        ("simple_test_answers.csv", "Demo version results"),
        ("test_answers.csv", "AI-powered results"), 
        ("quick_test_answers.csv", "Quick test results")
    ]
    
    for filename, description in results_files:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"   ✅ {filename} - {description} ({size:,} bytes)")
        else:
            print(f"   ⚪ {filename} - {description} (not found)")


def main():
    """Main function"""
    
    show_banner()
    
    # Check for test.csv
    if not check_test_csv():
        print("\n💡 Please make sure test.csv is in the current directory")
        return
    
    # Show current results
    show_results_info()
    
    # Show options
    show_options()
    
    # Get user choice
    print("\n" + "=" * 60)
    choice = input("🤔 Choose an option (1-5, or 'q' to quit): ").strip()
    
    if choice.lower() == 'q':
        print("👋 Goodbye!")
        return
    
    if choice in ['1', '2', '3', '4', '5']:
        run_option(choice)
        
        # Show updated results
        print("\n" + "=" * 60)
        show_results_info()
        
        # Ask if user wants to run another option
        again = input("\n🔄 Run another option? (y/n): ").lower().strip()
        if again in ['y', 'yes']:
            main()
    else:
        print("❌ Invalid choice. Please choose 1-5 or 'q'")


def show_quick_status():
    """Show quick status for command line usage"""
    if len(sys.argv) > 1 and sys.argv[1] == '--status':
        print("🎯 Thai Healthcare Q&A System Status")
        print("=" * 40)
        
        if check_test_csv():
            print("✅ test.csv ready for processing")
        
        show_results_info()
        
        print("\n💡 Quick commands:")
        print("   python simple_csv_processor.py  # Demo (works now)")
        print("   python run_qa_system.py         # Interactive menu")
        return True
    
    return False


if __name__ == "__main__":
    if show_quick_status():
        pass  # Status shown, exit
    else:
        main()