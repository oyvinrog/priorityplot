#!/bin/bash
# PriPlot Development Setup Script

echo "🔧 Setting up PriPlot development environment..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Remove any existing virtual environments
echo "🧹 Cleaning up old environments..."
rm -rf venv fresh_venv env .venv

# Create fresh virtual environment
echo "🆕 Creating fresh virtual environment..."
python3 -m venv dev_env

# Activate virtual environment
source dev_env/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Install development dependencies
echo "🛠️ Installing development tools..."
pip install black flake8 pytest

echo "✅ Development environment setup complete!"
echo ""
echo "🚀 To start developing:"
echo "   source dev_env/bin/activate"
echo "   python -m priorityplot.main"
echo ""
echo "🧪 To run tests:"
echo "   pytest"
echo ""
echo "🎨 To format code:"
echo "   black priorityplot/"
echo ""
echo "🔍 To check code style:"
echo "   flake8 priorityplot/" 