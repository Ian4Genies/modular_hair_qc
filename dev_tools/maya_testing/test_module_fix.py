"""
Test script to verify the module directory structure fix
"""

import sys
from pathlib import Path

# Add hair_qc_tool to path
project_path = Path(__file__).parent
if str(project_path) not in sys.path:
    sys.path.insert(0, str(project_path))

def test_module_directory_structure():
    """Test that modules are created in correct subdirectories"""
    print("Testing Module Directory Structure Fix...")
    
    try:
        from hair_qc_tool.managers import DataManager
        from hair_qc_tool.config import config
        
        # Check if we have a USD directory configured
        if not config.usd_directory:
            print("❌ No USD directory configured")
            return False
        
        print(f"✅ USD directory: {config.usd_directory}")
        
        # Create data manager
        data_manager = DataManager()
        
        # Load a group first
        groups = data_manager.get_groups()
        if not groups:
            print("❌ No groups available")
            return False
        
        test_group = groups[0]
        success, message = data_manager.load_group(test_group)
        print(f"✅ Loaded group '{test_group}': {success}")
        
        if not success:
            print(f"❌ Failed to load group: {message}")
            return False
        
        # Test creating a module in each type directory
        import time
        timestamp = int(time.time())
        
        for module_type in ["scalp", "crown", "tail", "bang"]:
            test_module_name = f"test_{module_type}_{timestamp}"
            
            print(f"\nTesting {module_type} module creation...")
            success, message = data_manager.create_module(test_module_name, module_type)
            
            if success:
                print(f"✅ Created {module_type} module: {test_module_name}")
                
                # Check if file was created in correct location
                expected_path = config.usd_directory / "module" / module_type / f"{test_module_name}.usd"
                if expected_path.exists():
                    print(f"✅ File created in correct location: {expected_path}")
                else:
                    print(f"❌ File not found at expected location: {expected_path}")
                    return False
                
                # Test loading the module
                success, message = data_manager.load_module(test_module_name)
                if success:
                    print(f"✅ Successfully loaded module: {test_module_name}")
                else:
                    print(f"❌ Failed to load module: {message}")
                    return False
            else:
                print(f"❌ Failed to create {module_type} module: {message}")
                return False
        
        # Test getting available modules
        print(f"\nTesting module listing...")
        modules = data_manager.get_modules(force_refresh=True)
        print(f"✅ Found {len(modules)} modules total")
        
        # Check if our test modules appear in the list
        test_modules_found = 0
        for module_type in ["scalp", "crown", "tail", "bang"]:
            test_module_name = f"test_{module_type}_{timestamp}"
            if test_module_name in modules:
                test_modules_found += 1
                print(f"✅ Test module '{test_module_name}' found in list")
            else:
                print(f"❌ Test module '{test_module_name}' NOT found in list")
        
        if test_modules_found == 4:
            print(f"✅ All 4 test modules found in module list")
            return True
        else:
            print(f"❌ Only {test_modules_found}/4 test modules found in list")
            return False
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("="*60)
    print("Module Directory Structure Fix Test")
    print("="*60)
    
    success = test_module_directory_structure()
    
    print("\n" + "="*60)
    if success:
        print("🎉 Module directory structure fix test PASSED!")
        print("\nThe fix should resolve:")
        print("✅ Modules created in correct type subdirectories (module/type/)")
        print("✅ Modules appearing in the module list after creation")
        print("✅ Module loading from correct subdirectory locations")
    else:
        print("❌ Module directory structure fix test FAILED!")
        print("Check the error messages above for details.")