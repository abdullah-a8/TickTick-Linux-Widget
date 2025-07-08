import sys
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                            QListWidget, QListWidgetItem, QPushButton, QLabel,
                            QFrame, QSizePolicy, QComboBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QMouseEvent

from ..backend.api import get_active_standard_tasks, save_tasks_to_json
from ..config.theme_manager import theme_manager


class TaskItemWidget(QWidget):
    """Custom widget for displaying a single task"""
    
    def __init__(self, task_data):
        super().__init__()
        self.task_data = task_data
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(16)  # 8px grid: 16px spacing
        layout.setContentsMargins(24, 16, 24, 16)  # 8px grid: 24px horizontal, 16px vertical
        
        # Main task info layout
        main_layout = QHBoxLayout()
        main_layout.setSpacing(16)  # 8px grid: 16px spacing
        
        # Task title
        title = self.task_data.get('title', 'Untitled Task')
        title_label = QLabel(title)
        title_label.setFont(QFont("Inter", 13, QFont.Weight.DemiBold))
        title_label.setObjectName("primaryText")
        title_label.setWordWrap(True)
        title_label.setStyleSheet("line-height: 1.4;")
        
        # Priority indicator - 8px grid aligned
        priority = self.task_data.get('priority', 0)
        priority_text = self.get_priority_text(priority)
        priority_label = QLabel(priority_text)
        priority_label.setFont(QFont("Inter", 7, QFont.Weight.Bold))
        priority_label.setObjectName(self.get_priority_style(priority))
        priority_label.setFixedSize(32, 16)  # 8px grid: 32px x 16px
        priority_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        main_layout.addWidget(title_label, 1)  # Give title more space
        main_layout.addWidget(priority_label, 0)  # Priority takes minimal space
        
        layout.addLayout(main_layout)
        
        # Add some spacing before metadata - 8px grid
        layout.addSpacing(8)
        
        # Due date if available - more prominent but still secondary
        if 'dueDate' in self.task_data:
            due_date = self.format_due_date(self.task_data['dueDate'])
            due_label = QLabel(f"📅 {due_date}")
            due_label.setFont(QFont("Inter", 10, QFont.Weight.Medium))
            due_label.setObjectName("subtitleText")
            layout.addWidget(due_label)
        
        # Content if available - clear but subdued
        if 'content' in self.task_data and self.task_data['content']:
            layout.addSpacing(8)  # 8px grid spacing
            content_label = QLabel(self.task_data['content'])
            content_label.setFont(QFont("Inter", 10))
            content_label.setObjectName("mutedText")
            content_label.setWordWrap(True)
            layout.addWidget(content_label)
        
        self.setLayout(layout)
    
    def get_priority_text(self, priority):
        priority_map = {
            5: "H",
            4: "H", 
            3: "M",
            2: "L",
            1: "L",
            0: "—"
        }
        return priority_map.get(priority, "—")
    
    def get_priority_style(self, priority):
        # Set object name for theme styling instead of inline styles
        if priority >= 4:
            return "priorityHigh"
        elif priority == 3:
            return "priorityMedium"
        elif priority >= 1:
            return "priorityLow"
        else:
            return "priorityNone"
    
    def format_due_date(self, due_date_str):
        try:
            # Parse the ISO datetime string
            due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)
            
            # Calculate time difference
            diff = due_date - now
            days = diff.days
            
            if days < 0:
                return f"Overdue by {abs(days)} days"
            elif days == 0:
                return "Due Today"
            elif days == 1:
                return "Due Tomorrow"
            else:
                return f"Due in {days} days"
        except:
            return due_date_str.split('T')[0]  # Fallback to date part


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
        self.setWindowTitle("TickTick Tasks")
        self.setFixedSize(440, 640)  # 8px grid: increased size to accommodate better spacing
        
        # Make window stay on top and frameless for widget-like appearance
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        
        # Main layout - 8px grid system
        layout = QVBoxLayout()
        layout.setSpacing(24)  # 8px grid: 24px spacing between major sections
        layout.setContentsMargins(24, 24, 24, 24)  # 8px grid: 24px all around
        
        # Header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)  # 8px grid: 16px between header elements
        
        title_label = QLabel("TickTick Tasks")
        title_label.setFont(QFont("Inter", 18, QFont.Weight.Bold))
        title_label.setObjectName("sectionTitle")
        title_label.setContentsMargins(0, 0, 0, 0)  # Remove extra margins for clean alignment
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_tasks)
        refresh_btn.setObjectName("secondaryButton")
        refresh_btn.setFixedSize(88, 32)  # 8px grid: 88px width, 32px height
        
        # Theme selector dropdown
        theme_combo = QComboBox()
        theme_combo.addItems(theme_manager.get_available_themes())
        theme_combo.setCurrentText(theme_manager.get_current_theme_name())
        theme_combo.currentTextChanged.connect(self.change_theme)
        theme_combo.setFixedSize(128, 32)  # 8px grid: 128px width, 32px height
        
        close_btn = QPushButton("×")
        close_btn.clicked.connect(self.close)
        close_btn.setFixedSize(32, 32)  # 8px grid: 32px square
        close_btn.setObjectName("secondaryButton")
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(theme_combo)
        header_layout.addWidget(refresh_btn)
        header_layout.addWidget(close_btn)
        
        layout.addLayout(header_layout)
        
        # Task list
        self.task_list = QListWidget()
        layout.addWidget(self.task_list)
        
        # Status label - 8px grid spacing
        self.status_label = QLabel("Loading tasks...")
        self.status_label.setFont(QFont("Inter", 10))
        self.status_label.setObjectName("mutedText")
        self.status_label.setContentsMargins(0, 16, 0, 8)  # 8px grid: top 16px, bottom 8px
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
    
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
        """Update the task list display"""
        self.task_list.clear()
        
        if not self.tasks:
            item = QListWidgetItem("No active tasks")
            self.task_list.addItem(item)
            return
        
        # Sort tasks by priority (high to low) then by due date
        sorted_tasks = sorted(self.tasks, key=lambda x: (
            -x.get('priority', 0),  # Negative for descending
            x.get('dueDate', '9999-12-31')  # Future date for tasks without due date
        ))
        
        for task in sorted_tasks:
            # Create custom widget for this task
            task_widget = TaskItemWidget(task)
            
            # Create list item and add widget
            item = QListWidgetItem()
            item.setSizeHint(task_widget.sizeHint())
            
            self.task_list.addItem(item)
            self.task_list.setItemWidget(item, task_widget)
    
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