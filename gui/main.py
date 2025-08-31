#!/usr/bin/env python3
"""Main entry point for A14 Charge Keeper GUI application."""

import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Main entry point with error handling."""
    try:
        from gui.system_tray import main as tray_main
        return tray_main()
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure PyQt5 is installed: pip install PyQt5")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    # Add CLI path to environment
    cli_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'cli'))
    current_path = os.environ.get('PATH', '')
    if cli_path not in current_path:
        os.environ['PATH'] = f"{cli_path}:{current_path}"
    
    sys.exit(main())