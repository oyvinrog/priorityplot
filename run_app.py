#!/usr/bin/env python3
"""
Simple launcher script for Priority Plot application
"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the main function
from priorityplot.main import main

if __name__ == "__main__":
    main() 