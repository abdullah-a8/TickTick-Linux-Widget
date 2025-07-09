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

def complete_task(task_id, project_id=None):
    """
    Mark a task as completed using the TickTick API
    
    Args:
        task_id (str): The ID of the task to complete
        project_id (str, optional): The project ID. If not provided, will be fetched from local cache
        
    Returns:
        dict: The completed task object on success, None on failure
        
    Raises:
        ValueError: If task_id is invalid or task not found
        ConnectionError: If API request fails
        Exception: For other unexpected errors
    """
    try:
        if not task_id or not isinstance(task_id, str):
            raise ValueError("Task ID must be a non-empty string")
        
        # If project_id not provided, try to get it from local cache
        if not project_id:
            project_id = _get_project_id_for_task(task_id)
            if not project_id:
                raise ValueError(f"Could not find project ID for task '{task_id}'. Task may not exist or cache needs refresh.")
        
        # Get the full task object first using pyticktick's v1 API
        task_obj = client.get_task_v1(project_id, task_id)
        
        if not task_obj:
            raise ValueError(f"Task with ID '{task_id}' not found in project '{project_id}'")
        
        # Verify it's not already completed (status field varies between v1/v2)
        task_status = getattr(task_obj, 'status', None)
        if task_status is True:  # v1 API uses boolean for status
            print(f"Task '{getattr(task_obj, 'title', 'Unknown')}' is already completed")
            return task_obj.model_dump() if hasattr(task_obj, 'model_dump') else task_obj
        
        # Mark task as complete using pyticktick's v1 API
        client.complete_task_v1(project_id, task_id)
        
        # Get the updated task object to return
        updated_task = client.get_task_v1(project_id, task_id)
        
        if updated_task:
            # Convert to dict if it's a model object
            if hasattr(updated_task, 'model_dump'):
                task_dict = updated_task.model_dump()
            elif hasattr(updated_task, '__dict__'):
                task_dict = updated_task.__dict__
            else:
                task_dict = updated_task
            
            # Get title safely
            title = task_dict.get('title', 'Unknown') if isinstance(task_dict, dict) else 'Unknown'
            print(f"✅ Successfully completed task: '{title}'")
            return task_dict
        else:
            raise Exception("Task completion succeeded but couldn't fetch updated task")
            
    except ValueError as e:
        print(f"Validation error completing task: {e}")
        raise
    except ConnectionError as e:
        print(f"Network error completing task: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error completing task '{task_id}': {e}")
        raise

def update_task_status(task_id, status, project_id=None):
    """
    Update a task's status (more granular control than complete_task)
    
    Args:
        task_id (str): The ID of the task to update
        status (int): New status (0=active, 2=completed) - Note: v1 API uses boolean
        project_id (str, optional): The project ID. If not provided, will be fetched from local cache
        
    Returns:
        dict: The updated task object on success, None on failure
        
    Raises:
        ValueError: If parameters are invalid or task not found
        ConnectionError: If API request fails
        Exception: For other unexpected errors
    """
    try:
        if not task_id or not isinstance(task_id, str):
            raise ValueError("Task ID must be a non-empty string")
        
        if status not in [0, 2]:
            raise ValueError("Status must be 0 (active) or 2 (completed)")
        
        # Convert v2 status (0=active, 2=completed) to v1 status (False=active, True=completed)
        v1_status = status == 2
        
        # If project_id not provided, try to get it from local cache
        if not project_id:
            project_id = _get_project_id_for_task(task_id)
            if not project_id:
                raise ValueError(f"Could not find project ID for task '{task_id}'. Task may not exist or cache needs refresh.")
        
        # Get the full task object first
        task_obj = client.get_task_v1(project_id, task_id)
        
        if not task_obj:
            raise ValueError(f"Task with ID '{task_id}' not found in project '{project_id}'")
        
        # Check if status change is needed (v1 API uses boolean)
        current_status = getattr(task_obj, 'status', False)
        if current_status == v1_status:
            status_text = "completed" if v1_status else "active"
            print(f"Task '{getattr(task_obj, 'title', 'Unknown')}' already has status {status_text}")
            return task_obj.model_dump() if hasattr(task_obj, 'model_dump') else task_obj
        
        # For completion, use the complete_task function
        if v1_status:  # Task should be completed
            return complete_task(task_id, project_id)
        else:
            # Task reactivation (uncompleting) is not supported by pyticktick v1 API
            # This would require a direct v2 API call or different approach
            raise NotImplementedError(
                "Task reactivation (marking completed task as active) is not supported by pyticktick v1 API. "
                "Use complete_task() to mark tasks as completed."
            )
            
    except ValueError as e:
        print(f"Validation error updating task status: {e}")
        raise
    except ConnectionError as e:
        print(f"Network error updating task status: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error updating task status '{task_id}': {e}")
        raise

