from datetime import datetime, timezone
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class TaskItemWidget(QWidget):
    """Modern card-style widget for displaying a single task"""
    
    def __init__(self, task_data):
        super().__init__()
        self.task_data = task_data
        self.setup_ui()
        self.setup_card_styling()
    
    def setup_ui(self):
        """Setup the modern card UI layout"""
        # Main container with card styling
        self.setObjectName("taskCard")
        
        # Main layout with proper card padding
        layout = QVBoxLayout()
        layout.setSpacing(12)  # 8px grid: 12px spacing between elements
        layout.setContentsMargins(20, 16, 20, 16)  # 8px grid: card padding
        
        # Header section with title and priority
        header_section = self.create_header_section()
        layout.addWidget(header_section)
        
        # Metadata section (due date, content)
        metadata_section = self.create_metadata_section()
        if metadata_section:
            layout.addWidget(metadata_section)
        
        self.setLayout(layout)
    
    def create_header_section(self):
        """Create the main header with title and priority badge"""
        header_widget = QWidget()
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)  # 8px grid: 12px spacing
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Task title with improved typography
        title = self.task_data.get('title', 'Untitled Task')
        title_label = QLabel(title)
        title_label.setFont(QFont("Inter", 14, QFont.Weight.DemiBold))
        title_label.setObjectName("taskTitle")
        title_label.setWordWrap(True)
        title_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        # Priority badge with modern styling
        priority_badge = self.create_priority_badge()
        
        # Layout
        header_layout.addWidget(title_label, 1)  # Title takes most space
        header_layout.addWidget(priority_badge, 0)  # Badge takes minimal space
        
        header_widget.setLayout(header_layout)
        return header_widget
    
    def create_priority_badge(self):
        """Create a modern priority badge"""
        priority = self.task_data.get('priority', 0)
        priority_text = self.get_priority_text(priority)
        
        badge = QLabel(priority_text)
        badge.setFont(QFont("Inter", 9, QFont.Weight.Bold))
        badge.setObjectName(self.get_priority_style(priority))
        badge.setFixedSize(28, 20)  # 8px grid: compact badge size
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        return badge
    
    def create_metadata_section(self):
        """Create metadata section with due date and content"""
        metadata_widget = QWidget()
        metadata_layout = QVBoxLayout()
        metadata_layout.setSpacing(8)  # 8px grid: tight spacing for metadata
        metadata_layout.setContentsMargins(0, 0, 0, 0)
        
        has_metadata = False
        
        # Due date with improved styling
        if 'dueDate' in self.task_data:
            due_info = self.create_due_date_info()
            metadata_layout.addWidget(due_info)
            has_metadata = True
        
        # Content/description with better typography
        if 'content' in self.task_data and self.task_data['content'].strip():
            content_widget = self.create_content_widget()
            metadata_layout.addWidget(content_widget)
            has_metadata = True
        
        if has_metadata:
            metadata_widget.setLayout(metadata_layout)
            return metadata_widget
        
        return None
    
    def create_due_date_info(self):
        """Create styled due date information"""
        due_date_text = self.format_due_date(self.task_data['dueDate'])
        
        # Create a container for due date
        due_container = QWidget()
        due_layout = QHBoxLayout()
        due_layout.setSpacing(8)  # 8px spacing
        due_layout.setContentsMargins(0, 0, 0, 0)
        
        # Due date icon and text
        icon_label = QLabel("📅")
        icon_label.setFont(QFont("Inter", 11))
        icon_label.setFixedSize(16, 16)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        text_label = QLabel(due_date_text)
        text_label.setFont(QFont("Inter", 11, QFont.Weight.Medium))
        text_label.setObjectName("taskDueDate")
        
        # Check if overdue for special styling
        if "Overdue" in due_date_text:
            text_label.setObjectName("taskOverdue")
            icon_label.setText("⚠️")
        elif "Today" in due_date_text:
            text_label.setObjectName("taskDueToday")
        
        due_layout.addWidget(icon_label)
        due_layout.addWidget(text_label)
        due_layout.addStretch()  # Push content to left
        
        due_container.setLayout(due_layout)
        return due_container
    
    def create_content_widget(self):
        """Create styled content/description widget"""
        content_text = self.task_data['content'].strip()
        
        # Truncate if too long
        if len(content_text) > 120:
            content_text = content_text[:120] + "..."
        
        content_label = QLabel(content_text)
        content_label.setFont(QFont("Inter", 11))
        content_label.setObjectName("taskContent")
        content_label.setWordWrap(True)
        content_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        return content_label
    
    def setup_card_styling(self):
        """Setup modern card styling"""
        # The actual card styling will be handled by the theme system
        # This ensures the widget has the right object name for styling
        pass
    
    def get_priority_text(self, priority):
        """Get priority badge text"""
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
        """Get priority badge style class"""
        if priority >= 4:
            return "priorityHigh"
        elif priority == 3:
            return "priorityMedium"
        elif priority >= 1:
            return "priorityLow"
        else:
            return "priorityNone"
    
    def format_due_date(self, due_date_str):
        """Format due date with improved text"""
        try:
            due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)
            
            # Use same calendar day logic as grouping function
            today = now.replace(hour=0, minute=0, second=0, microsecond=0)
            due_date_day = due_date.replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Calculate calendar day difference
            day_diff = (due_date_day - today).days
            
            # Also calculate time difference for more detailed "today" messages
            time_diff = due_date - now
            hours = max(0, int(time_diff.total_seconds() // 3600))
            
            if day_diff < 0:
                return f"Overdue by {abs(day_diff)} day{'s' if abs(day_diff) != 1 else ''}"
            elif day_diff == 0:
                if hours < 1:
                    return "Due very soon"
                elif hours < 12:
                    return f"Due today ({hours}h left)"
                else:
                    return "Due today"
            elif day_diff == 1:
                return "Due tomorrow"
            elif day_diff <= 7:
                return f"Due in {day_diff} days"
            else:
                # Show actual date for far future
                return due_date.strftime("%b %d")
        except:
            return due_date_str.split('T')[0]  # Fallback to date part 