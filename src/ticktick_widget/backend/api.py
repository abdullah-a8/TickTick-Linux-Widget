import json
import os
from pathlib import Path
from .auth import client

def get_active_standard_tasks():
    """Get active standard tasks (TEXT kind) and save to JSON file"""
    try:
        # Direct raw API call
        raw_response = client._get_api_v2("/batch/check/0")
        
        # Validate response structure
        if not isinstance(raw_response, dict):
            raise ValueError("Invalid API response format")
        
        # Extract tasks
        if 'syncTaskBean' not in raw_response or 'update' not in raw_response['syncTaskBean']:
            return []
        
        raw_tasks = raw_response['syncTaskBean']['update']
        if not isinstance(raw_tasks, list):
            return []
        
        # Filter for active TEXT tasks
        active_standard_tasks = []
        for task in raw_tasks:
            if (isinstance(task, dict) and 
                task.get('kind') == 'TEXT' and 
                task.get('status') == 0):
                
                # Clean and structure the task data with safe defaults
                clean_task = {
                    'id': str(task.get('id', '')),
                    'title': str(task.get('title', '')).strip(),
                    'content': str(task.get('content', '')).strip(),
                    'dueDate': task.get('dueDate'),
                    'startDate': task.get('startDate'),
                    'priority': max(0, min(5, int(task.get('priority', 0)))),  # Clamp 0-5
                    'projectId': str(task.get('projectId', '')),
                    'tags': task.get('tags', []) if isinstance(task.get('tags'), list) else [],
                    'createdTime': task.get('createdTime'),
                    'modifiedTime': task.get('modifiedTime'),
                    'reminder': task.get('reminder'),
                    'reminders': task.get('reminders', []) if isinstance(task.get('reminders'), list) else [],
                    'repeatFlag': task.get('repeatFlag'),
                    'timeZone': task.get('timeZone'),
                    'isAllDay': task.get('isAllDay'),
                    'kind': task.get('kind'),
                    'status': task.get('status')
                }
                
                # Remove null/empty values to keep JSON clean
                clean_task = {k: v for k, v in clean_task.items() if v is not None and v != ''}
                active_standard_tasks.append(clean_task)
        
        return active_standard_tasks
        
    except Exception as e:
        print(f"Error fetching tasks: {e}")
        return []

def save_tasks_to_json(tasks):
    """Save tasks to data/allActiveTasks.json file"""
    try:
        if not isinstance(tasks, list):
            raise ValueError("Tasks must be a list")
        
        # Get project root directory (3 levels up from this file)
        project_root = Path(__file__).parent.parent.parent.parent
        data_dir = project_root / "data"
        data_dir.mkdir(exist_ok=True)
        
        file_path = data_dir / "allActiveTasks.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving file: {e}")
        return False

if __name__ == "__main__":
    # Get active standard tasks
    tasks = get_active_standard_tasks()
    
    # Save to JSON file
    if save_tasks_to_json(tasks):
        print(f"✅ Saved {len(tasks)} active standard tasks to data/allActiveTasks.json")
    else:
        print("❌ Failed to save tasks")
