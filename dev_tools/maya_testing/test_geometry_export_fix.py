#!/usr/bin/env python3
"""
Test script to verify geometry export fix
Run this in Maya after loading a module with geometry
"""

def test_geometry_export_fix():
    """Test if geometry export to Maya viewport works"""
    
    print("="*60)
    print("TESTING GEOMETRY EXPORT FIX")
    print("="*60)
    
    try:
        from hair_qc_tool.managers.data_manager import DataManager
        from hair_qc_tool.managers import get_directory_manager
        from pathlib import Path
        
        # Test file with known geometry
        test_file = Path("docs/TestDirectory/module/crown/Test_GEO.usd")
        
        if not test_file.exists():
            print(f"Test file not found: {test_file}")
            return False
        
        print(f"Testing with: {test_file}")
        
        # Create data manager and load module
        directory_manager = get_directory_manager()
        data_manager = DataManager(directory_manager)
        
        # Load the group first
        success, message = data_manager.load_group("long")
        if not success:
            print(f"Failed to load group: {message}")
            return False
        
        print("✓ Loaded group")
        
        # Load the module
        success, message = data_manager.load_module("Test_GEO")
        if not success:
            print(f"Failed to load module: {message}")
            return False
        
        print("✓ Loaded module")
        
        # Check if module has geometry
        module_info = data_manager.get_current_module_info()
        print(f"Module info: {module_info}")
        
        if not module_info or not module_info.get('has_geometry', False):
            print("Module has no geometry - cannot test export")
            return False
        
        print("✓ Module has geometry")
        
        # Test geometry export to Maya
        print("Testing geometry export to Maya...")
        success, message = data_manager.load_geometry_to_scene()
        
        if success:
            print("✓ SUCCESS: Geometry exported to Maya successfully!")
            print(f"Message: {message}")
            return True
        else:
            print(f"✗ FAILED: Geometry export failed: {message}")
            return False
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_geometry_export_fix()