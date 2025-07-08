from datetime import datetime, timezone, timedelta, tzinfo
from typing import List, Dict, Any
import zoneinfo
import os


def get_user_timezone(tasks: List[Dict[str, Any]]) -> tzinfo:
    """
    Determine user's timezone from tasks or system
    
    Args:
        tasks: List of task dictionaries from TickTick API
        
    Returns:
        timezone object representing user's timezone
    """
    # Try to get timezone from first task that has one
    for task in tasks:
        task_tz = task.get('timeZone')
        if task_tz:
            try:
                return zoneinfo.ZoneInfo(task_tz)
            except Exception:
                # Invalid timezone, continue searching
                continue
    
    # Fallback to system timezone
    try:
        # Try to get system timezone
        system_tz = datetime.now().astimezone().tzinfo
        if system_tz is not None:
            return system_tz
        # If system_tz is None, fall through to UTC
    except Exception:
        # Exception occurred, fall through to UTC
        pass
    
    # Ultimate fallback to UTC
    return timezone.utc


def group_tasks_by_time(tasks: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Group tasks by time periods: Overdue, Today, Tomorrow, Later
    Now timezone-aware for accurate grouping
    
    Args:
        tasks: List of task dictionaries from TickTick API
        
    Returns:
        Dictionary with keys: 'overdue', 'today', 'tomorrow', 'later'
    """
    if not tasks:
        return {'overdue': [], 'today': [], 'tomorrow': [], 'later': []}
    
    # Determine user's timezone from tasks
    user_tz = get_user_timezone(tasks)
    
    # Get current time in user's timezone for accurate "today" calculation
    now_user_tz = datetime.now(user_tz)
    today_start = now_user_tz.replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow_start = today_start + timedelta(days=1)
    day_after_tomorrow_start = today_start + timedelta(days=2)
    
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
            # Parse the UTC datetime string
            due_date_utc = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
            
            # Convert to user's timezone for accurate day comparison
            due_date_user_tz = due_date_utc.astimezone(user_tz)
            due_date_day_start = due_date_user_tz.replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Compare dates in user's timezone
            if due_date_day_start < today_start:
                groups['overdue'].append(task)
            elif due_date_day_start == today_start:
                groups['today'].append(task)
            elif due_date_day_start == tomorrow_start:
                groups['tomorrow'].append(task)
            else:
                groups['later'].append(task)
                
        except (ValueError, AttributeError, TypeError) as e:
            # If we can't parse the date, put it in 'later'
            # More specific error handling for debugging
            print(f"Warning: Could not parse due date '{due_date_str}' for task '{task.get('title', 'Unknown')}': {e}")
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
    Now timezone-aware for accurate time sorting
    
    Args:
        tasks: List of tasks in the group
        group_key: The group key to determine sorting strategy
        
    Returns:
        Sorted list of tasks
    """
    if not tasks:
        return []
    
    # Get user timezone for consistent sorting
    user_tz = get_user_timezone(tasks)
    
    def sort_key(task):
        # Primary sort: priority (5=highest, 0=none)
        priority = task.get('priority', 0)
        
        # Secondary sort: due time for today/tomorrow, creation time for others
        if group_key in ['today', 'tomorrow']:
            due_date_str = task.get('dueDate', '')
            try:
                # Parse UTC time and convert to user timezone for accurate sorting
                due_date_utc = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
                due_date_user_tz = due_date_utc.astimezone(user_tz)
                return (-priority, due_date_user_tz.timestamp())
            except (ValueError, AttributeError, TypeError):
                return (-priority, float('inf'))
        else:
            # For overdue and later, sort by creation time
            created_time = task.get('createdTime', '')
            try:
                # Parse UTC time and convert to user timezone
                created_date_utc = datetime.fromisoformat(created_time.replace('Z', '+00:00'))
                created_date_user_tz = created_date_utc.astimezone(user_tz)
                return (-priority, created_date_user_tz.timestamp())
            except (ValueError, AttributeError, TypeError):
                return (-priority, 0)
    
    return sorted(tasks, key=sort_key) 