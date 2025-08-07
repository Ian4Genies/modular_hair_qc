"""
Check if the code changes are properly saved by inspecting the source files
"""

import sys
from pathlib import Path

# Add hair_qc_tool to path
project_path = Path(__file__).parent
if str(project_path) not in sys.path:
    sys.path.insert(0, str(project_path))

def check_code_changes():
    """Check if the key fixes are in the source files"""
    print("="*60)
    print("CHECK: Code Changes in Source Files")
    print("="*60)
    
    # Check 1: USDGroupUtils get_module_whitelist method
    print("🔍 Checking USDGroupUtils.get_module_whitelist...")
    usd_utils_file = Path("hair_qc_tool/utils/usd_utils.py")
    
    if usd_utils_file.exists():
        with open(usd_utils_file, 'r') as f:
            content = f.read()
            
        # Check if the new method signature exists
        if "def get_module_whitelist(self, module_type: str = None)" in content:
            print("✅ get_module_whitelist has optional module_type parameter")
        else:
            print("❌ get_module_whitelist still has old signature")
            
        # Check if it returns Dict
        if "-> Dict[str, Dict[str, Any]]:" in content:
            print("✅ get_module_whitelist returns correct type")
        else:
            print("❌ get_module_whitelist has wrong return type")
            
        # Check if set_module_whitelist takes Dict
        if "def set_module_whitelist(self, module_whitelist: Dict[str, Dict[str, Any]]):" in content:
            print("✅ set_module_whitelist takes Dict parameter")
        else:
            print("❌ set_module_whitelist has old signature")
    else:
        print("❌ usd_utils.py not found")
    
    # Check 2: ModuleManager directory structure
    print("\n🔍 Checking ModuleManager.create_module...")
    module_manager_file = Path("hair_qc_tool/managers/module_manager.py")
    
    if module_manager_file.exists():
        with open(module_manager_file, 'r') as f:
            content = f.read()
            
        # Check if it creates in subdirectory
        if 'module_file = config.usd_directory / "module" / module_type / f"{module_name}.usd"' in content:
            print("✅ create_module creates in type subdirectory")
        else:
            print("❌ create_module uses old directory structure")
            
        # Check if it creates parent directory
        if "module_type_dir.mkdir(parents=True, exist_ok=True)" in content:
            print("✅ create_module creates parent directories")
        else:
            print("❌ create_module doesn't create parent directories")
            
        # Check if it uses save_stage
        if "group_utils.save_stage()" in content:
            print("✅ Uses save_stage() method")
        else:
            print("❌ Still uses save_changes() method")
    else:
        print("❌ module_manager.py not found")
    
    # Check 3: DataManager integration
    print("\n🔍 Checking DataManager...")
    data_manager_file = Path("hair_qc_tool/managers/data_manager.py")
    
    if data_manager_file.exists():
        with open(data_manager_file, 'r') as f:
            content = f.read()
            
        if "from .module_manager import ModuleManager" in content:
            print("✅ DataManager imports ModuleManager")
        else:
            print("❌ DataManager missing ModuleManager import")
            
        if "self.module_manager = ModuleManager()" in content:
            print("✅ DataManager creates ModuleManager instance")
        else:
            print("❌ DataManager doesn't create ModuleManager")
    else:
        print("❌ data_manager.py not found")
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print("If all checks show ✅, then the code changes are saved.")
    print("If you see ❌, the old code might still be cached in Maya.")
    print("\nTo fix Maya caching:")
    print("1. Restart Maya completely")
    print("2. Run the install script again in Maya")
    print("3. The new code should then work")

if __name__ == "__main__":
    check_code_changes()