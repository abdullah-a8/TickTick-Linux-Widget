import json
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal, QPoint


class PositionManager(QObject):
    """Manages widget position persistence for the TickTick widget"""
    
    position_loaded = pyqtSignal(QPoint)  # Signal emitted when position is loaded
    
    def __init__(self):
        super().__init__()
        self.config_file = self._get_config_path()
        self.default_position = QPoint(100, 100)
    
    def _get_config_path(self):
        """Get the path to the position configuration file"""
        project_root = Path(__file__).parent.parent.parent.parent
        config_dir = project_root / "data" / "config"
        config_dir.mkdir(exist_ok=True)
        return config_dir / "position_config.json"
    
    def save_position(self, position):
        """Save the widget position to disk"""
        try:
            # Load existing config to preserve lock state
            existing_config = {}
            if self.config_file.exists():
                try:
                    with open(self.config_file, 'r', encoding='utf-8') as f:
                        existing_config = json.load(f)
                except Exception:
                    pass
            
            config = {
                "x": position.x(),
                "y": position.y(),
                "locked": existing_config.get("locked", False),  # Preserve lock state
                "version": "1.0"
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving position: {e}")
    
    def load_position(self):
        """Load the saved position from disk"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                x = config.get("x", self.default_position.x())
                y = config.get("y", self.default_position.y())
                
                # Validate position values
                if isinstance(x, int) and isinstance(y, int):
                    position = QPoint(x, y)
                    self.position_loaded.emit(position)
                    return position
                
            # Return default position if file doesn't exist or has invalid data
            return self.default_position
                
        except Exception as e:
            print(f"Error loading position: {e}")
            # Fallback to default position
            return self.default_position
    
    def reset_position(self):
        """Reset position to default"""
        self.save_position(self.default_position)
        return self.default_position
    
    def save_lock_state(self, locked):
        """Save the widget lock state to disk"""
        try:
            # Load existing config to preserve position
            existing_config = {}
            if self.config_file.exists():
                try:
                    with open(self.config_file, 'r', encoding='utf-8') as f:
                        existing_config = json.load(f)
                except Exception:
                    pass
            
            config = {
                "x": existing_config.get("x", self.default_position.x()),
                "y": existing_config.get("y", self.default_position.y()),
                "locked": locked,
                "version": "1.0"
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving lock state: {e}")
    
    def load_lock_state(self):
        """Load the saved lock state from disk"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                return config.get("locked", False)
                
            # Return default (unlocked) if file doesn't exist
            return False
                
        except Exception as e:
            print(f"Error loading lock state: {e}")
            # Fallback to default (unlocked)
            return False


# Global position manager instance
position_manager = PositionManager() 