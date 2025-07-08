#!/usr/bin/env python3
"""
TickTick Widget - Main Entry Point

Usage:
    python -m ticktick_widget            # Launch GUI widget
    python -m ticktick_widget --cli       # Run CLI version (fetch and save tasks)
"""

import sys
import argparse
from .backend.api import get_active_standard_tasks, save_tasks_to_json


def run_cli():
    """Run CLI version - fetch and save tasks"""
    print("Fetching active tasks from TickTick...")
    tasks = get_active_standard_tasks()
    
    if save_tasks_to_json(tasks):
        print(f"✅ Saved {len(tasks)} active standard tasks to data/allActiveTasks.json")
    else:
        print("❌ Failed to save tasks")


def run_gui():
    """Run GUI version - launch the widget"""
    try:
        from .gui.main_widget import main
        main()
    except ImportError as e:
        print(f"❌ GUI dependencies not installed: {e}")
        print("Please install PyQt6: pip install PyQt6")
        sys.exit(1)


def main():
    # Set process title for better process identification
    try:
        import importlib
        setproctitle = importlib.import_module('setproctitle')
        setproctitle.setproctitle("TickTick Widget")
    except ImportError:
        pass
    
    parser = argparse.ArgumentParser(description="TickTick Widget")
    parser.add_argument('--cli', action='store_true', 
                      help='Run CLI version instead of GUI')
    parser.add_argument('--setup-autostart', action='store_true',
                      help='Set up autostart configuration')
    
    args = parser.parse_args()
    
    if args.cli:
        run_cli()
    elif args.setup_autostart:
        run_autostart_setup()
    else:
        run_gui()


def run_autostart_setup():
    """Run autostart setup"""
    import subprocess
    import sys
    from pathlib import Path
    
    try:
        # Get path to setup script
        project_root = Path(__file__).parent.parent.parent
        setup_script = project_root / "scripts" / "setup_autostart.py"
        
        if not setup_script.exists():
            print("❌ Autostart setup script not found!")
            print(f"Expected location: {setup_script}")
            sys.exit(1)
        
        # Run the setup script
        subprocess.run([sys.executable, str(setup_script)], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running autostart setup: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error setting up autostart: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 