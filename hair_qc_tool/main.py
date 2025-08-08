"""
Main entry point for Hair QC Tool

Handles Maya integration, UI launching, and tool lifecycle management.
"""

import maya.cmds as cmds
import maya.mel as mel
from PySide2 import QtWidgets
import sys
import traceback
from .utils.logging_utils import get_logger

from .ui.main_window import HairQCMainWindow
from .config import config
from .utils.maya_utils import MayaUtils


class HairQCTool:
    """Main Hair QC Tool controller"""
    
    def __init__(self):
        self.main_window = None
        self.maya_utils = MayaUtils()
        self._log = get_logger(__name__)
    
    def launch(self):
        """Launch the Hair QC Tool UI"""
        try:
            # Check if tool is already open
            if self.main_window and self.main_window.isVisible():
                self.main_window.raise_()
                self.main_window.activateWindow()
                return
            
            # Validate configuration
            validation_result, message = config.validate_usd_directory()
            if validation_result == "empty":
                self._show_initialization_dialog(message)
                return
            elif not validation_result:
                self._show_setup_dialog(message)
                return
            
            # Create and show main window
            self.main_window = HairQCMainWindow()
            self.main_window.show()
            
            self._log.info("Tool launched successfully")
            
        except Exception as e:
            error_msg = f"Failed to launch Hair QC Tool: {str(e)}"
            self._log.exception(error_msg)
            
            # Show error dialog
            cmds.confirmDialog(
                title="Hair QC Tool Error",
                message=error_msg,
                button=["OK"],
                defaultButton="OK"
            )
    
    def _show_setup_dialog(self, message):
        """Show setup dialog for first-time configuration"""
        result = cmds.confirmDialog(
            title="Hair QC Tool Setup",
            message=f"Setup required: {message}\n\nWould you like to configure the USD directory?",
            button=["Browse for Directory", "Cancel"],
            defaultButton="Browse for Directory",
            cancelButton="Cancel"
        )
        
        if result == "Browse for Directory":
            self._browse_usd_directory()
    
    def _show_initialization_dialog(self, message):
        """Show initialization dialog for empty directories"""
        result = cmds.confirmDialog(
            title="Initialize USD Directory",
            message=f"{message}\n\nThis will create:\n• Group/, module/, style/ directories\n• Sample group files (short.usd, long.usd)\n• Required subdirectory structure\n• README documentation",
            button=["Initialize Directory", "Browse for Different Directory", "Cancel"],
            defaultButton="Initialize Directory",
            cancelButton="Cancel"
        )
        
        if result == "Initialize Directory":
            self._initialize_current_directory()
        elif result == "Browse for Different Directory":
            self._browse_usd_directory()
    
    def _initialize_current_directory(self):
        """Initialize the current USD directory"""
        success, message = config.initialize_usd_directory()
        
        if success:
            cmds.confirmDialog(
                title="Success",
                message=f"USD directory initialized successfully!\n\n{message}\n\nThe Hair QC Tool will now launch.",
                button=["OK"]
            )
            # Launch the tool after successful initialization
            self.launch()
        else:
            cmds.confirmDialog(
                title="Initialization Failed",
                message=f"Failed to initialize USD directory:\n\n{message}",
                button=["OK"]
            )
    
    def _browse_usd_directory(self):
        """Open file browser to select USD directory"""
        directory = cmds.fileDialog2(
            caption="Select USD Directory",
            fileMode=3,  # Directory mode
            okCaption="Select"
        )
        
        if directory:
            config.usd_directory = directory[0]
            print(f"[Hair QC Tool] USD directory set to: {config.usd_directory}")
            
            # Validate and launch if valid
            validation_result, message = config.validate_usd_directory()
            if validation_result == True:
                self.launch()
            elif validation_result == "empty":
                self._show_initialization_dialog(message)
            else:
                cmds.confirmDialog(
                    title="Invalid Directory",
                    message=f"Selected directory is not valid: {message}",
                    button=["OK"]
                )


# Global tool instance
_hair_qc_tool = None


def launch_hair_qc_tool():
    """Public function to launch Hair QC Tool"""
    global _hair_qc_tool
    
    if _hair_qc_tool is None:
        _hair_qc_tool = HairQCTool()
    
    _hair_qc_tool.launch()


def install_maya_menu():
    """Install Hair QC Tool in Maya's main menu bar"""
    try:
        # Remove existing menu if it exists
        if cmds.menu("HairQCMenu", exists=True):
            cmds.deleteUI("HairQCMenu", menu=True)
        
        # Create main menu
        main_menu = cmds.menu(
            "HairQCMenu",
            label="Hair QC",
            parent=mel.eval("$temp = $gMainWindow"),
            tearOff=True
        )
        
        # Add menu items
        cmds.menuItem(
            label="Open Hair QC Tool",
            command=lambda x: launch_hair_qc_tool(),
            annotation="Launch the Hair QC Tool",
            parent=main_menu
        )
        
        cmds.menuItem(divider=True, parent=main_menu)
        
        cmds.menuItem(
            label="Refresh Data",
            command=lambda x: refresh_tool_data(),
            annotation="Refresh USD data (F5)",
            parent=main_menu
        )
        
        cmds.menuItem(
            label="Settings",
            command=lambda x: show_settings_dialog(),
            annotation="Open Hair QC Tool settings",
            parent=main_menu
        )
        
        get_logger(__name__).info("Menu installed successfully")
        
    except Exception as e:
        get_logger(__name__).error(f"Error installing menu: {e}")


def create_shelf_button():
    """Create Hair QC Tool shelf button"""
    try:
        # Get current shelf using proper MEL evaluation
        shelf_top_level = mel.eval('$tempVar = $gShelfTopLevel')
        current_shelf = cmds.tabLayout(shelf_top_level, query=True, selectTab=True)
        
        # Create shelf button
        cmds.shelfButton(
            command="from hair_qc_tool import launch_hair_qc_tool; launch_hair_qc_tool()",
            annotation="Launch Hair QC Tool",
            label="Hair QC",
            image="polyCreateFacet.png",  # Default Maya icon, can be customized
            parent=current_shelf
        )
        
        get_logger(__name__).info("Shelf button created successfully")
        
    except Exception as e:
        get_logger(__name__).error(f"Error creating shelf button: {e}")


def refresh_tool_data():
    """Refresh tool data - called by F5 shortcut"""
    global _hair_qc_tool
    if _hair_qc_tool and _hair_qc_tool.main_window:
        _hair_qc_tool.main_window.refresh_data()
    else:
        get_logger(__name__).warning("No active tool window to refresh")


def show_settings_dialog():
    """Show settings dialog"""
    # TODO: Implement settings dialog
    cmds.confirmDialog(
        title="Settings",
        message="Settings dialog not yet implemented",
        button=["OK"]
    )