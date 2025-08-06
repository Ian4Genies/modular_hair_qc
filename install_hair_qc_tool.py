"""
Installation script for Hair QC Tool

Run this script in Maya's Script Editor to install the Hair QC Tool.
Creates menu items, shelf buttons, and sets up the tool for use.
"""

import sys
from pathlib import Path

# Add hair_qc_tool to Python path
tool_path = Path(__file__).parent
if str(tool_path) not in sys.path:
    sys.path.insert(0, str(tool_path))

# Import and install
try:
    from hair_qc_tool.main import install_maya_menu, create_shelf_button
    from hair_qc_tool import launch_hair_qc_tool
    
    # Install menu and shelf button
    install_maya_menu()
    create_shelf_button()
    
    print("="*50)
    print("Hair QC Tool installed successfully!")
    print("="*50)
    print("• Menu: Hair QC > Open Hair QC Tool")
    print("• Shelf: Hair QC button added to current shelf")
    print("• Launch: hair_qc_tool.launch_hair_qc_tool()")
    print("="*50)
    
    # Optionally launch the tool immediately
    launch_result = input("Launch Hair QC Tool now? (y/n): ").lower().strip()
    if launch_result in ['y', 'yes']:
        launch_hair_qc_tool()
    
except Exception as e:
    print(f"Error installing Hair QC Tool: {e}")
    import traceback
    traceback.print_exc()