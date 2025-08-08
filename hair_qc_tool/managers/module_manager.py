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
        
        # Maya scene state - using display geometry (DAG nodes) for interactive editing
        self.display_geometry: Dict[str, str] = {}  # module_name -> maya_group_name
        self.maya_blendshapes: Dict[str, Dict[str, str]] = {}  # module_name -> {blendshape_name -> maya_attribute}
        self.stage_references: Dict[str, Any] = {}  # module_name -> USD stage reference
        self._module_root_group: str = "module"  # Persistent container group
        self._current_display_module: Optional[str] = None
        
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
            
            # Load blendshapes with proper weights from USD BlendShape schema
            try:
                blendshapes_with_weights = module_utils.get_blendshapes_with_weights()
                if blendshapes_with_weights:
                    module_info.blendshapes = blendshapes_with_weights
                else:
                    # Fallback to old method for compatibility
                    blendshape_names = module_utils.get_blendshape_names()
                    if blendshape_names:
                        module_info.blendshapes = {name: 0.0 for name in blendshape_names}
            except Exception as e:
                print(f"[Module Manager] Warning: Error loading blendshapes: {e}")
                # Fallback to old method
                blendshape_names = module_utils.get_blendshape_names()
                if blendshape_names:
                    module_info.blendshapes = {name: 0.0 for name in blendshape_names}
            
            # Load internal exclusions
            exclusions = module_utils.get_internal_exclusions()
            if exclusions:
                module_info.exclusions = exclusions
            
            # Load alpha blacklist (skip for now - needs category parameter)
            # alpha_blacklist = module_utils.get_alpha_blacklist('scalp')
            # if alpha_blacklist:
            #     module_info.alpha_blacklist = alpha_blacklist
            
            # Check if geometry exists
            has_geometry = module_utils.has_geometry_data()
            module_info.geometry_loaded = has_geometry
            
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
            
            # Save current blendshape weights from UI to USD
            if module_info.blendshapes:
                print(f"[Module Manager] Saving {len(module_info.blendshapes)} blendshape weights to USD")
                for bs_name, weight in module_info.blendshapes.items():
                    try:
                        module_utils.set_blendshape_weight_via_animation(bs_name, weight)
                    except Exception as bs_error:
                        print(f"[Module Manager] Warning: Could not save weight for {bs_name}: {bs_error}")
            
            # Save internal exclusions
            if module_info.exclusions:
                module_utils.set_internal_exclusions(module_info.exclusions)
            
            # Save alpha blacklist (skip for now - needs category parameter)
            # if module_info.alpha_blacklist:
            #     module_utils.set_alpha_blacklist('scalp', module_info.alpha_blacklist)
            
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
            
            # Note: We don't store Maya node references anymore since we use proxy shapes
            # The geometry is now stored in the USD file and will be displayed via proxy shape
            
            return True, f"Successfully imported geometry from '{maya_object_name}'"
            
        except Exception as e:
            return False, f"Error importing geometry: {str(e)}"
    
    def clear_all_display_geometry(self) -> None:
        """Clear ONLY the contents under the persistent module root group.

        This is non-destructive to the rest of the scene. The root group itself persists.
        USD stages remain loaded for rapid swapping.
        """
        try:
            # Ensure root exists
            self._ensure_module_root_group()

            # Delete all children under the root container only
            children = cmds.listRelatives(self._module_root_group, children=True, fullPath=False) or []
            for child in children:
                try:
                    cmds.delete(child)
                except Exception as node_error:
                    print(f"Warning: Error clearing child '{child}' of module root: {node_error}")

            # Clear display geometry tracking and current display module
            self.display_geometry.clear()
            self.maya_blendshapes.clear()
            self._current_display_module = None

            # Force viewport refresh
            try:
                cmds.refresh(currentView=True, force=True)
            except Exception as refresh_error:
                print(f"Warning: Error refreshing viewport: {refresh_error}")
            
        except Exception as e:
            print(f"Warning: Error clearing display geometry: {e}")
    
    def clear_usd_stages(self) -> None:
        """Clear USD stages when changing groups (full cleanup)"""
        try:
            # Close USD stages to free memory when switching groups
            for stage in self.stage_references.values():
                try:
                    if hasattr(stage, 'Close'):
                        stage.Close()
                except Exception as stage_error:
                    print(f"Warning: Error closing USD stage: {stage_error}")
            
            # Clear stage references
            self.stage_references.clear()
            
            # Also clear global USD stage cache when switching groups
            try:
                from pxr import Usd
                # Clear all stage caches
                Usd.StageCache.Get().Clear()
            except (ImportError, AttributeError) as e:
                print(f"Warning: Could not clear USD stage cache: {e}")
                pass
                
        except Exception as e:
            print(f"Warning: Error clearing USD stages: {e}")
    
    def load_geometry_to_scene(self, module_name: Optional[str] = None) -> Tuple[bool, str]:
        """
        Load module as Maya display geometry for interactive editing (exclusive - clears other display geo)
        
        Args:
            module_name: Module to load (uses current module if None)
            
        Returns:
            Tuple of (success, message)
        """
        target_module = module_name or self.current_module
        if not target_module:
            # If no module specified, just clear all display geometry
            self.clear_all_display_geometry()
            return True, "Cleared all module display geometry"
        
        if target_module not in self.modules:
            # Try to load the module first
            success, message = self.load_module(target_module)
            if not success:
                return False, f"Failed to load module: {message}"
        
        module_info = self.modules[target_module]
        
        try:
            # Prepare persistent module root
            self._ensure_module_root_group()

            # Remove only previous module contents (non-destructive to rest of scene)
            self._clear_previous_module_group()

            # Import USD as Maya DAG nodes for interactive editing
            success, maya_nodes = self._import_usd_as_maya_geometry(module_info)
            if not success:
                return False, f"Failed to import USD as Maya geometry: {maya_nodes}"
            
            # Create organized group structure under persistent root
            module_group_name = f"{target_module}_Module"
            if cmds.objExists(f"{self._module_root_group}|{module_group_name}"):
                try:
                    cmds.delete(f"{self._module_root_group}|{module_group_name}")
                except Exception:
                    pass
            module_group = cmds.group(empty=True, name=module_group_name, parent=self._module_root_group)

            # Parent imported geometry under this module subgroup
            if maya_nodes:
                try:
                    # Reparent all to subgroup
                    cmds.parent(maya_nodes, module_group)
                except Exception as parent_error:
                    print(f"Warning: Could not parent some nodes to group: {parent_error}")
            
            # Store display geometry reference
            self.display_geometry[target_module] = module_group
            self._current_display_module = target_module
            
            # Set up blendshape controls for interactive editing
            self._setup_maya_blendshape_controls(target_module, maya_nodes)
            
            # Store USD stage reference for data synchronization (reuse if already loaded)
            try:
                from pxr import Usd
                if target_module not in self.stage_references:
                    stage = Usd.Stage.Open(str(module_info.file_path))
                    self.stage_references[target_module] = stage
            except ImportError:
                print("Warning: USD Python API not available for stage control")
            
            return True, f"Loaded module into '{self._module_root_group}|{module_group_name}'"
            
        except Exception as e:
            return False, f"Error loading display geometry: {str(e)}"
    
    def add_blendshape_from_scene(self, maya_object_name: str, blendshape_name: Optional[str] = None) -> Tuple[bool, str]:
        """
        Add a blendshape from Maya scene to current module (updates both USD and Maya display geometry)
        
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
            
            # STEP 1: Add blendshape to USD file (for pipeline compatibility)
            module_utils = USDModuleUtils(module_info.file_path)
            usd_success = module_utils.add_blendshape_from_maya(maya_object_name, blendshape_name)
            if not usd_success:
                return False, "Failed to add blendshape to USD"
            
            # STEP 2: Add blendshape to Maya display geometry (for interactive control)
            if self.current_module in self.display_geometry:
                maya_success = self._add_blendshape_to_maya_geometry(maya_object_name, blendshape_name)
                if not maya_success:
                    print(f"[Module Manager] Warning: Added to USD but failed to add to Maya display geometry")
            
            # STEP 3: Update module info
            module_info.blendshapes[blendshape_name] = 0.0
            
            # STEP 4: Refresh display geometry to show new blendshape
            if self.current_module in self.display_geometry:
                self._refresh_display_geometry(self.current_module)
            
            return True, f"Successfully added blendshape '{blendshape_name}' to USD and display geometry"
            
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
        Set blendshape weight on Maya display geometry (real-time viewport updates)
        
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
            
            # Control Maya blendshape directly for real-time viewport updates
            if self.current_module in self.maya_blendshapes:
                maya_blendshapes = self.maya_blendshapes[self.current_module]
                
                if blendshape_name in maya_blendshapes:
                    maya_attr = maya_blendshapes[blendshape_name]
                    
                    try:
                        # Set Maya blendshape weight directly
                        cmds.setAttr(maya_attr, weight)
                        print(f"[Module Manager] Set Maya blendshape: {maya_attr} = {weight}")
                        
                        # Viewport updates automatically with Maya blendshapes!
                        return True, f"Set weight for '{blendshape_name}' to {weight}"
                        
                    except Exception as maya_error:
                        print(f"[Module Manager] Maya blendshape control failed: {maya_error}")
                        return False, f"Failed to set Maya blendshape weight: {maya_error}"
                else:
                    return False, f"Maya blendshape control not found for '{blendshape_name}'"
            else:
                return False, f"No Maya blendshapes set up for module '{self.current_module}'"
            
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
    

    
    def _import_usd_as_maya_geometry(self, module_info: ModuleInfo) -> Tuple[bool, List[str]]:
        """Import USD module as Maya DAG nodes for interactive editing"""
        try:
            from ..utils.maya_utils import MayaUtils
            
            # Use Maya's USD import to convert to DAG nodes
            imported_nodes = MayaUtils.import_usd_as_maya_geometry(
                str(module_info.file_path), 
                import_blendshapes=True,
                import_skeletons=False  # We handle skeletons separately
            )
            
            if not imported_nodes:
                return False, "No geometry imported from USD"
            
            print(f"[Module Manager] Imported {len(imported_nodes)} nodes from USD: {imported_nodes}")

            # Keep only transforms for grouping
            transform_nodes = [n for n in imported_nodes if cmds.objExists(n) and cmds.nodeType(n) == 'transform']
            if transform_nodes:
                imported_nodes = transform_nodes
            return True, imported_nodes
            
        except Exception as e:
            print(f"[Module Manager] Error importing USD as Maya geometry: {e}")
            return False, []
    
    def _setup_maya_blendshape_controls(self, module_name: str, maya_nodes: List[str]) -> None:
        """Set up Maya blendshape controls for interactive editing"""
        try:
            # Find blendShape nodes in the imported geometry
            blendshape_nodes = []
            for node in maya_nodes:
                try:
                    # Check if node is a blendShape or has blendShape history
                    history = cmds.listHistory(node, pruneDagObjects=True) or []
                    # Filter for blendShape nodes
                    for hist_node in history:
                        if cmds.nodeType(hist_node) == "blendShape":
                            blendshape_nodes.append(hist_node)
                except Exception as e:
                    print(f"[Module Manager] Warning: Could not check history for {node}: {e}")
                    continue
            
            # If no blendShape nodes were imported, create them from USD targets (Skel standard)
            if not blendshape_nodes:
                try:
                    from ..utils.maya_utils import MayaUtils
                    module_info = self.modules.get(module_name)
                    if module_info and module_name in self.display_geometry:
                        group_name = self.display_geometry[module_name]
                        # Find BaseMesh transform under the group
                        mesh_shapes = cmds.listRelatives(group_name, allDescendents=True, type='mesh') or []
                        base_mesh_transform = None
                        for shape in mesh_shapes:
                            parent = cmds.listRelatives(shape, parent=True, type='transform')
                            if parent and (shape.endswith('BaseMeshShape') or parent[0].endswith('BaseMesh')):
                                base_mesh_transform = parent[0]
                                break
                        if not base_mesh_transform and mesh_shapes:
                            base_mesh_transform = cmds.listRelatives(mesh_shapes[0], parent=True, type='transform')[0]

                        # Create Maya blendshapes from USD targets
                        # Use only proper USD names (filter out accidental single-char keys)
                        bs_names = [n for n in (module_info.blendshapes or {}).keys() if isinstance(n, str) and len(n) > 1]
                        if base_mesh_transform and bs_names:
                            MayaUtils.create_blendshapes_from_usd_data(
                                base_mesh_transform,
                                str(module_info.file_path),
                                bs_names,
                            )
                            # Re-scan for blendShape nodes after creation
                            history2 = cmds.listHistory(base_mesh_transform, pruneDagObjects=True) or []
                            for hist_node in history2:
                                if cmds.nodeType(hist_node) == "blendShape":
                                    blendshape_nodes.append(hist_node)
                except Exception as create_bs_err:
                    print(f"[Module Manager] Warning: Could not create Maya blendshapes from USD: {create_bs_err}")
            
            # Set up control attributes for each blendshape
            module_blendshapes = {}
            for blend_node in blendshape_nodes:
                # Get all blendshape targets
                targets = cmds.listAttr(f"{blend_node}.weight", multi=True) or []
                for target in targets:
                    # Get the actual target name (Maya uses aliases)
                    alias = cmds.aliasAttr(f"{blend_node}.{target}", query=True)
                    if alias:
                        maya_alias = alias[0]  # First alias is the name
                        # Normalize alias to proper USD name when possible
                        normalized_name = self._normalize_blendshape_name(
                            module_name,
                            maya_alias,
                        )
                        attr_name = f"{blend_node}.{maya_alias}"
                        module_blendshapes[normalized_name] = attr_name
                        print(f"[Module Manager] Found blendshape control: {maya_alias} (as {normalized_name}) -> {attr_name}")
            
            # Store blendshape mappings for this module
            self.maya_blendshapes[module_name] = module_blendshapes
            
            # Update module info with current blendshape weights
            if module_name in self.modules:
                module_info = self.modules[module_name]
                # Only keep weights for normalized USD names we know about
                known_usd_names = set([n for n in module_info.blendshapes.keys() if isinstance(n, str) and len(n) > 1])
                new_weights: Dict[str, float] = {}
                for bs_name, attr_name in module_blendshapes.items():
                    if bs_name not in known_usd_names:
                        # Skip unknown or short aliases
                        continue
                    try:
                        current_weight = cmds.getAttr(attr_name)
                        new_weights[bs_name] = current_weight
                    except Exception:
                        new_weights[bs_name] = 0.0
                # Merge with existing known keys to avoid adding stray one-letter entries
                for k in list(module_info.blendshapes.keys()):
                    if isinstance(k, str) and len(k) == 1:
                        # Drop stray single-letter entries
                        del module_info.blendshapes[k]
                module_info.blendshapes.update(new_weights)
            
            print(f"[Module Manager] Set up {len(module_blendshapes)} blendshape controls for module {module_name}")
            
        except Exception as e:
            print(f"[Module Manager] Error setting up blendshape controls: {e}")
    
    def _add_blendshape_to_maya_geometry(self, maya_object_name: str, blendshape_name: str) -> bool:
        """Add blendshape to current Maya display geometry"""
        try:
            if self.current_module not in self.display_geometry:
                print(f"[Module Manager] No display geometry loaded for {self.current_module}")
                return False
            
            # Find the mesh in the display geometry
            group_name = self.display_geometry[self.current_module]
            mesh_nodes = cmds.listRelatives(group_name, allDescendents=True, type='mesh') or []
            
            if not mesh_nodes:
                print(f"[Module Manager] No mesh found in display geometry")
                return False
            
            # Use the first mesh (assume single mesh per module for now)
            target_mesh = cmds.listRelatives(mesh_nodes[0], parent=True)[0]  # Get transform
            
            # Check if blendShape node already exists
            existing_blend_nodes = cmds.listHistory(target_mesh, type="blendShape")
            
            if existing_blend_nodes:
                # Add to existing blendShape node
                blend_node = existing_blend_nodes[0]
                try:
                    # Get current target count
                    current_targets = cmds.listAttr(f"{blend_node}.weight", multi=True) or []
                    target_index = len(current_targets)
                    
                    # Add new target
                    cmds.blendShape(blend_node, edit=True, target=(target_mesh, target_index, maya_object_name, 1.0))
                    
                    # Set alias name
                    cmds.aliasAttr(blendshape_name, f"{blend_node}.weight[{target_index}]")
                    
                    print(f"[Module Manager] Added blendshape '{blendshape_name}' to existing blendShape node")
                    
                except Exception as e:
                    print(f"[Module Manager] Error adding to existing blendShape: {e}")
                    return False
            else:
                # Create new blendShape node
                try:
                    blend_node = cmds.blendShape(maya_object_name, target_mesh, name=f"{target_mesh}_blendShape")[0]
                    cmds.aliasAttr(blendshape_name, f"{blend_node}.weight[0]")
                    
                    print(f"[Module Manager] Created new blendShape node with '{blendshape_name}'")
                    
                except Exception as e:
                    print(f"[Module Manager] Error creating new blendShape: {e}")
                    return False
            
            return True
            
        except Exception as e:
            print(f"[Module Manager] Error adding blendshape to Maya geometry: {e}")
            return False
    
    def _clear_imported_namespaces(self) -> None:
        """Clear any existing imported namespaces to prevent accumulation"""
        try:
            # Get all namespaces that start with "imported"
            all_namespaces = cmds.namespaceInfo(listOnlyNamespaces=True, recurse=True) or []
            imported_namespaces = [ns for ns in all_namespaces if ns.startswith('imported')]
            
            for namespace in imported_namespaces:
                try:
                    # Get all nodes in the namespace
                    nodes_in_ns = cmds.namespaceInfo(namespace, listNamespace=True, dagPath=True) or []
                    
                    # Delete all nodes in the namespace
                    if nodes_in_ns:
                        for node in nodes_in_ns:
                            if cmds.objExists(node):
                                try:
                                    cmds.delete(node)
                                except:
                                    pass
                    
                    # Remove the namespace
                    if cmds.namespace(exists=namespace):
                        cmds.namespace(removeNamespace=namespace, mergeNamespaceWithRoot=True)
                        print(f"[Module Manager] Cleared namespace: {namespace}")
                        
                except Exception as ns_error:
                    print(f"[Module Manager] Warning: Could not clear namespace {namespace}: {ns_error}")
                    
        except Exception as e:
            print(f"[Module Manager] Warning: Error clearing imported namespaces: {e}")
    
    def _refresh_display_geometry(self, module_name: str) -> None:
        """Refresh display geometry to match USD changes"""
        try:
            if module_name not in self.display_geometry:
                print(f"[Module Manager] No display geometry to refresh for {module_name}")
                return
            
            # Remove only the current module subgroup
            current_group = self.display_geometry[module_name]
            if cmds.objExists(current_group):
                try:
                    cmds.delete(current_group)
                except Exception as e:
                    print(f"[Module Manager] Warning: could not delete group {current_group}: {e}")
            
            # Reload from USD
            module_info = self.modules[module_name]
            success, maya_nodes = self._import_usd_as_maya_geometry(module_info)
            if success:
                # Recreate group and setup
                self._ensure_module_root_group()
                module_group_name = f"{module_name}_Module"
                module_group = cmds.group(empty=True, name=module_group_name, parent=self._module_root_group)
                
                if maya_nodes:
                    try:
                        cmds.parent(maya_nodes, module_group)
                    except Exception:
                        pass
                
                self.display_geometry[module_name] = module_group
                self._setup_maya_blendshape_controls(module_name, maya_nodes)
                
                print(f"[Module Manager] Refreshed display geometry for {module_name}")
            
        except Exception as e:
            print(f"[Module Manager] Error refreshing display geometry: {e}")
    
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

    def _normalize_blendshape_name(self, module_name: str, maya_alias: str) -> str:
        """Normalize a Maya blendshape alias to a canonical USD blendshape name.
        
        - Prefer full USD target names from the module's USD relationship
        - If alias is single-character and a full match exists starting with that letter, pick the full name
        - Otherwise return the alias unchanged
        """
        try:
            if module_name not in self.modules:
                return maya_alias
            module_info = self.modules[module_name]
            # Gather USD names from module_info
            usd_names = [n for n in module_info.blendshapes.keys() if isinstance(n, str) and len(n) > 1]
            if not usd_names:
                return maya_alias
            if isinstance(maya_alias, str) and len(maya_alias) == 1:
                # Try to find a unique USD name that starts with this letter
                candidates = [n for n in usd_names if n.startswith(maya_alias)]
                if len(candidates) == 1:
                    return candidates[0]
            # If alias matches a USD name exactly, keep it
            if maya_alias in usd_names:
                return maya_alias
            return maya_alias
        except Exception:
            return maya_alias

    # ---------------------------
    # Internal helpers (scene)
    # ---------------------------
    def _ensure_module_root_group(self) -> None:
        """Ensure the persistent module root group exists."""
        try:
            if not cmds.objExists(self._module_root_group):
                cmds.group(empty=True, name=self._module_root_group)
        except Exception as e:
            print(f"[Module Manager] Warning: could not ensure module root group '{self._module_root_group}': {e}")

    def _clear_previous_module_group(self) -> None:
        """Delete the previous module subgroup under the root, if any."""
        try:
            if self._current_display_module:
                prev_group = self.display_geometry.get(self._current_display_module)
                if prev_group and cmds.objExists(prev_group):
                    try:
                        cmds.delete(prev_group)
                    except Exception as e:
                        print(f"[Module Manager] Warning: could not delete previous module group '{prev_group}': {e}")
                # Clear tracking of previous
                if self._current_display_module in self.display_geometry:
                    del self.display_geometry[self._current_display_module]
                self._current_display_module = None
        except Exception as e:
            print(f"[Module Manager] Warning: error clearing previous module: {e}")