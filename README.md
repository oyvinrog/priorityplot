# 🎯 PriPlot - Interactive Task Priority Visualization

<div align="center">

![PriPlot Screenshot](https://github.com/oyvinrog/priorityplot/raw/main/img/priplot.png)

[![PyPI version](https://badge.fury.io/py/priorityplot.svg)](https://badge.fury.io/py/priorityplot)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Downloads](https://pepy.tech/badge/priorityplot)](https://pepy.tech/project/priorityplot)

**Transform your task management with interactive priority plotting**

[Features](#-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [Usage](#-usage) • [Contributing](#-contributing)

</div>

---

## 🌟 Overview

**PriPlot** is a modern, intuitive desktop application that revolutionizes how you prioritize tasks and goals. By visualizing tasks on an interactive **Value vs. Time** plot, you can instantly identify high-impact, low-effort opportunities and make data-driven decisions about where to focus your energy.

### Why PriPlot?

- 📊 **Visual Priority Matrix**: See all your tasks plotted by value and time investment
- 🖱️ **Interactive Drag & Drop**: Easily adjust task priorities with your mouse
- 🎨 **Modern Dark UI**: Beautiful, professional interface that's easy on the eyes
- 📋 **Bulk Import**: Add multiple tasks from clipboard or use test data
- 📈 **Smart Sorting**: Automatically calculates and ranks tasks by priority score
- 📊 **Export Ready**: Export your prioritized tasks to Excel for sharing
- ⚡ **Instant Feedback**: Real-time priority calculations as you adjust values

## ✨ Features

### 🎯 Core Functionality
- **Interactive Priority Plotting**: Drag tasks around the value/time matrix
- **Smart Priority Calculation**: Automatic ranking based on value-to-time ratio
- **Multi-Tab Interface**: Separate views for input, plotting, and results
- **Hover Tooltips**: See task details without clicking

### 📊 Data Management
- **Flexible Input**: Add tasks one by one or import from clipboard
- **Test Data Generator**: Pre-loaded sample tasks for quick testing
- **Excel Export**: Professional spreadsheet output with priority rankings
- **Real-time Updates**: See priority changes instantly as you adjust positions

### 🎨 User Experience
- **Modern Dark Theme**: Professional appearance with excellent contrast
- **Responsive Design**: Smooth interactions and visual feedback
- **Intuitive Controls**: No learning curve - just drag and prioritize
- **Cross-Platform**: Works on Windows, macOS, and Linux

## 🚀 Installation

### From PyPI (Recommended)

```bash
pip install priorityplot
```

### From Source

```bash
git clone https://github.com/oyvinrog/priorityplot.git
cd priorityplot
pip install -e .
```

### Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Dependencies**: Automatically installed with pip

## ⚡ Quick Start

1. **Install PriPlot**:
   ```bash
   pip install priorityplot
   ```

2. **Launch the application**:
   ```bash
   priorityplot
   ```

3. **Add your tasks** in the "Input Goals" tab

4. **Visualize and prioritize** in the "Plot" tab by dragging tasks

5. **Export your results** from the "Table" tab

## 📖 Usage

### Adding Tasks

**Method 1: Manual Entry**
1. Open the "Input Goals" tab
2. Type your task name
3. Click "Add Goal"
4. Repeat for all tasks

**Method 2: Clipboard Import**
1. Copy a list of tasks (one per line) to your clipboard
2. Click "Add Goals from Clipboard"
3. All tasks will be imported automatically

**Method 3: Test Data**
1. Click "Add Test Goals" to load sample tasks
2. Perfect for exploring the application features

### Interactive Prioritization

1. Switch to the "Plot" tab after adding tasks
2. **Drag tasks** around the plot:
   - **Right side**: Higher value tasks
   - **Bottom**: Lower time investment tasks
   - **Bottom-right**: High-value, low-time (highest priority!)
3. **Hover** over points to see task details
4. Watch the priority scores update in real-time

### Exporting Results

1. Click "Apply" to generate the priority table
2. Switch to the "Table" tab to see ranked results
3. Click "Export to Excel" to save your prioritized task list
4. Share with your team or use for planning

## 🎨 Interface Guide

### Value Axis (X-axis)
- **1-2**: Low value tasks
- **3-4**: Medium value tasks  
- **5-6**: High value tasks

### Time Axis (Y-axis)
- **1-2 hours**: Quick tasks
- **3-4 hours**: Medium effort
- **5+ hours**: Major time investment

### Priority Quadrants
- **Top-Left**: Low value, high time (avoid these!)
- **Top-Right**: High value, high time (plan carefully)
- **Bottom-Left**: Low value, low time (fill-in tasks)
- **Bottom-Right**: High value, low time (do these first!)

## 🛠️ Development

### Setting Up Development Environment

```bash
git clone https://github.com/oyvinrog/priplot.git
cd priorityplot
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

### Running from Source

```bash
python -m priorityplot.main
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Areas for Contribution
- 🐛 Bug fixes and improvements
- ✨ New features and enhancements
- 📚 Documentation improvements
- 🎨 UI/UX enhancements
- 🧪 Test coverage expansion

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) for the modern GUI
- Plotting powered by [Matplotlib](https://matplotlib.org/)
- Data handling with [NumPy](https://numpy.org/) and [OpenPyXL](https://openpyxl.readthedocs.io/)

## 📞 Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/oyvinrog/priplot/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/oyvinrog/priplot/discussions)
- 📧 **Email**: oyvinrog@example.com

---

<div align="center">

**Made with ❤️ for better productivity**

[⭐ Star this repo](https://github.com/oyvinrog/priplot) if you find it helpful!

</div> 