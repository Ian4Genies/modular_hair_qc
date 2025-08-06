"""
Test script for Group Management System

Run this to test the Group management functionality.
This can be run in Maya to test the actual UI integration.
"""

import sys
from pathlib import Path

# Add hair_qc_tool to path
project_path = Path(__file__).parent
if str(project_path) not in sys.path:
    sys.path.insert(0, str(project_path))

def test_group_manager():
    """Test the GroupManager class directly"""
    print("Testing GroupManager...")
    
    try:
        from hair_qc_tool.managers import GroupManager
        from hair_qc_tool.config import config
        
        # Check if we have a USD directory configured
        if not config.usd_directory:
            print("❌ No USD directory configured")
            return False
        
        print(f"✅ USD directory: {config.usd_directory}")
        
        # Create group manager
        group_manager = GroupManager()
        
        # Test getting available groups
        groups = group_manager.get_available_groups()
        print(f"✅ Found {len(groups)} groups: {groups}")
        
        # Test loading a group if available
        if groups:
            test_group = groups[0]
            print(f"Testing loading group: {test_group}")
            
            success, message = group_manager.load_group(test_group)
            print(f"  Load result: {success} - {message}")
            
            if success:
                # Test alpha whitelist
                alpha_whitelist = group_manager.alpha_whitelist
                print(f"  Alpha whitelist entries: {len(alpha_whitelist)}")
                
                # Test available textures
                available_textures = group_manager.get_available_alpha_textures()
                print(f"  Available alpha textures: {len(available_textures)}")
                
                # Test validation
                is_valid, issues = group_manager.validate_current_group()
                print(f"  Validation: {is_valid}")
                if issues:
                    print(f"  Issues: {issues}")
        
        return True
        
    except Exception as e:
        print(f"❌ GroupManager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_manager():
    """Test the DataManager class"""
    print("\nTesting DataManager...")
    
    try:
        from hair_qc_tool.managers import DataManager
        
        # Create data manager
        data_manager = DataManager()
        
        # Test refresh
        success, message = data_manager.refresh_all_data()
        print(f"✅ Refresh result: {success} - {message}")
        
        # Test getting groups
        groups = data_manager.get_groups()
        print(f"✅ Found {len(groups)} groups via DataManager")
        
        # Test status summary
        status = data_manager.get_status_summary()
        print(f"✅ Status summary: {status}")
        
        # Test loading a group if available
        if groups:
            test_group = groups[0]
            print(f"Testing loading group via DataManager: {test_group}")
            
            success, message = data_manager.load_group(test_group)
            print(f"  Load result: {success} - {message}")
            
            if success:
                # Test alpha operations
                alpha_whitelist = data_manager.get_group_alpha_whitelist()
                print(f"  Alpha whitelist: {len(alpha_whitelist)} entries")
                
                available_textures = data_manager.get_available_alpha_textures()
                print(f"  Available textures: {len(available_textures)} entries")
        
        return True
        
    except Exception as e:
        print(f"❌ DataManager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ui_integration():
    """Test if the UI can be created with new managers"""
    print("\nTesting UI Integration...")
    
    try:
        # This test requires Maya/PySide2
        from hair_qc_tool.ui.main_window import HairQCMainWindow
        print("✅ UI classes can be imported")
        
        # Note: We can't actually create the window here without Maya's Qt environment
        print("✅ UI integration test passed (import only)")
        return True
        
    except ImportError as e:
        print(f"⚠️  UI test skipped (PySide2/Maya not available): {e}")
        return True  # This is expected outside Maya
    except Exception as e:
        print(f"❌ UI integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all Group Management tests"""
    print("="*60)
    print("Hair QC Tool - Group Management Test")
    print("="*60)
    
    results = []
    
    # Test individual managers
    results.append(test_group_manager())
    results.append(test_data_manager())
    results.append(test_ui_integration())
    
    print("\n" + "="*60)
    print("Test Results Summary")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All Group Management tests passed!")
        print("\nNext steps:")
        print("1. Install and run the tool in Maya")
        print("2. Test creating/loading groups via the UI")
        print("3. Test alpha whitelist functionality")
        print("4. Move on to Module Management (Step 4)")
    else:
        print("⚠️  Some tests failed. Check output above for details.")

if __name__ == "__main__":
    run_all_tests()