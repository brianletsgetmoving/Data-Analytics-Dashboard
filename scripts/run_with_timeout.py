#!/usr/bin/env python3
"""
Run a Python script with a timeout to prevent hanging.
"""

import sys
import subprocess
import signal
import os
from pathlib import Path

def run_with_timeout(script_path: str, timeout: int, args: list = None):
    """Run a Python script with timeout."""
    if args is None:
        args = []
    
    cmd = [sys.executable, script_path] + args
    
    try:
        # Start process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Wait with timeout
        try:
            stdout, _ = process.communicate(timeout=timeout)
            return_code = process.returncode
            print(stdout, end='')
            return return_code
        except subprocess.TimeoutExpired:
            process.kill()
            print(f"\nERROR: Script timed out after {timeout} seconds")
            return 124  # Timeout exit code
            
    except Exception as e:
        print(f"ERROR: Failed to run script: {e}")
        return 1


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: run_with_timeout.py <timeout_seconds> <script_path> [script_args...]")
        sys.exit(1)
    
    timeout = int(sys.argv[1])
    script_path = sys.argv[2]
    script_args = sys.argv[3:] if len(sys.argv) > 3 else []
    
    exit_code = run_with_timeout(script_path, timeout, script_args)
    sys.exit(exit_code)

