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
            # Check if directory is completely empty
            if self.is_directory_empty():
                return "empty", f"Directory is empty. Would you like to initialize it with the required USD structure?"
            else:
                return False, f"Missing required directories: {', '.join(missing_dirs)}"
        
        return True, "USD directory structure is valid"
    
    def is_directory_empty(self):
        """Check if the USD directory is completely empty"""
        if not self.usd_directory or not self.usd_directory.exists():
            return True
        
        # Check if directory has any files or folders
        try:
            return len(list(self.usd_directory.iterdir())) == 0
        except:
            return True
    
    def initialize_usd_directory(self):
        """Initialize USD directory with required structure and sample files"""
        if not self.usd_directory:
            return False, "No USD directory set"
        
        try:
            # Create required directories
            required_structure = {
                "Group": [],
                "module": ["scalp", "crown", "tail", "bang"],
                "style": []
            }
            
            for main_dir, subdirs in required_structure.items():
                main_path = self.usd_directory / main_dir
                main_path.mkdir(exist_ok=True)
                
                for subdir in subdirs:
                    sub_path = main_path / subdir
                    sub_path.mkdir(exist_ok=True)
                    
                    # Create alpha directories for scalp
                    if subdir == "scalp":
                        alpha_dirs = ["fade", "hairline", "sideburn"]
                        alpha_path = sub_path / "alpha"
                        alpha_path.mkdir(exist_ok=True)
                        
                        for alpha_dir in alpha_dirs:
                            (alpha_path / alpha_dir).mkdir(exist_ok=True)
                        
                        # Create normal directory
                        (sub_path / "normal").mkdir(exist_ok=True)
                    
                    # Create normal directories for other modules
                    elif subdir in ["crown", "tail", "bang"]:
                        (sub_path / "normal").mkdir(exist_ok=True)
            
            # Create sample group files
            self._create_sample_group_files()
            
            # Create README file
            self._create_readme_file()
            
            print(f"[Hair QC Tool] Initialized USD directory structure at: {self.usd_directory}")
            return True, "USD directory initialized successfully"
            
        except Exception as e:
            return False, f"Failed to initialize USD directory: {str(e)}"
    
    def _create_sample_group_files(self):
        """Create sample group USD files"""
        sample_groups = ["short", "long"]
        
        for group_name in sample_groups:
            group_file = self.usd_directory / "Group" / f"{group_name}.usd"
            
            # Create basic group USD structure
            group_content = f'''#usda 1.0
(
    doc = "Sample {group_name} hair group"
    metersPerUnit = 1
    upAxis = "Y"
)

def "HairGroup" (
    variants = {{
        string groupType = "{group_name}"
    }}
)
{{
    # Module whitelist - modules included in this group
    def "ModuleWhitelist" {{
        def "Crown" {{
            asset[] moduleFiles = []
        }}
        
        def "Tail" {{
            asset[] moduleFiles = []
        }}
        
        def "Bang" {{
            asset[] moduleFiles = []
        }}
        
        def "Scalp" {{
            asset[] moduleFiles = [@module/scalp/scalp.usd@]
        }}
    }}
    
    # Alpha texture whitelist for this group
    def "AlphaWhitelist" {{
        def "Scalp" {{
            def "fade" {{
                asset[] whitelistedTextures = []
            }}
            
            def "hairline" {{
                asset[] whitelistedTextures = []
            }}
            
            def "sideburn" {{
                asset[] whitelistedTextures = []
            }}
        }}
    }}
    
    # Cross-module rules storage
    def "CrossModuleRules" {{
        def "Exclusions" {{
            # Cross-module exclusions will be stored here
        }}
        
        def "WeightConstraints" {{
            # Cross-module weight constraints will be stored here
        }}
    }}
}}
'''
            
            with open(group_file, 'w') as f:
                f.write(group_content)
    
    def _create_readme_file(self):
        """Create README file explaining the directory structure"""
        readme_content = '''# Hair QC Tool USD Directory

This directory has been initialized for use with the Hair QC Tool.

## Directory Structure

- **Group/**: Contains group USD files that define module collections and QC boundaries
- **module/**: Contains individual module USD files organized by type
  - **scalp/**: Scalp modules with alpha texture directories
  - **crown/**: Crown hair modules  
  - **tail/**: Tail/ponytail modules
  - **bang/**: Bang/fringe modules
- **style/**: Contains style USD files that combine modules with animation data

## Getting Started

1. Create modules using the Hair QC Tool's Module tab
2. Generate style combinations using the Style tab
3. Set up QC rules and exclusions for quality control
4. Export animation timelines for testing

## Sample Files

- `Group/short.usd` and `Group/long.usd` are sample group files
- Add your own groups as needed for different hair categories

For more information, see the Hair QC Tool documentation.
'''
        
        readme_file = self.usd_directory / "README.md"
        with open(readme_file, 'w') as f:
            f.write(readme_content)


# Global config instance
config = HairQCConfig()