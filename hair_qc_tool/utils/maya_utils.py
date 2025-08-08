"""
Maya integration utilities

Handles Maya-specific operations like geometry import, blendshape management,
and timeline manipulation.
"""

import maya.cmds as cmds
import maya.api.OpenMaya as om
from pathlib import Path
from typing import List
import traceback


class MayaUtils:
    """Utility class for Maya operations"""
    
    @staticmethod
    def get_selected_mesh():
        """Get the currently selected mesh object"""
        selection = cmds.ls(selection=True, type="mesh")
        if not selection:
            selection = cmds.ls(selection=True, type="transform")
            if selection:
                # Check if transform has mesh shape
                shapes = cmds.listRelatives(selection[0], shapes=True, type="mesh")
                if shapes:
                    return selection[0]
        elif selection:
            # Get transform parent of mesh
            transform = cmds.listRelatives(selection[0], parent=True, type="transform")
            if transform:
                return transform[0]
        
        return None
    
    @staticmethod
    def get_mesh_blendshapes(mesh_name):
        """Get all blendshapes associated with a mesh"""
        if not mesh_name or not cmds.objExists(mesh_name):
            return []
        
        # Find blendShape nodes connected to this mesh
        # Avoid using unsupported flags on some Maya versions
        history = cmds.listHistory(mesh_name, pruneDagObjects=True) or []
        blendshapes = []
        
        for blend_node in history:
            if cmds.nodeType(blend_node) != "blendShape":
                continue
            # Get all targets for this blendShape node
            targets = cmds.listAttr(f"{blend_node}.weight", multi=True) or []
            for target in targets:
                target_name = target.replace(f"{blend_node}.weight[", "").replace("]", "")
                # Get the actual target name
                alias = cmds.aliasAttr(f"{blend_node}.weight[{target_name}]", query=True)
                if alias:
                    blendshapes.append(alias[0])
        
        return blendshapes
    
    @staticmethod
    def create_blendshape_from_mesh(base_mesh, target_mesh, blendshape_name):
        """Create a blendshape from target mesh to base mesh"""
        try:
            if not cmds.objExists(base_mesh) or not cmds.objExists(target_mesh):
                raise ValueError("Base mesh or target mesh does not exist")
            
            # Check if blendShape node already exists
            existing_blend_nodes = [n for n in (cmds.listHistory(base_mesh, pruneDagObjects=True) or []) if cmds.nodeType(n) == "blendShape"]
            
            if existing_blend_nodes:
                # Add to existing blendShape node
                blend_node = existing_blend_nodes[0]
                cmds.blendShape(blend_node, edit=True, target=(base_mesh, len(cmds.listAttr(f"{blend_node}.weight", multi=True) or []), target_mesh, 1.0))
                
                # Set alias name
                target_index = len(cmds.listAttr(f"{blend_node}.weight", multi=True)) - 1
                cmds.aliasAttr(blendshape_name, f"{blend_node}.weight[{target_index}]")
            else:
                # Create new blendShape node
                blend_node = cmds.blendShape(target_mesh, base_mesh, name=f"{base_mesh}_blendShape")[0]
                cmds.aliasAttr(blendshape_name, f"{blend_node}.weight[0]")
            
            return blend_node
            
        except Exception as e:
            print(f"[Maya Utils] Error creating blendshape: {e}")
            return None
    
    @staticmethod
    def create_blendshapes_from_usd_data(base_mesh, usd_file_path, blendshape_names):
        """Create Maya blendshapes from USD Skel-standard blendshape data

        Expects BaseMesh with rel skel:blendShapeTargets to Mesh targets
        and primvars:skel:blendShapeWeights.
        """
        try:
            from pxr import Usd, UsdGeom, Sdf
            
            print(f"[Maya Utils] Creating blendshapes from USD: {usd_file_path}")
            print(f"[Maya Utils] Target blendshapes: {blendshape_names}")
            
            # Open USD stage
            stage = Usd.Stage.Open(str(usd_file_path))
            if not stage:
                print(f"[Maya Utils] Could not open USD stage: {usd_file_path}")
                return []
            
            # Find the base mesh
            base_mesh_prim = stage.GetPrimAtPath("/HairModule/BaseMesh")
            if not base_mesh_prim or not base_mesh_prim.IsA(UsdGeom.Mesh):
                print(f"[Maya Utils] Base mesh not found in USD")
                return []
            
            base_mesh_usd = UsdGeom.Mesh(base_mesh_prim)
            base_points = base_mesh_usd.GetPointsAttr().Get() or []
            print(f"[Maya Utils] Found {len(base_points)} base points in USD mesh")
            
            # Get Maya base mesh points for validation
            if not cmds.objExists(base_mesh):
                print(f"[Maya Utils] Maya base mesh not found: {base_mesh}")
                return []
            
            # Create blendshapes from USD data
            created_blendshapes = []
            
            # Map requested names to target paths from relationship
            rel = base_mesh_prim.GetRelationship("skel:blendShapeTargets")
            target_paths = rel.GetTargets() if rel else []
            name_to_path = {}
            for p in target_paths:
                try:
                    name = Sdf.Path(p).name
                except Exception:
                    name = str(p).split('/')[-1]
                name_to_path[name] = p

            for blendshape_name in blendshape_names:
                try:
                    # Resolve target mesh path
                    bs_path = name_to_path.get(blendshape_name)
                    if not bs_path:
                        print(f"[Maya Utils] USD blendshape target not found: {blendshape_name}")
                        continue
                    target_prim = stage.GetPrimAtPath(bs_path)
                    if not target_prim or not target_prim.IsA(UsdGeom.Mesh):
                        print(f"[Maya Utils] Blendshape target is not a mesh: {blendshape_name}")
                        continue
                    target_mesh_usd = UsdGeom.Mesh(target_prim)
                    target_points = target_mesh_usd.GetPointsAttr().Get() or []
                    if len(target_points) != len(base_points):
                        print(f"[Maya Utils] Point mismatch for {blendshape_name}: base {len(base_points)} vs target {len(target_points)}")
                        continue
                    
                    # Create temporary Maya mesh with target points
                    temp_mesh_name = f"temp_{blendshape_name}_target"
                    
                    # Duplicate base mesh
                    duplicated = cmds.duplicate(base_mesh, name=temp_mesh_name)
                    if not duplicated:
                        print(f"[Maya Utils] Could not duplicate base mesh for {blendshape_name}")
                        continue
                    
                    temp_mesh = duplicated[0]
                    
                    # Set the target points on the duplicated mesh
                    for i, target_point in enumerate(target_points):
                        try:
                            cmds.move(target_point[0], target_point[1], target_point[2], 
                                    f"{temp_mesh}.vtx[{i}]", absolute=True)
                        except:
                            # Skip vertices that don't exist
                            pass
                    
                    # Create blendshape from temp mesh
                    blend_node = MayaUtils.create_blendshape_from_mesh(base_mesh, temp_mesh, blendshape_name)
                    
                    if blend_node:
                        created_blendshapes.append((blendshape_name, f"{blend_node}.{blendshape_name}"))
                        print(f"[Maya Utils] Created Maya blendshape: {blendshape_name}")
                    
                    # Clean up temp mesh
                    try:
                        cmds.delete(temp_mesh)
                    except:
                        pass
                        
                except Exception as bs_error:
                    print(f"[Maya Utils] Error creating blendshape {blendshape_name}: {bs_error}")
                    continue
            
            print(f"[Maya Utils] Successfully created {len(created_blendshapes)} Maya blendshapes")
            return created_blendshapes
            
        except Exception as e:
            print(f"[Maya Utils] Error creating blendshapes from USD: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    @staticmethod
    def import_usd_as_maya_geometry(usd_file_path: str, import_blendshapes: bool = True, import_skeletons: bool = False) -> List[str]:
        """
        Import specific USD prims as Maya DAG nodes for interactive editing
        
        Imports only BaseMesh and blendshape targets directly by prim path.
        
        Args:
            usd_file_path: Path to USD file
            import_blendshapes: Whether to import blendshapes
            import_skeletons: Whether to import skeletons (unused)
            
        Returns:
            List of imported Maya geometry node names
        """
        try:
            imported_nodes = []
            
            # Method 1: Import BaseMesh directly
            try:
                print("[Maya Utils] Importing BaseMesh prim")
                cmds.select(clear=True)
                nodes_before = set(cmds.ls(long=True))
                
                cmds.mayaUSDImport(
                    file=usd_file_path,
                    primPath="/HairModule/BaseMesh",
                    importInstances=False,
                    importUSDZTextures=False,
                    importDisplayColor=False
                )
                
                new_nodes = list(set(cmds.ls(long=True)) - nodes_before)
                base_mesh_nodes = [n for n in new_nodes if cmds.objExists(n) and cmds.nodeType(n) == 'transform']
                
                if base_mesh_nodes:
                    print(f"[Maya Utils] Imported BaseMesh: {base_mesh_nodes}")
                    imported_nodes.extend(base_mesh_nodes)
                
            except Exception as e:
                print(f"[Maya Utils] BaseMesh import failed: {e}")
                
                # Fallback: Try importing the entire file and filter
                try:
                    print("[Maya Utils] Fallback: importing entire file")
                    cmds.select(clear=True)
                    nodes_before = set(cmds.ls(long=True))
                    
                    cmds.mayaUSDImport(
                        file=usd_file_path,
                        importInstances=False,
                        importUSDZTextures=False,
                        importDisplayColor=False
                    )
                    
                    new_nodes = list(set(cmds.ls(long=True)) - nodes_before)
                    # Filter for BaseMesh only
                    base_mesh_nodes = [n for n in new_nodes if cmds.objExists(n) and 
                                     cmds.nodeType(n) == 'transform' and 'BaseMesh' in n]
                    
                    if base_mesh_nodes:
                        print(f"[Maya Utils] Fallback BaseMesh import: {base_mesh_nodes}")
                        imported_nodes.extend(base_mesh_nodes)
                        
                        # Clean up unwanted nodes
                        unwanted = [n for n in new_nodes if cmds.objExists(n) and 
                                  cmds.nodeType(n) == 'transform' and 
                                  any(bad in n.lower() for bad in ['hairmodule', 'exclusions', 'assets', 'blacklist'])]
                        for node in unwanted:
                            try:
                                cmds.delete(node)
                                print(f"[Maya Utils] Deleted unwanted node: {node}")
                            except:
                                pass
                                
                except Exception as fallback_e:
                    print(f"[Maya Utils] Fallback import also failed: {fallback_e}")
            
            # Method 2: Import individual blendshape targets if requested
            if import_blendshapes:
                try:
                    # Get blendshape target paths from USD
                    from pxr import Usd, UsdGeom
                    stage = Usd.Stage.Open(str(usd_file_path))
                    if stage:
                        base_mesh_prim = stage.GetPrimAtPath("/HairModule/BaseMesh")
                        if base_mesh_prim and base_mesh_prim.IsValid():
                            # Get blendshape targets from relationship
                            rel = base_mesh_prim.GetRelationship("skel:blendShapeTargets")
                            if rel:
                                target_paths = rel.GetTargets()
                                print(f"[Maya Utils] Found {len(target_paths)} blendshape targets")
                                
                                for target_path in target_paths:
                                    try:
                                        print(f"[Maya Utils] Importing blendshape: {target_path}")
                                        cmds.select(clear=True)
                                        nodes_before = set(cmds.ls(long=True))
                                        
                                        cmds.mayaUSDImport(
                                            file=usd_file_path,
                                            primPath=str(target_path),
                                            importInstances=False,
                                            importUSDZTextures=False,
                                            importDisplayColor=False
                                        )
                                        
                                        new_nodes = list(set(cmds.ls(long=True)) - nodes_before)
                                        blend_nodes = [n for n in new_nodes if cmds.objExists(n) and cmds.nodeType(n) == 'transform']
                                        
                                        if blend_nodes:
                                            print(f"[Maya Utils] Imported blendshape {target_path}: {blend_nodes}")
                                            imported_nodes.extend(blend_nodes)
                                        
                                    except Exception as e:
                                        print(f"[Maya Utils] Failed to import blendshape {target_path}: {e}")
                
                except Exception as e:
                    print(f"[Maya Utils] Error reading blendshape targets: {e}")
            
            # Clean up node names (remove namespaces if any)
            clean_nodes = []
            for node in imported_nodes:
                if cmds.objExists(node):
                    if ':' in node:
                        try:
                            short_name = node.split(':')[-1]
                            new_name = cmds.rename(node, short_name)
                            clean_nodes.append(new_name)
                            print(f"[Maya Utils] Renamed {node} -> {new_name}")
                        except Exception:
                            clean_nodes.append(node)
                    else:
                        clean_nodes.append(node)
            
            print(f"[Maya Utils] Successfully imported {len(clean_nodes)} geometry nodes: {clean_nodes}")
            return clean_nodes
            
        except Exception as e:
            print(f"[Maya Utils] Error importing USD geometry: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    @staticmethod
    def set_blendshape_weight(mesh_name, blendshape_name, weight):
        """Set weight for a specific blendshape"""
        try:
            blend_nodes = cmds.listHistory(mesh_name, type="blendShape")
            for blend_node in blend_nodes:
                if cmds.objExists(f"{blend_node}.{blendshape_name}"):
                    cmds.setAttr(f"{blend_node}.{blendshape_name}", weight)
                    return True
            return False
        except Exception as e:
            print(f"[Maya Utils] Error setting blendshape weight: {e}")
            return False
    
    @staticmethod
    def get_blendshape_weight(mesh_name, blendshape_name):
        """Get current weight for a specific blendshape"""
        try:
            blend_nodes = cmds.listHistory(mesh_name, type="blendShape")
            for blend_node in blend_nodes:
                if cmds.objExists(f"{blend_node}.{blendshape_name}"):
                    return cmds.getAttr(f"{blend_node}.{blendshape_name}")
            return 0.0
        except Exception as e:
            print(f"[Maya Utils] Error getting blendshape weight: {e}")
            return 0.0
    
    @staticmethod
    def keyframe_blendshape(mesh_name, blendshape_name, frame, weight):
        """Set keyframe for blendshape at specific frame"""
        try:
            blend_nodes = cmds.listHistory(mesh_name, type="blendShape")
            for blend_node in blend_nodes:
                attr_name = f"{blend_node}.{blendshape_name}"
                if cmds.objExists(attr_name):
                    cmds.setKeyframe(attr_name, time=frame, value=weight)
                    return True
            return False
        except Exception as e:
            print(f"[Maya Utils] Error keyframing blendshape: {e}")
            return False
    
    @staticmethod
    def clear_timeline_keyframes(start_frame=1, end_frame=6000):
        """Clear all keyframes in timeline range"""
        try:
            # Get all keyframeable attributes in scene
            all_keys = cmds.ls(type="animCurve")
            if all_keys:
                cmds.cutKey(all_keys, time=(start_frame, end_frame), clear=True)
            return True
        except Exception as e:
            print(f"[Maya Utils] Error clearing timeline: {e}")
            return False
    
    @staticmethod
    def set_timeline_range(start_frame, end_frame):
        """Set Maya timeline frame range"""
        try:
            cmds.playbackOptions(minTime=start_frame, maxTime=end_frame)
            return True
        except Exception as e:
            print(f"[Maya Utils] Error setting timeline range: {e}")
            return False
    

    
    @staticmethod
    def export_mesh_to_usd(mesh_name, usd_file_path, include_blendshapes=True):
        """Export Maya mesh to USD file"""
        try:
            if not cmds.objExists(mesh_name):
                print(f"[Maya Utils] Mesh does not exist: {mesh_name}")
                return False
            
            print(f"[Maya Utils] Exporting mesh '{mesh_name}' to '{usd_file_path}'")
            
            # Select the mesh
            cmds.select(mesh_name, replace=True)
            
            # Try different USD export methods based on what's available
            try:
                # Method 1: Maya USD plugin (Maya 2022+)
                if cmds.pluginInfo('mayaUsdPlugin', query=True, loaded=True) or cmds.loadPlugin('mayaUsdPlugin', quiet=True):
                    print("[Maya Utils] Using mayaUSDExport")
                    cmds.mayaUSDExport(
                        file=str(usd_file_path),
                        selection=True,
                        exportBlendShapes=include_blendshapes
                    )
                    return True
            except Exception as e:
                print(f"[Maya Utils] mayaUSDExport failed: {e}")
            
            try:
                # Method 2: AL_USDMaya plugin
                if cmds.pluginInfo('AL_USDMayaPlugin', query=True, loaded=True) or cmds.loadPlugin('AL_USDMayaPlugin', quiet=True):
                    print("[Maya Utils] Using AL_usdmaya_ExportCommand")
                    cmds.AL_usdmaya_ExportCommand(
                        file=str(usd_file_path),
                        selection=True
                    )
                    return True
            except Exception as e:
                print(f"[Maya Utils] AL_USDMaya export failed: {e}")
            
            try:
                # Method 3: Pixar USD plugin
                if cmds.pluginInfo('pxrUsd', query=True, loaded=True) or cmds.loadPlugin('pxrUsd', quiet=True):
                    print("[Maya Utils] Using usdExport")
                    cmds.usdExport(
                        file=str(usd_file_path),
                        selection=True,
                        exportBlendShapes=include_blendshapes
                    )
                    return True
            except Exception as e:
                print(f"[Maya Utils] Pixar USD export failed: {e}")
            
            # Method 4: Fallback using OBJ export + USD conversion
            try:
                print("[Maya Utils] Trying fallback method: OBJ export + USD conversion")
                
                # Export to OBJ first
                obj_path = str(usd_file_path).replace('.usd', '.obj')
                cmds.file(obj_path, force=True, options="groups=1;ptgroups=1;materials=0;smoothing=1;normals=1", type="OBJexport", exportSelected=True)
                
                if Path(obj_path).exists():
                    print(f"[Maya Utils] OBJ exported successfully: {obj_path}")
                    
                    # Convert OBJ to USD using direct mesh data extraction
                    success = MayaUtils._convert_obj_to_usd(obj_path, str(usd_file_path))
                    
                    # Clean up OBJ file
                    Path(obj_path).unlink(missing_ok=True)
                    
                    if success:
                        print("[Maya Utils] OBJ to USD conversion successful")
                        return True
                    else:
                        print("[Maya Utils] OBJ to USD conversion failed")
                        
            except Exception as e:
                print(f"[Maya Utils] Fallback method failed: {e}")
            
            # Method 5: Direct mesh data extraction (no plugins needed)
            try:
                print("[Maya Utils] Trying direct mesh data extraction")
                return MayaUtils._export_mesh_data_to_usd(mesh_name, str(usd_file_path))
            except Exception as e:
                print(f"[Maya Utils] Direct mesh data extraction failed: {e}")
            
            # If all methods fail
            print("[Maya Utils] All export methods failed!")
            print("[Maya Utils] Tried: mayaUsdPlugin, AL_USDMayaPlugin, pxrUsd, OBJ fallback, direct extraction")
            return False
            
        except Exception as e:
            print(f"[Maya Utils] Error exporting to USD: {e}")
            traceback.print_exc()
            return False