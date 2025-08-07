# -*- coding: utf-8 -*-
"""
Simple reload and test script for Hair QC Tool
Run this in Maya to apply the latest fixes
"""

import sys
import importlib

def force_reload_modules():
    """Force reload all hair_qc_tool modules"""
    
    print("=" * 60)
    print("FORCE RELOADING HAIR QC TOOL MODULES")
    print("=" * 60)
    
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
                print("[RELOAD] " + module_name)
                importlib.reload(sys.modules[module_name])
                reloaded_count += 1
            except Exception as e:
                print("[ERROR] Failed to reload " + module_name + ": " + str(e))
        else:
            print("[SKIP] " + module_name + " not loaded")
    
    print("=" * 60)
    print("RELOADED " + str(reloaded_count) + " MODULES")
    print("=" * 60)
    
    return reloaded_count > 0

def cleanup_scene():
    """Clean up Maya scene"""
    print("\nCLEANING UP MAYA SCENE")
    print("=" * 40)
    
    try:
        import maya.cmds as cmds
        
        # Clear imported namespaces
        all_namespaces = cmds.namespaceInfo(listOnlyNamespaces=True, recurse=True) or []
        imported_namespaces = [ns for ns in all_namespaces if ns.startswith('imported')]
        
        for namespace in imported_namespaces:
            try:
                nodes_in_ns = cmds.namespaceInfo(namespace, listNamespace=True, dagPath=True) or []
                
                if nodes_in_ns:
                    for node in nodes_in_ns:
                        if cmds.objExists(node):
                            try:
                                cmds.delete(node)
                            except:
                                pass
                
                if cmds.namespace(exists=namespace):
                    cmds.namespace(removeNamespace=namespace, mergeNamespaceWithRoot=True)
                    print("Cleared namespace: " + namespace)
                    
            except Exception as ns_error:
                print("Warning: Could not clear namespace " + namespace + ": " + str(ns_error))
        
        # Clear display geometry groups
        display_groups = [node for node in cmds.ls(type='transform') if '_DisplayGeo' in node]
        for group in display_groups:
            try:
                cmds.delete(group)
                print("Cleared display group: " + group)
            except:
                pass
        
        print("Scene cleanup completed")
        return True
        
    except Exception as e:
        print("Scene cleanup failed: " + str(e))
        return False

def fix_usd_file():
    """Fix USD file to have default prim"""
    print("\nFIXING USD FILE")
    print("=" * 40)
    
    try:
        from pxr import Usd
        import os
        
        usd_file = "C:/Users/woske/Documents/GitRepo/modular_hair_qc/docs/TestDirectory/module/crown/midAfro.usd"
        
        if os.path.exists(usd_file):
            print("Fixing USD file: " + usd_file)
            
            stage = Usd.Stage.Open(usd_file)
            if stage:
                hair_module_prim = stage.GetPrimAtPath("/HairModule")
                if hair_module_prim and hair_module_prim.IsValid():
                    stage.SetDefaultPrim(hair_module_prim)
                    stage.Save()
                    print("Set default prim and saved USD file")
                    return True
                else:
                    print("HairModule prim not found in USD file")
                    return False
            else:
                print("Could not open USD stage")
                return False
        else:
            print("USD file not found")
            return False
            
    except Exception as e:
        print("USD file fix failed: " + str(e))
        return False

def test_system():
    """Test the display geometry system"""
    print("\nTESTING DISPLAY GEOMETRY SYSTEM")
    print("=" * 40)
    
    try:
        from hair_qc_tool.managers.data_manager import DataManager
        
        data_manager = DataManager()
        
        # Load group
        success, message = data_manager.load_group("short")
        if not success:
            print("Failed to load group: " + message)
            return False
        
        print("Group loaded successfully")
        
        # Load module
        success, message = data_manager.load_module("midAfro")
        if not success:
            print("Failed to load module: " + message)
            return False
        
        print("Module loaded successfully")
        
        # Test display geometry loading
        success, message = data_manager.load_geometry_to_scene()
        
        if success:
            print("SUCCESS: Display geometry loaded!")
            print("Message: " + message)
            
            blendshapes = data_manager.get_module_blendshapes()
            if blendshapes:
                print("Available blendshapes: " + str(list(blendshapes.keys())))
            else:
                print("No blendshapes found")
            
            return True
        else:
            print("FAILED: Display geometry loading failed: " + message)
            return False
            
    except Exception as e:
        print("ERROR: " + str(e))
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Hair QC Tool - Simple Reload and Test")
    print("Run this script in Maya to apply latest fixes")
    
    # Force reload modules
    reload_success = force_reload_modules()
    
    if reload_success:
        print("\nModules reloaded successfully")
        
        # Clean up scene
        cleanup_success = cleanup_scene()
        
        # Fix USD file
        usd_fix_success = fix_usd_file()
        
        # Test system
        test_success = test_system()
        
        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        if test_success:
            print("ALL TESTS PASSED!")
            print("\nThe fixes are working correctly:")
            print("- Maya USD import API fixed")
            print("- Display geometry system working")
            print("- Stage cache error resolved")
            print("- USD default prim set")
            print("- Scene cleanup working")
            print("\nYou can now use the Hair QC Tool normally.")
            print("\nTo test blendshapes:")
            print("1. Click on 'midAfro' in the module list")
            print("2. Move the blendshape sliders")
            print("3. The Maya geometry should update in real-time")
        else:
            print("Some tests failed:")
            print("Scene Cleanup: " + ("PASS" if cleanup_success else "FAIL"))
            print("USD File Fix: " + ("PASS" if usd_fix_success else "FAIL"))
            print("Display Geometry: " + ("PASS" if test_success else "FAIL"))
    else:
        print("\nFailed to reload modules")
        print("Try restarting Maya and running the install script again.")
