import subprocess
import time
import sys

def run_step(step_name, script_name):
    print(f"=========================================")
    print(f"Starting {step_name} ({script_name})...")
    start_time = time.time()
    
    try:
        # Run the script using the current Python executable
        result = subprocess.run([sys.executable, script_name], check=True, text=True)
        elapsed = time.time() - start_time
        print(f"SUCCESS: {step_name} completed in {elapsed:.2f} seconds.")
    except subprocess.CalledProcessError as e:
        elapsed = time.time() - start_time
        print(f"FAILURE: {step_name} failed after {elapsed:.2f} seconds.")
        print(f"Error output:\n{e.stderr}")
        sys.exit(1)
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"FAILURE: {step_name} failed unexpectedly after {elapsed:.2f} seconds.")
        print(f"Error: {e}")
        sys.exit(1)

def main():
    print("Starting USPTO Patent Analytics Pipeline")
    
    steps = [
        ("Database Creation", "create_db.py"),
        ("Data Extraction", "extract_data.py"),
        ("Data Cleaning", "clean_data.py"),
        ("Data Loading", "load_data.py"),
        ("Export Results", "export_results.py")
    ]
    
    total_start_time = time.time()
    for step_name, script_name in steps:
        run_step(step_name, script_name)
        
    total_elapsed = time.time() - total_start_time
    print(f"=========================================")
    print(f"Pipeline completed successfully in {total_elapsed:.2f} seconds.")

if __name__ == "__main__":
    main()
