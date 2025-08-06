"""
File management utilities for Hair QC Tool

Handles file operations, directory scanning, and USD file management.
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
import re


class USDDirectoryManager:
    """Manages USD directory structure and file operations"""
    
    def __init__(self, base_directory: Path):
        self.base_directory = Path(base_directory)
        self.group_dir = self.base_directory / "Group"
        self.module_dir = self.base_directory / "module"
        self.style_dir = self.base_directory / "style"
    
    def scan_groups(self) -> List[str]:
        """Scan for available group USD files"""
        groups = []
        if self.group_dir.exists():
            for usd_file in self.group_dir.glob("*.usd"):
                groups.append(usd_file.stem)
        return sorted(groups)
    
    def scan_modules(self, module_type: Optional[str] = None) -> Dict[str, List[str]]:
        """Scan for available module USD files"""
        modules = {"scalp": [], "crown": [], "tail": [], "bang": []}
        
        if not self.module_dir.exists():
            return modules
        
        # Scan each module type directory
        for mod_type in modules.keys():
            if module_type and mod_type != module_type:
                continue
            
            type_dir = self.module_dir / mod_type
            if type_dir.exists():
                for usd_file in type_dir.glob("*.usd"):
                    modules[mod_type].append(usd_file.stem)
        
        # Sort all lists
        for mod_type in modules:
            modules[mod_type].sort()
        
        return modules
    
    def scan_styles(self) -> List[str]:
        """Scan for available style USD files"""
        styles = []
        if self.style_dir.exists():
            for usd_file in self.style_dir.glob("*.usd"):
                styles.append(usd_file.stem)
        return sorted(styles)
    
    def scan_alpha_textures(self, module_type: str = "scalp") -> Dict[str, List[str]]:
        """Scan for available alpha textures"""
        alpha_textures = {"fade": [], "hairline": [], "sideburn": []}
        
        alpha_dir = self.module_dir / module_type / "alpha"
        if not alpha_dir.exists():
            return alpha_textures
        
        for category in alpha_textures.keys():
            category_dir = alpha_dir / category
            if category_dir.exists():
                for texture_file in category_dir.glob("*.png"):
                    # Store relative path from module directory
                    relative_path = f"{module_type}/alpha/{category}/{texture_file.name}"
                    alpha_textures[category].append(relative_path)
        
        # Sort all lists
        for category in alpha_textures:
            alpha_textures[category].sort()
        
        return alpha_textures
    
    def get_group_file_path(self, group_name: str) -> Path:
        """Get full path to group USD file"""
        return self.group_dir / f"{group_name}.usd"
    
    def get_module_file_path(self, module_type: str, module_name: str) -> Path:
        """Get full path to module USD file"""
        return self.module_dir / module_type / f"{module_name}.usd"
    
    def get_style_file_path(self, style_name: str) -> Path:
        """Get full path to style USD file"""
        return self.style_dir / f"{style_name}.usd"
    
    def create_group_file(self, group_name: str, group_type: str = "") -> bool:
        """Create new group USD file"""
        from .usd_utils import create_group_file
        
        file_path = self.get_group_file_path(group_name)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        return create_group_file(file_path, group_name, group_type)
    
    def create_module_file(self, module_type: str, module_name: str) -> bool:
        """Create new module USD file"""
        from .usd_utils import create_module_file
        
        file_path = self.get_module_file_path(module_type, module_name)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        return create_module_file(file_path, module_name, module_type)
    
    def create_style_file(self, style_name: str) -> bool:
        """Create new style USD file"""
        from .usd_utils import create_style_file
        
        file_path = self.get_style_file_path(style_name)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        return create_style_file(file_path, style_name)
    
    def delete_group_file(self, group_name: str) -> bool:
        """Delete group USD file"""
        try:
            file_path = self.get_group_file_path(group_name)
            if file_path.exists():
                file_path.unlink()
                return True
        except Exception as e:
            print(f"[File Utils] Error deleting group file: {e}")
        return False
    
    def delete_module_file(self, module_type: str, module_name: str) -> bool:
        """Delete module USD file"""
        try:
            file_path = self.get_module_file_path(module_type, module_name)
            if file_path.exists():
                file_path.unlink()
                return True
        except Exception as e:
            print(f"[File Utils] Error deleting module file: {e}")
        return False
    
    def delete_style_file(self, style_name: str) -> bool:
        """Delete style USD file"""
        try:
            file_path = self.get_style_file_path(style_name)
            if file_path.exists():
                file_path.unlink()
                return True
        except Exception as e:
            print(f"[File Utils] Error deleting style file: {e}")
        return False
    
    def validate_file_name(self, name: str) -> Tuple[bool, str]:
        """Validate file name for USD files"""
        if not name:
            return False, "Name cannot be empty"
        
        # Check for invalid characters
        invalid_chars = r'[<>:"/\\|?*\s]'
        if re.search(invalid_chars, name):
            return False, "Name contains invalid characters (spaces, special characters)"
        
        # Check length
        if len(name) > 100:
            return False, "Name is too long (max 100 characters)"
        
        # Check for reserved names
        reserved_names = ["con", "prn", "aux", "nul"] + [f"com{i}" for i in range(1, 10)] + [f"lpt{i}" for i in range(1, 10)]
        if name.lower() in reserved_names:
            return False, f"'{name}' is a reserved name"
        
        return True, "Name is valid"
    
    def sanitize_file_name(self, name: str) -> str:
        """Sanitize file name by replacing invalid characters"""
        # Replace spaces and invalid characters with underscores
        sanitized = re.sub(r'[<>:"/\\|?*\s]+', '_', name)
        
        # Remove leading/trailing underscores and dots
        sanitized = sanitized.strip('_.')
        
        # Ensure not empty
        if not sanitized:
            sanitized = "unnamed"
        
        # Limit length
        if len(sanitized) > 100:
            sanitized = sanitized[:100]
        
        return sanitized
    
    def get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """Get information about a USD file"""
        info = {
            "exists": file_path.exists(),
            "size": 0,
            "modified": None,
            "is_valid": False,
            "error": None
        }
        
        if info["exists"]:
            try:
                stat = file_path.stat()
                info["size"] = stat.st_size
                info["modified"] = stat.st_mtime
                
                # Basic validation - check if it's a valid USD file
                from .usd_utils import USDValidationUtils
                
                if "group" in str(file_path).lower():
                    info["is_valid"], info["error"] = USDValidationUtils.validate_group_file(file_path)
                elif "module" in str(file_path).lower():
                    info["is_valid"], info["error"] = USDValidationUtils.validate_module_file(file_path)
                elif "style" in str(file_path).lower():
                    info["is_valid"], info["error"] = USDValidationUtils.validate_style_file(file_path)
                else:
                    info["is_valid"] = True  # Unknown type, assume valid
                    
            except Exception as e:
                info["error"] = str(e)
        
        return info


class StyleCombinationGenerator:
    """Generates style combinations from available modules"""
    
    def __init__(self, directory_manager: USDDirectoryManager):
        self.directory_manager = directory_manager
    
    def generate_style_combinations(self, group_name: str) -> List[Dict[str, str]]:
        """
        Generate all possible style combinations for a group
        
        Returns:
            List of combinations: [{"crown": "name", "tail": "name", "bang": "name"}]
        """
        from .usd_utils import USDGroupUtils
        
        # Load group file to get module whitelist
        group_file = self.directory_manager.get_group_file_path(group_name)
        if not group_file.exists():
            return []
        
        group_utils = USDGroupUtils(group_file)
        
        try:
            # Get whitelisted modules for each type
            crown_modules = group_utils.get_module_whitelist("Crown")
            tail_modules = group_utils.get_module_whitelist("Tail")
            bang_modules = group_utils.get_module_whitelist("Bang")
            
            # Convert USD references to module names
            def extract_module_name(usd_ref: str) -> str:
                """Extract module name from USD reference path"""
                if "@" in usd_ref:
                    # Format: @module/crown/crown_name.usd@
                    path_part = usd_ref.split("@")[1]
                    return Path(path_part).stem
                return usd_ref
            
            crown_names = [extract_module_name(ref) for ref in crown_modules]
            tail_names = [extract_module_name(ref) for ref in tail_modules]
            bang_names = [extract_module_name(ref) for ref in bang_modules]
            
            # Generate all combinations
            combinations = []
            
            # Handle case where some module types might be empty
            if not crown_names:
                crown_names = [None]
            if not tail_names:
                tail_names = [None]
            if not bang_names:
                bang_names = [None]
            
            from itertools import product
            
            for crown, tail, bang in product(crown_names, tail_names, bang_names):
                # Skip if all optional modules are None
                if crown is None and tail is None and bang is None:
                    continue
                
                combination = {}
                if crown:
                    combination["crown"] = crown
                if tail:
                    combination["tail"] = tail
                if bang:
                    combination["bang"] = bang
                
                combinations.append(combination)
            
            return combinations
            
        except Exception as e:
            print(f"[Style Generator] Error generating combinations: {e}")
            return []
        finally:
            group_utils.close_stage()
    
    def get_existing_styles(self) -> List[Dict[str, str]]:
        """Get existing style files and parse their combinations"""
        existing_styles = []
        
        for style_name in self.directory_manager.scan_styles():
            combination = self.parse_style_name(style_name)
            if combination:
                combination["style_name"] = style_name
                existing_styles.append(combination)
        
        return existing_styles
    
    def parse_style_name(self, style_name: str) -> Optional[Dict[str, str]]:
        """
        Parse style name to extract module combination
        
        Expected format: group_crown_tail_bang or group_crown_bang (no tail)
        """
        parts = style_name.split("_")
        
        if len(parts) < 2:
            return None
        
        # First part is group, remaining parts are modules
        group = parts[0]
        modules = parts[1:]
        
        # Try to identify module types based on known patterns or position
        combination = {"group": group}
        
        # This is a simplified parser - in practice, you might need more sophisticated logic
        # based on your actual naming conventions
        if len(modules) >= 1:
            combination["crown"] = modules[0]
        if len(modules) >= 2:
            combination["tail"] = modules[1]
        if len(modules) >= 3:
            combination["bang"] = modules[2]
        
        return combination
    
    def generate_style_name(self, group: str, combination: Dict[str, str]) -> str:
        """Generate style name from combination"""
        parts = [group]
        
        # Add modules in consistent order
        if "crown" in combination:
            parts.append(combination["crown"])
        if "tail" in combination:
            parts.append(combination["tail"])
        if "bang" in combination:
            parts.append(combination["bang"])
        
        return "_".join(parts)
    
    def find_missing_styles(self, group_name: str) -> List[Dict[str, str]]:
        """Find style combinations that should exist but don't have USD files"""
        possible_combinations = self.generate_style_combinations(group_name)
        existing_styles = self.get_existing_styles()
        
        # Extract combinations from existing styles (ignore style_name key)
        existing_combinations = []
        for style in existing_styles:
            combo = {k: v for k, v in style.items() if k != "style_name"}
            existing_combinations.append(combo)
        
        # Find missing combinations
        missing = []
        for combo in possible_combinations:
            if combo not in existing_combinations:
                combo["style_name"] = self.generate_style_name(group_name, combo)
                missing.append(combo)
        
        return missing
    
    def find_invalid_styles(self, group_name: str) -> List[Dict[str, str]]:
        """Find style files that reference non-existent modules"""
        existing_styles = self.get_existing_styles()
        available_modules = self.directory_manager.scan_modules()
        
        invalid = []
        
        for style in existing_styles:
            is_invalid = False
            
            # Check if referenced modules exist
            for module_type in ["crown", "tail", "bang"]:
                if module_type in style:
                    module_name = style[module_type]
                    if module_name not in available_modules.get(module_type, []):
                        is_invalid = True
                        break
            
            if is_invalid:
                invalid.append(style)
        
        return invalid


# Convenience functions
def get_directory_manager(base_path: Path) -> USDDirectoryManager:
    """Get directory manager instance"""
    return USDDirectoryManager(base_path)


def validate_usd_directory_structure(base_path: Path) -> Tuple[bool, str]:
    """Validate USD directory structure"""
    base_path = Path(base_path)
    
    if not base_path.exists():
        return False, f"Directory does not exist: {base_path}"
    
    required_dirs = ["Group", "module", "style"]
    missing_dirs = []
    
    for dir_name in required_dirs:
        if not (base_path / dir_name).exists():
            missing_dirs.append(dir_name)
    
    if missing_dirs:
        return False, f"Missing required directories: {', '.join(missing_dirs)}"
    
    # Check module subdirectories
    module_dir = base_path / "module"
    required_module_types = ["scalp", "crown", "tail", "bang"]
    missing_module_dirs = []
    
    for module_type in required_module_types:
        if not (module_dir / module_type).exists():
            missing_module_dirs.append(module_type)
    
    if missing_module_dirs:
        return False, f"Missing module type directories: {', '.join(missing_module_dirs)}"
    
    return True, "Directory structure is valid"