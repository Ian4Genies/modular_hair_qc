"""
Module Management System

Handles loading, creating, editing, and saving of Module USD files.
Manages module geometry, blendshapes, and internal exclusions.
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any, Set

import maya.cmds as cmds

from ..config import config
from ..utils import (
    USDModuleUtils, USDDirectoryManager, USDValidationUtils,
    create_module_file, BlendshapeRulesManager, get_directory_manager
)


class ModuleInfo:
    """Data class for module information"""
    
    def __init__(self, name: str, module_type: str, file_path: Path):
        self.name = name
        self.module_type = module_type
        self.file_path = file_path
        self.geometry_loaded = False
        self.blendshapes: Dict[str, float] = {}
        self.exclusions: Dict[str, Set[str]] = {}
        self.alpha_blacklist: List[str] = []


class ModuleManager:
    """Manages Module USD files and Maya scene integration"""
    
    def __init__(self):
        self.current_module: Optional[str] = None
        self.current_group: Optional[str] = None
        self.modules: Dict[str, ModuleInfo] = {}
        self.directory_manager: Optional[USDDirectoryManager] = None
        
        # Maya scene state
        self.loaded_geometry: Dict[str, str] = {}  # module_name -> maya_node_name
        self.blendshape_nodes: Dict[str, str] = {}  # module_name -> blendshape_node_name
        
        # Initialize directory manager if USD directory is set
        if config.usd_directory:
            self.directory_manager = get_directory_manager(config.usd_directory)
    
    def set_current_group(self, group_name: str) -> None:
        """Set the current group context for lazy loading"""
        if self.current_group != group_name:
            self.current_group = group_name
            # Clear current modules when group changes
            self.clear_modules()
    
    def clear_modules(self) -> None:
        """Clear all loaded modules"""
        self.modules.clear()
        self.current_module = None
        # Note: We don't automatically clear Maya scene geometry
        # as user might want to keep it loaded
    
    def get_available_modules(self, group_name: Optional[str] = None) -> List[str]:
        """
        Get list of available modules for a group
        
        Args:
            group_name: Group to get modules for (uses current group if None)
            
        Returns:
            List of module names
        """
        if not config.usd_directory:
            return []
        
        target_group = group_name or self.current_group
        if not target_group:
            return []
        
        # Get modules from group's module whitelist
        try:
            group_file = config.usd_directory / "Group" / f"{target_group}.usd"
            if not group_file.exists():
                return []
            
            from ..utils import USDGroupUtils
            group_utils = USDGroupUtils(group_file)
            module_whitelist = group_utils.get_module_whitelist()
            
            if not module_whitelist:
                return []
            
            # Filter to only modules that actually exist on disk
            available_modules = []
            for module_name, module_info in module_whitelist.items():
                module_type = module_info.get('type', 'unknown')
                
                # Check in the correct type subdirectory
                if module_type != 'unknown':
                    module_file = config.usd_directory / "module" / module_type / f"{module_name}.usd"
                    if module_file.exists():
                        available_modules.append(module_name)
                else:
                    # If type is unknown, search all type directories
                    for potential_type in ["scalp", "crown", "tail", "bang"]:
                        potential_file = config.usd_directory / "module" / potential_type / f"{module_name}.usd"
                        if potential_file.exists():
                            available_modules.append(module_name)
                            break
            
            return sorted(available_modules)
            
        except Exception as e:
            print(f"Error getting available modules: {e}")
            return []
    
    def load_module(self, module_name: str) -> Tuple[bool, str]:
        """
        Load a module and its data
        
        Args:
            module_name: Name of the module to load
            
        Returns:
            Tuple of (success, message)
        """
        if not config.usd_directory:
            return False, "No USD directory set"
        
        # First, we need to find which type subdirectory the module is in
        # We'll check the group's module whitelist for the type
        module_type = None
        if self.current_group:
            try:
                group_file = config.usd_directory / "Group" / f"{self.current_group}.usd"
                if group_file.exists():
                    from ..utils import USDGroupUtils
                    group_utils = USDGroupUtils(group_file)
                    module_whitelist = group_utils.get_module_whitelist()
                    if module_whitelist and module_name in module_whitelist:
                        module_type = module_whitelist[module_name].get('type', 'unknown')
            except Exception:
                pass
        
        # If we couldn't get the type from the group, search all type directories
        if not module_type or module_type == 'unknown':
            for potential_type in ["scalp", "crown", "tail", "bang"]:
                potential_file = config.usd_directory / "module" / potential_type / f"{module_name}.usd"
                if potential_file.exists():
                    module_type = potential_type
                    break
        
        if not module_type:
            return False, f"Module '{module_name}' not found in any module type directory"
        
        module_file = config.usd_directory / "module" / module_type / f"{module_name}.usd"
        if not module_file.exists():
            return False, f"Module file not found: {module_file}"
        
        try:
            # Validate module file
            is_valid, validation_msg = USDValidationUtils.validate_module_file(module_file)
            if not is_valid:
                return False, f"Invalid module file: {validation_msg}"
            
            # Load module data using USD utilities
            module_utils = USDModuleUtils(module_file)
            
            # Get module info
            module_info_data = module_utils.get_module_info()
            if not module_info_data:
                return False, "Failed to read module information"
            
            # Create ModuleInfo object
            module_info = ModuleInfo(
                name=module_name,
                module_type=module_info_data.get('type', 'unknown'),
                file_path=module_file
            )
            
            # Load blendshapes
            blendshapes = module_utils.get_blendshapes()
            if blendshapes:
                module_info.blendshapes = {name: 0.0 for name in blendshapes.keys()}
            
            # Load internal exclusions
            exclusions = module_utils.get_internal_exclusions()
            if exclusions:
                module_info.exclusions = exclusions
            
            # Load alpha blacklist
            alpha_blacklist = module_utils.get_alpha_blacklist()
            if alpha_blacklist:
                module_info.alpha_blacklist = alpha_blacklist
            
            # Check if geometry exists
            geometry_data = module_utils.get_geometry_data()
            module_info.geometry_loaded = bool(geometry_data)
            
            # Store module info
            self.modules[module_name] = module_info
            self.current_module = module_name
            
            return True, f"Successfully loaded module '{module_name}'"
            
        except Exception as e:
            return False, f"Error loading module: {str(e)}"
    
    def create_module(self, module_name: str, module_type: str) -> Tuple[bool, str]:
        """
        Create a new module USD file
        
        Args:
            module_name: Name for the new module
            module_type: Type of module (scalp, crown, tail, bang)
            
        Returns:
            Tuple of (success, message)
        """
        if not config.usd_directory:
            return False, "No USD directory set"
        
        if not self.directory_manager:
            self.directory_manager = get_directory_manager(config.usd_directory)
        
        # Validate module name
        is_valid, validation_msg = self.directory_manager.validate_file_name(module_name)
        if not is_valid:
            # Try to sanitize the name
            sanitized_name = self.directory_manager.sanitize_file_name(module_name)
            if sanitized_name:
                module_name = sanitized_name
            else:
                return False, f"Invalid module name: {validation_msg}"
        
        # Validate module type
        valid_types = ["scalp", "crown", "tail", "bang"]
        if module_type not in valid_types:
            return False, f"Invalid module type. Must be one of: {', '.join(valid_types)}"
        
        # Create module in the correct type subdirectory
        module_file = config.usd_directory / "module" / module_type / f"{module_name}.usd"
        
        # Check if module already exists
        if module_file.exists():
            return False, f"Module '{module_name}' already exists"
        
        try:
            # Ensure the module type directory exists
            module_type_dir = module_file.parent
            module_type_dir.mkdir(parents=True, exist_ok=True)
            
            # Create the module file
            success = create_module_file(module_file, module_name, module_type)
            if not success:
                return False, "Failed to create module USD file"
            
            # Add to current group's module whitelist if we have a current group
            if self.current_group:
                self._add_module_to_group_whitelist(module_name, module_type)
            
            return True, f"Successfully created module '{module_name}'"
            
        except Exception as e:
            return False, f"Error creating module: {str(e)}"
    
    def save_current_module(self) -> Tuple[bool, str]:
        """
        Save current module data to USD file
        
        Returns:
            Tuple of (success, message)
        """
        if not self.current_module:
            return False, "No module currently loaded"
        
        if self.current_module not in self.modules:
            return False, "Current module data not found"
        
        module_info = self.modules[self.current_module]
        
        try:
            module_utils = USDModuleUtils(module_info.file_path)
            
            # Save blendshapes if any
            if module_info.blendshapes:
                blendshape_data = {name: {"weight": weight} for name, weight in module_info.blendshapes.items()}
                module_utils.set_blendshapes(blendshape_data)
            
            # Save internal exclusions
            if module_info.exclusions:
                module_utils.set_internal_exclusions(module_info.exclusions)
            
            # Save alpha blacklist
            if module_info.alpha_blacklist:
                module_utils.set_alpha_blacklist(module_info.alpha_blacklist)
            
            # Save changes to disk
            module_utils.save_stage()
            
            return True, f"Successfully saved module '{self.current_module}'"
            
        except Exception as e:
            return False, f"Error saving module: {str(e)}"
    
    def import_geometry_from_scene(self, maya_object_name: str) -> Tuple[bool, str]:
        """
        Import geometry from Maya scene to current module
        
        Args:
            maya_object_name: Name of Maya object to import
            
        Returns:
            Tuple of (success, message)
        """
        if not self.current_module:
            return False, "No module currently loaded"
        
        # Validate Maya object
        if not cmds.objExists(maya_object_name):
            return False, f"Maya object '{maya_object_name}' not found"
        
        # Check if it's a mesh
        if not cmds.objectType(maya_object_name) == 'mesh' and not cmds.listRelatives(maya_object_name, shapes=True, type='mesh'):
            return False, f"Object '{maya_object_name}' is not a mesh"
        
        try:
            module_info = self.modules[self.current_module]
            module_utils = USDModuleUtils(module_info.file_path)
            
            # Export geometry to USD
            success = module_utils.import_geometry_from_maya(maya_object_name)
            if not success:
                return False, "Failed to import geometry to USD"
            
            # Update module info
            module_info.geometry_loaded = True
            
            # Store Maya node reference
            self.loaded_geometry[self.current_module] = maya_object_name
            
            return True, f"Successfully imported geometry from '{maya_object_name}'"
            
        except Exception as e:
            return False, f"Error importing geometry: {str(e)}"
    
    def load_geometry_to_scene(self, module_name: Optional[str] = None) -> Tuple[bool, str]:
        """
        Load module geometry into Maya scene
        
        Args:
            module_name: Module to load (uses current module if None)
            
        Returns:
            Tuple of (success, message)
        """
        target_module = module_name or self.current_module
        if not target_module:
            return False, "No module specified"
        
        if target_module not in self.modules:
            # Try to load the module first
            success, message = self.load_module(target_module)
            if not success:
                return False, f"Failed to load module: {message}"
        
        module_info = self.modules[target_module]
        
        try:
            module_utils = USDModuleUtils(module_info.file_path)
            
            # Import geometry to Maya
            maya_node = module_utils.export_geometry_to_maya(f"{target_module}_geo")
            if not maya_node:
                return False, "Failed to load geometry from USD"
            
            # Store Maya node reference
            self.loaded_geometry[target_module] = maya_node
            
            return True, f"Successfully loaded geometry as '{maya_node}'"
            
        except Exception as e:
            return False, f"Error loading geometry: {str(e)}"
    
    def add_blendshape_from_scene(self, maya_object_name: str, blendshape_name: Optional[str] = None) -> Tuple[bool, str]:
        """
        Add a blendshape from Maya scene to current module
        
        Args:
            maya_object_name: Name of Maya object to use as blendshape
            blendshape_name: Name for the blendshape (uses object name if None)
            
        Returns:
            Tuple of (success, message)
        """
        if not self.current_module:
            return False, "No module currently loaded"
        
        # Validate Maya object
        if not cmds.objExists(maya_object_name):
            return False, f"Maya object '{maya_object_name}' not found"
        
        # Check if it's a mesh
        if not cmds.objectType(maya_object_name) == 'mesh' and not cmds.listRelatives(maya_object_name, shapes=True, type='mesh'):
            return False, f"Object '{maya_object_name}' is not a mesh"
        
        # Use object name as blendshape name if not provided
        if not blendshape_name:
            blendshape_name = maya_object_name
        
        # Validate blendshape name
        if not self.directory_manager:
            self.directory_manager = get_directory_manager(config.usd_directory)
        
        is_valid, validation_msg = self.directory_manager.validate_file_name(blendshape_name)
        if not is_valid:
            # Try to sanitize the name
            sanitized_name = self.directory_manager.sanitize_file_name(blendshape_name)
            if sanitized_name:
                blendshape_name = sanitized_name
            else:
                return False, f"Invalid blendshape name: {validation_msg}"
        
        try:
            module_info = self.modules[self.current_module]
            
            # Check if blendshape already exists
            if blendshape_name in module_info.blendshapes:
                return False, f"Blendshape '{blendshape_name}' already exists"
            
            module_utils = USDModuleUtils(module_info.file_path)
            
            # Add blendshape to USD
            success = module_utils.add_blendshape_from_maya(maya_object_name, blendshape_name)
            if not success:
                return False, "Failed to add blendshape to USD"
            
            # Update module info
            module_info.blendshapes[blendshape_name] = 0.0
            
            return True, f"Successfully added blendshape '{blendshape_name}'"
            
        except Exception as e:
            return False, f"Error adding blendshape: {str(e)}"
    
    def remove_blendshape(self, blendshape_name: str) -> Tuple[bool, str]:
        """
        Remove a blendshape from current module
        
        Args:
            blendshape_name: Name of blendshape to remove
            
        Returns:
            Tuple of (success, message)
        """
        if not self.current_module:
            return False, "No module currently loaded"
        
        module_info = self.modules[self.current_module]
        
        if blendshape_name not in module_info.blendshapes:
            return False, f"Blendshape '{blendshape_name}' not found"
        
        try:
            module_utils = USDModuleUtils(module_info.file_path)
            
            # Remove from USD
            success = module_utils.remove_blendshape(blendshape_name)
            if not success:
                return False, "Failed to remove blendshape from USD"
            
            # Update module info
            del module_info.blendshapes[blendshape_name]
            
            # Remove any exclusions involving this blendshape
            if blendshape_name in module_info.exclusions:
                del module_info.exclusions[blendshape_name]
            
            # Remove from other blendshape exclusions
            for bs_name, excluded_set in module_info.exclusions.items():
                excluded_set.discard(blendshape_name)
            
            return True, f"Successfully removed blendshape '{blendshape_name}'"
            
        except Exception as e:
            return False, f"Error removing blendshape: {str(e)}"
    
    def set_blendshape_weight(self, blendshape_name: str, weight: float) -> Tuple[bool, str]:
        """
        Set blendshape weight for preview in Maya
        
        Args:
            blendshape_name: Name of blendshape
            weight: Weight value (0.0 to 1.0)
            
        Returns:
            Tuple of (success, message)
        """
        if not self.current_module:
            return False, "No module currently loaded"
        
        module_info = self.modules[self.current_module]
        
        if blendshape_name not in module_info.blendshapes:
            return False, f"Blendshape '{blendshape_name}' not found"
        
        # Clamp weight to valid range
        weight = max(0.0, min(1.0, weight))
        
        try:
            # Update module info
            module_info.blendshapes[blendshape_name] = weight
            
            # Update Maya blendshape node if loaded
            if self.current_module in self.blendshape_nodes:
                blendshape_node = self.blendshape_nodes[self.current_module]
                if cmds.objExists(blendshape_node):
                    attr_name = f"{blendshape_node}.{blendshape_name}"
                    if cmds.objExists(attr_name):
                        cmds.setAttr(attr_name, weight)
            
            return True, f"Set weight for '{blendshape_name}' to {weight}"
            
        except Exception as e:
            return False, f"Error setting blendshape weight: {str(e)}"
    
    def set_blendshape_exclusion(self, blendshape_name: str, excluded_blendshape: str, excluded: bool) -> Tuple[bool, str]:
        """
        Set internal exclusion between blendshapes
        
        Args:
            blendshape_name: Name of primary blendshape
            excluded_blendshape: Name of blendshape to exclude/include
            excluded: Whether to exclude the blendshape
            
        Returns:
            Tuple of (success, message)
        """
        if not self.current_module:
            return False, "No module currently loaded"
        
        module_info = self.modules[self.current_module]
        
        if blendshape_name not in module_info.blendshapes:
            return False, f"Blendshape '{blendshape_name}' not found"
        
        if excluded_blendshape not in module_info.blendshapes:
            return False, f"Excluded blendshape '{excluded_blendshape}' not found"
        
        try:
            # Initialize exclusions set if needed
            if blendshape_name not in module_info.exclusions:
                module_info.exclusions[blendshape_name] = set()
            
            # Update exclusions
            if excluded:
                module_info.exclusions[blendshape_name].add(excluded_blendshape)
                # Make exclusion bidirectional
                if excluded_blendshape not in module_info.exclusions:
                    module_info.exclusions[excluded_blendshape] = set()
                module_info.exclusions[excluded_blendshape].add(blendshape_name)
            else:
                module_info.exclusions[blendshape_name].discard(excluded_blendshape)
                # Remove bidirectional exclusion
                if excluded_blendshape in module_info.exclusions:
                    module_info.exclusions[excluded_blendshape].discard(blendshape_name)
            
            action = "excluded" if excluded else "included"
            return True, f"Successfully {action} '{excluded_blendshape}' from '{blendshape_name}'"
            
        except Exception as e:
            return False, f"Error setting exclusion: {str(e)}"
    
    def validate_current_module(self) -> Tuple[bool, List[str]]:
        """
        Validate the current module and return any issues found
        
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        if not self.current_module:
            return False, ["No module currently loaded"]
        
        if self.current_module not in self.modules:
            return False, ["Current module data not found"]
        
        issues = []
        module_info = self.modules[self.current_module]
        
        # Validate module file exists
        if not module_info.file_path.exists():
            issues.append(f"Module file not found: {module_info.file_path}")
            return False, issues
        
        # Validate USD file
        is_valid, validation_msg = USDValidationUtils.validate_module_file(module_info.file_path)
        if not is_valid:
            issues.append(f"Invalid module file: {validation_msg}")
        
        # Check geometry
        if not module_info.geometry_loaded:
            issues.append("No geometry loaded in module")
        
        # Validate blendshape exclusions
        for bs_name, excluded_set in module_info.exclusions.items():
            if bs_name not in module_info.blendshapes:
                issues.append(f"Exclusion references missing blendshape: {bs_name}")
            
            for excluded_bs in excluded_set:
                if excluded_bs not in module_info.blendshapes:
                    issues.append(f"Exclusion references missing blendshape: {excluded_bs}")
        
        return len(issues) == 0, issues
    
    def _add_module_to_group_whitelist(self, module_name: str, module_type: str) -> None:
        """Add module to current group's whitelist"""
        try:
            if not self.current_group or not config.usd_directory:
                return
            
            group_file = config.usd_directory / "Group" / f"{self.current_group}.usd"
            if not group_file.exists():
                return
            
            from ..utils import USDGroupUtils
            group_utils = USDGroupUtils(group_file)
            
            # Get existing whitelist
            module_whitelist = group_utils.get_module_whitelist() or {}
            
            # Add new module
            module_whitelist[module_name] = {"type": module_type, "enabled": True}
            
            # Save back to group
            group_utils.set_module_whitelist(module_whitelist)
            group_utils.save_stage()
            
        except Exception as e:
            print(f"Warning: Failed to add module to group whitelist: {e}")