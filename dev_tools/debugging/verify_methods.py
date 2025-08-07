#!/usr/bin/env python3
"""
Simple verification script to check if the USDModuleUtils methods are correct.
Run this after installing to verify the fixes are loaded.
"""

def verify_usd_module_utils():
    """Verify USDModuleUtils has the correct methods"""
    
    print("=" * 50)
    print("VERIFYING USDModuleUtils METHODS")
    print("=" * 50)
    
    try:
        from hair_qc_tool.utils.usd_utils import USDModuleUtils
        
        # Methods that should exist
        required_methods = [
            'get_blendshape_names',  # NOT get_blendshapes
            'set_blendshapes',
            'remove_blendshape', 
            'get_module_info',
            'has_geometry_data',     # NOT get_geometry_data
            'import_geometry_from_maya',
            'add_blendshape_from_maya',
            'export_geometry_to_maya'
        ]
        
        # Methods that should NOT exist (old names)
        forbidden_methods = [
            'get_blendshapes',       # OLD NAME - should be get_blendshape_names
            'get_geometry_data'      # OLD NAME - should be has_geometry_data
        ]
        
        print("✓ Required methods:")
        all_good = True
        for method in required_methods:
            if hasattr(USDModuleUtils, method):
                print(f"  ✓ {method}")
            else:
                print(f"  ✗ {method} - MISSING!")
                all_good = False
        
        print("\n✗ Forbidden methods (old names):")
        for method in forbidden_methods:
            if hasattr(USDModuleUtils, method):
                print(f"  ✗ {method} - STILL EXISTS! (should be removed)")
                all_good = False
            else:
                print(f"  ✓ {method} - correctly removed")
        
        if all_good:
            print("\n🎉 ALL METHODS CORRECT! Module loading should work now.")
        else:
            print("\n❌ SOME METHODS ARE WRONG! Maya is still using old cached modules.")
            print("   Try restarting Maya completely and reinstalling.")
            
        return all_good
        
    except ImportError as e:
        print(f"❌ Failed to import USDModuleUtils: {e}")
        return False
    except Exception as e:
        print(f"❌ Error checking methods: {e}")
        return False

if __name__ == "__main__":
    verify_usd_module_utils()