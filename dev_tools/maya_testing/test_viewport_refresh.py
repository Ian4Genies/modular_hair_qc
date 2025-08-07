#!/usr/bin/env python
"""
Test script for USD blendshape viewport refresh

This script tests different approaches to refresh Maya's viewport
when USD blendshape weights are changed programmatically.
"""

import maya.cmds as cmds
import time
from pathlib import Path


def test_viewport_refresh_approaches():
    """Test different viewport refresh approaches"""
    print("=== Testing Viewport Refresh Approaches ===")
    
    # Get all proxy shapes in the scene
    proxy_shapes = cmds.ls(type="mayaUsdProxyShape") or []
    
    if not proxy_shapes:
        print("No USD proxy shapes found in scene")
        return
    
    for proxy_shape in proxy_shapes:
        print(f"\nTesting refresh for proxy shape: {proxy_shape}")
        
        # Get the file path
        try:
            file_path = cmds.getAttr(f"{proxy_shape}.filePath")
            print(f"USD file: {file_path}")
            
            # Test different refresh approaches
            test_approaches = [
                ("File Path Reset", test_file_path_reset),
                ("Stage Cache Clear", test_stage_cache_clear),
                ("Hydra Geometry Dirty", test_hydra_dirty),
                ("DG Dirty", test_dg_dirty),
                ("Time Scrub", test_time_scrub),
                ("Viewport Reset", test_viewport_reset),
            ]
            
            for approach_name, test_func in test_approaches:
                print(f"\n  Testing: {approach_name}")
                try:
                    test_func(proxy_shape)
                    time.sleep(0.5)  # Give time for refresh
                    print(f"    {approach_name}: SUCCESS")
                except Exception as e:
                    print(f"    {approach_name}: FAILED - {e}")
                    
        except Exception as e:
            print(f"Error testing proxy shape {proxy_shape}: {e}")


def test_file_path_reset(proxy_shape):
    """Test file path reset approach"""
    current_file_path = cmds.getAttr(f"{proxy_shape}.filePath")
    cmds.setAttr(f"{proxy_shape}.filePath", "", type="string")
    cmds.refresh(currentView=True, force=True)
    cmds.setAttr(f"{proxy_shape}.filePath", current_file_path, type="string")


def test_stage_cache_clear(proxy_shape):
    """Test USD stage cache clearing"""
    try:
        from pxr import Usd
        stage_cache = Usd.StageCache.Get()
        stage_cache.Clear()
    except ImportError:
        raise Exception("USD not available")


def test_hydra_dirty(proxy_shape):
    """Test marking Hydra geometry as dirty"""
    try:
        import maya.api.OpenMayaRender as omr
        renderer = omr.MRenderer.theRenderer()
        if renderer:
            renderer.setGeometryDrawDirty(omr.MRenderer.kAllGeometry)
    except ImportError:
        raise Exception("Maya API not available")


def test_dg_dirty(proxy_shape):
    """Test dependency graph dirty"""
    cmds.dgdirty(proxy_shape)
    cmds.dgdirty(allPlugs=True)


def test_time_scrub(proxy_shape):
    """Test time scrubbing to trigger refresh"""
    current_time = cmds.currentTime(query=True)
    cmds.currentTime(current_time + 1)
    cmds.currentTime(current_time)


def test_viewport_reset(proxy_shape):
    """Test viewport reset"""
    cmds.ogs(reset=True)
    cmds.refresh(currentView=True, force=True)


def test_blendshape_weight_visibility():
    """Test if blendshape weight changes are visible"""
    print("\n=== Testing Blendshape Weight Visibility ===")
    
    # This would need to be integrated with the actual Hair QC Tool
    # For now, just provide instructions
    print("""
To test blendshape visibility:

1. Load a module with blendshapes using the Hair QC Tool
2. Move a blendshape slider in the UI
3. Observe if the geometry changes in the viewport
4. Check the console output for refresh messages

Expected console output should include:
- "Saved USD stage after blendshape weight change"
- "Cleared USD stage cache"
- "Marked Hydra geometry as dirty"
- "Completed comprehensive USD proxy refresh"

If geometry doesn't update, try manually:
1. Scrubbing the timeline
2. Switching viewport modes (Viewport 2.0 vs Legacy)
3. Toggling wireframe/shaded mode
4. Moving the camera
""")


if __name__ == "__main__":
    print("=== USD Viewport Refresh Test ===")
    
    # Check if we're running in Maya
    try:
        import maya.cmds as cmds
        print("Running in Maya environment")
        
        test_viewport_refresh_approaches()
        test_blendshape_weight_visibility()
        
    except ImportError:
        print("Not running in Maya - this script requires Maya environment")
        print("Run this script from Maya's Script Editor or as a Maya Python script")
    
    print("\n=== Test Complete ===")

