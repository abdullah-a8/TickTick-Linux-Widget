import sys
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                            QScrollArea, QPushButton, QLabel,
                            QFrame, QSizePolicy, QComboBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QMouseEvent, QShowEvent

from ..backend.api import get_active_standard_tasks, save_tasks_to_json
from ..config.theme_manager import theme_manager
from ..utils.task_grouping import group_tasks_by_time, get_group_display_info, sort_tasks_in_group
from .task_group_widget import TaskGroupWidget
from .task_item_widget import TaskItemWidget



class TickTickWidget(QWidget):
    """Main widget for displaying TickTick tasks"""
    
    def __init__(self):
        super().__init__()
        self.tasks = []
        self.setup_ui()
        self.load_tasks()
        
        # Setup auto-refresh timer (every 5 minutes)
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_tasks)
        self.timer.start(300000)  # 5 minutes in milliseconds
        
        # Connect to theme manager
        theme_manager.theme_changed.connect(self.on_theme_changed)
        self.apply_theme()
    
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
        
        # Position the widget in a reasonable default location
        self.move(100, 100)  # Start away from corner
    
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
    
    def load_tasks(self):
        """Load tasks from JSON file"""
        try:
            project_root = Path(__file__).parent.parent.parent.parent
            json_file = project_root / "data" / "allActiveTasks.json"
            
            if json_file.exists():
                with open(json_file, 'r', encoding='utf-8') as f:
                    self.tasks = json.load(f)
                self.update_task_display()
            else:
                self.status_label.setText("No tasks file found. Click Refresh to fetch tasks.")
        except Exception as e:
            self.status_label.setText(f"Error loading tasks: {str(e)}")
    
    def refresh_tasks(self):
        """Refresh tasks from TickTick API"""
        self.status_label.setText("Refreshing tasks...")
        QApplication.processEvents()  # Update UI immediately
        
        try:
            # Fetch new tasks
            tasks = get_active_standard_tasks()
            
            # Save to file
            if save_tasks_to_json(tasks):
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
        grouped_tasks = group_tasks_by_time(self.tasks)
        
        # Define the order of groups to display
        group_order = ['overdue', 'today', 'tomorrow', 'later']
        
        # Create and add group widgets
        for group_key in group_order:
            tasks_in_group = grouped_tasks.get(group_key, [])
            
            if tasks_in_group:  # Only show groups that have tasks
                # Sort tasks within the group
                sorted_tasks = sort_tasks_in_group(tasks_in_group, group_key)
                
                # Get group display info
                group_info = get_group_display_info(group_key, len(sorted_tasks))
                
                # Create group widget
                group_widget = TaskGroupWidget(group_key, group_info, sorted_tasks)
                
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
        if a0 and a0.button() == Qt.MouseButton.LeftButton:
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
            a0.buttons() == Qt.MouseButton.LeftButton):
            # Manual dragging - works reliably across all platforms and window types
            new_pos = a0.globalPosition().toPoint() - self.drag_start_position
            self.move(new_pos)
    
    def mouseReleaseEvent(self, a0: QMouseEvent | None):
        """End dragging when mouse is released"""
        if hasattr(self, 'dragging'):
            self.dragging = False
    
    def keyPressEvent(self, a0):
        """Handle keyboard shortcuts"""
        # Toggle always on top with Ctrl+T
        if a0 and a0.key() == Qt.Key.Key_T and a0.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.toggle_always_on_top()
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