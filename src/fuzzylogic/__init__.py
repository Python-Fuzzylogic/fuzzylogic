__version__ = (1, 5, 0)

def run_gui(port=8000):
    """Start the fuzzy logic experimentation GUI.
    
    Args:
        port: Port to run the web server on (default: 8000)
    """
    try:
        from .gui.app import run_gui as _run_gui
        _run_gui(port)
    except ImportError as e:
        print(f"GUI dependencies not available: {e}")
        print("Please install matplotlib if you haven't already: pip install matplotlib")
