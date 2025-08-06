"""
Configuration system for Hair QC Tool

Manages USD directory paths, tool settings, and user preferences.
"""

import os
import json
from pathlib import Path


class HairQCConfig:
    """Configuration manager for Hair QC Tool"""
    
    # Default settings
    DEFAULT_CONFIG = {
        "usd_directory": "",
        "max_timeline_frames": 6000,
        "frames_per_combination": 10,
        "auto_save_enabled": True,
        "lazy_loading_enabled": True,
        "validation_on_load": True,
        "show_debug_info": False
    }
    
    def __init__(self):
        self.config_file = Path.home() / ".hair_qc_tool_config.json"
        self._config = self.DEFAULT_CONFIG.copy()
        self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    saved_config = json.load(f)
                    self._config.update(saved_config)
                    print(f"[Hair QC Tool] Config loaded from {self.config_file}")
        except Exception as e:
            print(f"[Hair QC Tool] Warning: Could not load config: {e}")
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self._config, f, indent=2)
                print(f"[Hair QC Tool] Config saved to {self.config_file}")
        except Exception as e:
            print(f"[Hair QC Tool] Error: Could not save config: {e}")
    
    @property
    def usd_directory(self):
        """Get USD directory path"""
        return Path(self._config["usd_directory"]) if self._config["usd_directory"] else None
    
    @usd_directory.setter
    def usd_directory(self, path):
        """Set USD directory path"""
        self._config["usd_directory"] = str(path) if path else ""
        self.save_config()
    
    @property
    def max_timeline_frames(self):
        """Maximum frames allowed in timeline"""
        return self._config["max_timeline_frames"]
    
    @property
    def frames_per_combination(self):
        """Frames allocated per blendshape combination"""
        return self._config["frames_per_combination"]
    
    def get(self, key, default=None):
        """Get configuration value"""
        return self._config.get(key, default)
    
    def set(self, key, value):
        """Set configuration value and save"""
        self._config[key] = value
        self.save_config()
    
    def validate_usd_directory(self):
        """Validate that USD directory exists and has expected structure"""
        if not self.usd_directory:
            return False, "No USD directory set"
        
        if not self.usd_directory.exists():
            return False, f"USD directory does not exist: {self.usd_directory}"
        
        # Check for expected subdirectories
        required_dirs = ["Group", "module", "style"]
        missing_dirs = []
        
        for dir_name in required_dirs:
            dir_path = self.usd_directory / dir_name
            if not dir_path.exists():
                missing_dirs.append(dir_name)
        
        if missing_dirs:
            return False, f"Missing required directories: {', '.join(missing_dirs)}"
        
        return True, "USD directory structure is valid"


# Global config instance
config = HairQCConfig()