from PyQt6.QtWidgets import QCheckBox, QWidget, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor


class PriorityCheckbox(QCheckBox):
    """
    Color-coded checkbox based on task priority that handles task completion
    
    Features:
    - Color matches TickTick priority system (High=Red, Medium=Orange, Low=Green, None=Gray)
    - Smooth hover and click interactions
    - Emits signals for task completion
    - Integrates with existing theme system
    """
    
    # Signal emitted when task should be completed
    task_completed = pyqtSignal(str)  # Emits task_id
    
    def __init__(self, task_data, parent=None):
        super().__init__(parent)
        self.task_data = task_data
        self.task_id = task_data.get('id', '')
        self.priority = task_data.get('priority', 0)
        
        # Setup checkbox appearance and behavior
        self.setup_checkbox()
        self.apply_priority_colors()
        
        # Connect signals
        self.clicked.connect(self.on_checkbox_clicked)
    
    def setup_checkbox(self):
        """Setup basic checkbox properties"""
        # Make checkbox larger for better touch/click target
        self.setFixedSize(22, 22)
        
        # Use text to show checkmark when checked
        self.setText("")
        self.stateChanged.connect(self.update_text)
        
        # Set tooltip for accessibility
        self.setToolTip(f"Mark task as completed (Priority: {self.get_priority_text()})")
        
        # Ensure checkbox is focusable for keyboard navigation
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
    
    def update_text(self, state):
        """Update checkbox text based on state"""
        if state == Qt.CheckState.Checked.value:
            self.setText("✓")
        else:
            self.setText("")
    
    def apply_priority_colors(self):
        """Apply color styling based on task priority using the existing priority color system"""
        priority_colors = self.get_priority_colors()
        
        # Create custom stylesheet for the checkbox with priority colors
        checkbox_style = f"""
        QCheckBox {{
            spacing: 2px;
            outline: none;
            color: white;
            font-weight: bold;
            font-size: 12px;
        }}
        
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border-radius: 9px;
            border: 2px solid {priority_colors['border']};
            background-color: {priority_colors['background']};
        }}
        
        QCheckBox::indicator:hover {{
            border: 3px solid #d1d5db;
            background-color: #f3f4f615;
        }}
        
        QCheckBox::indicator:pressed {{
            border: 2px solid {priority_colors['pressed_border']};
            background-color: {priority_colors['pressed_background']};
        }}
        
        QCheckBox::indicator:checked {{
            border: 2px solid {priority_colors['checked_border']};
            background-color: {priority_colors['checked_background']};
        }}
        
        QCheckBox::indicator:checked:hover {{
            border: 3px solid #d1d5db;
            background-color: {priority_colors['checked_background']};
        }}
        
        QCheckBox::indicator:focus {{
            border: 3px solid {priority_colors['focus_border']};
        }}
        """
        
        self.setStyleSheet(checkbox_style)
    
    def get_priority_colors(self):
        """Get color scheme for the checkbox based on priority level"""
        # Use the same color mapping as the existing priority badges
        if self.priority >= 4:  # High priority
            base_color = "#ef4444"  # Red
        elif self.priority == 3:  # Medium priority
            base_color = "#f59e0b"  # Orange/Amber
        elif self.priority >= 1:  # Low priority
            base_color = "#10b981"  # Green
        else:  # No priority
            base_color = "#6b7280"  # Gray
        
        # Generate color variations for different states
        return {
            'border': base_color,
            'background': 'transparent',
            'pressed_border': base_color,
            'pressed_background': f'{base_color}25',  # 25% opacity
            'checked_border': base_color,
            'checked_background': base_color,
            'focus_border': base_color,
            'focus_outline': f'{base_color}40'  # 40% opacity for outline
        }
    
    def get_priority_text(self):
        """Get human-readable priority text"""
        if self.priority >= 4:
            return "High"
        elif self.priority == 3:
            return "Medium"
        elif self.priority >= 1:
            return "Low"
        else:
            return "None"
    
    def on_checkbox_clicked(self, checked):
        """Handle checkbox click event"""
        if checked:
            # Complete task immediately for responsive feel
            self.complete_task()
        # Note: We don't handle unchecking as task reactivation is not supported by the v1 API
    
    def complete_task(self):
        """Emit signal to complete the task"""
        if self.task_id:
            self.task_completed.emit(self.task_id)
    
    def set_completing_state(self, is_completing=True):
        """Set visual state for when task is being completed"""
        if is_completing:
            # Disable checkbox and show loading state
            self.setEnabled(False)
            self.setToolTip("Completing task...")
            
            # Add loading styles (simplified for Qt compatibility)
            loading_style = """
            QCheckBox::indicator {
                border: 2px solid #6b7280;
                background-color: #f3f4f6;
            }
            """
            self.setStyleSheet(self.styleSheet() + loading_style)
        else:
            # Reset to normal state
            self.setEnabled(True)
            self.setToolTip(f"Mark task as completed (Priority: {self.get_priority_text()})")
            self.apply_priority_colors()
    
    def set_completed_state(self):
        """Set visual state for completed task"""
        # Keep checkbox checked and disabled
        self.setChecked(True)
        self.setEnabled(False)
        self.setToolTip("Task completed")
        
        # Apply completed styling (simplified for Qt compatibility)
        completed_style = """
        QCheckBox::indicator:checked {
            border: 2px solid #10b981;
            background-color: #10b981;
        }
        QCheckBox {
            color: #10b981;
        }
        """
        self.setStyleSheet(self.styleSheet() + completed_style)
    
    def set_error_state(self, error_message=""):
        """Set visual state for when task completion fails"""
        # Reset checkbox to unchecked
        self.setChecked(False)
        self.setEnabled(True)
        
        # Show error tooltip
        tooltip = f"Failed to complete task"
        if error_message:
            tooltip += f": {error_message}"
        tooltip += f" (Priority: {self.get_priority_text()})"
        self.setToolTip(tooltip)
        
        # Apply error styling temporarily
        error_style = """
        QCheckBox::indicator {
            border: 2px solid #ef4444;
            background-color: #fef2f2;
        }
        """
        self.setStyleSheet(self.styleSheet() + error_style)
        
        # Reset to normal style after 3 seconds
        QTimer.singleShot(3000, self.apply_priority_colors)


class PriorityCheckboxContainer(QWidget):
    """
    Container widget for the priority checkbox that provides proper spacing and alignment
    """
    
    # Forward the signal from the checkbox
    task_completed = pyqtSignal(str)
    
    def __init__(self, task_data, parent=None):
        super().__init__(parent)
        self.task_data = task_data
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the container layout"""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 8, 0)  # 8px right margin for spacing
        layout.setSpacing(0)
        
        # Create the priority checkbox
        self.checkbox = PriorityCheckbox(self.task_data, self)
        
        # Connect signals
        self.checkbox.task_completed.connect(self.task_completed.emit)
        
        # Add checkbox to layout with top-left alignment for better text alignment
        layout.addWidget(self.checkbox, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        
        self.setLayout(layout)
        
        # Set fixed size for consistent layout - match task title height
        self.setFixedSize(30, 22)  # Wider for better spacing
    
    def get_checkbox(self):
        """Get the checkbox widget for external control"""
        return self.checkbox
    
    def set_completing_state(self, is_completing=True):
        """Forward state to checkbox"""
        self.checkbox.set_completing_state(is_completing)
    
    def set_completed_state(self):
        """Forward state to checkbox"""
        self.checkbox.set_completed_state()
    
    def set_error_state(self, error_message=""):
        """Forward state to checkbox"""
        self.checkbox.set_error_state(error_message) 