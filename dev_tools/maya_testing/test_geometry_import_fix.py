#!/usr/bin/env python3
"""
Test script for the geometry import fix
Run this in Maya with a sphere selected
"""

def test_geometry_import_fix():
    """Test the fixed geometry import"""
    
    print("="*60)
    print("TESTING GEOMETRY IMPORT FIX")
    print("="*60)
    
    try:
        import maya.cmds as cmds
        from hair_qc_tool.utils.usd_utils import USDModuleUtils
        from pathlib import Path
        
        # Check selection
        selected = cmds.ls(selection=True)
        if not selected:
            print("ERROR: Please select a mesh object first")
            return False
        
        mesh_name = selected[0]
        print(f"Testing with: {mesh_name}")
        
        # Create a test module file
        test_module_path = Path.cwd() / "test_module.usd"
        print(f"Test module path: {test_module_path}")
        
        # Create module structure
        module_utils = USDModuleUtils(test_module_path)
        success = module_utils.create_module_structure("test_module", "scalp")
        
        if not success:
            print("Failed to create test module structure")
            return False
        
        print("✓ Created test module structure")
        
        # Test geometry import
        print(f"\nImporting geometry from '{mesh_name}'...")
        success = module_utils.import_geometry_from_maya(mesh_name)
        
        if success:
            print("✓ Geometry import successful!")
            
            # Test geometry detection
            has_geometry = module_utils.has_geometry_data()
            print(f"Has geometry data: {has_geometry}")
            
            # Get module info
            module_info = module_utils.get_module_info()
            print(f"Module info: {module_info}")
            
            # Clean up
            test_module_path.unlink(missing_ok=True)
            print("✓ Test completed successfully")
            return True
        else:
            print("✗ Geometry import failed")
            test_module_path.unlink(missing_ok=True)
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_geometry_import_fix()