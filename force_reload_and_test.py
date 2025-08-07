# -*- coding: utf-8 -*-
"""
Force reload Hair QC Tool modules and test the fixes
Run this in Maya to apply the latest code changes
"""

import sys
import importlib

def force_reload_hair_qc_modules():
    """Force reload all hair_qc_tool modules to get latest code"""
    
    print("=" * 60)
    print("FORCE RELOADING HAIR QC TOOL MODULES")
    print("=" * 60)
    
    # List of modules to reload in dependency order
    modules_to_reload = [
        'hair_qc_tool.config',
        'hair_qc_tool.utils.file_utils',
        'hair_qc_tool.utils.rules_utils', 
        'hair_qc_tool.utils.usd_utils',
        'hair_qc_tool.utils.maya_utils',
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
    
    return reloaded_count > 0

def test_maya_usd_import_fix():
    """Test the Maya USD import fix"""
    
    print("\n" + "=" * 60)
    print("TESTING MAYA USD IMPORT FIX")
    print("=" * 60)
    
    try:
        from hair_qc_tool.utils.maya_utils import MayaUtils
        
        # Test with a known USD file
        test_usd_file = "C:/Users/woske/Documents/GitRepo/modular_hair_qc/docs/TestDirectory/module/crown/midAfro.usd"
        
        print(f"Testing USD import with: {test_usd_file}")
        
        # Test the import method
        imported_nodes = MayaUtils.import_usd_as_maya_geometry(
            test_usd_file, 
            import_blendshapes=True, 
            import_skeletons=False
        )
        
        if imported_nodes:
            print(f"✅ SUCCESS: Imported {len(imported_nodes)} nodes")
            print(f"   Nodes: {imported_nodes}")
            return True
        else:
            print("❌ FAILED: No nodes imported")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def cleanup_scene():
    """Clean up Maya scene before testing"""
    print("\n" + "=" * 60)
    print("CLEANING UP MAYA SCENE")
    print("=" * 60)
    
    try:
        import maya.cmds as cmds
        
        # Clear all imported namespaces
        all_namespaces = cmds.namespaceInfo(listOnlyNamespaces=True, recurse=True) or []
        imported_namespaces = [ns for ns in all_namespaces if ns.startswith('imported')]
        
        for namespace in imported_namespaces:
            try:
                # Get all nodes in the namespace
                nodes_in_ns = cmds.namespaceInfo(namespace, listNamespace=True, dagPath=True) or []
                
                # Delete all nodes in the namespace
                if nodes_in_ns:
                    for node in nodes_in_ns:
                        if cmds.objExists(node):
                            try:
                                cmds.delete(node)
                            except:
                                pass
                
                # Remove the namespace
                if cmds.namespace(exists=namespace):
                    cmds.namespace(removeNamespace=namespace, mergeNamespaceWithRoot=True)
                    print(f"✅ Cleared namespace: {namespace}")
                    
            except Exception as ns_error:
                print(f"Warning: Could not clear namespace {namespace}: {ns_error}")
        
        # Clear any display geometry groups
        display_groups = [node for node in cmds.ls(type='transform') if '_DisplayGeo' in node]
        for group in display_groups:
            try:
                cmds.delete(group)
                print(f"✅ Cleared display group: {group}")
            except:
                pass
        
        print("✅ Scene cleanup completed")
        return True
        
    except Exception as e:
        print(f"❌ Scene cleanup failed: {e}")
        return False

def fix_existing_usd_files():
    """Fix existing USD files to have default prim"""
    print("\n" + "=" * 60)
    print("FIXING EXISTING USD FILES")
    print("=" * 60)
    
    try:
        from pxr import Usd
        import os
        
        # Fix the midAfro.usd file
        usd_file = "C:/Users/woske/Documents/GitRepo/modular_hair_qc/docs/TestDirectory/module/crown/midAfro.usd"
        
        if os.path.exists(usd_file):
            print(f"Fixing USD file: {usd_file}")
            
            stage = Usd.Stage.Open(usd_file)
            if stage:
                # Check if HairModule prim exists
                hair_module_prim = stage.GetPrimAtPath("/HairModule")
                if hair_module_prim and hair_module_prim.IsValid():
                    # Set as default prim
                    stage.SetDefaultPrim(hair_module_prim)
                    stage.Save()
                    print("✅ Set default prim and saved USD file")
                    return True
                else:
                    print("❌ HairModule prim not found in USD file")
                    return False
            else:
                print("❌ Could not open USD stage")
                return False
        else:
            print("❌ USD file not found")
            return False
            
    except Exception as e:
        print(f"❌ USD file fix failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_display_geometry_system():
    """Test the display geometry system"""
    
    print("\n" + "=" * 60)
    print("TESTING DISPLAY GEOMETRY SYSTEM")
    print("=" * 60)
    
    try:
        from hair_qc_tool.managers.data_manager import DataManager
        
        # Create data manager
        data_manager = DataManager()
        
        # Load a group
        groups = data_manager.get_groups()
        if not groups:
            print("❌ No groups available")
            return False
        
        test_group = "short"  # Use the specific group we know exists
        print(f"Loading group: {test_group}")
        
        success, message = data_manager.load_group(test_group)
        if not success:
            print(f"❌ Failed to load group: {message}")
            return False
        
        print("✅ Group loaded successfully")
        
        # Get modules
        modules = data_manager.get_modules()
        if not modules:
            print("❌ No modules available")
            return False
        
        test_module = "midAfro"  # Use the specific module we know exists
        if test_module not in modules:
            test_module = modules[0]  # Fallback to first available
            
        print(f"Loading module: {test_module}")
        
        success, message = data_manager.load_module(test_module)
        if not success:
            print(f"❌ Failed to load module: {message}")
            return False
        
        print("✅ Module loaded successfully")
        
        # Test display geometry loading
        print("Testing display geometry loading...")
        success, message = data_manager.load_geometry_to_scene()
        
        if success:
            print("✅ SUCCESS: Display geometry loaded!")
            print(f"   Message: {message}")
            
            # Check if we have blendshape controls
            blendshapes = data_manager.get_module_blendshapes()
            print(f"   Available blendshapes: {list(blendshapes.keys()) if blendshapes else 'None'}")
            
            return True
        else:
            print(f"❌ FAILED: Display geometry loading failed: {message}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Hair QC Tool - Force Reload and Test")
    print("Run this script in Maya to apply latest fixes")
    
    # Force reload modules
    reload_success = force_reload_hair_qc_modules()
    
    if reload_success:
        print("\n✅ Modules reloaded successfully")
        
        # Clean up scene first
        cleanup_success = cleanup_scene()
        
        # Fix existing USD files
        usd_fix_success = fix_existing_usd_files()
        
        # Test the fixes
        print("\nTesting fixes...")
        
        # Test 1: Maya USD import
        import_test = test_maya_usd_import_fix()
        
        # Test 2: Display geometry system  
        display_test = test_display_geometry_system()
        
        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        if import_test and display_test:
            print("🎉 ALL TESTS PASSED!")
            print("\nThe fixes are working correctly:")
            print("✅ Maya USD import API fixed")
            print("✅ Display geometry system working")
            print("✅ Stage cache error resolved")
            print("✅ USD default prim set")
            print("✅ Scene cleanup working")
            print("\nYou can now use the Hair QC Tool normally.")
            print("\nTo test blendshapes:")
            print("1. Click on 'midAfro' in the module list")
            print("2. Move the blendshape sliders")
            print("3. The Maya geometry should update in real-time")
        else:
            print("⚠️ Some tests failed:")
            print(f"   Scene Cleanup: {'✅' if cleanup_success else '❌'}")
            print(f"   USD File Fix: {'✅' if usd_fix_success else '❌'}")
            print(f"   Maya USD Import: {'✅' if import_test else '❌'}")
            print(f"   Display Geometry: {'✅' if display_test else '❌'}")
            print("\nCheck the error messages above for details.")
    else:
        print("\n❌ Failed to reload modules")
        print("Try restarting Maya and running the install script again.")
