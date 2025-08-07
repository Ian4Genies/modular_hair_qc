"""
Test creating a module and adding it to a group whitelist
"""

import sys
from pathlib import Path

# Add hair_qc_tool to path
project_path = Path(__file__).parent
if str(project_path) not in sys.path:
    sys.path.insert(0, str(project_path))

def test_create_module():
    """Test creating a module without Maya dependencies"""
    print("="*60)
    print("TEST: Create Module and Add to Group")
    print("="*60)
    
    try:
        from hair_qc_tool.config import config
        from hair_qc_tool.utils import USDGroupUtils, create_module_file
        import time
        
        # Check USD directory
        if not config.usd_directory:
            print("❌ No USD directory configured")
            return
        
        print(f"✅ USD directory: {config.usd_directory}")
        
        # Get first available group
        group_dir = config.usd_directory / "Group"
        group_files = list(group_dir.glob("*.usd"))
        
        if not group_files:
            print("❌ No groups available")
            return
        
        test_group = group_files[0].stem
        print(f"✅ Using test group: {test_group}")
        
        # Create a test module
        timestamp = int(time.time())
        module_name = f"test_module_{timestamp}"
        module_type = "crown"
        
        print(f"✅ Creating module: {module_name} (type: {module_type})")
        
        # Create module directory
        module_type_dir = config.usd_directory / "module" / module_type
        module_type_dir.mkdir(parents=True, exist_ok=True)
        
        # Create module file
        module_file = module_type_dir / f"{module_name}.usd"
        success = create_module_file(module_file, module_name, module_type)
        
        if success:
            print(f"✅ Module file created: {module_file}")
        else:
            print(f"❌ Failed to create module file")
            return
        
        # Add module to group whitelist
        print(f"✅ Adding module to group '{test_group}' whitelist...")
        
        group_file = group_dir / f"{test_group}.usd"
        group_utils = USDGroupUtils(group_file)
        
        # Get existing whitelist
        module_whitelist = group_utils.get_module_whitelist() or {}
        print(f"✅ Existing whitelist: {module_whitelist}")
        
        # Add new module
        module_whitelist[module_name] = {"type": module_type, "enabled": True}
        print(f"✅ Updated whitelist: {module_whitelist}")
        
        # Save back to group
        group_utils.set_module_whitelist(module_whitelist)
        group_utils.save_stage()
        
        print(f"✅ Module added to group whitelist")
        
        # Verify by reading back
        print(f"✅ Verifying by reading back...")
        group_utils_verify = USDGroupUtils(group_file)
        verify_whitelist = group_utils_verify.get_module_whitelist()
        print(f"✅ Verified whitelist: {verify_whitelist}")
        
        if module_name in verify_whitelist:
            print(f"🎉 SUCCESS: Module '{module_name}' is now in group '{test_group}' whitelist!")
            print(f"   This module should now appear in the UI module list when '{test_group}' is selected.")
        else:
            print(f"❌ FAILED: Module not found in verified whitelist")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_create_module()