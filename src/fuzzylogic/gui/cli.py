#!/usr/bin/env python3
"""
cli.py - Command line interface for the fuzzy logic GUI.

This provides a simple command to start the GUI.
"""

import argparse
import sys
from .app import run_gui


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Fuzzy Logic Experimentation GUI")
    parser.add_argument(
        '--port', 
        type=int, 
        default=8000, 
        help='Port to run the web server on (default: 8000)'
    )
    parser.add_argument(
        '--no-browser',
        action='store_true',
        help="Don't open browser automatically"
    )
    
    args = parser.parse_args()
    
    print("Starting Fuzzy Logic GUI...")
    print(f"Web interface will be available at http://localhost:{args.port}")
    
    if args.no_browser:
        print("Browser will not open automatically")
    
    try:
        run_gui(port=args.port)
    except KeyboardInterrupt:
        print("\nGUI stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting GUI: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()