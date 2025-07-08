"""
Main entry point for TickTick Linux Widget.
"""

import sys
from .backend.api import get_active_standard_tasks, save_tasks_to_json

def main():
    """Main function for the TickTick Widget."""
    print("🚀 TickTick Linux Widget v0.1.0")
    print("=" * 40)
    
    try:
        # For now, just run the backend functionality
        print("📡 Fetching active tasks...")
        tasks = get_active_standard_tasks()
        
        if tasks:
            success = save_tasks_to_json(tasks)
            if success:
                print(f"✅ Successfully saved {len(tasks)} tasks to data/allActiveTasks.json")
                print("\n📋 Task Summary:")
                for i, task in enumerate(tasks[:5], 1):  # Show first 5 tasks
                    title = task.get('title', 'Untitled')
                    priority = '⭐' * task.get('priority', 0)
                    print(f"  {i}. {title} {priority}")
                
                if len(tasks) > 5:
                    print(f"  ... and {len(tasks) - 5} more tasks")
            else:
                print("❌ Failed to save tasks")
                sys.exit(1)
        else:
            print("ℹ️  No active tasks found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    
    print("\n🎯 GUI implementation coming in Phase 1!")

if __name__ == "__main__":
    main() 