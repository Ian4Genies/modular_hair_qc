"""
Debug script to understand why modules aren't showing in the list
"""

import sys
from pathlib import Path

# Add hair_qc_tool to path
project_path = Path(__file__).parent
if str(project_path) not in sys.path:
    sys.path.insert(0, str(project_path))

def debug_module_listing():
    """Debug the module listing process step by step"""
    print("="*60)
    print("DEBUG: Module Listing Process")
    print("="*60)
    
    try:
        from hair_qc_tool.managers import DataManager
        from hair_qc_tool.config import config
        from hair_qc_tool.utils import USDGroupUtils
        
        # Check USD directory
        if not config.usd_directory:
            print("❌ No USD directory configured")
            return
        
        print(f"✅ USD directory: {config.usd_directory}")
        
        # Check if directories exist
        group_dir = config.usd_directory / "Group"
        module_dir = config.usd_directory / "module"
        
        print(f"✅ Group directory exists: {group_dir.exists()}")
        print(f"✅ Module directory exists: {module_dir.exists()}")
        
        # List actual files in directories
        if group_dir.exists():
            group_files = list(group_dir.glob("*.usd"))
            print(f"✅ Group files found: {[f.stem for f in group_files]}")
        
        if module_dir.exists():
            print(f"✅ Module subdirectories:")
            for subdir in ["scalp", "crown", "tail", "bang"]:
                subdir_path = module_dir / subdir
                if subdir_path.exists():
                    module_files = list(subdir_path.glob("*.usd"))
                    print(f"  - {subdir}: {[f.stem for f in module_files]}")
                else:
                    print(f"  - {subdir}: directory doesn't exist")
        
        # Create data manager and test group loading
        data_manager = DataManager()
        
        print(f"\n" + "="*40)
        print("TESTING GROUP OPERATIONS")
        print("="*40)
        
        # Get groups
        groups = data_manager.get_groups()
        print(f"✅ Available groups: {groups}")
        
        if not groups:
            print("❌ No groups found - this is the problem!")
            return
        
        # Load first group
        test_group = groups[0]
        print(f"\n🔍 Testing group: {test_group}")
        
        success, message = data_manager.load_group(test_group)
        print(f"✅ Load group result: {success} - {message}")
        
        if not success:
            print("❌ Failed to load group - this could be why modules don't show")
            return
        
        # Check group's module whitelist
        print(f"\n" + "="*40)
        print("CHECKING GROUP MODULE WHITELIST")
        print("="*40)
        
        group_file = config.usd_directory / "Group" / f"{test_group}.usd"
        print(f"✅ Group file: {group_file}")
        print(f"✅ Group file exists: {group_file.exists()}")
        
        if group_file.exists():
            try:
                group_utils = USDGroupUtils(group_file)
                module_whitelist = group_utils.get_module_whitelist()
                print(f"✅ Module whitelist from group: {module_whitelist}")
                
                if not module_whitelist:
                    print("❌ PROBLEM FOUND: Group has no module whitelist!")
                    print("   This is why no modules show up in the list.")
                    print("   New modules should be added to the group whitelist when created.")
                else:
                    print(f"✅ Group has {len(module_whitelist)} modules in whitelist")
            except Exception as e:
                print(f"❌ Error reading group module whitelist: {e}")
                import traceback
                traceback.print_exc()
        
        # Test getting available modules
        print(f"\n" + "="*40)
        print("TESTING MODULE LISTING")
        print("="*40)
        
        modules = data_manager.get_modules(force_refresh=True)
        print(f"✅ Available modules from DataManager: {modules}")
        
        # Test ModuleManager directly
        module_manager = data_manager.module_manager
        direct_modules = module_manager.get_available_modules()
        print(f"✅ Available modules from ModuleManager directly: {direct_modules}")
        
        if not modules and not direct_modules:
            print("❌ PROBLEM CONFIRMED: No modules found by either method!")
        
    except Exception as e:
        print(f"❌ Debug failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_module_listing()