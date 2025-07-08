# Base theme template - all themes use this structure with different colors
def create_theme(colors):
    return f"""
QWidget {{
    background-color: {colors['bg_primary']};
    color: {colors['text_primary']};
    font-family: 'Inter', 'SF Pro Display', 'Segoe UI Variable', 'Roboto', sans-serif;
    font-size: 12pt;
    font-weight: 400;
}}

/* Group Box Styling */
QGroupBox {{
    font-size: 13pt;
    font-weight: 500;
    color: {colors['text_primary']};
    border: 1px solid {colors['border']};
    border-radius: 8px;
    margin-top: 10px;
    padding-top: 10px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 15px;
    padding: 0 8px 0 8px;
    color: {colors['text_primary']};
    font-weight: 600;
}}

/* Label Styling */
QLabel {{
    color: {colors['text_primary']};
    font-size: 11pt;
    font-weight: 400;
    line-height: 1.5;
}}

/* Main Title (H1) */
QLabel[objectName="mainTitle"] {{
    color: {colors['text_primary']};
    font-size: 28pt;
    font-weight: 700;
    font-family: 'Inter', 'SF Pro Display', 'Segoe UI Variable', 'Roboto', sans-serif;
    line-height: 1.2;
    letter-spacing: -0.5px;
}}

/* Typography Hierarchy - Modern Design System */

/* Main Widget Title (H1) */
QLabel[objectName="sectionTitle"] {{
    color: {colors['text_primary']};
    font-size: 20pt;
    font-weight: 700;
    font-family: 'Inter', 'SF Pro Display', 'Segoe UI Variable', 'Roboto', sans-serif;
    line-height: 1.2;
    letter-spacing: -0.4px;
}}

/* Task Group Headers (H2) */
QLabel[objectName="sectionSubtitle"] {{
    color: {colors['text_primary']};
    font-size: 13pt;
    font-weight: 600;
    font-family: 'Inter', 'SF Pro Display', 'Segoe UI Variable', 'Roboto', sans-serif;
    line-height: 1.3;
    letter-spacing: -0.1px;
}}

/* Task Titles (H3) - Now handled by taskTitle */
QLabel[objectName="primaryText"] {{
    color: {colors['text_primary']};
    font-size: 14pt;
    font-weight: 600;
    font-family: 'Inter', 'SF Pro Display', 'Segoe UI Variable', 'Roboto', sans-serif;
    line-height: 1.4;
    letter-spacing: -0.1px;
}}

/* Secondary Text - Group counts, etc */
QLabel[objectName="subtitleText"] {{
    color: {colors['text_muted']};
    font-size: 11pt;
    font-weight: 500;
    line-height: 1.3;
    letter-spacing: 0.05px;
}}

/* Muted Text - General descriptive text */
QLabel[objectName="mutedText"] {{
    color: {colors['text_muted']};
    font-size: 11pt;
    font-weight: 400;
    line-height: 1.4;
    opacity: 0.9;
}}

/* Icon Labels */
QLabel[objectName="iconLabel"] {{
    color: {colors['text_muted']};
}}

/* Input Fields - 8px grid system */
QLineEdit, QListWidget {{
    background-color: {colors['bg_secondary']};
    border: 1px solid {colors['border']};
    padding: 8px 16px;
    border-radius: 8px;
    font-size: 12pt;
    font-weight: 400;
    color: {colors['text_primary']};
    selection-background-color: {colors['accent']};
}}

QLineEdit:focus, QListWidget:focus {{
    border: 1px solid {colors['accent']};
    outline: none;
}}

QLineEdit::placeholder {{
    color: {colors['text_muted']};
    font-style: italic;
}}

/* List Widget Items - 8px grid spacing */
QListWidget::item {{
    padding: 0px;
    border-radius: 8px;
    margin: 8px 0px;
    background-color: transparent;
}}

QListWidget::item:hover {{
    background-color: transparent;
}}

QListWidget::item:selected {{
    background-color: transparent;
    color: {colors['text_primary']};
    font-weight: 400;
}}

QListWidget::item:selected:hover {{
    background-color: transparent;
}}

/* Button Styling - 8px grid system */
QPushButton {{
    background-color: {colors['accent']};
    border: none;
    color: {colors['text_on_accent']};
    padding: 8px 16px;
    border-radius: 8px;
    font-size: 11pt;
    font-weight: 500;
    min-height: 32px;
}}

QPushButton:hover {{
    background-color: {colors['accent_hover']};
}}

QPushButton:pressed {{
    background-color: {colors['accent_pressed']};
}}

QPushButton:disabled {{
    background-color: {colors['disabled']};
    color: {colors['text_muted']};
}}

/* Primary Button Styling - 8px grid */
QPushButton[objectName="primaryButton"] {{
    background-color: {colors['accent']};
    border: none;
    color: {colors['text_on_accent']};
    padding: 8px 24px;
    border-radius: 8px;
    font-size: 12pt;
    font-weight: 500;
    min-height: 40px;
    min-width: 128px;
}}

QPushButton[objectName="primaryButton"]:hover {{
    background-color: {colors['accent_hover']};
}}

QPushButton[objectName="primaryButton"]:pressed {{
    background-color: {colors['accent_pressed']};
}}

QPushButton[objectName="primaryButton"]:disabled {{
    background-color: {colors['disabled']};
    color: {colors['text_muted']};
}}

/* Large Primary Button - 8px grid */
QPushButton[objectName="primaryButton"][buttonType="large"] {{
    padding: 16px 32px;
    font-size: 13pt;
    font-weight: 600;
    min-height: 48px;
    min-width: 160px;
}}

/* Secondary Button Styling - 8px grid */
QPushButton[objectName="secondaryButton"] {{
    background-color: {colors['bg_secondary']};
    border: 1px solid {colors['border']};
    color: {colors['text_primary']};
    padding: 8px 16px;
    border-radius: 8px;
    font-size: 11pt;
    font-weight: 500;
    height: 32px;
}}

QPushButton[objectName="secondaryButton"]:hover {{
    background-color: {colors['hover']};
    border-color: {colors['accent']};
}}

QPushButton[objectName="secondaryButton"]:pressed {{
    background-color: {colors['pressed']};
}}

QPushButton[objectName="secondaryButton"]:disabled {{
    background-color: {colors['disabled']};
    color: {colors['text_muted']};
}}

/* ComboBox Styling - 8px grid system */
QComboBox {{
    background-color: {colors['bg_secondary']};
    border: 1px solid {colors['border']};
    padding: 8px 16px;
    border-radius: 8px;
    font-size: 11pt;
    font-weight: 400;
    color: {colors['text_primary']};
    height: 32px;
    padding-right: 32px;
}}

QComboBox:focus {{
    border: 1px solid {colors['accent']};
}}

QComboBox::drop-down {{
    border: none;
    width: 32px;
    subcontrol-origin: padding;
    subcontrol-position: top right;
    border-left: 1px solid {colors['border']};
}}

QComboBox::down-arrow {{
    width: 16px;
    height: 16px;
}}

QComboBox QAbstractItemView {{
    background-color: {colors['bg_secondary']};
    border: 1px solid {colors['border']};
    border-radius: 8px;
    selection-background-color: {colors['accent']};
    color: {colors['text_primary']};
    outline: none;
    padding: 8px;
}}

/* Tool Button Styling */
QToolButton {{
    background-color: transparent;
    border: none;
    padding: 4px;
    border-radius: 6px;
}}

QToolButton:hover {{
    background-color: {colors['hover']};
}}

QToolButton:pressed {{
    background-color: {colors['pressed']};
}}

/* Frame Styling */
QFrame {{
    border: none;
    border-radius: 8px;
}}

/* Progress Dialog */
QProgressDialog {{
    font-size: 12pt;
    font-weight: 400;
}}

QProgressBar {{
    background-color: {colors['bg_secondary']};
    border: 1px solid {colors['border']};
    border-radius: 4px;
    text-align: center;
    color: {colors['text_primary']};
}}

QProgressBar::chunk {{
    background-color: {colors['accent']};
    border-radius: 3px;
}}

/* Scrollbar */
QScrollBar:vertical {{
    background-color: {colors['bg_secondary']};
    width: 12px;
    border-radius: 6px;
}}

QScrollBar::handle:vertical {{
    background-color: {colors['border']};
    border-radius: 6px;
    min-height: 20px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {colors['hover']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
    border: none;
}}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: none;
}}

/* Message Boxes */
QMessageBox {{
    background-color: {colors['bg_primary']};
    color: {colors['text_primary']};
    border: 1px solid {colors['border']};
    border-radius: 8px;
}}

QMessageBox QPushButton {{
    background-color: {colors['accent']};
    border: none;
    border-radius: 6px;
    color: {colors['text_on_accent']};
    font-size: 12pt;
    font-weight: 500;
    padding: 8px 16px;
    min-width: 80px;
}}

QMessageBox QPushButton:hover {{
    background-color: {colors['accent_hover']};
}}

/* Widget specific styling for TickTick widget */
TickTickWidget {{
    background-color: {colors['bg_primary']};
    border: 2px solid {colors['border']};
    border-radius: 12px;
}}

/* Modern Task Card Styling - 8px grid system */
QWidget[objectName="taskCard"] {{
    background-color: {colors['bg_secondary']};
    border: 1px solid {colors['border']};
    border-radius: 12px;
    margin: 4px 0px;
    padding: 0px;
}}

QWidget[objectName="taskCard"]:hover {{
    background-color: {colors['hover']};
    border-color: {colors['accent']};
    border-width: 1px;
}}

/* Task Typography Hierarchy */
QLabel[objectName="taskTitle"] {{
    color: {colors['text_primary']};
    font-size: 14pt;
    font-weight: 600;
    line-height: 1.3;
    letter-spacing: -0.2px;
}}

QLabel[objectName="taskDueDate"] {{
    color: {colors['text_muted']};
    font-size: 11pt;
    font-weight: 500;
}}

QLabel[objectName="taskOverdue"] {{
    color: #ef4444;
    font-size: 11pt;
    font-weight: 600;
}}

QLabel[objectName="taskDueToday"] {{
    color: {colors['accent']};
    font-size: 11pt;
    font-weight: 600;
}}

QLabel[objectName="taskContent"] {{
    color: {colors['text_muted']};
    font-size: 11pt;
    font-weight: 400;
    line-height: 1.4;
    opacity: 0.8;
}}

/* Modern Priority Badges */
QLabel[objectName="priorityHigh"] {{
    background-color: #ef4444;
    color: white;
    border-radius: 10px;
    padding: 2px 6px;
    font-weight: 700;
    font-size: 9pt;
    min-width: 20px;
}}

QLabel[objectName="priorityMedium"] {{
    background-color: #f59e0b;
    color: white;
    border-radius: 10px;
    padding: 2px 6px;
    font-weight: 700;
    font-size: 9pt;
    min-width: 20px;
}}

QLabel[objectName="priorityLow"] {{
    background-color: #10b981;
    color: white;
    border-radius: 10px;
    padding: 2px 6px;
    font-weight: 700;
    font-size: 9pt;
    min-width: 20px;
}}

QLabel[objectName="priorityNone"] {{
    background-color: {colors['text_muted']};
    color: {colors['bg_primary']};
    border-radius: 10px;
    padding: 2px 6px;
    font-weight: 500;
    font-size: 9pt;
    min-width: 20px;
    opacity: 0.7;
}}

/* Task Group Widget styling */
TaskGroupWidget {{
    background-color: transparent;
    border: none;
}}

/* Task Group Header styling */
QWidget[objectName="taskGroupHeader"] {{
    background-color: {colors['bg_secondary']};
    border: 1px solid {colors['border']};
    border-radius: 8px;
    margin: 0px;
    padding: 0px;
}}

QWidget[objectName="taskGroupHeader"]:hover {{
    background-color: {colors['hover']};
    border-color: {colors['accent']};
}}

/* Scroll Area styling */
QScrollArea {{
    background-color: transparent;
    border: none;
}}

QScrollArea > QWidget > QWidget {{
    background-color: transparent;
}}
"""

