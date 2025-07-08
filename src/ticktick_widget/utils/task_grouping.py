from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any


def group_tasks_by_time(tasks: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Group tasks by time periods: Overdue, Today, Tomorrow, Later
    
    Args:
        tasks: List of task dictionaries from TickTick API
        
    Returns:
        Dictionary with keys: 'overdue', 'today', 'tomorrow', 'later'
    """
    now = datetime.now(timezone.utc)
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    day_after_tomorrow = today + timedelta(days=2)
    
    groups = {
        'overdue': [],
        'today': [],
        'tomorrow': [],
        'later': []
    }
    
    for task in tasks:
        due_date_str = task.get('dueDate')
        
        if not due_date_str:
            # Tasks without due dates go to 'later'
            groups['later'].append(task)
            continue
            
        try:
            # Parse the ISO datetime string
            due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
            due_date_day = due_date.replace(hour=0, minute=0, second=0, microsecond=0)
            
            if due_date_day < today:
                groups['overdue'].append(task)
            elif due_date_day == today:
                groups['today'].append(task)
            elif due_date_day == tomorrow:
                groups['tomorrow'].append(task)
            else:
                groups['later'].append(task)
                
        except (ValueError, AttributeError):
            # If we can't parse the date, put it in 'later'
            groups['later'].append(task)
    
    return groups


def get_group_display_info(group_key: str, task_count: int) -> Dict[str, str]:
    """
    Get display information for a task group
    
    Args:
        group_key: The group key ('overdue', 'today', 'tomorrow', 'later')
        task_count: Number of tasks in the group
        
    Returns:
        Dictionary with 'title', 'subtitle', and 'icon' keys
    """
    group_info = {
        'overdue': {
            'title': 'Overdue',
            'subtitle': f'{task_count} task{"s" if task_count != 1 else ""}',
            'icon': '⚠️'
        },
        'today': {
            'title': 'Today',
            'subtitle': f'{task_count} task{"s" if task_count != 1 else ""}',
            'icon': '📅'
        },
        'tomorrow': {
            'title': 'Tomorrow', 
            'subtitle': f'{task_count} task{"s" if task_count != 1 else ""}',
            'icon': '⭐'
        },
        'later': {
            'title': 'Later',
            'subtitle': f'{task_count} task{"s" if task_count != 1 else ""}',
            'icon': '📝'
        }
    }
    
    return group_info.get(group_key, {
        'title': 'Unknown',
        'subtitle': f'{task_count} tasks',
        'icon': '📋'
    })


def sort_tasks_in_group(tasks: List[Dict[str, Any]], group_key: str) -> List[Dict[str, Any]]:
    """
    Sort tasks within a group by priority and due time
    
    Args:
        tasks: List of tasks in the group
        group_key: The group key to determine sorting strategy
        
    Returns:
        Sorted list of tasks
    """
    def sort_key(task):
        # Primary sort: priority (5=highest, 0=none)
        priority = task.get('priority', 0)
        
        # Secondary sort: due time for today/tomorrow, creation time for others
        if group_key in ['today', 'tomorrow']:
            due_date_str = task.get('dueDate', '')
            try:
                due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
                return (-priority, due_date.timestamp())
            except:
                return (-priority, float('inf'))
        else:
            # For overdue and later, sort by creation time
            created_time = task.get('createdTime', '')
            try:
                created_date = datetime.fromisoformat(created_time.replace('Z', '+00:00'))
                return (-priority, created_date.timestamp())
            except:
                return (-priority, 0)
    
    return sorted(tasks, key=sort_key) 