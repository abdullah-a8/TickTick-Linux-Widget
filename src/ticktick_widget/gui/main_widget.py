import sys
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                            QListWidget, QListWidgetItem, QPushButton, QLabel,
                            QFrame, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QMouseEvent

from ..backend.api import get_active_standard_tasks, save_tasks_to_json


class TaskItemWidget(QWidget):
    """Custom widget for displaying a single task"""
    
    def __init__(self, task_data):
        super().__init__()
        self.task_data = task_data
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(4)
        layout.setContentsMargins(8, 6, 8, 6)
        
        # Main task info layout
        main_layout = QHBoxLayout()
        
        # Task title
        title = self.task_data.get('title', 'Untitled Task')
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        title_label.setWordWrap(True)
        
        # Priority indicator
        priority = self.task_data.get('priority', 0)
        priority_text = self.get_priority_text(priority)
        priority_label = QLabel(priority_text)
        priority_label.setFont(QFont("Arial", 8))
        priority_label.setStyleSheet(self.get_priority_style(priority))
        priority_label.setFixedWidth(60)
        priority_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        main_layout.addWidget(title_label)
        main_layout.addWidget(priority_label)
        
        layout.addLayout(main_layout)
        
        # Due date if available
        if 'dueDate' in self.task_data:
            due_date = self.format_due_date(self.task_data['dueDate'])
            due_label = QLabel(f"Due: {due_date}")
            due_label.setFont(QFont("Arial", 8))
            due_label.setStyleSheet("color: #666666;")
            layout.addWidget(due_label)
        
        # Content if available
        if 'content' in self.task_data and self.task_data['content']:
            content_label = QLabel(self.task_data['content'])
            content_label.setFont(QFont("Arial", 8))
            content_label.setStyleSheet("color: #888888;")
            content_label.setWordWrap(True)
            layout.addWidget(content_label)
        
        self.setLayout(layout)
        
        # Add border and background
        self.setStyleSheet("""
            TaskItemWidget {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 6px;
                margin: 2px;
            }
            TaskItemWidget:hover {
                background-color: #e9ecef;
            }
        """)
    
    def get_priority_text(self, priority):
        priority_map = {
            5: "High",
            4: "High", 
            3: "Med",
            2: "Low",
            1: "Low",
            0: "None"
        }
        return priority_map.get(priority, "None")
    
    def get_priority_style(self, priority):
        if priority >= 4:
            return "background-color: #dc3545; color: white; border-radius: 3px; padding: 2px;"
        elif priority == 3:
            return "background-color: #fd7e14; color: white; border-radius: 3px; padding: 2px;"
        elif priority >= 1:
            return "background-color: #28a745; color: white; border-radius: 3px; padding: 2px;"
        else:
            return "background-color: #6c757d; color: white; border-radius: 3px; padding: 2px;"
    
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
    
    def setup_ui(self):
        self.setWindowTitle("TickTick Tasks")
        self.setFixedSize(400, 600)
        
        # Make window stay on top and frameless for widget-like appearance
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("TickTick Tasks")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_tasks)
        refresh_btn.setMaximumWidth(80)
        
        close_btn = QPushButton("×")
        close_btn.clicked.connect(self.close)
        close_btn.setMaximumWidth(30)
        close_btn.setStyleSheet("QPushButton { color: red; font-weight: bold; }")
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(refresh_btn)
        header_layout.addWidget(close_btn)
        
        layout.addLayout(header_layout)
        
        # Task list
        self.task_list = QListWidget()
        self.task_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                background-color: white;
            }
            QListWidget::item {
                border: none;
                padding: 0px;
                margin: 4px;
            }
        """)
        layout.addWidget(self.task_list)
        
        # Status label
        self.status_label = QLabel("Loading tasks...")
        self.status_label.setFont(QFont("Arial", 9))
        self.status_label.setStyleSheet("color: #666666;")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
        # Widget styling
        self.setStyleSheet("""
            TickTickWidget {
                background-color: #ffffff;
                border: 2px solid #dee2e6;
                border-radius: 10px;
            }
        """)
    
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
    
    widget = TickTickWidget()
    widget.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 