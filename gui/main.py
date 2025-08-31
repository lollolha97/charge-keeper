#!/usr/bin/env python3
"""Main entry point for A14 Charge Keeper GUI application."""

import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def setup_qt_for_root():
    """Setup Qt environment for safe root execution."""
    # Fix XDG_RUNTIME_DIR issue for root
    if os.geteuid() == 0:  # Running as root
        original_user = os.environ.get('SUDO_USER', 'root')
        
        # Set proper XDG_RUNTIME_DIR for Qt
        if not os.environ.get('XDG_RUNTIME_DIR'):
            runtime_dir = f"/tmp/runtime-{original_user}"
            os.makedirs(runtime_dir, mode=0o700, exist_ok=True)
            os.environ['XDG_RUNTIME_DIR'] = runtime_dir
        
        # Set HOME to original user's home for Qt config
        if original_user != 'root':
            import pwd
            try:
                user_info = pwd.getpwnam(original_user)
                os.environ['HOME'] = user_info.pw_dir
            except KeyError:
                pass
        
        # Disable Qt's security restrictions for root
        os.environ['QT_X11_NO_MITSHM'] = '1'
        os.environ['QT_QUICK_BACKEND'] = 'software'

def main():
    """Main entry point with error handling."""
    try:
        # Setup Qt environment for root execution
        setup_qt_for_root()
        
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtGui import QIcon
        from gui.system_tray import main as tray_main
        
        # Create application as global to prevent QBasicTimer issues
        global app
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            
        # Set proper exit behavior for Qt application
        app.setQuitOnLastWindowClosed(False)
        
        # Set application icon globally
        try:
            icon_path = os.path.join(os.path.dirname(__file__), '..', 'icon-Photoroom.png')
            icon_path = os.path.abspath(icon_path)
            if os.path.exists(icon_path):
                app.setWindowIcon(QIcon(icon_path))
        except:
            pass
            
        # Store reference to prevent garbage collection
        result = tray_main()
        
        # Explicit cleanup to prevent segfault
        if hasattr(app, 'processEvents'):
            app.processEvents()
            
        return result
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