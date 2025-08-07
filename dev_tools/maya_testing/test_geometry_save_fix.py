#!/usr/bin/env python3
"""
Test the geometry save fix
Run this in Maya with a sphere selected
"""

def test_geometry_save_fix():
    """Test if geometry saves correctly to USD"""
    
    print("="*60)
    print("TESTING GEOMETRY SAVE FIX")
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
        
        # Create a test USD file
        test_file = Path.cwd() / "test_geometry_save.usd"
        print(f"Test file: {test_file}")
        
        # Clean up any existing file
        if test_file.exists():
            test_file.unlink()
        
        # Create module utils and structure
        module_utils = USDModuleUtils(test_file)
        success = module_utils.create_module_structure("test_save", "scalp")
        
        if not success:
            print("Failed to create module structure")
            return False
        
        print("✓ Created module structure")
        
        # Import geometry
        print(f"Importing geometry from '{mesh_name}'...")
        import_success = module_utils.import_geometry_from_maya(mesh_name)
        
        print(f"Import result: {import_success}")
        
        if import_success:
            # Test if data persists by creating a new instance
            print("Testing persistence with new module utils instance...")
            module_utils2 = USDModuleUtils(test_file)
            
            has_geometry = module_utils2.has_geometry_data()
            print(f"Has geometry after reload: {has_geometry}")
            
            module_info = module_utils2.get_module_info()
            print(f"Module info: {module_info}")
            
            if has_geometry:
                print("✓ SUCCESS: Geometry data persisted correctly!")
                # Clean up
                test_file.unlink()
                return True
            else:
                print("✗ FAILED: Geometry data did not persist")
                # Keep file for inspection
                return False
        else:
            print("✗ FAILED: Geometry import failed")
            return False
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_geometry_save_fix()