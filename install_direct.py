"""
Hair QC Tool Installation Script

Run this script in Maya's Script Editor (Python tab) to install the Hair QC Tool.
The script will automatically detect the project location and install the tool.

Usage:
exec(open(r'C:\path\to\your\project\install_direct.py').read())
"""

import sys
import os
from pathlib import Path

# Try to auto-detect project path from script location
def get_project_path():
    """Auto-detect project path from various sources"""
    # Try to get from execution context
    import inspect
    try:
        frame = inspect.currentframe()
        if frame and frame.f_back:
            # Look for globals that might contain file path info
            caller_globals = frame.f_back.f_globals
            if '__file__' in caller_globals:
                script_path = Path(caller_globals['__file__']).parent
                if (script_path / "hair_qc_tool").exists():
                    return script_path
    except:
        pass
    
    # Fallback: try common locations
    possible_paths = [
        Path(r'C:\Users\woske\Documents\GitRepo\modular_hair_qc'),
        Path(os.getcwd()),
        Path(os.getcwd()).parent,
    ]
    
    # Add Maya scripts directory
    try:
        import maya.cmds as cmds
        scripts_dir = Path(cmds.internalVar(userScriptDir=True))
        possible_paths.append(scripts_dir)
    except:
        pass
    
    # Find the first path that contains hair_qc_tool
    for path in possible_paths:
        if path.exists() and (path / "hair_qc_tool").exists():
            return path
    
    return None

def install_hair_qc_tool():
    """Install Hair QC Tool with automatic path detection"""
    
    print("="*60)
    print("Hair QC Tool Installation")
    print("="*60)
    
    # Auto-detect project path
    project_path = get_project_path()
    
    if not project_path:
        print("[ERROR] Could not find hair_qc_tool directory!")
        print("\nSearched in:")
        print("  - Current working directory")
        print("  - Parent directories") 
        print("  - Maya scripts directory")
        print("  - Default project location")
        print("\nPlease ensure the hair_qc_tool folder exists in one of these locations.")
        return False
    
    print(f"[SUCCESS] Found hair_qc_tool at: {project_path}")
    
    # Add to Python path
    if str(project_path) not in sys.path:
        sys.path.insert(0, str(project_path))
        print(f"[SUCCESS] Added to Python path: {project_path}")
    else:
        print(f"[INFO] Already in Python path: {project_path}")
    
    try:
        # Reload modules if they were previously imported to get latest changes
        print("[INFO] Importing Hair QC Tool modules...")
        
        # Check if modules are already imported and reload them
        if 'hair_qc_tool' in sys.modules:
            print("[INFO] Reloading existing modules to get latest changes...")
            import importlib
            
            # Reload in dependency order (from leaf modules to root)
            modules_to_reload = [
                'hair_qc_tool.config',
                'hair_qc_tool.utils.usd_utils',
                'hair_qc_tool.utils.rules_utils',
                'hair_qc_tool.utils.file_utils',
                'hair_qc_tool.utils.maya_utils',
                'hair_qc_tool.utils',
                'hair_qc_tool.managers.group_manager',
                'hair_qc_tool.managers.data_manager',
                'hair_qc_tool.managers',
                'hair_qc_tool.ui.main_window',
                'hair_qc_tool.ui',
                'hair_qc_tool.main',
                'hair_qc_tool'
            ]
            
            for module_name in modules_to_reload:
                if module_name in sys.modules:
                    importlib.reload(sys.modules[module_name])
        
        from hair_qc_tool.main import install_maya_menu, create_shelf_button
        from hair_qc_tool import launch_hair_qc_tool
        
        print("[SUCCESS] Modules imported successfully")
        
        # Install menu and shelf button
        print("[INFO] Installing Maya menu...")
        install_maya_menu()
        
        print("[INFO] Creating shelf button...")
        create_shelf_button()
        
        print("="*60)
        print("Hair QC Tool installed successfully!")
        print("="*60)
        print("Available options:")
        print("  - Menu: Hair QC > Open Hair QC Tool")
        print("  - Shelf: Hair QC button added to current shelf")
        print("  - Command: launch_hair_qc_tool()")
        print("="*60)
        
        # Launch the tool with new directory initialization features
        import maya.cmds as cmds
        result = cmds.confirmDialog(
            title="Hair QC Tool Installed",
            message="Hair QC Tool installed successfully!\n\nThe tool now includes automatic USD directory initialization.\n\nWould you like to launch it now?",
            button=["Launch Tool", "Later"],
            defaultButton="Launch Tool"
        )
        
        if result == "Launch Tool":
            print("[INFO] Launching Hair QC Tool...")
            launch_hair_qc_tool()
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error installing Hair QC Tool: {e}")
        import traceback
        traceback.print_exc()
        
        # Show error dialog
        try:
            import maya.cmds as cmds
            cmds.confirmDialog(
                title="Installation Error",
                message=f"Failed to install Hair QC Tool:\n\n{str(e)}\n\nCheck the Script Editor for details.",
                button=["OK"]
            )
        except:
            pass
        
        return False

# Run the installation
if __name__ == "__main__":
    install_hair_qc_tool()
else:
    # When executed with exec(), run immediately
    install_hair_qc_tool()