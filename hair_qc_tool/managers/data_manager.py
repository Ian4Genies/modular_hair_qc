"""
Data Manager

Coordinates between Group, Module, and Style managers.
Provides a unified interface for the UI to interact with USD data.
"""

from typing import Optional, List, Dict, Tuple, Any
from pathlib import Path

from ..config import config
from .group_manager import GroupManager


class DataManager:
    """
    Unified data management interface
    
    Coordinates between different managers and provides caching,
    change tracking, and unified operations.
    """
    
    def __init__(self):
        self.group_manager = GroupManager()
        self._change_tracking: Dict[str, bool] = {
            'group': False,
            'modules': False,
            'styles': False
        }
        
        # Cache for UI data
        self._cached_groups: Optional[List[str]] = None
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
        
        # TODO: Add module and style validation when those managers are implemented
        
        return len(all_issues) == 0, all_issues
    
    def get_status_summary(self) -> Dict[str, Any]:
        """
        Get summary of current data status
        
        Returns:
            Dictionary with status information
        """
        return {
            'current_group': self.get_current_group(),
            'available_groups': len(self.get_groups()),
            'unsaved_changes': self.get_unsaved_categories(),
            'usd_directory': str(config.usd_directory) if config.usd_directory else None,
            'has_changes': self.has_unsaved_changes()
        }