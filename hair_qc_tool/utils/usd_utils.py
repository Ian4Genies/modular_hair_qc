"""
USD utility classes and functions

Provides high-level interfaces for USD operations, including custom data serialization
for Hair QC Tool specific data types like BlendshapeRules and CrossModuleExclusions.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
import traceback

try:
    from pxr import Usd, UsdGeom, Sdf, UsdSkel
    USD_AVAILABLE = True
except ImportError:
    print("[Hair QC Tool] Warning: USD not available. Some features will be limited.")
    USD_AVAILABLE = False


class USDUtilsBase:
    """Base class for USD utilities with common functionality"""
    
    def __init__(self, usd_file_path: Union[str, Path]):
        self.file_path = Path(usd_file_path)
        self.stage = None
        self._is_dirty = False
    
    def open_stage(self, create_if_missing=False):
        """Open USD stage for reading/writing"""
        if not USD_AVAILABLE:
            raise RuntimeError("USD not available")
        
        try:
            if self.file_path.exists():
                self.stage = Usd.Stage.Open(str(self.file_path))
            elif create_if_missing:
                self.stage = Usd.Stage.CreateNew(str(self.file_path))
                self._is_dirty = True
            else:
                raise FileNotFoundError(f"USD file not found: {self.file_path}")
            
            return self.stage
        except Exception as e:
            print(f"[USD Utils] Error opening stage: {e}")
            return None
    
    def save_stage(self):
        """Save changes to USD file"""
        if not self.stage:
            print(f"[USD Utils] Cannot save - no stage loaded")
            return False
        
        if not self._is_dirty:
            print(f"[USD Utils] Stage not dirty, skipping save")
            return True
        
        try:
            print(f"[USD Utils] Saving stage to: {self.file_path}")
            self.stage.Save()
            self._is_dirty = False
            print(f"[USD Utils] Stage saved successfully")
            return True
        except Exception as e:
            print(f"[USD Utils] Error saving stage: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def close_stage(self):
        """Close USD stage"""
        if self.stage:
            self.stage = None
    
    def get_prim(self, prim_path: str):
        """Get prim by path"""
        if self.stage:
            return self.stage.GetPrimAtPath(prim_path)
        return None
    
    def create_prim(self, prim_path: str, prim_type: str = ""):
        """Create prim at path"""
        if self.stage:
            prim = self.stage.DefinePrim(prim_path, prim_type)
            self._is_dirty = True
            return prim
        return None
    
    def set_custom_data(self, prim_path: str, key: str, data: Any):
        """Set custom data on prim"""
        prim = self.get_prim(prim_path)
        if prim:
            # Serialize data to JSON string for storage
            json_data = json.dumps(data, indent=2)
            prim.SetCustomDataByKey(key, json_data)
            self._is_dirty = True
            return True
        return False
    
    def get_custom_data(self, prim_path: str, key: str, default=None):
        """Get custom data from prim"""
        prim = self.get_prim(prim_path)
        if prim and prim.HasCustomDataKey(key):
            try:
                json_data = prim.GetCustomDataByKey(key)
                return json.loads(json_data)
            except (json.JSONDecodeError, TypeError):
                print(f"[USD Utils] Warning: Invalid JSON data for key '{key}' on prim '{prim_path}'")
        return default
    
    def list_prims(self, root_path: str = "/") -> List[str]:
        """List all prims under root path"""
        if not self.stage:
            return []
        
        prims = []
        root_prim = self.get_prim(root_path)
        if root_prim:
            for prim in Usd.PrimRange(root_prim):
                prims.append(str(prim.GetPath()))
        return prims


class USDGroupUtils(USDUtilsBase):
    """Utility class for Group USD operations"""
    
    def create_group_structure(self, group_name: str, group_type: str = ""):
        """Create basic group USD structure"""
        if not self.open_stage(create_if_missing=True):
            return False
        
        try:
            # Create root prim with variants
            root_prim = self.create_prim("/HairGroup")
            if root_prim:
                # Set group type variant
                variant_set = root_prim.GetVariantSets().AddVariantSet("groupType")
                variant_set.AddVariant(group_type or group_name)
                variant_set.SetVariantSelection(group_type or group_name)
                
                # Create module whitelist structure
                self.create_prim("/HairGroup/ModuleWhitelist")
                self.create_prim("/HairGroup/ModuleWhitelist/Crown")
                self.create_prim("/HairGroup/ModuleWhitelist/Tail")
                self.create_prim("/HairGroup/ModuleWhitelist/Bang")
                self.create_prim("/HairGroup/ModuleWhitelist/Scalp")
                
                # Create alpha whitelist structure
                self.create_prim("/HairGroup/AlphaWhitelist")
                self.create_prim("/HairGroup/AlphaWhitelist/Scalp")
                self.create_prim("/HairGroup/AlphaWhitelist/Scalp/fade")
                self.create_prim("/HairGroup/AlphaWhitelist/Scalp/hairline")
                self.create_prim("/HairGroup/AlphaWhitelist/Scalp/sideburn")
                
                # Create cross-module rules structure
                self.create_prim("/HairGroup/CrossModuleRules")
                self.create_prim("/HairGroup/CrossModuleRules/Exclusions")
                self.create_prim("/HairGroup/CrossModuleRules/WeightConstraints")
                
                return self.save_stage()
        
        except Exception as e:
            print(f"[USD Group Utils] Error creating group structure: {e}")
            return False
    
    def get_module_whitelist(self, module_type: str = None) -> Dict[str, Dict[str, Any]]:
        """
        Get module whitelist. 
        
        Args:
            module_type: Specific type to get (deprecated, use get_module_whitelist_by_type)
            
        Returns:
            Dictionary of {module_name: {"type": type, "enabled": bool}}
        """
        if not self.stage:
            self.open_stage()
        
        # If module_type is specified, return old format for backward compatibility
        if module_type:
            files = self.get_custom_data(f"/HairGroup/ModuleWhitelist/{module_type}", "moduleFiles", [])
            # Convert to new format
            result = {}
            for file_path in files:
                # Extract module name from path like "@module/scalp/scalp.usd@"
                if file_path.startswith("@") and file_path.endswith("@"):
                    path_parts = file_path[1:-1].split("/")
                    if len(path_parts) >= 3:
                        module_name = path_parts[-1].replace(".usd", "")
                        result[module_name] = {"type": module_type.lower(), "enabled": True}
            return result
        
        # Get all modules from all types
        all_modules = {}
        module_types = ["Crown", "Tail", "Bang", "Scalp"]  # USD uses capitalized names
        
        for usd_type in module_types:
            files = self.get_custom_data(f"/HairGroup/ModuleWhitelist/{usd_type}", "moduleFiles", [])
            for file_path in files:
                # Extract module name from path like "@module/scalp/scalp.usd@"
                if file_path.startswith("@") and file_path.endswith("@"):
                    path_parts = file_path[1:-1].split("/")
                    if len(path_parts) >= 3:
                        module_name = path_parts[-1].replace(".usd", "")
                        all_modules[module_name] = {"type": usd_type.lower(), "enabled": True}
        
        return all_modules
    
    def get_module_whitelist_by_type(self, module_type: str) -> List[str]:
        """Get module whitelist for specific type (returns list of file paths)"""
        if not self.stage:
            self.open_stage()
        
        return self.get_custom_data(f"/HairGroup/ModuleWhitelist/{module_type}", "moduleFiles", [])
    
    def set_module_whitelist(self, module_whitelist: Dict[str, Dict[str, Any]]):
        """
        Set complete module whitelist across all types
        
        Args:
            module_whitelist: Dictionary of {module_name: {"type": type, "enabled": bool}}
        """
        if not self.stage:
            self.open_stage()
        
        # Group modules by type
        modules_by_type = {"Crown": [], "Tail": [], "Bang": [], "Scalp": []}
        
        for module_name, module_info in module_whitelist.items():
            module_type = module_info.get("type", "scalp").lower()
            enabled = module_info.get("enabled", True)
            
            if enabled:  # Only add enabled modules
                # Convert to USD path format
                usd_path = f"@module/{module_type}/{module_name}.usd@"
                
                # Add to appropriate type (capitalize for USD)
                usd_type = module_type.capitalize()
                if usd_type in modules_by_type:
                    modules_by_type[usd_type].append(usd_path)
        
        # Set each type's whitelist
        for usd_type, module_files in modules_by_type.items():
            self.set_custom_data(f"/HairGroup/ModuleWhitelist/{usd_type}", "moduleFiles", module_files)
        
        return True
    
    def set_module_whitelist_by_type(self, module_type: str, module_files: List[str]):
        """Set module whitelist for specific type (legacy method)"""
        if not self.stage:
            self.open_stage()
        
        return self.set_custom_data(f"/HairGroup/ModuleWhitelist/{module_type}", "moduleFiles", module_files)
    
    def get_alpha_whitelist(self, category: str) -> List[str]:
        """Get alpha texture whitelist for category"""
        if not self.stage:
            self.open_stage()
        
        return self.get_custom_data(f"/HairGroup/AlphaWhitelist/Scalp/{category}", "whitelistedTextures", [])
    
    def set_alpha_whitelist(self, category: str, texture_files: List[str]):
        """Set alpha texture whitelist for category"""
        if not self.stage:
            self.open_stage()
        
        return self.set_custom_data(f"/HairGroup/AlphaWhitelist/Scalp/{category}", "whitelistedTextures", texture_files)
    
    def set_alpha_whitelist_dict(self, whitelist_dict: Dict[str, bool]):
        """Set alpha whitelist from dictionary format {texture_path: enabled}"""
        if not self.stage:
            self.open_stage()
        
        # Store the whitelist as a flat dictionary at the group level
        return self.set_custom_data("/HairGroup/AlphaWhitelist", "textureWhitelist", whitelist_dict)
    
    def get_alpha_whitelist_dict(self) -> Dict[str, bool]:
        """Get alpha whitelist as dictionary format {texture_path: enabled}"""
        if not self.stage:
            self.open_stage()
        
        return self.get_custom_data("/HairGroup/AlphaWhitelist", "textureWhitelist", {})
    
    def get_cross_module_exclusions(self) -> Dict[str, Any]:
        """Get all cross-module exclusions"""
        if not self.stage:
            self.open_stage()
        
        return self.get_custom_data("/HairGroup/CrossModuleRules/Exclusions", "exclusionRules", {})
    
    def set_cross_module_exclusions(self, exclusions: Dict[str, Any]):
        """Set cross-module exclusions"""
        if not self.stage:
            self.open_stage()
        
        return self.set_custom_data("/HairGroup/CrossModuleRules/Exclusions", "exclusionRules", exclusions)
    
    def get_weight_constraints(self) -> Dict[str, Any]:
        """Get all weight constraints"""
        if not self.stage:
            self.open_stage()
        
        return self.get_custom_data("/HairGroup/CrossModuleRules/WeightConstraints", "constraintRules", {})
    
    def set_weight_constraints(self, constraints: Dict[str, Any]):
        """Set weight constraints"""
        if not self.stage:
            self.open_stage()
        
        return self.set_custom_data("/HairGroup/CrossModuleRules/WeightConstraints", "constraintRules", constraints)


class USDModuleUtils(USDUtilsBase):
    """Utility class for Module USD operations"""
    
    def create_module_structure(self, module_name: str, module_type: str):
        """Create basic module USD structure"""
        if not self.open_stage(create_if_missing=True):
            return False
        
        try:
            # Create root prim with variants
            root_prim = self.create_prim("/HairModule")
            if root_prim:
                # Set as default prim for proper USD import
                self.stage.SetDefaultPrim(root_prim)
                
                # Set module type variant
                variant_set = root_prim.GetVariantSets().AddVariantSet("moduleType")
                variant_set.AddVariant(module_type)
                variant_set.SetVariantSelection(module_type)
                
                # Create basic structure
                self.create_prim("/HairModule/BaseMesh", "Mesh")
                self.create_prim("/HairModule/BlendShapes")
                self.create_prim("/HairModule/BlendshapeExclusions")
                
                # Create UsdSkel animation structure for proper blendshape weight control
                anim_prim = self.create_prim("/HairModule/Animation", "SkelAnimation")
                
                # Apply SkelBindingAPI to the root and bind the animation
                from pxr import UsdSkel
                binding_api = UsdSkel.BindingAPI.Apply(root_prim)
                binding_api.CreateAnimationSourceRel().SetTargets(["/HairModule/Animation"])
                
                # Create texture assets structure (no materials for now)
                self.create_prim("/HairModule/TextureAssets")
                self.create_prim("/HairModule/TextureAssets/WhitelistedTextures")
                self.create_prim("/HairModule/TextureAssets/WhitelistedTextures/NormalTextures")
                self.create_prim("/HairModule/TextureAssets/WhitelistedTextures/AlphaSlots")
                
                # Optional alpha blacklist
                if module_type != "scalp":  # Only non-scalp modules can blacklist scalp alphas
                    self.create_prim("/HairModule/AlphaBlacklist")
                    self.create_prim("/HairModule/AlphaBlacklist/Scalp")
                    self.create_prim("/HairModule/AlphaBlacklist/Scalp/fade")
                    self.create_prim("/HairModule/AlphaBlacklist/Scalp/hairline")
                    self.create_prim("/HairModule/AlphaBlacklist/Scalp/sideburn")
                
                return self.save_stage()
        
        except Exception as e:
            print(f"[USD Module Utils] Error creating module structure: {e}")
            return False
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get basic module information"""
        if not self.stage:
            self.open_stage()
        
        try:
            # Get module type from variant
            root_prim = self.stage.GetPrimAtPath("/HairModule")
            if not root_prim or not root_prim.IsValid():
                return {}
            
            module_type = "unknown"
            variant_sets = root_prim.GetVariantSets()
            if variant_sets.HasVariantSet("moduleType"):
                variant_set = variant_sets.GetVariantSet("moduleType")
                module_type = variant_set.GetVariantSelection()
            
            return {
                "type": module_type,
                "name": self.file_path.stem if self.file_path else "unknown",
                "has_geometry": self.has_geometry_data(),
                "blendshape_count": len(self.get_blendshape_names())
            }
            
        except Exception as e:
            print(f"[USD Module Utils] Error getting module info: {e}")
            return {}
    
    def has_geometry_data(self) -> bool:
        """Check if module has geometry data"""
        if not self.stage:
            self.open_stage()
        
        try:
            from pxr import UsdGeom
            base_mesh = self.stage.GetPrimAtPath("/HairModule/BaseMesh")
            
            if not base_mesh or not base_mesh.IsValid():
                return False
            
            # Check if it's actually a mesh with geometry data
            if not base_mesh.IsA(UsdGeom.Mesh):
                return False
            
            mesh = UsdGeom.Mesh(base_mesh)
            points_attr = mesh.GetPointsAttr()
            
            # Check if points attribute exists and has actual data
            if not points_attr or not points_attr.HasValue():
                return False
            
            # Get the points data and check if it's not empty
            points = points_attr.Get()
            return points is not None and len(points) > 0
            
        except Exception as e:
            print(f"[USD Module Utils] Error checking geometry data: {e}")
            return False
    
    def import_geometry_from_maya(self, maya_object_name: str) -> bool:
        """Import geometry from Maya object to USD"""
        if not self.stage:
            self.open_stage()
        
        try:
            from .maya_utils import MayaUtils
            
            # Check if the Maya object exists
            import maya.cmds as cmds
            if not cmds.objExists(maya_object_name):
                print(f"[USD Module Utils] Maya object '{maya_object_name}' does not exist")
                return False
            
            print(f"[USD Module Utils] Starting geometry import from '{maya_object_name}'")
            
            # Export the Maya mesh to a temporary USD file
            temp_usd_path = self.file_path.parent / f"temp_{maya_object_name}.usd"
            print(f"[USD Module Utils] Exporting to temp file: {temp_usd_path}")
            
            # Use Maya utils to export mesh to USD
            success = MayaUtils.export_mesh_to_usd(maya_object_name, str(temp_usd_path), include_blendshapes=False)
            
            if not success:
                print(f"[USD Module Utils] Failed to export Maya mesh to USD")
                return False
            
            if not temp_usd_path.exists():
                print(f"[USD Module Utils] Temp USD file was not created: {temp_usd_path}")
                return False
            
            print(f"[USD Module Utils] Temp USD file created successfully")
            
            # Import the geometry from temp USD into our BaseMesh
            from pxr import Usd, UsdGeom, Sdf
            
            temp_stage = Usd.Stage.Open(str(temp_usd_path))
            if not temp_stage:
                print(f"[USD Module Utils] Failed to open temp USD stage")
                temp_usd_path.unlink(missing_ok=True)
                return False
            
            print(f"[USD Module Utils] Opened temp USD stage")
            
            # Find and extract mesh data from temp stage
            mesh_found = False
            mesh_data = {}
            
            # Extract all mesh data while temp stage is still valid
            for prim in temp_stage.Traverse():
                if prim.IsA(UsdGeom.Mesh):
                    print(f"[USD Module Utils] Found mesh prim: {prim.GetPath()}")
                    
                    source_mesh = UsdGeom.Mesh(prim)
                    
                    # Extract all mesh data
                    if source_mesh.GetPointsAttr().HasValue():
                        mesh_data['points'] = source_mesh.GetPointsAttr().Get()
                        print(f"[USD Module Utils] Extracted {len(mesh_data['points'])} points")
                    
                    if source_mesh.GetFaceVertexIndicesAttr().HasValue():
                        mesh_data['indices'] = source_mesh.GetFaceVertexIndicesAttr().Get()
                        print(f"[USD Module Utils] Extracted {len(mesh_data['indices'])} face vertex indices")
                    
                    if source_mesh.GetFaceVertexCountsAttr().HasValue():
                        mesh_data['counts'] = source_mesh.GetFaceVertexCountsAttr().Get()
                        print(f"[USD Module Utils] Extracted {len(mesh_data['counts'])} face vertex counts")
                    
                    # Also extract normals if available
                    try:
                        if source_mesh.GetNormalsAttr().HasValue():
                            mesh_data['normals'] = source_mesh.GetNormalsAttr().Get()
                            print(f"[USD Module Utils] Extracted {len(mesh_data['normals'])} normals")
                    except Exception as e:
                        print(f"[USD Module Utils] Could not extract normals: {e}")
                    
                    # Extract UVs if available
                    try:
                        # Try to get UV primvar using correct USD API
                        primvars_api = UsdGeom.PrimvarsAPI(prim)
                        uv_primvar = primvars_api.GetPrimvar('st')
                        if not uv_primvar:
                            uv_primvar = primvars_api.GetPrimvar('uv')
                        
                        if uv_primvar and uv_primvar.HasValue():
                            mesh_data['uvs'] = uv_primvar.Get()
                            print(f"[USD Module Utils] Extracted {len(mesh_data['uvs'])} UV coordinates")
                    except Exception as e:
                        print(f"[USD Module Utils] Could not extract UVs (this is optional): {e}")
                        # UVs are optional, continue without them
                    
                    mesh_found = True
                    break
            
            # Release temp stage now that we have the data
            temp_stage = None
            
            # Now apply the mesh data to our module
            if mesh_found and mesh_data:
                # Ensure BaseMesh is a proper mesh
                base_mesh_prim = self.stage.GetPrimAtPath("/HairModule/BaseMesh")
                if not base_mesh_prim or not base_mesh_prim.IsA(UsdGeom.Mesh):
                    print(f"[USD Module Utils] Creating/redefining BaseMesh as UsdGeom.Mesh")
                    if base_mesh_prim:
                        self.stage.RemovePrim(base_mesh_prim.GetPath())
                    base_mesh_prim = UsdGeom.Mesh.Define(self.stage, "/HairModule/BaseMesh").GetPrim()
                
                target_mesh = UsdGeom.Mesh(base_mesh_prim)
                
                # Apply mesh data
                copied_data = False
                if 'points' in mesh_data:
                    target_mesh.GetPointsAttr().Set(mesh_data['points'])
                    self._is_dirty = True
                    copied_data = True
                
                if 'indices' in mesh_data:
                    target_mesh.GetFaceVertexIndicesAttr().Set(mesh_data['indices'])
                    self._is_dirty = True
                    copied_data = True
                
                if 'counts' in mesh_data:
                    target_mesh.GetFaceVertexCountsAttr().Set(mesh_data['counts'])
                    self._is_dirty = True
                    copied_data = True
                
                if 'normals' in mesh_data:
                    try:
                        target_mesh.GetNormalsAttr().Set(mesh_data['normals'])
                        print(f"[USD Module Utils] Applied normals")
                    except Exception as e:
                        print(f"[USD Module Utils] Could not apply normals: {e}")
                
                if 'uvs' in mesh_data:
                    # Create UV primvar using correct API
                    try:
                        primvars_api = UsdGeom.PrimvarsAPI(base_mesh_prim)
                        uv_primvar = primvars_api.CreatePrimvar('st', Sdf.ValueTypeNames.TexCoord2fArray, UsdGeom.Tokens.faceVarying)
                        uv_primvar.Set(mesh_data['uvs'])
                        print(f"[USD Module Utils] Applied UV coordinates")
                    except Exception as e:
                        print(f"[USD Module Utils] Could not apply UVs: {e}")
                        # UVs are optional, continue without them
                
                if copied_data:
                    # Store metadata
                    base_mesh_prim.SetCustomDataByKey("maya_source", maya_object_name)
                    base_mesh_prim.SetCustomDataByKey("imported", True)
                    
                    # Mark stage as dirty and save
                    self._is_dirty = True
                    self.save_stage()
                    
                    print(f"[USD Module Utils] Successfully imported geometry from '{maya_object_name}'")
                else:
                    print(f"[USD Module Utils] No geometry data found in mesh")
                    mesh_found = False
            
            # Clean up temp file
            try:
                temp_usd_path.unlink(missing_ok=True)
                print(f"[USD Module Utils] Cleaned up temp file: {temp_usd_path}")
            except PermissionError as e:
                print(f"[USD Module Utils] Warning: Could not delete temp file (file may be in use): {e}")
                # File will be cleaned up later or on next run
            except Exception as e:
                print(f"[USD Module Utils] Warning: Error cleaning up temp file: {e}")
            
            if not mesh_found:
                print(f"[USD Module Utils] No mesh prim found in exported USD")
                return False
            
            return True
            
        except Exception as e:
            # Check if this is just a cleanup error after successful import
            error_msg = str(e)
            if "Access is denied" in error_msg and "temp_" in error_msg:
                print(f"[USD Module Utils] Geometry import succeeded, but temp file cleanup failed: {e}")
                print(f"[USD Module Utils] This is not a critical error - geometry was imported successfully")
                return True
            else:
                print(f"[USD Module Utils] Error importing geometry: {e}")
                import traceback
                traceback.print_exc()
                return False
    
    def export_geometry_to_maya(self, target_name: str) -> str:
        """Export USD geometry to Maya"""
        if not self.stage:
            self.open_stage()
        
        try:
            from .maya_utils import MayaUtils
            
            # Check if BaseMesh has geometry
            base_mesh_prim = self.stage.GetPrimAtPath("/HairModule/BaseMesh")
            if not base_mesh_prim or not base_mesh_prim.IsValid():
                print("[USD Module Utils] No BaseMesh found in module")
                return None
            
            from pxr import UsdGeom
            if not base_mesh_prim.IsA(UsdGeom.Mesh):
                print("[USD Module Utils] BaseMesh is not a valid mesh")
                return None
            
            # Create temporary USD file with just the mesh
            temp_usd_path = self.file_path.parent / f"temp_export_{target_name}.usd"
            
            from pxr import Usd
            temp_stage = Usd.Stage.CreateNew(str(temp_usd_path))
            
            # Copy the mesh to temp stage
            temp_mesh_prim = UsdGeom.Mesh.Define(temp_stage, f"/{target_name}").GetPrim()
            source_mesh = UsdGeom.Mesh(base_mesh_prim)
            target_mesh = UsdGeom.Mesh(temp_mesh_prim)
            
            # Set the mesh as the default prim
            temp_stage.SetDefaultPrim(temp_mesh_prim)
            
            # Copy mesh data
            if source_mesh.GetPointsAttr().HasValue():
                points = source_mesh.GetPointsAttr().Get()
                target_mesh.GetPointsAttr().Set(points)
                print(f"[USD Module Utils] Copied {len(points)} points to temp USD")
            
            if source_mesh.GetFaceVertexIndicesAttr().HasValue():
                indices = source_mesh.GetFaceVertexIndicesAttr().Get()
                target_mesh.GetFaceVertexIndicesAttr().Set(indices)
                print(f"[USD Module Utils] Copied {len(indices)} face indices to temp USD")
            
            if source_mesh.GetFaceVertexCountsAttr().HasValue():
                counts = source_mesh.GetFaceVertexCountsAttr().Get()
                target_mesh.GetFaceVertexCountsAttr().Set(counts)
                print(f"[USD Module Utils] Copied {len(counts)} face counts to temp USD")
            
            print(f"[USD Module Utils] Saving temp USD with default prim: {temp_mesh_prim.GetPath()}")
            temp_stage.Save()
            
            # Release temp stage before import
            temp_stage = None
            
            # Import USD into Maya
            imported_nodes = MayaUtils.import_usd_as_maya_geometry(str(temp_usd_path))
            
            # Clean up temp file
            try:
                temp_usd_path.unlink(missing_ok=True)
                print(f"[USD Module Utils] Cleaned up temp export file: {temp_usd_path}")
            except PermissionError as e:
                print(f"[USD Module Utils] Warning: Could not delete temp export file (file may be in use): {e}")
                # File will be cleaned up later
            except Exception as e:
                print(f"[USD Module Utils] Warning: Error cleaning up temp export file: {e}")
            
            if imported_nodes and len(imported_nodes) > 0:
                # Get the first imported node (should be our mesh)
                maya_node = imported_nodes[0]
                print(f"[USD Module Utils] Imported node: {maya_node}")
                
                # Rename to target name if different
                import maya.cmds as cmds
                if cmds.objExists(maya_node) and maya_node != target_name:
                    try:
                        maya_node = cmds.rename(maya_node, target_name)
                        print(f"[USD Module Utils] Renamed to: {maya_node}")
                    except:
                        print(f"[USD Module Utils] Could not rename, keeping original name: {maya_node}")
                        pass  # Keep original name if rename fails
                
                return maya_node
            
            return None
            
        except Exception as e:
            # Check if this is just a cleanup error after successful export
            error_msg = str(e)
            if "Access is denied" in error_msg and "temp_export_" in error_msg:
                print(f"[USD Module Utils] Geometry export succeeded, but temp file cleanup failed: {e}")
                print(f"[USD Module Utils] This is not a critical error - geometry was exported successfully")
                # Return the maya_node if it was created successfully
                if 'maya_node' in locals() and maya_node:
                    return maya_node
                elif 'imported_nodes' in locals() and imported_nodes and len(imported_nodes) > 0:
                    return imported_nodes[0]
            
            print(f"[USD Module Utils] Error exporting geometry: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def add_blendshape_from_maya(self, maya_object_name: str, blendshape_name: str) -> bool:
        """Add a blendshape from Maya object with proper USD BlendShape schema"""
        if not self.stage:
            self.open_stage()
        
        try:
            from pxr import UsdSkel, UsdGeom, Gf
            import maya.cmds as cmds
            
            # Get base mesh for comparison
            base_mesh_prim = self.get_prim("/HairModule/BaseMesh")
            if not base_mesh_prim or not UsdGeom.Mesh(base_mesh_prim):
                print(f"[USD Module Utils] No base mesh found for blendshape comparison")
                return False
            
            base_mesh = UsdGeom.Mesh(base_mesh_prim)
            base_points_attr = base_mesh.GetPointsAttr()
            if not base_points_attr:
                print(f"[USD Module Utils] Base mesh has no points")
                return False
                
            base_points = base_points_attr.Get()
            if not base_points:
                print(f"[USD Module Utils] Could not read base mesh points")
                return False
            
            # Get target mesh points from Maya
            if not cmds.objExists(maya_object_name):
                print(f"[USD Module Utils] Maya object '{maya_object_name}' not found")
                return False
            
            # Get mesh points from Maya
            target_points = []
            try:
                # Get vertex positions
                vertex_count = cmds.polyEvaluate(maya_object_name, vertex=True)
                for i in range(vertex_count):
                    pos = cmds.pointPosition(f"{maya_object_name}.vtx[{i}]", world=True)
                    target_points.append(Gf.Vec3f(pos[0], pos[1], pos[2]))
            except Exception as maya_error:
                print(f"[USD Module Utils] Error reading Maya mesh points: {maya_error}")
                return False
            
            # Verify point counts match
            if len(target_points) != len(base_points):
                print(f"[USD Module Utils] Point count mismatch: base={len(base_points)}, target={len(target_points)}")
                return False
            
            # Calculate offsets (target - base)
            offsets = []
            for i in range(len(base_points)):
                offset = target_points[i] - base_points[i]
                offsets.append(offset)
            
            # Create proper USD BlendShape prim
            blendshape_path = f"/HairModule/BlendShapes/{blendshape_name}"
            blendshape_prim = UsdSkel.BlendShape.Define(self.stage, blendshape_path)
            
            if blendshape_prim:
                # Set the offsets attribute (this is what makes it a real blendshape)
                offsets_attr = blendshape_prim.CreateOffsetsAttr()
                offsets_attr.Set(offsets)
                
                # Create the weight attribute for interactive control
                from pxr import Sdf
                prim = blendshape_prim.GetPrim()
                weight_attr = prim.CreateAttribute("weight", Sdf.ValueTypeNames.Float)
                weight_attr.Set(0.0)  # Default weight
                
                # Store Maya source info as custom data
                prim = blendshape_prim.GetPrim()
                prim.SetCustomDataByKey("maya_source", maya_object_name)
                prim.SetCustomDataByKey("default_weight", 0.0)
                
                # Update the SkelAnimation to include this blendshape
                self._update_skel_animation_blendshapes()
                
                # Mark stage as dirty and save immediately
                self._is_dirty = True
                self.save_stage()
                
                print(f"[USD Module Utils] Created and saved BlendShape '{blendshape_name}' with {len(offsets)} offsets and weight attribute")
                return True
            else:
                print(f"[USD Module Utils] Failed to create BlendShape prim")
                return False
                
        except Exception as e:
            print(f"[USD Module Utils] Error adding blendshape from Maya: {e}")
            return False
    
    def _update_skel_animation_blendshapes(self):
        """Update the UsdSkelAnimation with current blendshapes for proper Maya USD integration"""
        if not self.stage:
            return False
        
        try:
            # Get or create the SkelAnimation prim
            anim_path = "/HairModule/Animation"
            anim_prim = self.stage.GetPrimAtPath(anim_path)
            
            if not anim_prim.IsValid():
                anim_prim = UsdSkel.Animation.Define(self.stage, anim_path).GetPrim()
            
            # Get all blendshapes
            blendshapes_prim = self.stage.GetPrimAtPath("/HairModule/BlendShapes")
            if not blendshapes_prim.IsValid():
                return False
            
            # Collect all blendshape names and weights
            blendshape_names = []
            blendshape_weights = []
            
            for child in blendshapes_prim.GetChildren():
                if UsdSkel.BlendShape(child):
                    blendshape_names.append(child.GetName())
                    # Get current weight (default to 0.0)
                    weight_attr = child.GetAttribute("weight")
                    if weight_attr and weight_attr.IsValid():
                        weight = weight_attr.Get()
                        if weight is None:
                            weight = 0.0
                    else:
                        weight = 0.0
                    blendshape_weights.append(float(weight))
            
            if blendshape_names:
                # Set up the SkelAnimation with blendshape data
                skel_anim = UsdSkel.Animation(anim_prim)
                
                # Set blendShapes array (names of blendshapes)
                blend_shapes_attr = skel_anim.CreateBlendShapesAttr()
                blend_shapes_attr.Set(blendshape_names)
                
                # Set blendShapeWeights array (current weights)
                blend_weights_attr = skel_anim.CreateBlendShapeWeightsAttr()
                blend_weights_attr.Set(blendshape_weights)
                
                print(f"[USD Module Utils] Updated SkelAnimation with {len(blendshape_names)} blendshapes: {blendshape_names}")
                return True
            else:
                print("[USD Module Utils] No blendshapes found to update SkelAnimation")
                return False
                
        except Exception as e:
            print(f"[USD Module Utils] Error updating SkelAnimation: {e}")
            return False
    
    def set_blendshape_weight_via_animation(self, blendshape_name: str, weight: float) -> bool:
        """Set blendshape weight using UsdSkelAnimation (proper Maya USD approach)"""
        if not self.stage:
            self.open_stage()
        
        try:
            # Get the SkelAnimation prim
            anim_path = "/HairModule/Animation"
            anim_prim = self.stage.GetPrimAtPath(anim_path)
            
            if not anim_prim.IsValid():
                print(f"[USD Module Utils] No SkelAnimation found at {anim_path}")
                return False
            
            skel_anim = UsdSkel.Animation(anim_prim)
            
            # Get current blendshape names and weights
            blend_shapes_attr = skel_anim.GetBlendShapesAttr()
            blend_weights_attr = skel_anim.GetBlendShapeWeightsAttr()
            
            if not blend_shapes_attr or not blend_weights_attr:
                print("[USD Module Utils] SkelAnimation missing blendShapes or blendShapeWeights attributes")
                return False
            
            # Get current arrays
            blendshape_names = blend_shapes_attr.Get()
            blendshape_weights = blend_weights_attr.Get()
            
            if not blendshape_names or not blendshape_weights:
                print("[USD Module Utils] Empty blendshape arrays in SkelAnimation")
                return False
            
            # Debug output
            print(f"[USD Module Utils] Found {len(blendshape_names)} blendshapes in SkelAnimation: {list(blendshape_names)}")
            print(f"[USD Module Utils] Current weights: {list(blendshape_weights)}")
            print(f"[USD Module Utils] Looking for blendshape: '{blendshape_name}'")
            
            # Find the index of our blendshape
            try:
                # Convert TokenArray to list to use index() method
                blendshape_names_list = list(blendshape_names)
                blend_index = blendshape_names_list.index(blendshape_name)
            except (ValueError, AttributeError) as e:
                print(f"[USD Module Utils] Blendshape '{blendshape_name}' not found in SkelAnimation or error accessing blendshape names: {e}")
                return False
            
            # Update the weight at that index
            blendshape_weights = list(blendshape_weights)  # Convert to mutable list
            blendshape_weights[blend_index] = float(weight)
            
            # Set the updated weights back to the attribute
            blend_weights_attr.Set(blendshape_weights)
            
            # Also update the individual blendshape prim weight for consistency
            blendshape_prim_path = f"/HairModule/BlendShapes/{blendshape_name}"
            blendshape_prim = self.stage.GetPrimAtPath(blendshape_prim_path)
            if blendshape_prim.IsValid():
                weight_attr = blendshape_prim.GetAttribute("weight")
                if weight_attr:
                    weight_attr.Set(float(weight))
                    print(f"[USD Module Utils] Also updated individual blendshape prim weight")
            
            # Mark stage as dirty (but don't save immediately for interactive performance)
            self._is_dirty = True
            
            # Verify the weight was set correctly
            verification_weights = blend_weights_attr.Get()
            if verification_weights and len(verification_weights) > blend_index:
                actual_weight = verification_weights[blend_index]
                print(f"[USD Module Utils] Set blendshape '{blendshape_name}' weight to {actual_weight} (in-memory)")
            
            return True
            
        except Exception as e:
            print(f"[USD Module Utils] Error setting blendshape weight via animation: {e}")
            return False
    
    def get_blendshape_names(self) -> List[str]:
        """Get all blendshape names in this module"""
        if not self.stage:
            self.open_stage()
        
        blendshapes = []
        blendshape_prim = self.get_prim("/HairModule/BlendShapes")
        if blendshape_prim:
            for child in blendshape_prim.GetChildren():
                blendshapes.append(child.GetName())
        return blendshapes
    
    def get_blendshapes_with_weights(self) -> Dict[str, float]:
        """Get blendshape data (names and weights) from USD BlendShape schema"""
        if not self.stage:
            self.open_stage()
        
        blendshapes = {}
        blendshapes_prim = self.get_prim("/HairModule/BlendShapes")
        if blendshapes_prim:
            for child in blendshapes_prim.GetChildren():
                name = child.GetName()
                
                # Try to get weight from USD BlendShape schema
                weight = 0.0
                try:
                    from pxr import UsdSkel
                    blendshape_schema = UsdSkel.BlendShape(child)
                    if blendshape_schema:
                        # Use the weight attribute on the prim
                        weight_attr = child.GetAttribute("weight")
                        if weight_attr:
                            weight_value = weight_attr.Get()
                            if weight_value is not None:
                                weight = float(weight_value)
                        else:
                            # Fallback to custom data
                            custom_weight = child.GetCustomDataByKey("default_weight")
                            if custom_weight is not None:
                                weight = float(custom_weight)
                except Exception as e:
                    print(f"[USD Module Utils] Warning: Error reading blendshape weight for {name}: {e}")
                    # Fallback to custom data
                    custom_weight = child.GetCustomDataByKey("default_weight")
                    if custom_weight is not None:
                        weight = float(custom_weight)
                
                blendshapes[name] = weight
        return blendshapes
    
    def add_blendshape(self, blendshape_name: str):
        """Add a blendshape to the module"""
        if not self.stage:
            self.open_stage()
        
        blendshape_prim = self.create_prim(f"/HairModule/BlendShapes/{blendshape_name}")
        return blendshape_prim is not None
    
    def remove_blendshape(self, blendshape_name: str):
        """Remove a blendshape from the module"""
        if not self.stage:
            self.open_stage()
        
        try:
            blendshape_prim = self.stage.GetPrimAtPath(f"/HairModule/BlendShapes/{blendshape_name}")
            if blendshape_prim and blendshape_prim.IsValid():
                self.stage.RemovePrim(blendshape_prim.GetPath())
                return True
            return False
        except Exception as e:
            print(f"[USD Module Utils] Error removing blendshape: {e}")
            return False
    
    def set_blendshapes(self, blendshape_data: Dict[str, float]):
        """Set blendshape data (names and weights)"""
        if not self.stage:
            self.open_stage()
        
        try:
            # Clear existing blendshapes
            blendshapes_prim = self.get_prim("/HairModule/BlendShapes")
            if blendshapes_prim:
                for child in blendshapes_prim.GetChildren():
                    self.stage.RemovePrim(child.GetPath())
            
            # Add new blendshapes
            for blendshape_name, weight in blendshape_data.items():
                blendshape_prim = self.create_prim(f"/HairModule/BlendShapes/{blendshape_name}")
                if blendshape_prim:
                    # Store weight as custom data
                    blendshape_prim.SetCustomDataByKey("weight", weight)
            
            return True
        except Exception as e:
            print(f"[USD Module Utils] Error setting blendshapes: {e}")
            return False
    
    def get_internal_exclusions(self) -> Dict[str, List[str]]:
        """Get internal blendshape exclusions"""
        if not self.stage:
            self.open_stage()
        
        return self.get_custom_data("/HairModule/BlendshapeExclusions", "internalExclusions", {})
    
    def set_internal_exclusions(self, exclusions: Dict[str, List[str]]):
        """Set internal blendshape exclusions"""
        if not self.stage:
            self.open_stage()
        
        return self.set_custom_data("/HairModule/BlendshapeExclusions", "internalExclusions", exclusions)
    
    def get_alpha_blacklist(self, category: str) -> List[str]:
        """Get alpha texture blacklist for category"""
        if not self.stage:
            self.open_stage()
        
        return self.get_custom_data(f"/HairModule/AlphaBlacklist/Scalp/{category}", "blacklistedTextures", [])
    
    def set_alpha_blacklist(self, category: str, texture_files: List[str]):
        """Set alpha texture blacklist for category"""
        if not self.stage:
            self.open_stage()
        
        return self.set_custom_data(f"/HairModule/AlphaBlacklist/Scalp/{category}", "blacklistedTextures", texture_files)


class USDStyleUtils(USDUtilsBase):
    """Utility class for Style USD operations"""
    
    def create_style_structure(self, style_name: str):
        """Create basic style USD structure"""
        if not self.open_stage(create_if_missing=True):
            return False
        
        try:
            # Create root prim
            root_prim = self.create_prim("/HairStyle")
            if root_prim:
                # Create module references structure
                self.create_prim("/HairStyle/Modules")
                self.create_prim("/HairStyle/Modules/Scalp")  # Required
                self.create_prim("/HairStyle/Modules/Crown")  # Optional
                self.create_prim("/HairStyle/Modules/Tail")   # Optional
                self.create_prim("/HairStyle/Modules/Bang")   # Optional
                
                # Create cross-module rules (inherit from group)
                self.create_prim("/HairStyle/CrossModuleExclusions")
                self.create_prim("/HairStyle/BlendshapeConstraints")
                
                # Create animation system
                self.create_prim("/HairStyle/HairRig")
                self.create_prim("/HairStyle/HairRig/HairAnimation")
                self.create_prim("/HairStyle/HairRig/HairAnimation/ModuleAnimations")
                self.create_prim("/HairStyle/HairRig/HairAnimation/ModuleAnimations/Scalp")
                self.create_prim("/HairStyle/HairRig/HairAnimation/ModuleAnimations/Crown")
                self.create_prim("/HairStyle/HairRig/HairAnimation/ModuleAnimations/Tail")
                self.create_prim("/HairStyle/HairRig/HairAnimation/ModuleAnimations/Bang")
                
                # Animation rules and metadata
                self.create_prim("/HairStyle/AnimationRules")
                self.create_prim("/HairStyle/AnimationRules/TimelineMetadata")
                
                # Quality control
                self.create_prim("/HairStyle/QualityControl")
                
                return self.save_stage()
        
        except Exception as e:
            print(f"[USD Style Utils] Error creating style structure: {e}")
            return False
    
    def set_module_reference(self, module_type: str, module_file_path: str):
        """Set module reference for style"""
        if not self.stage:
            self.open_stage()
        
        module_prim = self.get_prim(f"/HairStyle/Modules/{module_type}")
        if module_prim:
            # Add USD reference to module file
            references = module_prim.GetReferences()
            references.AddReference(module_file_path, "/HairModule")
            self._is_dirty = True
            return True
        return False
    
    def get_module_references(self) -> Dict[str, str]:
        """Get all module references"""
        if not self.stage:
            self.open_stage()
        
        references = {}
        module_types = ["Scalp", "Crown", "Tail", "Bang"]
        
        for module_type in module_types:
            module_prim = self.get_prim(f"/HairStyle/Modules/{module_type}")
            if module_prim and module_prim.HasAuthoredReferences():
                refs = module_prim.GetReferences()
                # Get first reference (should only be one)
                for ref in refs.GetAddedOrExplicitItems():
                    references[module_type] = ref.assetPath
                    break
        
        return references
    
    def get_animation_data(self) -> Dict[str, Any]:
        """Get animation timeline data"""
        if not self.stage:
            self.open_stage()
        
        return self.get_custom_data("/HairStyle/HairRig/HairAnimation", "animationData", {})
    
    def set_animation_data(self, animation_data: Dict[str, Any]):
        """Set animation timeline data"""
        if not self.stage:
            self.open_stage()
        
        return self.set_custom_data("/HairStyle/HairRig/HairAnimation", "animationData", animation_data)
    
    def get_timeline_metadata(self) -> Dict[str, Any]:
        """Get timeline metadata"""
        if not self.stage:
            self.open_stage()
        
        return self.get_custom_data("/HairStyle/AnimationRules/TimelineMetadata", "metadata", {
            "frameRate": 24,
            "timeUnit": "frames",
            "looping": False,
            "maxFrames": 6000
        })
    
    def set_timeline_metadata(self, metadata: Dict[str, Any]):
        """Set timeline metadata"""
        if not self.stage:
            self.open_stage()
        
        return self.set_custom_data("/HairStyle/AnimationRules/TimelineMetadata", "metadata", metadata)


class USDValidationUtils:
    """Utility class for USD validation operations"""
    
    @staticmethod
    def validate_group_file(file_path: Path) -> Tuple[bool, str]:
        """Validate Group USD file structure"""
        try:
            if not USD_AVAILABLE:
                return False, "USD not available"
            
            if not file_path.exists():
                return False, f"File does not exist: {file_path}"
            
            stage = Usd.Stage.Open(str(file_path))
            if not stage:
                return False, "Could not open USD stage"
            
            # Check for required prims
            required_prims = [
                "/HairGroup",
                "/HairGroup/ModuleWhitelist",
                "/HairGroup/AlphaWhitelist"
            ]
            
            for prim_path in required_prims:
                if not stage.GetPrimAtPath(prim_path):
                    return False, f"Missing required prim: {prim_path}"
            
            return True, "Group USD file is valid"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    @staticmethod
    def validate_module_file(file_path: Path) -> Tuple[bool, str]:
        """Validate Module USD file structure"""
        try:
            if not USD_AVAILABLE:
                return False, "USD not available"
            
            if not file_path.exists():
                return False, f"File does not exist: {file_path}"
            
            stage = Usd.Stage.Open(str(file_path))
            if not stage:
                return False, "Could not open USD stage"
            
            # Check for required prims
            required_prims = [
                "/HairModule",
                "/HairModule/BaseMesh",
                "/HairModule/BlendShapes"
            ]
            
            for prim_path in required_prims:
                if not stage.GetPrimAtPath(prim_path):
                    return False, f"Missing required prim: {prim_path}"
            
            return True, "Module USD file is valid"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    @staticmethod
    def validate_style_file(file_path: Path) -> Tuple[bool, str]:
        """Validate Style USD file structure"""
        try:
            if not USD_AVAILABLE:
                return False, "USD not available"
            
            if not file_path.exists():
                return False, f"File does not exist: {file_path}"
            
            stage = Usd.Stage.Open(str(file_path))
            if not stage:
                return False, "Could not open USD stage"
            
            # Check for required prims
            required_prims = [
                "/HairStyle",
                "/HairStyle/Modules",
                "/HairStyle/Modules/Scalp"  # Scalp is required
            ]
            
            for prim_path in required_prims:
                if not stage.GetPrimAtPath(prim_path):
                    return False, f"Missing required prim: {prim_path}"
            
            return True, "Style USD file is valid"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"


# Convenience functions for quick operations
def create_group_file(file_path: Path, group_name: str, group_type: str = "") -> bool:
    """Create a new Group USD file"""
    utils = USDGroupUtils(file_path)
    return utils.create_group_structure(group_name, group_type)


def create_module_file(file_path: Path, module_name: str, module_type: str) -> bool:
    """Create a new Module USD file"""
    utils = USDModuleUtils(file_path)
    return utils.create_module_structure(module_name, module_type)


def create_style_file(file_path: Path, style_name: str) -> bool:
    """Create a new Style USD file"""
    utils = USDStyleUtils(file_path)
    return utils.create_style_structure(style_name)