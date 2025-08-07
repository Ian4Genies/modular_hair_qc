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
        history = cmds.listHistory(mesh_name, type="blendShape")
        blendshapes = []
        
        for blend_node in history:
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
            existing_blend_nodes = cmds.listHistory(base_mesh, type="blendShape")
            
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
    def import_usd_as_maya_geometry(usd_file_path: str, import_blendshapes: bool = True, import_skeletons: bool = False) -> List[str]:
        """
        Import USD file as native Maya DAG nodes for interactive editing
        
        Args:
            usd_file_path: Path to USD file
            import_blendshapes: Whether to import blendshapes
            import_skeletons: Whether to import skeletons
            
        Returns:
            List of imported Maya node names
        """
        try:
            # Use Maya's USD import command
            imported_nodes = []
            
            # Maya USD import options
            import_options = {
                'importUSDZTextures': True,
                'importBlendShapes': import_blendshapes,
                'importSkeletons': import_skeletons,
                'importInstances': False,  # Import as DAG nodes, not instances
                'importDisplayColor': True,
                'importPrimvars': True
            }
            
            # Try different USD import methods
            imported_nodes = []
            
            # Method 1: Try mayaUSDImport command
            try:
                print("[Maya Utils] Trying mayaUSDImport command")
                # Clear selection first
                cmds.select(clear=True)
                
                # Import USD file
                cmds.mayaUSDImport(
                    file=usd_file_path,
                    readAnimData=import_blendshapes,
                    importInstances=False
                )
                
                # Get what was imported (should be selected)
                imported_nodes = cmds.ls(selection=True) or []
                
                if imported_nodes:
                    print(f"[Maya Utils] mayaUSDImport successful: {imported_nodes}")
                else:
                    print("[Maya Utils] mayaUSDImport completed but no nodes selected")
                    
            except Exception as e:
                print(f"[Maya Utils] mayaUSDImport failed: {e}")
            
            # Method 2: Try file import if mayaUSDImport didn't work
            if not imported_nodes:
                try:
                    print("[Maya Utils] Trying file import with USD Import type")
                    cmds.select(clear=True)
                    
                    # Use file import with USD type
                    cmds.file(usd_file_path, i=True, type="USD Import", 
                             importTimeRange="combine", namespace="imported")
                    
                    imported_nodes = cmds.ls(selection=True) or []
                    
                    if imported_nodes:
                        print(f"[Maya Utils] File import successful: {imported_nodes}")
                    else:
                        print("[Maya Utils] File import completed but no nodes selected")
                        
                except Exception as e:
                    print(f"[Maya Utils] File import failed: {e}")
            
            # Method 3: Try basic file import without USD type
            if not imported_nodes:
                try:
                    print("[Maya Utils] Trying basic file import")
                    cmds.select(clear=True)
                    
                    # Get nodes before import
                    nodes_before = set(cmds.ls(long=True))
                    
                    # Basic file import
                    cmds.file(usd_file_path, i=True, namespace="imported")
                    
                    # Get nodes after import
                    nodes_after = set(cmds.ls(long=True))
                    
                    # Find new nodes
                    new_nodes = list(nodes_after - nodes_before)
                    imported_nodes = [node for node in new_nodes if not node.startswith("|imported:")]
                    
                    if imported_nodes:
                        print(f"[Maya Utils] Basic import successful: {imported_nodes}")
                    else:
                        print("[Maya Utils] Basic import completed but no new nodes found")
                        
                except Exception as e:
                    print(f"[Maya Utils] Basic file import failed: {e}")
            
            print(f"[Maya Utils] Imported {len(imported_nodes)} nodes from USD: {imported_nodes}")
            return imported_nodes
            
        except Exception as e:
            print(f"[Maya Utils] Error importing USD as Maya geometry: {e}")
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