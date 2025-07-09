from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QFrame, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from .task_item_widget import TaskItemWidget


class TaskGroupWidget(QWidget):
    """Widget for displaying a group of tasks with a header"""
    
    # Signal emitted when a task should be completed
    task_completed = pyqtSignal(str)  # Emits task_id
    
    def __init__(self, group_key, group_info, tasks, parent=None):
        super().__init__(parent)
        self.group_key = group_key
        self.group_info = group_info  
        self.tasks = tasks
        self.task_widgets = {}  # Store task widgets for state management
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI for the task group"""
        layout = QVBoxLayout()
        layout.setSpacing(16)  # 8px grid: 16px spacing
        layout.setContentsMargins(0, 0, 0, 0)  # No extra margins
        
        # Only show group if it has tasks
        if not self.tasks:
            self.hide()
            return
            
        # Group header
        header_widget = self.create_group_header()
        layout.addWidget(header_widget)
        
        # Tasks container
        tasks_container = self.create_tasks_container()
        layout.addWidget(tasks_container)
        
        self.setLayout(layout)
    
    def create_group_header(self):
        """Create the group header with title, count, and icon"""
        header_widget = QWidget()
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)  # 8px grid: 12px spacing
        header_layout.setContentsMargins(24, 12, 24, 12)  # 8px grid: equal top/bottom margins
        
        # Icon label
        icon_label = QLabel(self.group_info['icon'])
        icon_label.setFont(QFont("Inter", 16))
        icon_label.setFixedSize(24, 24)  # 8px grid: 24px square
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)  # Center both horizontally and vertically
        
        # Title label with improved typography
        title_label = QLabel(self.group_info['title'])
        title_label.setFont(QFont("Inter", 13, QFont.Weight.DemiBold))
        title_label.setObjectName("sectionSubtitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)  # Vertical center alignment
        
        # Count label with better styling
        count_label = QLabel(self.group_info['subtitle'])
        count_label.setFont(QFont("Inter", 11, QFont.Weight.Medium))
        count_label.setObjectName("subtitleText")
        count_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)  # Vertical center alignment
        
        # Add to layout with proper alignment
        header_layout.addWidget(icon_label, 0, Qt.AlignmentFlag.AlignVCenter)
        header_layout.addWidget(title_label, 0, Qt.AlignmentFlag.AlignVCenter)
        header_layout.addStretch()  # Push count to the right
        header_layout.addWidget(count_label, 0, Qt.AlignmentFlag.AlignVCenter)
        
        # Style the header
        header_widget.setLayout(header_layout)
        header_widget.setObjectName("taskGroupHeader")
        header_widget.setMinimumHeight(48)  # 8px grid: consistent header height
        
        # Ensure all child labels have transparent backgrounds for consistency
        header_widget.setStyleSheet("""
            QWidget#taskGroupHeader QLabel {
                background-color: transparent;
            }
        """)
        
        # Add priority styling for overdue tasks
        if self.group_key == 'overdue':
            header_widget.setStyleSheet("""
                QWidget#taskGroupHeader {
                    border-left: 3px solid #ef4444;
                    background-color: rgba(239, 68, 68, 0.05);
                    border-radius: 8px;
                }
                QWidget#taskGroupHeader QLabel {
                    background-color: transparent;
                }
            """)
        
        return header_widget
    
    def create_tasks_container(self):
        """Create container for task items"""
        container = QWidget()
        container_layout = QVBoxLayout()
        container_layout.setSpacing(8)  # 8px grid: 8px between task items
        container_layout.setContentsMargins(16, 0, 16, 0)  # 8px grid: 16px horizontal
        
        # Create task widgets and connect signals
        for task in self.tasks:
            task_widget = TaskItemWidget(task)
            
            # Connect task completion signal
            task_widget.task_completed.connect(self.task_completed.emit)
            
            # Store widget for state management
            task_id = task.get('id', '')
            if task_id:
                self.task_widgets[task_id] = task_widget
            
            container_layout.addWidget(task_widget)
        
        container.setLayout(container_layout)
        return container
    
    def update_tasks(self, tasks):
        """Update the tasks in this group"""
        self.tasks = tasks
        
        # Clear existing layout
        layout = self.layout()
        if layout:
            while layout.count():
                child = layout.takeAt(0)
                if child:
                    widget = child.widget()
                    if widget:
                        widget.deleteLater()
        
        # Rebuild UI
        self.setup_ui()
    
    def get_task_count(self):
        """Get the number of tasks in this group"""
        return len(self.tasks)
    
    def set_task_completing_state(self, task_id, is_completing=True):
        """Set completing state for a specific task"""
        if task_id in self.task_widgets:
            self.task_widgets[task_id].set_completing_state(is_completing)
    
    def set_task_completed_state(self, task_id):
        """Set completed state for a specific task"""
        if task_id in self.task_widgets:
            self.task_widgets[task_id].set_completed_state()
    
    def set_task_error_state(self, task_id, error_message=""):
        """Set error state for a specific task"""
        if task_id in self.task_widgets:
            self.task_widgets[task_id].set_error_state(error_message)
    
    def remove_completed_task(self, task_id):
        """Remove a completed task from the group"""
        if task_id in self.task_widgets:
            # Remove from widget tracking
            task_widget = self.task_widgets.pop(task_id)
            
            # Remove from tasks list
            self.tasks = [task for task in self.tasks if task.get('id') != task_id]
            
            # Remove widget from UI
            task_widget.deleteLater()
            
            # Update group header count
            self.update_group_header()
    
    def update_group_header(self):
        """Update the group header information after task changes"""
        # Update group info with new task count
        from ..utils.task_grouping import get_group_display_info
        self.group_info = get_group_display_info(self.group_key, len(self.tasks))
        
        # If no tasks left, hide the group
        if len(self.tasks) == 0:
            self.hide()
        
        # Rebuild the UI to reflect changes
        self.setup_ui()
    
    def is_empty(self):
        """Check if the group has no tasks"""
        return len(self.tasks) == 0 