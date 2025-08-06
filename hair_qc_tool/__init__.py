"""
Hair QC Tool - Maya Plugin for Modular Hair Quality Control

A comprehensive Maya tool for managing modular hair assets using USD-based data structures.
Supports group-based organization, cross-module blendshape rules, and automated QC workflows.
"""

__version__ = "1.0.0"
__author__ = "Hair QC Tool Development"

# Import main components for easy access
from .main import launch_hair_qc_tool
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