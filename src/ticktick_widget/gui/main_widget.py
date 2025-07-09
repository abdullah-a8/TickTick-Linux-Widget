import sys
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QPushButton, QLabel, QFrame, QSizePolicy, QComboBox
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QPalette, QMouseEvent, QShowEvent

# Lazy imports for startup optimization
_backend_api = None
_task_grouping = None
_task_widgets = None

def _get_backend_api():
    global _backend_api
    if _backend_api is None:
        from ..backend.api import (
            get_active_standard_tasks, 
            save_tasks_to_json,
            complete_task,
            update_task_status,
            refresh_local_task_cache
        )
        _backend_api = {
            'get_active_standard_tasks': get_active_standard_tasks, 
            'save_tasks_to_json': save_tasks_to_json,
            'complete_task': complete_task,
            'update_task_status': update_task_status,
            'refresh_local_task_cache': refresh_local_task_cache
        }
    return _backend_api

def _get_task_grouping():
    global _task_grouping
    if _task_grouping is None:
        from ..utils.task_grouping import group_tasks_by_time, get_group_display_info, sort_tasks_in_group
        _task_grouping = {'group_tasks_by_time': group_tasks_by_time, 'get_group_display_info': get_group_display_info, 'sort_tasks_in_group': sort_tasks_in_group}
    return _task_grouping

def _get_task_widgets():
    global _task_widgets
    if _task_widgets is None:
        from .task_group_widget import TaskGroupWidget
        from .task_item_widget import TaskItemWidget
        from .priority_checkbox import PriorityCheckboxContainer
        _task_widgets = {
            'TaskGroupWidget': TaskGroupWidget, 
            'TaskItemWidget': TaskItemWidget,
            'PriorityCheckboxContainer': PriorityCheckboxContainer
        }
    return _task_widgets

# Import managers immediately as they're lightweight
from ..config.theme_manager import theme_manager
from ..config.position_manager import position_manager


class StartupOptimizer(QThread):
    """Background thread for heavy startup operations"""
    tasks_loaded = pyqtSignal(list)
    
    def __init__(self):
        super().__init__()
        self.project_root = Path(__file__).parent.parent.parent.parent
        
    def run(self):
        """Load tasks in background"""
        try:
            json_file = self.project_root / "data" / "allActiveTasks.json"
            if json_file.exists():
                with open(json_file, 'r', encoding='utf-8') as f:
                    tasks = json.load(f)
                self.tasks_loaded.emit(tasks)
            else:
                self.tasks_loaded.emit([])
        except Exception as e:
            self.tasks_loaded.emit([])


class TaskCompletionWorker(QThread):
    """Background thread for task completion to avoid blocking UI"""
    
    # Signals for different outcomes
    task_completed = pyqtSignal(str, dict)  # task_id, completed_task_data
    task_completion_failed = pyqtSignal(str, str)  # task_id, error_message
    
    def __init__(self, task_id):
        super().__init__()
        self.task_id = task_id
        
    def run(self):
        """Complete task in background"""
        try:
            # Get backend API functions
            backend_api = _get_backend_api()
            
            # Attempt to complete the task
            completed_task = backend_api['complete_task'](self.task_id)
            
            if completed_task:
                self.task_completed.emit(self.task_id, completed_task)
            else:
                self.task_completion_failed.emit(self.task_id, "Task completion returned empty response")
                
        except Exception as e:
            error_msg = str(e)
            self.task_completion_failed.emit(self.task_id, error_msg)