# Color schemes for each theme
DARK_MODE_COLORS = {
    'bg_primary': '#1a1a1a',
    'bg_secondary': '#2a2a2a',
    'border': '#404040',
    'text_primary': '#e6e6e6',
    'text_muted': '#808080',
    'accent': '#0078d4',
    'accent_hover': '#106ebe',
    'accent_pressed': '#005a9e',
    'text_on_accent': '#ffffff',
    'hover': '#404040',
    'pressed': '#505050',
    'disabled': '#404040'
}

CATPPUCCIN_COLORS = {
    'bg_primary': '#1e1e2e',
    'bg_secondary': '#2a273f',
    'border': '#36304a',
    'text_primary': '#c6d0f5',
    'text_muted': '#a5adce',
    'accent': '#f5c2e7',
    'accent_hover': '#f2a6cf',
    'accent_pressed': '#ef8bb7',
    'text_on_accent': '#1e1e2e',
    'hover': '#36304a',
    'pressed': '#414155',
    'disabled': '#36304a'
}

DRACULA_COLORS = {
    'bg_primary': '#282a36',
    'bg_secondary': '#44475a',
    'border': '#6272a4',
    'text_primary': '#f8f8f2',
    'text_muted': '#6272a4',
    'accent': '#bd93f9',
    'accent_hover': '#ff79c6',
    'accent_pressed': '#8be9fd',
    'text_on_accent': '#282a36',
    'hover': '#6272a4',
    'pressed': '#44475a',
    'disabled': '#44475a'
}

TRUE_BLACK_COLORS = {
    'bg_primary': '#000000',
    'bg_secondary': '#111111',
    'border': '#333333',
    'text_primary': '#ffffff',
    'text_muted': '#666666',
    'accent': '#ffffff',
    'accent_hover': '#cccccc',
    'accent_pressed': '#999999',
    'text_on_accent': '#000000',
    'hover': '#333333',
    'pressed': '#555555',
    'disabled': '#333333'
}

# Generate themes
dark_mode = create_theme(DARK_MODE_COLORS)
catppuccin_mocha = create_theme(CATPPUCCIN_COLORS)
dracula_theme = create_theme(DRACULA_COLORS)
true_black = create_theme(TRUE_BLACK_COLORS)

THEMES = {
    "Dark Mode": dark_mode,
    "Catppuccin Mocha": catppuccin_mocha,
    "Dracula": dracula_theme,
    "True Black": true_black,
}

# Default theme for imports
default_theme = dark_mode

# Export color schemes for dynamic icon updates
__all__ = ['THEMES', 'default_theme', 'DARK_MODE_COLORS', 'CATPPUCCIN_COLORS', 'DRACULA_COLORS', 'TRUE_BLACK_COLORS'] 