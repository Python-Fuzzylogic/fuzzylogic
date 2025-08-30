# Fuzzy Logic GUI

This directory contains a web-based GUI for experimenting with fuzzy logic and generating Python code.

## Features

- **Create Domains**: Define fuzzy logic domains with custom ranges and resolution
- **Add Fuzzy Sets**: Create fuzzy sets using various membership functions:
  - R (Rising): Sigmoid-like function that rises from 0 to 1
  - S (Falling): Sigmoid-like function that falls from 1 to 0
  - Triangular: Triangle-shaped membership function
  - Trapezoid: Trapezoid-shaped membership function  
  - Rectangular: Rectangular/plateau membership function
- **Visualization**: Plot domains and their fuzzy sets using matplotlib
- **Test Values**: Test input values against all sets in a domain
- **Code Generation**: Generate Python code that recreates your fuzzy logic setup

## Usage

### Command Line

Start the GUI from the command line:

```bash
# From the repository root
python -m fuzzylogic.gui.cli

# Or with custom port
python -m fuzzylogic.gui.cli --port 8080

# Don't open browser automatically
python -m fuzzylogic.gui.cli --no-browser
```

### Python API

Start the GUI programmatically:

```python
import fuzzylogic

# Start the GUI (will open browser automatically)
fuzzylogic.run_gui()

# Or with custom port
fuzzylogic.run_gui(port=8080)
```

### Direct Module Usage

```python
from fuzzylogic.gui.app import run_gui

# Start the server
run_gui(port=8000)
```

## Example Workflow

1. **Create a Domain**: Enter a name (e.g., "temperature"), set the range (0-40), and click "Create Domain"

2. **Add Fuzzy Sets**: 
   - Select the domain from the dropdown
   - Enter a set name (e.g., "cold")
   - Choose function type (e.g., "S" for falling)
   - Set parameters (e.g., low=0, high=15)
   - Click "Add Set"

3. **Visualize**: Select the domain and click "Plot Domain" to see a graph of all fuzzy sets

4. **Test Values**: Enter a test value and see the membership degrees for each set

5. **Generate Code**: Click "Generate Python Code" to get Python code that recreates your setup

## Implementation Details

The GUI is implemented as a simple HTTP server that serves a single-page web application. It uses:

- Pure Python with built-in `http.server` (no external web framework dependencies)
- Matplotlib for plotting (with Agg backend for server-side rendering)
- HTML/CSS/JavaScript for the frontend
- JSON API for communication between frontend and backend

## Files

- `app.py`: Main GUI application with web server and fuzzy logic interface
- `cli.py`: Command-line interface for starting the GUI
- `__init__.py`: Module initialization