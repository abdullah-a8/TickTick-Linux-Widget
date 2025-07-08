import os
import json
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal
from .themes import THEMES, default_theme


class ThemeManager(QObject):
    """Manages theme switching and persistence for the TickTick widget"""
    
    theme_changed = pyqtSignal(str)  # Signal emitted when theme changes
    
    def __init__(self):
        super().__init__()
        self.current_theme_name = "Dark Mode"
        self.config_file = self._get_config_path()
        self.load_saved_theme()
    
    def _get_config_path(self):
        """Get the path to the theme configuration file"""
        project_root = Path(__file__).parent.parent.parent.parent
        config_dir = project_root / "data" / "config"
        config_dir.mkdir(exist_ok=True)
        return config_dir / "theme_config.json"
    
    def get_available_themes(self):
        """Get list of available theme names"""
        return list(THEMES.keys())
    
    def get_current_theme(self):
        """Get the current theme stylesheet"""
        return THEMES.get(self.current_theme_name, default_theme)
    
    def get_current_theme_name(self):
        """Get the current theme name"""
        return self.current_theme_name
    
    def set_theme(self, theme_name):
        """Set the current theme"""
        if theme_name in THEMES:
            self.current_theme_name = theme_name
            self.save_theme_preference()
            self.theme_changed.emit(theme_name)
            return True
        return False
    
    def apply_theme_to_app(self, app=None):
        """Apply the current theme to the application"""
        if app is None:
            app = QApplication.instance()
        
        if app and isinstance(app, QApplication):
            stylesheet = self.get_current_theme()
            app.setStyleSheet(stylesheet)
    
    def apply_theme_to_widget(self, widget):
        """Apply the current theme to a specific widget"""
        stylesheet = self.get_current_theme()
        widget.setStyleSheet(stylesheet)
    
    def save_theme_preference(self):
        """Save the current theme preference to disk"""
        try:
            config = {
                "current_theme": self.current_theme_name,
                "version": "1.0"
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving theme preference: {e}")
    
    def load_saved_theme(self):
        """Load the saved theme preference from disk"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                saved_theme = config.get("current_theme", "Dark Mode")
                if saved_theme in THEMES:
                    self.current_theme_name = saved_theme
                else:
                    # Fallback to default if saved theme doesn't exist
                    self.current_theme_name = "Dark Mode"
            else:
                # First time setup - use default
                self.current_theme_name = "Dark Mode"
                self.save_theme_preference()
        except Exception as e:
            print(f"Error loading theme preference: {e}")
            # Fallback to default theme
            self.current_theme_name = "Dark Mode"
    
    def cycle_theme(self):
        """Cycle to the next theme in the list"""
        themes = self.get_available_themes()
        current_index = themes.index(self.current_theme_name)
        next_index = (current_index + 1) % len(themes)
        next_theme = themes[next_index]
        self.set_theme(next_theme)
        return next_theme


# Global theme manager instance
theme_manager = ThemeManager() 