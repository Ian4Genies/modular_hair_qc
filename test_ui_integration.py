"""
Test if the UI integration is working with the new module management
"""

import sys
from pathlib import Path

# Add hair_qc_tool to path
project_path = Path(__file__).parent
if str(project_path) not in sys.path:
    sys.path.insert(0, str(project_path))

def test_ui_integration():
    """Test the UI integration without Maya"""
    print("="*60)
    print("TEST: UI Integration (Module Management)")
    print("="*60)
    
    try:
        # Test that we can import and create the data manager
        from hair_qc_tool.managers import DataManager
        from hair_qc_tool.config import config
        
        print(f"✅ USD directory: {config.usd_directory}")
        
        # Create data manager (like the UI does)
        data_manager = DataManager()
        print("✅ DataManager created")
        
        # Test loading a group (like the UI does)
        groups = data_manager.get_groups()
        print(f"✅ Available groups: {groups}")
        
        if groups:
            test_group = groups[0]
            print(f"✅ Loading group: {test_group}")
            
            success, message = data_manager.load_group(test_group)
            print(f"✅ Load group result: {success} - {message}")
            
            if success:
                # Test getting modules (like the UI does)
                modules = data_manager.get_modules(force_refresh=True)
                print(f"✅ Available modules: {modules}")
                
                # Test creating a module (like the UI does)
                import time
                test_module_name = f"ui_test_module_{int(time.time())}"
                test_module_type = "tail"
                
                print(f"✅ Creating module: {test_module_name} (type: {test_module_type})")
                success, message = data_manager.create_module(test_module_name, test_module_type)
                print(f"✅ Create module result: {success} - {message}")
                
                if success:
                    # Test getting modules again (like UI refresh)
                    modules_after = data_manager.get_modules(force_refresh=True)
                    print(f"✅ Modules after creation: {modules_after}")
                    
                    if test_module_name in modules_after:
                        print(f"🎉 SUCCESS: Module '{test_module_name}' appears in module list!")
                        
                        # Check if file was created in correct location
                        expected_path = config.usd_directory / "module" / test_module_type / f"{test_module_name}.usd"
                        print(f"✅ Expected file location: {expected_path}")
                        print(f"✅ File exists: {expected_path.exists()}")
                        
                    else:
                        print(f"❌ PROBLEM: Module '{test_module_name}' NOT in module list!")
                        print("   This means the UI won't show the created module.")
                else:
                    print(f"❌ Module creation failed: {message}")
            else:
                print(f"❌ Group loading failed: {message}")
        else:
            print("❌ No groups available")
    
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ui_integration()