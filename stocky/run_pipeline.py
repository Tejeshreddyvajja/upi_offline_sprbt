"""
Run the complete data pipeline for any stock ticker.
Usage: python run_pipeline.py TICKER
Example: python run_pipeline.py TSLA
"""
import sys
import subprocess
import os

def run_pipeline(ticker):
    """Run all pipeline steps for a given ticker."""
    ticker = ticker.upper()
    print(f"\n{'='*50}")
    print(f"Running pipeline for {ticker}")
    print(f"{'='*50}\n")
    
    # Get the python executable from the venv
    venv_python = os.path.join(".venv", "Scripts", "python.exe")
    if not os.path.exists(venv_python):
        venv_python = sys.executable  # Fallback to current python
    
    steps = [
        ("collect.py", "Collecting data"),
        ("clean.py", "Cleaning data"),
        ("feature_extraction.py", "Extracting features")
    ]
    
    for script, description in steps:
        print(f"\n>>> {description}...")
        result = subprocess.run(
            [venv_python, script, ticker],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.returncode != 0:
            print(f"[ERROR] {result.stderr}")
            return False
    
    print(f"\n{'='*50}")
    print(f"Pipeline completed for {ticker}!")
    print(f"Output: data/{ticker}_features.csv")
    print(f"{'='*50}\n")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_pipeline.py TICKER")
        print("Example: python run_pipeline.py TSLA")
        sys.exit(1)
    
    ticker = sys.argv[1]
    success = run_pipeline(ticker)
    sys.exit(0 if success else 1)
