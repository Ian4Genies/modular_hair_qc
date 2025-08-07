"""
Simplified debug script to test module listing without Maya
"""

import sys
from pathlib import Path

# Add hair_qc_tool to path
project_path = Path(__file__).parent
if str(project_path) not in sys.path:
    sys.path.insert(0, str(project_path))

def debug_module_listing_simple():
    """Debug the module listing process without Maya dependencies"""
    print("="*60)
    print("DEBUG: Module Listing (No Maya)")
    print("="*60)
    
    try:
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
        
        # Test group module whitelist reading
        print(f"\n" + "="*40)
        print("CHECKING GROUP MODULE WHITELISTS")
        print("="*40)
        
        if group_dir.exists():
            for group_file in group_dir.glob("*.usd"):
                group_name = group_file.stem
                print(f"\n🔍 Testing group: {group_name}")
                print(f"✅ Group file: {group_file}")
                
                try:
                    group_utils = USDGroupUtils(group_file)
                    module_whitelist = group_utils.get_module_whitelist()
                    print(f"✅ Module whitelist: {module_whitelist}")
                    
                    if not module_whitelist:
                        print("❌ PROBLEM: Group has empty module whitelist!")
                    else:
                        print(f"✅ Group has {len(module_whitelist)} modules in whitelist")
                        for mod_name, mod_info in module_whitelist.items():
                            print(f"  - {mod_name}: {mod_info}")
                            
                except Exception as e:
                    print(f"❌ Error reading group {group_name}: {e}")
                    import traceback
                    traceback.print_exc()
        
    except Exception as e:
        print(f"❌ Debug failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_module_listing_simple()