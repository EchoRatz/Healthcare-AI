#!/usr/bin/env python3
"""
Stop Current Process and Restart Optimized
=========================================

Stops the looping process and starts optimized version
"""

import os
import sys
import subprocess
import signal
import time

def stop_current_processes():
    """Stop any running Python processes that might be looping"""
    print("🛑 Stopping any looping processes...")
    
    try:
        # On Unix systems
        if os.name != 'nt':
            # Find Python processes running our scripts
            result = subprocess.run(['pgrep', '-f', 'llama31'], capture_output=True, text=True)
            if result.stdout:
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    if pid:
                        try:
                            os.kill(int(pid), signal.SIGTERM)
                            print(f"  ✅ Stopped process {pid}")
                        except:
                            pass
        else:
            # On Windows
            subprocess.run(['taskkill', '/f', '/im', 'python.exe'], capture_output=True)
            print("  ✅ Stopped Python processes")
            
    except Exception as e:
        print(f"  ⚠️  Could not stop processes: {e}")
    
    print("  ⏳ Waiting 2 seconds...")
    time.sleep(2)

def restart_optimized():
    """Start the optimized version"""
    print("\n🚀 Starting Optimized Version...")
    
    if os.path.exists('run_llama31_optimized.py'):
        print("✅ Found optimized runner")
        print("🎯 This version:")
        print("  - Processes embeddings ONCE (not per question)")
        print("  - Shows clear progress through 500 questions")  
        print("  - No infinite embedding loops")
        print("  - Much faster processing")
        
        response = input("\nStart optimized processing? (Y/n): ").strip().lower()
        if response not in ['n', 'no']:
            try:
                subprocess.run([sys.executable, 'run_llama31_optimized.py'])
            except KeyboardInterrupt:
                print("\n⏹️  Stopped by user")
            except Exception as e:
                print(f"❌ Error: {e}")
        else:
            print("Cancelled.")
    else:
        print("❌ Optimized runner not found")
        print("💡 Make sure run_llama31_optimized.py exists")

def main():
    """Main function"""
    print("🔄 Stop Looping & Restart Optimized")
    print("=" * 40)
    
    # Stop current processes
    stop_current_processes()
    
    # Restart with optimized version
    restart_optimized()

if __name__ == "__main__":
    main()