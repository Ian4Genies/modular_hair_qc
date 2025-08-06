"""
Manager modules for Hair QC Tool

Provides high-level management interfaces for Groups, Modules, and Styles.
"""

from .group_manager import GroupManager
from .data_manager import DataManager

__all__ = ['GroupManager', 'DataManager']