def batch_complete_tasks(task_ids):
    """
    Complete multiple tasks in batch (optimized for multiple operations)
    
    Args:
        task_ids (list): List of task IDs to complete
        
    Returns:
        dict: Results with 'success' and 'failed' lists
        
    Example:
        result = batch_complete_tasks(['task1', 'task2', 'task3'])
        # Returns: {'success': [task_obj1, task_obj2], 'failed': [('task3', 'error_msg')]}
    """
    results = {
        'success': [],
        'failed': []
    }
    
    if not task_ids or not isinstance(task_ids, list):
        print("Warning: No valid task IDs provided for batch completion")
        return results
    
    print(f"Starting batch completion of {len(task_ids)} tasks...")
    
    for task_id in task_ids:
        try:
            completed_task = complete_task(task_id)
            if completed_task:
                results['success'].append(completed_task)
        except Exception as e:
            error_msg = str(e)
            results['failed'].append((task_id, error_msg))
            print(f"Failed to complete task '{task_id}': {error_msg}")
    
    print(f"Batch completion finished: {len(results['success'])} successful, {len(results['failed'])} failed")
    return results

def refresh_local_task_cache():
    """
    Refresh the local task cache after task modifications
    This ensures the UI stays in sync after task status changes
    
    Returns:
        bool: True if cache refresh was successful, False otherwise
    """
    try:
        print("Refreshing local task cache...")
        
        # Fetch fresh tasks from API
        fresh_tasks = get_active_standard_tasks()
        
        # Save to local cache
        if save_tasks_to_json(fresh_tasks):
            print(f"✅ Successfully refreshed cache with {len(fresh_tasks)} active tasks")
            return True
        else:
            print("❌ Failed to save refreshed tasks to cache")
            return False
            
    except Exception as e:
        print(f"Error refreshing task cache: {e}")
        return False

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

def _get_project_id_for_task(task_id):
    """
    Helper function to get project ID for a task from local cache
    
    Args:
        task_id (str): The task ID to find project for
        
    Returns:
        str or None: The project ID if found, None otherwise
    """
    try:
        project_root = Path(__file__).parent.parent.parent.parent
        tasks_file = project_root / "data" / "allActiveTasks.json"
        
        if not tasks_file.exists():
            return None
            
        with open(tasks_file, 'r', encoding='utf-8') as f:
            tasks = json.load(f)
            
        # Find the task in cached data
        for task in tasks:
            if task.get('id') == task_id:
                return task.get('projectId')
                
        return None
    except Exception as e:
        print(f"Error getting project ID for task {task_id}: {e}")
        return None

if __name__ == "__main__":
    # Get active standard tasks
    tasks = get_active_standard_tasks()
    
    # Save to JSON file
    if save_tasks_to_json(tasks):
        print(f"✅ Saved {len(tasks)} active standard tasks to data/allActiveTasks.json")
    else:
        print("❌ Failed to save tasks")
