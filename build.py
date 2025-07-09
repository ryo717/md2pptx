#!/usr/bin/env python3
"""Build script for creating md2pptx executable"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def build():
    """Build the executable using PyInstaller"""
    print("Building md2pptx executable...")
    
    # Clean previous builds
    for dir_name in ["build", "dist"]:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Cleaned {dir_name}/")
    
    # Create templates directory if it doesn't exist
    templates_dir = Path("templates")
    if not templates_dir.exists():
        templates_dir.mkdir()
        print("Created templates directory")
    
    # Run PyInstaller
    cmd = [sys.executable, "-m", "PyInstaller", "build.spec"]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build successful!")
        print(f"Executable created at: dist/md2pptx.exe")
        
        # Show build output if verbose
        if "--verbose" in sys.argv:
            print("\nBuild output:")
            print(result.stdout)
            
    except subprocess.CalledProcessError as e:
        print("Build failed!")
        print(f"Error: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        sys.exit(1)


if __name__ == "__main__":
    build()