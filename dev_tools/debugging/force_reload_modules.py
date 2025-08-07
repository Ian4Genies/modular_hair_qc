#!/usr/bin/env python3
"""
Force reload all hair_qc_tool modules to ensure latest code is used.
Run this in Maya to clear all cached modules.
"""

import sys
import importlib

def force_reload_all_modules():
    """Force reload all hair_qc_tool modules"""
    
    # List of all modules to reload in dependency order
    modules_to_reload = [
        'hair_qc_tool.config',
        'hair_qc_tool.utils.usd_utils',
        'hair_qc_tool.utils.maya_utils', 
        'hair_qc_tool.utils.rules_utils',
        'hair_qc_tool.utils.file_utils',
        'hair_qc_tool.utils',
        'hair_qc_tool.managers.group_manager',
        'hair_qc_tool.managers.module_manager',
        'hair_qc_tool.managers.data_manager',
        'hair_qc_tool.managers',
        'hair_qc_tool.ui.main_window',
        'hair_qc_tool.ui',
        'hair_qc_tool.main',
        'hair_qc_tool'
    ]
    
    print("=" * 60)
    print("FORCE RELOADING ALL HAIR_QC_TOOL MODULES")
    print("=" * 60)
    
    reloaded_count = 0
    
    for module_name in modules_to_reload:
        if module_name in sys.modules:
            try:
                print(f"[RELOAD] {module_name}")
                importlib.reload(sys.modules[module_name])
                reloaded_count += 1
            except Exception as e:
                print(f"[ERROR] Failed to reload {module_name}: {e}")
        else:
            print(f"[SKIP] {module_name} not loaded")
    
    print("=" * 60)
    print(f"RELOADED {reloaded_count} MODULES")
    print("=" * 60)
    
    # Verify the USDModuleUtils has the correct methods
    try:
        from hair_qc_tool.utils.usd_utils import USDModuleUtils
        
        print("\n[VERIFY] Checking USDModuleUtils methods:")
        methods = [attr for attr in dir(USDModuleUtils) if not attr.startswith('_')]
        
        # Check for specific methods that were problematic
        critical_methods = [
            'get_blendshape_names',
            'set_blendshapes', 
            'remove_blendshape',
            'get_module_info',
            'has_geometry_data',
            'import_geometry_from_maya',
            'add_blendshape_from_maya'
        ]
        
        print("Critical methods status:")
        for method in critical_methods:
            if hasattr(USDModuleUtils, method):
                print(f"  ✓ {method}")
            else:
                print(f"  ✗ {method} - MISSING!")
        
        # Check for old problematic methods
        old_methods = ['get_blendshapes', 'get_geometry_data']
        print("\nOld methods (should NOT exist):")
        for method in old_methods:
            if hasattr(USDModuleUtils, method):
                print(f"  ✗ {method} - STILL EXISTS!")
            else:
                print(f"  ✓ {method} - correctly removed")
                
        print(f"\nAll methods: {sorted(methods)}")
        
    except Exception as e:
        print(f"[ERROR] Failed to verify USDModuleUtils: {e}")

if __name__ == "__main__":
    force_reload_modules()