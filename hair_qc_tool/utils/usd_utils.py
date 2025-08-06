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
        if self.stage and self._is_dirty:
            try:
                self.stage.Save()
                self._is_dirty = False
                return True
            except Exception as e:
                print(f"[USD Utils] Error saving stage: {e}")
                return False
        return True
    
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
    
    def get_module_whitelist(self, module_type: str) -> List[str]:
        """Get module whitelist for specific type"""
        if not self.stage:
            self.open_stage()
        
        return self.get_custom_data(f"/HairGroup/ModuleWhitelist/{module_type}", "moduleFiles", [])
    
    def set_module_whitelist(self, module_type: str, module_files: List[str]):
        """Set module whitelist for specific type"""
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
                # Set module type variant
                variant_set = root_prim.GetVariantSets().AddVariantSet("moduleType")
                variant_set.AddVariant(module_type)
                variant_set.SetVariantSelection(module_type)
                
                # Create basic structure
                self.create_prim("/HairModule/BaseMesh", "Mesh")
                self.create_prim("/HairModule/BlendShapes")
                self.create_prim("/HairModule/BlendshapeExclusions")
                
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
    
    def add_blendshape(self, blendshape_name: str):
        """Add a blendshape to the module"""
        if not self.stage:
            self.open_stage()
        
        blendshape_prim = self.create_prim(f"/HairModule/BlendShapes/{blendshape_name}")
        return blendshape_prim is not None
    
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