#!/bin/bash
# PriPlot Launcher Script

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the project directory
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "fresh_venv" ]; then
    echo "🔧 Setting up virtual environment..."
    python3 -m venv fresh_venv
    source fresh_venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    echo "✅ Virtual environment setup complete!"
else
    # Activate the virtual environment
    source fresh_venv/bin/activate
fi

# Run the application
echo "🚀 Starting PriPlot..."
python -m priorityplot.main

# Deactivate when done
deactivate 