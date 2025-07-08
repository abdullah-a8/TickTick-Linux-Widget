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
    parser = argparse.ArgumentParser(description="TickTick Widget")
    parser.add_argument('--cli', action='store_true', 
                      help='Run CLI version instead of GUI')
    
    args = parser.parse_args()
    
    if args.cli:
        run_cli()
    else:
        run_gui()


if __name__ == "__main__":
    main() 