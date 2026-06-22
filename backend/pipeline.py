import subprocess
import sys
import os

def run_pipeline():
    base = os.path.dirname(os.path.abspath(__file__))
    
    scripts = [
        os.path.join(base, "fetcher", "fetch_matches.py"),
        os.path.join(base, "simulation", "ratings.py"),
        os.path.join(base, "simulation", "monte_carlo.py"),
    ]
    
    for script in scripts:
        print(f"\nRunning {os.path.basename(script)}...")
        result = subprocess.run([sys.executable, script], capture_output=True, text=True)
        print(result.stdout)
        if result.returncode != 0:
            print(f"ERROR: {result.stderr}")
            break
        print("Done.")

if __name__ == "__main__":
    run_pipeline()