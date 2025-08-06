"""
Maya integration utilities

Handles Maya-specific operations like geometry import, blendshape management,
and timeline manipulation.
"""

import maya.cmds as cmds
import maya.api.OpenMaya as om
from pathlib import Path
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
    def import_usd_as_maya_geometry(usd_file_path):
        """Import USD file as Maya geometry"""
        try:
            if not Path(usd_file_path).exists():
                raise FileNotFoundError(f"USD file not found: {usd_file_path}")
            
            # Use Maya's USD import
            imported_nodes = cmds.mayaUSDImport(file=str(usd_file_path), readAnimData=True)
            return imported_nodes
            
        except Exception as e:
            print(f"[Maya Utils] Error importing USD: {e}")
            traceback.print_exc()
            return []
    
    @staticmethod
    def export_mesh_to_usd(mesh_name, usd_file_path, include_blendshapes=True):
        """Export Maya mesh to USD file"""
        try:
            if not cmds.objExists(mesh_name):
                raise ValueError(f"Mesh does not exist: {mesh_name}")
            
            # Select the mesh
            cmds.select(mesh_name, replace=True)
            
            # Export to USD
            cmds.mayaUSDExport(
                file=str(usd_file_path),
                selection=True,
                exportBlendShapes=include_blendshapes
            )
            
            return True
            
        except Exception as e:
            print(f"[Maya Utils] Error exporting to USD: {e}")
            traceback.print_exc()
            return False