"""
Group Management System

Handles loading, creating, editing, and saving of Group USD files.
Manages group-level data including alpha whitelists and cross-module rules.
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any

from ..config import config
from ..utils import (
    USDGroupUtils, USDDirectoryManager, USDValidationUtils,
    create_group_file, BlendshapeRulesManager, get_directory_manager
)


class GroupManager:
    """Manages Group USD files and related data"""
    
    def __init__(self):
        self.current_group: Optional[str] = None
        self.group_data: Dict[str, Any] = {}
        self.alpha_whitelist: Dict[str, bool] = {}
        self.rules_manager: BlendshapeRulesManager = BlendshapeRulesManager()
        self.directory_manager: Optional[USDDirectoryManager] = None
        
        # Initialize directory manager if USD directory is set
        if config.usd_directory:
            self.directory_manager = get_directory_manager(config.usd_directory)
    
    def get_available_groups(self) -> List[str]:
        """Get list of all available group names"""
        if not config.usd_directory:
            return []
        
        group_dir = config.usd_directory / "Group"
        if not group_dir.exists():
            return []
        
        groups = []
        for usd_file in group_dir.glob("*.usd"):
            groups.append(usd_file.stem)
        
        return sorted(groups)
    
    def load_group(self, group_name: str) -> Tuple[bool, str]:
        """
        Load a group and all its data
        
        Args:
            group_name: Name of the group to load
            
        Returns:
            Tuple of (success, message)
        """
        if not config.usd_directory:
            return False, "No USD directory set"
        
        group_file = config.usd_directory / "Group" / f"{group_name}.usd"
        if not group_file.exists():
            return False, f"Group file not found: {group_file}"
        
        try:
            # Validate group file
            is_valid, validation_msg = USDValidationUtils.validate_group_file(group_file)
            if not is_valid:
                return False, f"Invalid group file: {validation_msg}"
            
            # Load group data using USD utilities
            group_utils = USDGroupUtils(group_file)
            
            # Open the stage before accessing prims
            if not group_utils.open_stage():
                return False, "Failed to open USD stage"
            
            # Load basic group info (group info is stored in the file structure itself)
            # We can validate the group structure exists
            if not group_utils.get_prim("/HairGroup"):
                return False, "Invalid group file structure"
            
            # Load alpha whitelist
            alpha_whitelist = group_utils.get_alpha_whitelist_dict()
            
            # Load cross-module rules
            exclusions_data = group_utils.get_cross_module_exclusions()
            constraints_data = group_utils.get_weight_constraints()
            
            # Combine rules data
            rules_data = {
                'exclusions': exclusions_data or {},
                'constraints': constraints_data or {}
            }
            
            # Update internal state
            self.current_group = group_name
            self.group_data = {'name': group_name, 'type': 'hair'}  # Basic group info
            self.alpha_whitelist = alpha_whitelist or {}
            
            # Load rules into rules manager
            self.rules_manager = BlendshapeRulesManager()
            if rules_data:
                try:
                    self.rules_manager.from_json(json.dumps(rules_data))
                except Exception as e:
                    print(f"Warning: Failed to load cross-module rules: {e}")
            
            return True, f"Successfully loaded group '{group_name}'"
            
        except Exception as e:
            return False, f"Error loading group: {str(e)}"
    
    def create_group(self, group_name: str, group_type: str = "hair") -> Tuple[bool, str]:
        """
        Create a new group USD file
        
        Args:
            group_name: Name for the new group
            group_type: Type of group (default: "hair")
            
        Returns:
            Tuple of (success, message)
        """
        if not config.usd_directory:
            return False, "No USD directory set"
        
        if not self.directory_manager:
            self.directory_manager = get_directory_manager(config.usd_directory)
        
        # Validate group name
        is_valid, validation_msg = self.directory_manager.validate_file_name(group_name)
        if not is_valid:
            # Try to sanitize the name
            sanitized_name = self.directory_manager.sanitize_file_name(group_name)
            if sanitized_name:
                group_name = sanitized_name
            else:
                return False, f"Invalid group name: {validation_msg}"
        
        group_file = config.usd_directory / "Group" / f"{group_name}.usd"
        
        # Check if group already exists
        if group_file.exists():
            return False, f"Group '{group_name}' already exists"
        
        try:
            # Create the group file
            success = create_group_file(group_file, group_name, group_type)
            if not success:
                return False, "Failed to create group USD file"
            
            # Initialize with default alpha whitelist (all alphas enabled)
            default_alpha_whitelist = self._get_default_alpha_whitelist()
            
            group_utils = USDGroupUtils(group_file)
            group_utils.set_alpha_whitelist_dict(default_alpha_whitelist)
            group_utils.save_stage()
            
            return True, f"Successfully created group '{group_name}'"
            
        except Exception as e:
            return False, f"Error creating group: {str(e)}"
    
    def save_current_group(self) -> Tuple[bool, str]:
        """
        Save current group data to USD file
        
        Returns:
            Tuple of (success, message)
        """
        if not self.current_group:
            return False, "No group currently loaded"
        
        if not config.usd_directory:
            return False, "No USD directory set"
        
        group_file = config.usd_directory / "Group" / f"{self.current_group}.usd"
        
        try:
            group_utils = USDGroupUtils(group_file)
            
            # Save alpha whitelist
            if self.alpha_whitelist:
                group_utils.set_alpha_whitelist_dict(self.alpha_whitelist)
            
            # Save cross-module rules
            if self.rules_manager.rules:
                rules_data = json.loads(self.rules_manager.to_json())
                
                # Split rules into exclusions and constraints
                exclusions = rules_data.get('exclusions', {})
                constraints = rules_data.get('constraints', {})
                
                if exclusions:
                    group_utils.set_cross_module_exclusions(exclusions)
                if constraints:
                    group_utils.set_weight_constraints(constraints)
            
            # Save changes to disk
            group_utils.save_stage()
            
            return True, f"Successfully saved group '{self.current_group}'"
            
        except Exception as e:
            return False, f"Error saving group: {str(e)}"
    
    def get_available_alpha_textures(self) -> Dict[str, str]:
        """
        Get all available alpha textures from the module directory
        
        Returns:
            Dictionary mapping texture paths to their display names
        """
        if not config.usd_directory:
            return {}
        
        textures = {}
        module_dir = config.usd_directory / "module"
        
        # Scan for alpha textures in module subdirectories
        for module_type_dir in module_dir.iterdir():
            if not module_type_dir.is_dir():
                continue
            
            alpha_dir = module_type_dir / "alpha"
            if not alpha_dir.exists():
                continue
            
            # Recursively find PNG files in alpha directory
            for png_file in alpha_dir.rglob("*.png"):
                # Create relative path from module directory
                rel_path = png_file.relative_to(module_dir)
                textures[str(rel_path)] = f"{module_type_dir.name}/{rel_path.name}"
        
        return textures
    
    def _get_default_alpha_whitelist(self) -> Dict[str, bool]:
        """Get default alpha whitelist with all textures enabled"""
        available_textures = self.get_available_alpha_textures()
        return {texture_path: True for texture_path in available_textures.keys()}
    
    def update_alpha_whitelist(self, texture_path: str, enabled: bool) -> None:
        """
        Update alpha whitelist for a specific texture
        
        Args:
            texture_path: Path to the texture relative to module directory
            enabled: Whether the texture should be whitelisted
        """
        self.alpha_whitelist[texture_path] = enabled
    
    def add_alpha_texture_path(self, texture_path: str, enabled: bool = True) -> Tuple[bool, str]:
        """
        Add a new alpha texture path to the whitelist
        
        Args:
            texture_path: Path to add
            enabled: Whether it should be enabled by default
            
        Returns:
            Tuple of (success, message)
        """
        if not texture_path.strip():
            return False, "Empty texture path"
        
        if texture_path in self.alpha_whitelist:
            return False, f"Texture path '{texture_path}' already exists"
        
        self.alpha_whitelist[texture_path] = enabled
        return True, f"Added texture path '{texture_path}'"
    
    def remove_alpha_texture_path(self, texture_path: str) -> Tuple[bool, str]:
        """
        Remove an alpha texture path from the whitelist
        
        Args:
            texture_path: Path to remove
            
        Returns:
            Tuple of (success, message)
        """
        if texture_path not in self.alpha_whitelist:
            return False, f"Texture path '{texture_path}' not found"
        
        del self.alpha_whitelist[texture_path]
        return True, f"Removed texture path '{texture_path}'"
    
    def get_group_modules(self) -> List[str]:
        """
        Get list of modules referenced by the current group
        
        Returns:
            List of module names
        """
        if not self.current_group or not config.usd_directory:
            return []
        
        try:
            group_file = config.usd_directory / "Group" / f"{self.current_group}.usd"
            group_utils = USDGroupUtils(group_file)
            
            # Get modules for all module types
            all_modules = []
            module_types = ["scalp", "crown", "tail", "bang"]
            
            for module_type in module_types:
                try:
                    module_list = group_utils.get_module_whitelist(module_type)
                    all_modules.extend(module_list)
                except:
                    # Module type might not exist yet, that's OK
                    continue
            
            return all_modules
            
        except Exception as e:
            print(f"Error getting group modules: {e}")
            return []
    
    def validate_current_group(self) -> Tuple[bool, List[str]]:
        """
        Validate the current group and return any issues found
        
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        if not self.current_group:
            return False, ["No group currently loaded"]
        
        if not config.usd_directory:
            return False, ["No USD directory set"]
        
        issues = []
        group_file = config.usd_directory / "Group" / f"{self.current_group}.usd"
        
        # Validate group file exists and is valid
        if not group_file.exists():
            issues.append(f"Group file not found: {group_file}")
            return False, issues
        
        is_valid, validation_msg = USDValidationUtils.validate_group_file(group_file)
        if not is_valid:
            issues.append(f"Invalid group file: {validation_msg}")
        
        # Validate alpha texture references
        for texture_path in self.alpha_whitelist.keys():
            full_path = config.usd_directory / "module" / texture_path
            if not full_path.exists():
                issues.append(f"Missing alpha texture: {texture_path}")
        
        # Validate module references
        modules = self.get_group_modules()
        for module_name in modules:
            module_file = config.usd_directory / "module" / f"{module_name}.usd"
            if not module_file.exists():
                issues.append(f"Missing module: {module_name}")
        
        return len(issues) == 0, issues