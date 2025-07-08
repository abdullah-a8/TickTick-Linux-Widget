import sys
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                            QScrollArea, QPushButton, QLabel,
                            QFrame, QSizePolicy, QComboBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QMouseEvent

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
        
        # Make window stay on top and frameless for widget-like appearance
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        
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
        """Allow dragging the widget"""
        if a0 and a0.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = a0.globalPosition().toPoint() - self.pos()
    
    def mouseMoveEvent(self, a0: QMouseEvent | None):
        """Handle widget dragging"""
        if a0 and hasattr(self, 'drag_start_position') and a0.buttons() == Qt.MouseButton.LeftButton:
            self.move(a0.globalPosition().toPoint() - self.drag_start_position)


def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Apply theme to application
    theme_manager.apply_theme_to_app(app)
    
    widget = TickTickWidget()
    widget.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 