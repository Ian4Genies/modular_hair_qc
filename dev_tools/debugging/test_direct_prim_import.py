#!/usr/bin/env python3
"""
Test script to verify direct prim path import approach
"""

def test_direct_prim_import():
    """Test importing specific USD prims directly"""
    
    print("="*60)
    print("TESTING DIRECT PRIM PATH IMPORT")
    print("="*60)
    
    try:
        import maya.cmds as cmds
        from hair_qc_tool.utils.maya_utils import MayaUtils
        from pathlib import Path
        
        # Test with a module USD file
        test_usd_file = Path("docs/TestDirectory/module/crown/midAfro.usd")
        
        if not test_usd_file.exists():
            print(f"ERROR: Test USD file not found: {test_usd_file}")
            print("Please ensure you have a valid module USD file to test with")
            return False
        
        print(f"Testing with USD file: {test_usd_file}")
        
        # Clear scene first
        cmds.file(new=True, force=True)
        print("Scene cleared")
        
        # Test the simplified import
        print("\n" + "-"*40)
        print("TESTING DIRECT PRIM IMPORT:")
        print("-"*40)
        
        imported_nodes = MayaUtils.import_usd_as_maya_geometry(
            str(test_usd_file), 
            import_blendshapes=True, 
            import_skeletons=False
        )
        
        print(f"\nFinal imported nodes: {imported_nodes}")
        print(f"Number of imported nodes: {len(imported_nodes)}")
        
        # Check what's actually in the scene
        print("\n" + "-"*40)
        print("SCENE ANALYSIS:")
        print("-"*40)
        
        all_transforms = cmds.ls(type='transform')
        scene_transforms = [t for t in all_transforms if t not in ['persp', 'top', 'front', 'side']]
        
        print(f"All transforms in scene: {scene_transforms}")
        
        # Check for expected nodes
        has_basemesh = any('BaseMesh' in node for node in scene_transforms)
        has_blendshapes = any(any(keyword in node.lower() for keyword in ['blend', 'target']) for node in scene_transforms)
        
        print(f"Has BaseMesh: {has_basemesh}")
        print(f"Has blendshapes: {has_blendshapes}")
        
        # Check for unwanted nodes
        unwanted_nodes = []
        for node in scene_transforms:
            if any(unwanted in node.lower() for unwanted in [
                'hairmodule', 'blendshapeexclusions', 'textureassets', 
                'alphablacklist', 'whitelistedtextures'
            ]):
                unwanted_nodes.append(node)
        
        print(f"Unwanted nodes: {unwanted_nodes}")
        
        # Success criteria
        success = (
            len(imported_nodes) > 0 and
            has_basemesh and
            len(unwanted_nodes) == 0
        )
        
        print("\n" + "="*40)
        if success:
            print("✓ SUCCESS: Direct prim import working!")
        else:
            print("✗ ISSUES: Direct prim import has problems")
            if len(imported_nodes) == 0:
                print("  - No nodes imported")
            if not has_basemesh:
                print("  - BaseMesh not found")
            if len(unwanted_nodes) > 0:
                print(f"  - Unwanted nodes present: {unwanted_nodes}")
        print("="*40)
        
        return success
        
    except Exception as e:
        print(f"ERROR: Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_direct_prim_import()
