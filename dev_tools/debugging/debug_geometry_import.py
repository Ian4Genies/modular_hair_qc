#!/usr/bin/env python3
"""
Debug script to test geometry import step by step
Run this in Maya with a sphere selected
"""

def debug_geometry_import():
    """Debug geometry import process step by step"""
    
    print("="*60)
    print("DEBUGGING GEOMETRY IMPORT")
    print("="*60)
    
    try:
        import maya.cmds as cmds
        
        # Check selection
        selected = cmds.ls(selection=True)
        print(f"Selected objects: {selected}")
        
        if not selected:
            print("ERROR: No objects selected. Please select a mesh object.")
            return False
        
        mesh_name = selected[0]
        print(f"Testing with mesh: {mesh_name}")
        
        # Check if object exists
        if not cmds.objExists(mesh_name):
            print(f"ERROR: Object '{mesh_name}' does not exist")
            return False
        
        print(f"✓ Object exists: {mesh_name}")
        
        # Check object type
        obj_type = cmds.objectType(mesh_name)
        print(f"Object type: {obj_type}")
        
        # Get shapes
        shapes = cmds.listRelatives(mesh_name, shapes=True) or []
        print(f"Shapes: {shapes}")
        
        if shapes:
            shape_type = cmds.objectType(shapes[0])
            print(f"Shape type: {shape_type}")
        
        # Test USD plugin availability
        print("\n" + "-"*40)
        print("TESTING USD PLUGINS")
        print("-"*40)
        
        plugins = ['mayaUsdPlugin', 'AL_USDMayaPlugin', 'pxrUsd']
        available_plugins = []
        
        for plugin in plugins:
            try:
                is_loaded = cmds.pluginInfo(plugin, query=True, loaded=True)
                print(f"{plugin}: loaded={is_loaded}")
                if is_loaded:
                    available_plugins.append(plugin)
            except:
                try:
                    loaded = cmds.loadPlugin(plugin, quiet=True)
                    print(f"{plugin}: loaded after attempt={loaded is not None}")
                    if loaded:
                        available_plugins.append(plugin)
                except Exception as e:
                    print(f"{plugin}: not available ({e})")
        
        print(f"Available USD plugins: {available_plugins}")
        
        if not available_plugins:
            print("ERROR: No USD plugins available!")
            return False
        
        # Test export
        print("\n" + "-"*40)
        print("TESTING USD EXPORT")
        print("-"*40)
        
        from pathlib import Path
        temp_path = Path.cwd() / f"test_export_{mesh_name}.usd"
        print(f"Test export path: {temp_path}")
        
        # Select the mesh
        cmds.select(mesh_name, replace=True)
        
        # Try each available plugin
        for plugin in available_plugins:
            print(f"\nTrying export with {plugin}...")
            
            try:
                if plugin == 'mayaUsdPlugin':
                    cmds.mayaUSDExport(
                        file=str(temp_path),
                        selection=True,
                        exportBlendShapes=False
                    )
                elif plugin == 'AL_USDMayaPlugin':
                    cmds.AL_usdmaya_ExportCommand(
                        file=str(temp_path),
                        selection=True
                    )
                elif plugin == 'pxrUsd':
                    cmds.usdExport(
                        file=str(temp_path),
                        selection=True,
                        exportBlendShapes=False
                    )
                
                # Check if file was created
                if temp_path.exists():
                    file_size = temp_path.stat().st_size
                    print(f"✓ Export successful with {plugin}! File size: {file_size} bytes")
                    
                    # Try to open the USD file
                    try:
                        from pxr import Usd, UsdGeom
                        stage = Usd.Stage.Open(str(temp_path))
                        if stage:
                            print("✓ USD stage opened successfully")
                            
                            # Find mesh prims
                            mesh_count = 0
                            for prim in stage.Traverse():
                                if prim.IsA(UsdGeom.Mesh):
                                    mesh_count += 1
                                    mesh = UsdGeom.Mesh(prim)
                                    points_attr = mesh.GetPointsAttr()
                                    if points_attr.HasValue():
                                        points = points_attr.Get()
                                        print(f"✓ Found mesh with {len(points)} points at {prim.GetPath()}")
                                    else:
                                        print(f"✗ Mesh at {prim.GetPath()} has no points")
                            
                            if mesh_count == 0:
                                print("✗ No mesh prims found in exported USD")
                            
                        else:
                            print("✗ Failed to open USD stage")
                    except Exception as e:
                        print(f"✗ Error reading USD file: {e}")
                    
                    # Clean up
                    temp_path.unlink(missing_ok=True)
                    return True
                else:
                    print(f"✗ Export failed with {plugin} - no file created")
                    
            except Exception as e:
                print(f"✗ Export failed with {plugin}: {e}")
                import traceback
                traceback.print_exc()
        
        print("ERROR: All export methods failed")
        return False
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_geometry_import()