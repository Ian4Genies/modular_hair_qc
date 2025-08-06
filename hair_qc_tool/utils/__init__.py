"""
Utility modules for Hair QC Tool

Contains reusable utility classes and functions for USD operations,
Maya integration, and data management.
"""

# Import main utility classes for easy access
from .usd_utils import (
    USDGroupUtils, USDModuleUtils, USDStyleUtils, USDValidationUtils,
    create_group_file, create_module_file, create_style_file
)

from .rules_utils import (
    BlendshapeRule, BlendshapeRulesManager, CombinationGenerator,
    ConstraintType
)

from .file_utils import (
    USDDirectoryManager, StyleCombinationGenerator,
    get_directory_manager, validate_usd_directory_structure
)

# Maya utils - only import if Maya is available
try:
    from .maya_utils import MayaUtils
    MAYA_UTILS_AVAILABLE = True
except ImportError:
    # Maya not available, create stub class
    class MayaUtils:
        @staticmethod
        def is_maya_available():
            return False
    MAYA_UTILS_AVAILABLE = False

__all__ = [
    # USD utilities
    'USDGroupUtils', 'USDModuleUtils', 'USDStyleUtils', 'USDValidationUtils',
    'create_group_file', 'create_module_file', 'create_style_file',
    
    # Rules and constraints
    'BlendshapeRule', 'BlendshapeRulesManager', 'CombinationGenerator',
    'ConstraintType',
    
    # File management
    'USDDirectoryManager', 'StyleCombinationGenerator',
    'get_directory_manager', 'validate_usd_directory_structure',
    
    # Maya integration
    'MayaUtils'
]