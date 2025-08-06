"""
Data Manager

Coordinates between Group, Module, and Style managers.
Provides a unified interface for the UI to interact with USD data.
"""

from typing import Optional, List, Dict, Tuple, Any
from pathlib import Path

from ..config import config
from .group_manager import GroupManager
from .module_manager import ModuleManager


class DataManager:
    """
    Unified data management interface
    
    Coordinates between different managers and provides caching,
    change tracking, and unified operations.
    """
    
    def __init__(self):
        self.group_manager = GroupManager()
        self.module_manager = ModuleManager()
        self._change_tracking: Dict[str, bool] = {
            'group': False,
            'modules': False,
            'styles': False
        }
        
        # Cache for UI data
        self._cached_groups: Optional[List[str]] = None
        self._cached_modules: Optional[List[str]] = None
        self._cache_valid = False
    
    def refresh_all_data(self) -> Tuple[bool, str]:
        """
        Refresh all cached data from USD files
        
        Returns:
            Tuple of (success, message)
        """
        try:
            # Clear caches
            self._cached_groups = None
            self._cached_modules = None
            self._cache_valid = False
            
            # Reset change tracking
            self._change_tracking = {key: False for key in self._change_tracking}
            
            # Refresh directory manager if needed
            if config.usd_directory:
                from ..utils import get_directory_manager
                self.group_manager.directory_manager = None
                self.group_manager.directory_manager = get_directory_manager(config.usd_directory)
            
            return True, "Data refreshed successfully"
            
        except Exception as e:
            return False, f"Error refreshing data: {str(e)}"
    
    def get_groups(self, force_refresh: bool = False) -> List[str]:
        """
        Get list of available groups with caching
        
        Args:
            force_refresh: Force refresh from disk
            
        Returns:
            List of group names
        """
        if force_refresh or self._cached_groups is None:
            self._cached_groups = self.group_manager.get_available_groups()
        
        return self._cached_groups or []
    
    def load_group(self, group_name: str) -> Tuple[bool, str]:
        """
        Load a group and mark as current
        
        Args:
            group_name: Name of group to load
            
        Returns:
            Tuple of (success, message)
        """
        success, message = self.group_manager.load_group(group_name)
        
        if success:
            # Reset change tracking for group
            self._change_tracking['group'] = False
            
            # Set current group context for module manager
            self.module_manager.set_current_group(group_name)
            
            # Clear cached modules when group changes
            self._cached_modules = None
        
        return success, message
    
    def create_group(self, group_name: str, group_type: str = "hair") -> Tuple[bool, str]:
        """
        Create a new group
        
        Args:
            group_name: Name for new group
            group_type: Type of group
            
        Returns:
            Tuple of (success, message)
        """
        success, message = self.group_manager.create_group(group_name, group_type)
        
        if success:
            # Invalidate group cache
            self._cached_groups = None
            # Mark as having changes
            self._change_tracking['group'] = True
        
        return success, message
    
    def save_current_group(self) -> Tuple[bool, str]:
        """
        Save current group data
        
        Returns:
            Tuple of (success, message)
        """
        success, message = self.group_manager.save_current_group()
        
        if success:
            # Clear change tracking for group
            self._change_tracking['group'] = False
        
        return success, message
    
    # Module Management Methods
    def get_modules(self, force_refresh: bool = False) -> List[str]:
        """
        Get list of available modules for current group with caching
        
        Args:
            force_refresh: Force refresh from disk
            
        Returns:
            List of module names
        """
        if force_refresh or self._cached_modules is None:
            self._cached_modules = self.module_manager.get_available_modules()
        
        return self._cached_modules or []
    
    def load_module(self, module_name: str) -> Tuple[bool, str]:
        """
        Load a module and mark as current
        
        Args:
            module_name: Name of module to load
            
        Returns:
            Tuple of (success, message)
        """
        success, message = self.module_manager.load_module(module_name)
        
        if success:
            # Reset change tracking for modules
            self._change_tracking['modules'] = False
        
        return success, message
    
    def create_module(self, module_name: str, module_type: str) -> Tuple[bool, str]:
        """
        Create a new module
        
        Args:
            module_name: Name for new module
            module_type: Type of module (scalp, crown, tail, bang)
            
        Returns:
            Tuple of (success, message)
        """
        success, message = self.module_manager.create_module(module_name, module_type)
        
        if success:
            # Invalidate module cache
            self._cached_modules = None
            # Mark as having changes
            self._change_tracking['modules'] = True
        
        return success, message
    
    def save_current_module(self) -> Tuple[bool, str]:
        """
        Save current module data
        
        Returns:
            Tuple of (success, message)
        """
        success, message = self.module_manager.save_current_module()
        
        if success:
            # Clear change tracking for modules
            self._change_tracking['modules'] = False
        
        return success, message
    
    def get_current_module(self) -> Optional[str]:
        """Get name of currently loaded module"""
        return self.module_manager.current_module
    
    def get_module_blendshapes(self) -> Dict[str, float]:
        """Get blendshapes for current module"""
        if not self.module_manager.current_module:
            return {}
        
        current_module = self.module_manager.current_module
        if current_module in self.module_manager.modules:
            return self.module_manager.modules[current_module].blendshapes.copy()
        
        return {}
    
    def get_module_exclusions(self) -> Dict[str, List[str]]:
        """Get internal exclusions for current module"""
        if not self.module_manager.current_module:
            return {}
        
        current_module = self.module_manager.current_module
        if current_module in self.module_manager.modules:
            # Convert sets to lists for UI consumption
            exclusions = self.module_manager.modules[current_module].exclusions
            return {bs_name: list(excluded_set) for bs_name, excluded_set in exclusions.items()}
        
        return {}
    
    def import_geometry_from_scene(self, maya_object_name: str) -> Tuple[bool, str]:
        """
        Import geometry from Maya scene to current module
        
        Args:
            maya_object_name: Name of Maya object to import
            
        Returns:
            Tuple of (success, message)
        """
        success, message = self.module_manager.import_geometry_from_scene(maya_object_name)
        
        if success:
            self._change_tracking['modules'] = True
        
        return success, message
    
    def load_geometry_to_scene(self, module_name: Optional[str] = None) -> Tuple[bool, str]:
        """
        Load module geometry into Maya scene
        
        Args:
            module_name: Module to load (uses current module if None)
            
        Returns:
            Tuple of (success, message)
        """
        return self.module_manager.load_geometry_to_scene(module_name)
    
    def add_blendshape_from_scene(self, maya_object_name: str, blendshape_name: Optional[str] = None) -> Tuple[bool, str]:
        """
        Add a blendshape from Maya scene to current module
        
        Args:
            maya_object_name: Name of Maya object to use as blendshape
            blendshape_name: Name for the blendshape (uses object name if None)
            
        Returns:
            Tuple of (success, message)
        """
        success, message = self.module_manager.add_blendshape_from_scene(maya_object_name, blendshape_name)
        
        if success:
            self._change_tracking['modules'] = True
        
        return success, message
    
    def remove_blendshape(self, blendshape_name: str) -> Tuple[bool, str]:
        """
        Remove a blendshape from current module
        
        Args:
            blendshape_name: Name of blendshape to remove
            
        Returns:
            Tuple of (success, message)
        """
        success, message = self.module_manager.remove_blendshape(blendshape_name)
        
        if success:
            self._change_tracking['modules'] = True
        
        return success, message
    
    def set_blendshape_weight(self, blendshape_name: str, weight: float) -> Tuple[bool, str]:
        """
        Set blendshape weight for preview in Maya
        
        Args:
            blendshape_name: Name of blendshape
            weight: Weight value (0.0 to 1.0)
            
        Returns:
            Tuple of (success, message)
        """
        return self.module_manager.set_blendshape_weight(blendshape_name, weight)
    
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
        success, message = self.module_manager.set_blendshape_exclusion(blendshape_name, excluded_blendshape, excluded)
        
        if success:
            self._change_tracking['modules'] = True
        
        return success, message
    
    def get_current_group(self) -> Optional[str]:
        """Get name of currently loaded group"""
        return self.group_manager.current_group
    
    def get_group_alpha_whitelist(self) -> Dict[str, bool]:
        """Get alpha whitelist for current group"""
        return self.group_manager.alpha_whitelist.copy()
    
    def get_available_alpha_textures(self) -> Dict[str, str]:
        """Get all available alpha textures"""
        return self.group_manager.get_available_alpha_textures()
    
    def update_alpha_whitelist(self, texture_path: str, enabled: bool) -> None:
        """
        Update alpha whitelist entry
        
        Args:
            texture_path: Path to texture
            enabled: Whether texture should be enabled
        """
        self.group_manager.update_alpha_whitelist(texture_path, enabled)
        self._change_tracking['group'] = True
    
    def add_alpha_texture_path(self, texture_path: str, enabled: bool = True) -> Tuple[bool, str]:
        """
        Add new alpha texture path
        
        Args:
            texture_path: Path to add
            enabled: Whether enabled by default
            
        Returns:
            Tuple of (success, message)
        """
        success, message = self.group_manager.add_alpha_texture_path(texture_path, enabled)
        
        if success:
            self._change_tracking['group'] = True
        
        return success, message
    
    def remove_alpha_texture_path(self, texture_path: str) -> Tuple[bool, str]:
        """
        Remove alpha texture path
        
        Args:
            texture_path: Path to remove
            
        Returns:
            Tuple of (success, message)
        """
        success, message = self.group_manager.remove_alpha_texture_path(texture_path)
        
        if success:
            self._change_tracking['group'] = True
        
        return success, message
    
    def has_unsaved_changes(self, category: Optional[str] = None) -> bool:
        """
        Check if there are unsaved changes
        
        Args:
            category: Specific category to check ('group', 'modules', 'styles')
                     If None, checks all categories
        
        Returns:
            True if there are unsaved changes
        """
        if category:
            return self._change_tracking.get(category, False)
        
        return any(self._change_tracking.values())
    
    def get_unsaved_categories(self) -> List[str]:
        """
        Get list of categories with unsaved changes
        
        Returns:
            List of category names with changes
        """
        return [category for category, has_changes in self._change_tracking.items() if has_changes]
    
    def validate_current_data(self) -> Tuple[bool, List[str]]:
        """
        Validate all current data
        
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        all_issues = []
        
        # Validate current group
        if self.group_manager.current_group:
            is_valid, group_issues = self.group_manager.validate_current_group()
            all_issues.extend(group_issues)
        
        # Validate current module
        if self.module_manager.current_module:
            is_valid, module_issues = self.module_manager.validate_current_module()
            all_issues.extend(module_issues)
        
        # TODO: Add style validation when style manager is implemented
        
        return len(all_issues) == 0, all_issues
    
    def get_status_summary(self) -> Dict[str, Any]:
        """
        Get summary of current data status
        
        Returns:
            Dictionary with status information
        """
        return {
            'current_group': self.get_current_group(),
            'current_module': self.get_current_module(),
            'available_groups': len(self.get_groups()),
            'available_modules': len(self.get_modules()),
            'unsaved_changes': self.get_unsaved_categories(),
            'usd_directory': str(config.usd_directory) if config.usd_directory else None,
            'has_changes': self.has_unsaved_changes()
        }