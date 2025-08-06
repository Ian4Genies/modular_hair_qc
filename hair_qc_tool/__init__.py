"""
Hair QC Tool - Maya Plugin for Modular Hair Quality Control

A comprehensive Maya tool for managing modular hair assets using USD-based data structures.
Supports group-based organization, cross-module blendshape rules, and automated QC workflows.
"""

__version__ = "1.0.0"
__author__ = "Hair QC Tool Development"

# Import main components for easy access (only when Maya is available)
try:
    import maya.cmds
    # Maya is available, import Maya-dependent components
    from .main import launch_hair_qc_tool
    MAYA_AVAILABLE = True
except ImportError:
    # Maya not available, define stub function
    def launch_hair_qc_tool():
        raise RuntimeError("Maya is required to launch the Hair QC Tool")
    MAYA_AVAILABLE = False

# Config is always available
from .config import HairQCConfig

# Maya plugin registration
def maya_useNewAPI():
    """Tell Maya to use the Maya Python API 2.0"""
    return True

def initializePlugin(plugin):
    """Initialize the Hair QC Tool plugin"""
    print("[Hair QC Tool] Plugin initialized successfully")
    return True

def uninitializePlugin(plugin):
    """Cleanup when plugin is unloaded"""
    print("[Hair QC Tool] Plugin unloaded")
    return True