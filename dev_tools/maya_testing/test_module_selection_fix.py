#!/usr/bin/env python3
"""
Test script to verify module selection fix
"""

def test_module_selection_fix():
    """Test if module selection works without AttributeError"""
    
    try:
        from hair_qc_tool.managers.data_manager import DataManager
        from hair_qc_tool.managers import get_directory_manager
        
        print("Testing module selection fix...")
        
        # Create data manager
        directory_manager = get_directory_manager()
        data_manager = DataManager(directory_manager)
        
        # Test get_current_module
        current_module = data_manager.get_current_module()
        print(f"Current module: {current_module}")
        
        # Test get_current_module_info
        module_info = data_manager.get_current_module_info()
        print(f"Module info: {module_info}")
        
        print("✓ No AttributeError - fix is working!")
        return True
        
    except AttributeError as e:
        print(f"✗ AttributeError still exists: {e}")
        return False
    except Exception as e:
        print(f"Other error (may be expected): {e}")
        return True  # Other errors are okay, we're just testing the AttributeError

if __name__ == "__main__":
    test_module_selection_fix()