class TickTickWidget(QWidget):
    """Main widget for displaying TickTick tasks"""
    
    def __init__(self):
        super().__init__()
        self.tasks = []
        self.startup_complete = False
        self.deferred_operations_pending = True
        self.completion_worker = None  # Initialize task completion worker
        self.pending_completion_task = None  # Store task data for potential rollback
        self.startup_refresh_timer = None  # Initialize startup refresh timer
        self.position_locked = position_manager.load_lock_state()  # Load lock state
        
        # Setup UI immediately (lightweight)
        self.setup_ui()
        
        # Defer heavy operations until after show
        self.startup_optimizer = StartupOptimizer()
        self.startup_optimizer.tasks_loaded.connect(self.on_tasks_loaded)
        
        # Setup auto-refresh timer (every 5 minutes)
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_tasks)
        self.timer.start(300000)  # 5 minutes in milliseconds
        
        # Connect to theme manager
        theme_manager.theme_changed.connect(self.on_theme_changed)
        
        # Mark for deferred initialization
        self.init_timer = QTimer()
        self.init_timer.setSingleShot(True)
        self.init_timer.timeout.connect(self.complete_startup)
        self.init_timer.start(50)  # Short delay to allow widget to show first
    
    def setup_ui(self):
        self.setWindowTitle("Tasks")
        self.setFixedSize(460, 680)  # 8px grid: optimized for modern card layout
        
        # Configure window for desktop widget behavior - avoid taskbar/dock
        # Use multiple approaches for maximum Wayland/GNOME compatibility
        
        # Check if we're likely on GNOME/Wayland and use alternative approach
        import os
        desktop_env = os.getenv('XDG_CURRENT_DESKTOP', '').lower()
        session_type = os.getenv('XDG_SESSION_TYPE', '').lower()
        
        # Use QT_QPA_PLATFORM environment to determine the best flags
        force_x11 = os.getenv('QT_QPA_PLATFORM') == 'xcb'
        
        if ('gnome' in desktop_env and session_type == 'wayland') and not force_x11:
            # GNOME Wayland: Use SplashScreen type which is often ignored by taskbars
            widget_flags = (
                Qt.WindowType.SplashScreen |  # Alternative that works better on GNOME Wayland
                Qt.WindowType.FramelessWindowHint  # Remove window decorations
                # Note: Removed WindowDoesNotAcceptFocus to allow keyboard shortcuts
            )
        else:
            # X11 or other compositors: Use traditional approach with better behavior
            widget_flags = (
                Qt.WindowType.Tool |  # Prevents taskbar appearance (primary method)
                Qt.WindowType.FramelessWindowHint  # Remove window decorations
                # Note: Removed WindowDoesNotAcceptFocus to allow keyboard shortcuts
            )
        
        self.setWindowFlags(widget_flags)
        
        # Additional platform-specific hints for taskbar avoidance
        self.setAttribute(Qt.WidgetAttribute.WA_X11DoNotAcceptFocus, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, False)  # Ensure it shows but not in taskbar
        
        # GNOME/Wayland specific workarounds
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)  # Avoid compositor issues
        
        # Set window role for GNOME Shell (helps with window classification)
        if hasattr(self, 'setWindowRole'):
            self.setWindowRole("desktop-widget")
        
        # Try to set skip taskbar hint at the window level (post-show)
        self.skip_taskbar_setup_pending = True
        
        # Main layout - 8px grid system
        layout = QVBoxLayout()
        layout.setSpacing(24)  # 8px grid: 24px spacing between major sections
        layout.setContentsMargins(24, 24, 24, 24)  # 8px grid: 24px all around
        
        # Modern Header Design
        header_widget = self.create_modern_header()
        layout.addWidget(header_widget)
        
        # Scrollable tasks area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        # Container widget for task groups
        self.tasks_container = QWidget()
        self.tasks_layout = QVBoxLayout()
        self.tasks_layout.setSpacing(24)  # 8px grid: 24px between groups
        self.tasks_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add stretch at the end to push content to top
        self.tasks_layout.addStretch()
        
        self.tasks_container.setLayout(self.tasks_layout)
        self.scroll_area.setWidget(self.tasks_container)
        layout.addWidget(self.scroll_area)
        
        # Status label - 8px grid spacing
        self.status_label = QLabel("Loading tasks...")
        self.status_label.setFont(QFont("Inter", 10))
        self.status_label.setObjectName("mutedText")
        self.status_label.setContentsMargins(0, 16, 0, 8)  # 8px grid: top 16px, bottom 8px
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
    
    def create_modern_header(self):
        """Create a clean, simple header design"""
        # Simple horizontal layout
        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)  # 8px grid: 16px spacing
        header_layout.setContentsMargins(0, 0, 0, 0)  # No extra margins
        
        # Title
        title_label = QLabel("Tasks")
        title_label.setFont(QFont("Inter", 20, QFont.Weight.Bold))
        title_label.setObjectName("sectionTitle")
        
        # Theme selector
        theme_combo = QComboBox()
        theme_combo.addItems(theme_manager.get_available_themes())
        theme_combo.setCurrentText(theme_manager.get_current_theme_name())
        theme_combo.currentTextChanged.connect(self.change_theme)
        theme_combo.setFixedSize(140, 32)  # 8px grid: wider for proper text display
        
        # Refresh button with circular arrow icon
        refresh_btn = QPushButton("⟲")
        refresh_btn.clicked.connect(self.refresh_tasks)
        refresh_btn.setObjectName("secondaryButton")
        refresh_btn.setFixedSize(36, 32)  # 8px grid: slightly wider for proper icon display
        refresh_btn.setFont(QFont("Arial", 14))  # Use Arial for better unicode support
        refresh_btn.setStyleSheet("""
            QPushButton {
                text-align: center;
                padding: 0px;
            }
        """)
        refresh_btn.setToolTip("Refresh tasks")
        
        # Create a container widget to return
        header_widget = QWidget()
        header_layout.addWidget(title_label)
        header_layout.addStretch()  # Push controls to the right
        header_layout.addWidget(theme_combo)
        header_layout.addWidget(refresh_btn)
        
        header_widget.setLayout(header_layout)
        return header_widget
    
    def complete_startup(self):
        """Complete the deferred startup operations"""
        if not self.deferred_operations_pending:
            return
            
        self.deferred_operations_pending = False
        
        # Apply theme
        self.apply_theme()
        
        # Load saved position
        saved_position = position_manager.load_position()
        self.move(saved_position)
        
        # Start background task loading
        self.startup_optimizer.start()
        
        # Set status
        self.status_label.setText("Loading tasks...")
        
        self.startup_complete = True

    def on_tasks_loaded(self, tasks):
        """Handle tasks loaded from background thread"""
        self.tasks = tasks
        if self.tasks:
            self.update_task_display()
            self.status_label.setText(f"Loaded {len(self.tasks)} tasks")
        else:
            self.status_label.setText("No tasks file found. Click Refresh to fetch tasks.")
        
        # Schedule automatic refresh 3 seconds after startup to get latest tasks
        self.startup_refresh_timer = QTimer()
        self.startup_refresh_timer.setSingleShot(True)
        self.startup_refresh_timer.timeout.connect(self.startup_refresh_tasks)
        self.startup_refresh_timer.start(3000)  # 3 seconds delay

    def startup_refresh_tasks(self):
        """Automatically refresh tasks after startup to ensure latest data"""
        # Prevent multiple startup refreshes
        if not hasattr(self, 'startup_refresh_timer') or not self.startup_refresh_timer:
            return
            
        # Only refresh if we have cached tasks (avoid unnecessary API calls on empty startup)
        if self.tasks:
            # Show subtle status update (different from manual refresh)
            self.status_label.setText("Syncing with server...")
            QApplication.processEvents()
            
            try:
                # Fetch latest tasks from API
                tasks = _get_backend_api()['get_active_standard_tasks']()
                
                # Save to file and update UI
                if _get_backend_api()['save_tasks_to_json'](tasks):
                    self.tasks = tasks
                    self.update_task_display()
                    self.status_label.setText(f"Synced - {len(tasks)} active tasks")
                else:
                    # If save fails, revert to showing cached count
                    self.status_label.setText(f"{len(self.tasks)} active tasks")
            except Exception:
                # If sync fails, silently revert to cached count (don't show error)
                self.status_label.setText(f"{len(self.tasks)} active tasks")
        
        # Clean up timer
        if hasattr(self, 'startup_refresh_timer') and self.startup_refresh_timer:
            self.startup_refresh_timer.deleteLater()
            self.startup_refresh_timer = None

    def load_tasks(self):
        """Load tasks from JSON file - now deprecated, using background loading"""
        # This method is kept for compatibility but now does nothing
        # Tasks are loaded in background via complete_startup()
        pass
    
    def refresh_tasks(self):
        """Refresh tasks from TickTick API"""
        # Clear any pending completion state
        if hasattr(self, 'pending_completion_task'):
            delattr(self, 'pending_completion_task')
        
        self.status_label.setText("Refreshing tasks...")
        QApplication.processEvents()  # Update UI immediately
        
        try:
            # Fetch new tasks
            tasks = _get_backend_api()['get_active_standard_tasks']()
            
            # Save to file
            if _get_backend_api()['save_tasks_to_json'](tasks):
                self.tasks = tasks
                self.update_task_display()
                self.status_label.setText(f"Last updated: {datetime.now().strftime('%H:%M:%S')} - {len(tasks)} tasks")
            else:
                self.status_label.setText("Failed to save tasks")
        except Exception as e:
            self.status_label.setText(f"Error refreshing: {str(e)}")
    
    def update_task_display(self):
        """Update the task display with grouped layout"""
        # Clear existing group widgets
        while self.tasks_layout.count() > 1:  # Keep the stretch at the end
            child = self.tasks_layout.takeAt(0)
            if child:
                widget = child.widget()
                if widget:
                    widget.deleteLater()
        
        if not self.tasks:
            # Show empty state
            empty_label = QLabel("No active tasks")
            empty_label.setFont(QFont("Inter", 12))
            empty_label.setObjectName("mutedText")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setContentsMargins(24, 48, 24, 48)
            self.tasks_layout.insertWidget(0, empty_label)
            return
        
        # Group tasks by time periods
        grouped_tasks = _get_task_grouping()['group_tasks_by_time'](self.tasks)
        
        # Define the order of groups to display
        group_order = ['overdue', 'today', 'tomorrow', 'later']
        
        # Create and add group widgets
        for group_key in group_order:
            tasks_in_group = grouped_tasks.get(group_key, [])
            
            if tasks_in_group:  # Only show groups that have tasks
                # Sort tasks within the group
                sorted_tasks = _get_task_grouping()['sort_tasks_in_group'](tasks_in_group, group_key)
                
                # Get group display info
                group_info = _get_task_grouping()['get_group_display_info'](group_key, len(sorted_tasks))
                
                # Create group widget
                group_widget = _get_task_widgets()['TaskGroupWidget'](group_key, group_info, sorted_tasks)
                
                # Connect task completion signal
                group_widget.task_completed.connect(self.handle_task_completion)
                
                # Insert before the stretch
                self.tasks_layout.insertWidget(self.tasks_layout.count() - 1, group_widget)
    
    def change_theme(self, theme_name):
        """Handle theme change from dropdown"""
        theme_manager.set_theme(theme_name)
    
    def on_theme_changed(self, theme_name):
        """Handle theme change signal"""
        self.apply_theme()
    
    def apply_theme(self):
        """Apply the current theme to this widget"""
        theme_manager.apply_theme_to_widget(self)
    
    def mousePressEvent(self, a0: QMouseEvent | None):
        """Allow dragging the widget - Cross-platform compatible"""
        if a0 and a0.button() == Qt.MouseButton.LeftButton and not self.position_locked:
            # Store the starting position for manual dragging
            self.drag_start_position = a0.globalPosition().toPoint() - self.pos()
            self.dragging = True
            
            # Also try the modern approach for systems that support it
            window_handle = self.windowHandle()
            if window_handle and hasattr(window_handle, 'startSystemMove'):
                try:
                    # This works on modern systems but may not work with Tool window type
                    window_handle.startSystemMove()
                    self.dragging = False  # System is handling it
                except Exception:
                    # Fall back to manual dragging
                    pass
    
    def mouseMoveEvent(self, a0: QMouseEvent | None):
        """Handle widget dragging - Manual dragging implementation"""
        if (a0 and hasattr(self, 'dragging') and self.dragging and 
            hasattr(self, 'drag_start_position') and 
            a0.buttons() == Qt.MouseButton.LeftButton and not self.position_locked):
            # Manual dragging - works reliably across all platforms and window types
            new_pos = a0.globalPosition().toPoint() - self.drag_start_position
            self.move(new_pos)
    
    def mouseReleaseEvent(self, a0: QMouseEvent | None):
        """End dragging when mouse is released"""
        if hasattr(self, 'dragging'):
            self.dragging = False
            # Save position after dragging (only if not locked)
            if not self.position_locked:
                position_manager.save_position(self.pos())
    
    def moveEvent(self, a0):
        """Handle widget being moved and save the new position"""
        super().moveEvent(a0)
        # Save position whenever widget is moved (by any means) - only if not locked
        if not self.position_locked:
            # Add a small delay to avoid excessive saves during dragging
            if hasattr(self, '_move_timer'):
                self._move_timer.stop()
            
            from PyQt6.QtCore import QTimer
            self._move_timer = QTimer()
            self._move_timer.setSingleShot(True)
            self._move_timer.timeout.connect(lambda: position_manager.save_position(self.pos()))
            self._move_timer.start(500)  # Save 500ms after last move
    
    def keyPressEvent(self, a0):
        """Handle keyboard shortcuts"""
        # Toggle always on top with Ctrl+T
        if a0 and a0.key() == Qt.Key.Key_T and a0.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.toggle_always_on_top()
        # Toggle position lock with Ctrl+L
        elif a0 and a0.key() == Qt.Key.Key_L and a0.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.toggle_position_lock()
        super().keyPressEvent(a0)
    
    def toggle_always_on_top(self):
        """Toggle whether the widget stays on top of other windows"""
        current_flags = self.windowFlags()
        if current_flags & Qt.WindowType.WindowStaysOnTopHint:
            # Remove always on top
            new_flags = current_flags & ~Qt.WindowType.WindowStaysOnTopHint
            self.setWindowFlags(new_flags)
            self.show()  # Need to show again after changing flags
        else:
            # Add always on top
            new_flags = current_flags | Qt.WindowType.WindowStaysOnTopHint
            self.setWindowFlags(new_flags)
            self.show()  # Need to show again after changing flags
    
    def toggle_position_lock(self):
        """Toggle whether the widget position is locked (prevents mouse dragging)"""
        self.position_locked = not self.position_locked
        position_manager.save_lock_state(self.position_locked)
        
        # Update status briefly to show lock state
        if self.position_locked:
            self.status_label.setText("🔒 Position locked (Ctrl+L to unlock)")
        else:
            self.status_label.setText("🔓 Position unlocked (Ctrl+L to lock)")
        
        # Reset status after 2 seconds
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(2000, lambda: self.status_label.setText(f"{len(self.tasks)} active tasks"))
    
    def showEvent(self, a0):
        """Handle post-show setup for Wayland/GNOME compatibility"""
        super().showEvent(a0)
        
        # Apply additional hints after window is realized
        if hasattr(self, 'skip_taskbar_setup_pending') and self.skip_taskbar_setup_pending:
            self.skip_taskbar_setup_pending = False
            self.setup_wayland_hints()
    
    def setup_wayland_hints(self):
        """Apply Wayland/GNOME specific hints for taskbar avoidance"""
        try:
            window_handle = self.windowHandle()
            if window_handle:
                # Try to set window type hint to dock/desktop for GNOME Shell
                from PyQt6.QtGui import QWindow
                
                # Set additional properties that GNOME Shell might respect
                window_handle.setProperty("_NET_WM_WINDOW_TYPE", "_NET_WM_WINDOW_TYPE_DOCK")
                window_handle.setProperty("_NET_WM_STATE", "_NET_WM_STATE_SKIP_TASKBAR")
                window_handle.setProperty("_NET_WM_STATE", "_NET_WM_STATE_SKIP_PAGER")
                
                # Alternative: try setting as a desktop widget
                window_handle.setProperty("_KDE_NET_WM_WINDOW_TYPE_OVERRIDE", 1)
                    
        except Exception:
            # Silently ignore errors in hint setting
            pass
    
    def handle_task_completion(self, task_id):
        """Handle task completion request from UI - aggressive optimistic updates"""
        if not task_id:
            return
        
        # Find the task data for potential rollback
        task_data = next((task for task in self.tasks if task.get('id') == task_id), None)
        if not task_data:
            return
        
        # Store original task data for potential rollback
        self.pending_completion_task = task_data.copy()
        
        # Aggressive optimistic UI update - remove task from UI immediately
        self.tasks = [task for task in self.tasks if task.get('id') != task_id]
        self.update_task_display()
        
        # Update status optimistically
        task_title = task_data.get('title', 'Task')
        self.status_label.setText(f"✅ Completed: {task_title} - {len(self.tasks)} active tasks")
        QApplication.processEvents()  # Update UI immediately
        
        # Create and start background worker thread for actual completion
        self.completion_worker = TaskCompletionWorker(task_id)
        
        # Connect worker signals to handlers
        self.completion_worker.task_completed.connect(self.on_task_completion_success)
        self.completion_worker.task_completion_failed.connect(self.on_task_completion_failed)
        
        # Start the background task
        self.completion_worker.start()
    
    def on_task_completion_success(self, task_id, completed_task):
        """Handle successful task completion from background thread"""
        # Task already removed from UI due to aggressive optimistic update
        # Just sync the backend state and update status properly
        
        # Clean up stored task data
        if hasattr(self, 'pending_completion_task'):
            delattr(self, 'pending_completion_task')
        
        # Update backend cache and status after showing completion message briefly
        QTimer.singleShot(1500, self.update_status_after_completion)
        
        # Clean up worker
        if self.completion_worker:
            self.completion_worker.deleteLater()
            self.completion_worker = None
    
    def update_status_after_completion(self):
        """Update backend cache and status bar after successful completion"""
        # Update backend cache
        if _get_backend_api()['refresh_local_task_cache']():
            # Update status to show normal state with task count
            self.status_label.setText(f"{len(self.tasks)} active tasks")
        else:
            # If cache refresh fails, still show task count
            self.status_label.setText(f"{len(self.tasks)} active tasks")
    
    def on_task_completion_failed(self, task_id, error_message):
        """Handle failed task completion from background thread"""
        # Revert aggressive optimistic update - restore task to UI
        if hasattr(self, 'pending_completion_task'):
            # Add the task back to the list
            self.tasks.append(self.pending_completion_task)
            
            # Re-sort tasks to maintain proper order
            # Simple sort by title for now, could be enhanced with proper grouping logic
            self.tasks.sort(key=lambda x: x.get('title', ''))
            
            # Refresh UI to show the task again
            self.update_task_display()
            
            # Find the restored task widget and set error state
            QTimer.singleShot(50, lambda: self.set_task_error_state(task_id, error_message))
            
            # Clean up stored task data
            delattr(self, 'pending_completion_task')
        
        # Update status
        self.status_label.setText(f"❌ Error completing task: {error_message}")
        
        # Clean up worker
        if self.completion_worker:
            self.completion_worker.deleteLater()
            self.completion_worker = None
    
    def set_task_error_state(self, task_id, error_message):
        """Helper to set error state on a task widget after UI refresh"""
        task_widget = self.find_task_widget(task_id)
        if task_widget:
            checkbox = task_widget.get_checkbox() if hasattr(task_widget, 'get_checkbox') else None
            if checkbox:
                checkbox.set_error_state(error_message)
    
    def find_task_widget(self, task_id):
        """Find the task widget for a given task ID"""
        # Iterate through all group widgets to find the task
        for i in range(self.tasks_layout.count() - 1):  # Exclude the stretch
            item = self.tasks_layout.itemAt(i)
            if item and item.widget():
                group_widget = item.widget()
                # Check if this is a TaskGroupWidget with task_widgets attribute
                task_widgets = getattr(group_widget, 'task_widgets', None)
                if (isinstance(task_widgets, dict) and task_id in task_widgets):
                    return task_widgets[task_id]
        return None
    



def main():
    app = QApplication(sys.argv)
    
    # Set application metadata and process name
    app.setApplicationName("TickTick Widget")
    app.setApplicationDisplayName("TickTick Widget") 
    app.setApplicationVersion("1.0")
    app.setOrganizationName("TickTick Widget")
    
    # Try to set process title for better process identification
    try:
        import importlib
        setproctitle = importlib.import_module('setproctitle')
        setproctitle.setproctitle("TickTick Widget")
    except ImportError:
        # setproctitle not available - install with: pip install setproctitle
        pass
    
    # Set application style
    app.setStyle('Fusion')
    
    # Apply theme to application
    theme_manager.apply_theme_to_app(app)
    
    widget = TickTickWidget()
    widget.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 