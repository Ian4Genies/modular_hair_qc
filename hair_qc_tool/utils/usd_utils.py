"""
USD utilities for minimal-load workflows in Maya.

This module follows the project's USD rules and documentation:
- Viewport-first operations via USD proxy shapes
- Minimal prim-path loading (no full-stage loads)
- Targeted Maya imports only when necessary (base mesh + connected blendshapes)
- Clear, predictable prim path conventions

References:
- docs/USD_paths.md
- docs/USD_reference.md
- .cursor/rules/usd_rules.mdc
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple, List, Dict, Any
import os

import maya.cmds as cmds
import mayaUsd.lib as maya_usd_lib
from .logging_utils import get_logger

try:
    # pxr is typically available in the Maya USD environment
    from pxr import Usd, Sdf
except Exception:  # pragma: no cover - runtime environment dependent
    Usd = None  # type: ignore
    Sdf = None  # type: ignore


@dataclass(frozen=True)
class StandardPrimPaths:
    """Canonical prim paths used in module files as per docs/USD_paths.md.

    These constants exist to avoid magic strings and keep path usage consistent.
    """

    MODULE_ROOT: str = "/HairModule"
    MODULE_BASE_MESH: str = "/HairModule/BaseMesh"
    MODULE_BLENDSHAPES_ROOT: str = "/HairModule/BlendShapes"

    STYLE_ROOT: str = "/HairStyle"
    STYLE_MODULES_ROOT: str = "/HairStyle/Modules"

    GROUP_ROOT: str = "/HairGroup"
    GROUP_MODULE_WHITELIST_ROOT: str = "/HairGroup/ModuleWhitelist"
    GROUP_ALPHA_WHITELIST_ROOT: str = "/HairGroup/AlphaWhitelist/Scalp"

    STYLE_EXCLUSIONS_ROOT: str = "/HairStyle/CrossModuleExclusions"
    STYLE_CONSTRAINTS_ROOT: str = "/HairStyle/BlendshapeConstraints"


class USDUtils:
    """Utility methods for USD operations in Maya following minimal-load rules."""

    _LOG = get_logger(__name__)

    # ----------------------
    # Viewport (USD Proxy)
    # ----------------------
    @staticmethod
    def create_usd_proxy(usd_file_path: str, proxy_name: str = "hair_qc_proxy") -> Tuple[str, str]:
        """Create a Maya USD proxy transform and shape, pointing to a USD file.

        Returns (proxy_transform, proxy_shape).
        """
        proxy_transform = cmds.createNode("transform", name=f"{proxy_name}")
        proxy_shape = cmds.createNode(
            "mayaUsdProxyShape",
            name=f"{proxy_name}Shape",
            parent=proxy_transform,
        )
        cmds.setAttr(f"{proxy_shape}.filePath", usd_file_path, type="string")
        return proxy_transform, proxy_shape

    @staticmethod
    def get_stage_from_proxy(proxy_shape: str):
        """Get the USD stage object from a Maya USD proxy shape."""
        prim = maya_usd_lib.GetPrim(proxy_shape)
        return prim.GetStage()

    @staticmethod
    def load_prim_in_viewport(proxy_shape: str, prim_path: str) -> bool:
        """Load ONLY the specified prim path into the USD proxy's stage for display.

        Does not import DAG nodes; keeps geometry USD-native in the viewport.
        """
        stage = USDUtils.get_stage_from_proxy(proxy_shape)
        if stage is None:
            return False
        try:
            stage.Load(prim_path)
            return True
        except Exception:
            USDUtils._LOG.warning(f"Failed to load prim in viewport: {prim_path}")
            return False

    @staticmethod
    def unload_prim_from_viewport(proxy_shape: str, prim_path: str) -> bool:
        """Unload the specified prim path from the USD proxy's stage."""
        stage = USDUtils.get_stage_from_proxy(proxy_shape)
        if stage is None:
            return False
        try:
            stage.Unload(prim_path)
            return True
        except Exception:
            USDUtils._LOG.warning(f"Failed to unload prim in viewport: {prim_path}")
            return False

    @staticmethod
    def prim_exists_in_view(proxy_shape: str, prim_path: str) -> bool:
        """Check if a prim exists on the proxy's stage (regardless of load state)."""
        stage = USDUtils.get_stage_from_proxy(proxy_shape)
        if stage is None:
            return False
        try:
            return stage.GetPrimAtPath(prim_path).IsValid()
        except Exception:
            USDUtils._LOG.warning(f"prim_exists_in_view failed for: {prim_path}")
            return False

    @staticmethod
    def set_usd_blendshape_weight(
        proxy_shape: str,
        prim_path: str,
        shape_name: str,
        weight: float,
    ) -> bool:
        """Set a USD-authored blendshape weight on a prim in the proxy stage.

        This drives viewport-only animation without importing geometry into the Maya DAG.
        """
        stage = USDUtils.get_stage_from_proxy(proxy_shape)
        if stage is None:
            return False

        try:
            clamped_weight = max(0.0, min(1.0, float(weight)))
            prim = stage.GetPrimAtPath(prim_path)
            if not prim.IsValid():
                return False
            attr = prim.GetAttribute(f"blendShapes:{shape_name}")
            if not attr:
                return False
            attr.Set(clamped_weight)
            return True
        except Exception:
            USDUtils._LOG.warning(
                f"Failed to set blendshape weight: prim={prim_path} shape={shape_name}"
            )
            return False

    # ----------------------
    # Targeted Maya Imports
    # ----------------------
    @staticmethod
    def import_module_base_with_blendshapes(
        usd_file_path: str,
        module_root_prim: str = StandardPrimPaths.MODULE_ROOT,
    ) -> List[str]:
        """Import the module root prim to bring in BaseMesh and its connected blendshapes.

        Notes:
        - We import ONLY the module root prim (e.g., "/HairModule").
        - This is the smallest practical scope that ensures BaseMesh and BlendShapes
          come in together and remain connected in Maya's blendShape node.
        - We DO NOT import the entire USD stage/root.
        """
        if not usd_file_path:
            return []
        try:
            imported_nodes = cmds.mayaUSDImport(
                file=str(usd_file_path),
                primPath=str(module_root_prim),
                readAnimData=True,
            )
            return imported_nodes or []
        except Exception:
            return []

    # ----------------------
    # Helpers
    # ----------------------
    @staticmethod
    def ensure_minimal_import_for_edit(
        usd_file_path: str,
        module_root_prim: str = StandardPrimPaths.MODULE_ROOT,
    ) -> Optional[str]:
        """Convenience: import just enough data for Maya-native editing.

        - Imports the module root prim (BaseMesh + BlendShapes)
        - Returns the top imported DAG node if available
        """
        nodes = USDUtils.import_module_base_with_blendshapes(
            usd_file_path=usd_file_path,
            module_root_prim=module_root_prim,
        )
        if not nodes:
            return None
        # Heuristic: first returned node is typically the top-most transform
        return nodes[0]


@dataclass(frozen=True)
class CrossModuleExclusion:
    """Represents a cross-module exclusion entry.

    name: Arbitrary stable identifier for the exclusion entry
    target_prim_paths: List of absolute prim paths that are mutually exclusive
    """

    name: str
    target_prim_paths: List[str]


@dataclass(frozen=True)
class BlendshapeConstraint:
    """Represents a cross-module weight constraint.

    name: Identifier for the constraint entry
    constrained_prim_paths: Prim paths being constrained (same order as max_weights)
    max_weights: Upper bound weights corresponding to constrained_prim_paths
    """

    name: str
    constrained_prim_paths: List[str]
    max_weights: List[float]


class USDStageManager:
    """Utilities for opening, creating, and saving USD stages."""

    _cache: Dict[str, Tuple[Any, float]] = {}

    @staticmethod
    def open_stage(usd_file_path: str):
        if Usd is None:
            return None
        try:
            path = str(usd_file_path)
            # Use mtime-based cache to avoid reopening unchanged stages
            try:
                mtime = os.path.getmtime(path)
            except Exception:
                mtime = 0.0
            cached = USDStageManager._cache.get(path)
            if cached and cached[1] == mtime:
                return cached[0]
            stage = Usd.Stage.Open(path)
            if stage:
                USDStageManager._cache[path] = (stage, mtime)
            return stage
        except Exception:
            return None

    @staticmethod
    def create_new_stage(usd_file_path: str):
        if Usd is None:
            return None
        try:
            path = str(usd_file_path)
            stage = Usd.Stage.CreateNew(path)
            # Invalidate any cached entry; mtime will update after save
            USDStageManager._cache.pop(path, None)
            return stage
        except Exception:
            return None

    @staticmethod
    def save_stage(stage) -> bool:
        if stage is None:
            return False
        try:
            stage.GetRootLayer().Save()
            # Refresh cache mtime
            try:
                root_path = stage.GetRootLayer().realPath
                if root_path:
                    USDStageManager._cache[root_path] = (
                        stage,
                        os.path.getmtime(root_path) if os.path.exists(root_path) else 0.0,
                    )
            except Exception:
                pass
            return True
        except Exception:
            return False

    @staticmethod
    def get_or_define_prim(stage, prim_path: str, type_name: str = "Xform"):
        """Get an existing prim or define one with provided schema type."""
        if stage is None:
            return None
        try:
            prim = stage.GetPrimAtPath(prim_path)
            if prim and prim.IsValid():
                return prim
            # Define creates the prim if missing
            return stage.DefinePrim(prim_path, type_name)
        except Exception:
            return None

    @staticmethod
    def clear_cache() -> None:
        USDStageManager._cache.clear()


class USDGroupUtils:
    """Group USD operations (whitelists and discovery)."""

    @staticmethod
    def list_groups(usd_directory) -> List[str]:
        """Return sorted list of group file stems in `Group/` directory."""
        try:
            from pathlib import Path
            base = Path(usd_directory) if not isinstance(usd_directory, Path) else usd_directory
            group_dir = base / "Group"
            if not group_dir.exists():
                return []
            return sorted([p.stem for p in group_dir.glob("*.usd")])
        except Exception:
            get_logger(__name__).warning("Failed to list groups from directory")
            return []

    @staticmethod
    def read_module_whitelist(stage, module_whitelist_root: str = StandardPrimPaths.GROUP_MODULE_WHITELIST_ROOT) -> Dict[str, List[str]]:
        """Read module whitelist entries from a Group stage.

        Returns mapping of module type (e.g., "Crown") to list of asset paths (strings).
        """
        results: Dict[str, List[str]] = {}
        if stage is None:
            return results
        try:
            root_prim = stage.GetPrimAtPath(module_whitelist_root)
            if not root_prim or not root_prim.IsValid():
                return results
            for child in root_prim.GetChildren():
                module_type = child.GetName()
                attr = child.GetAttribute("moduleFiles")
                if not attr:
                    results[module_type] = []
                    continue
                try:
                    values = attr.Get() or []
                    # values may be list of Sdf.AssetPath or plain strings
                    parsed = []
                    for v in values:
                        try:
                            parsed.append(str(v.path) if hasattr(v, "path") else str(v))
                        except Exception:
                            parsed.append(str(v))
                    results[module_type] = parsed
                except Exception:
                    results[module_type] = []
            return results
        except Exception:
            return results

    @staticmethod
    def read_alpha_whitelist(stage, alpha_whitelist_root: str = StandardPrimPaths.GROUP_ALPHA_WHITELIST_ROOT) -> Dict[str, List[str]]:
        """Read scalp alpha whitelist categories to asset paths mapping."""
        results: Dict[str, List[str]] = {}
        if stage is None:
            return results
        try:
            scalp_root = stage.GetPrimAtPath(alpha_whitelist_root)
            if not scalp_root or not scalp_root.IsValid():
                return results
            for category in scalp_root.GetChildren():
                cat_name = category.GetName()
                attr = category.GetAttribute("whitelistedTextures")
                if not attr:
                    results[cat_name] = []
                    continue
                try:
                    values = attr.Get() or []
                    parsed = []
                    for v in values:
                        try:
                            parsed.append(str(v.path) if hasattr(v, "path") else str(v))
                        except Exception:
                            parsed.append(str(v))
                    results[cat_name] = parsed
                except Exception:
                    results[cat_name] = []
            return results
        except Exception:
            return results


class USDModuleUtils:
    """Module USD operations (blendshapes, alpha blacklist, classification)."""

    @staticmethod
    def list_blendshape_names(stage, blendshapes_root: str = StandardPrimPaths.MODULE_BLENDSHAPES_ROOT) -> List[str]:
        names: List[str] = []
        if stage is None:
            return names
        try:
            root = stage.GetPrimAtPath(blendshapes_root)
            if not root or not root.IsValid():
                return names
            for child in root.GetChildren():
                names.append(child.GetName())
            return names
        except Exception:
            return names

    @staticmethod
    def read_alpha_blacklist(stage, alpha_blacklist_root: str = f"{StandardPrimPaths.MODULE_ROOT}/AlphaBlacklist/Scalp") -> Dict[str, List[str]]:
        """Read optional per-module alpha blacklist by category."""
        results: Dict[str, List[str]] = {}
        if stage is None:
            return results
        try:
            scalp_root = stage.GetPrimAtPath(alpha_blacklist_root)
            if not scalp_root or not scalp_root.IsValid():
                return results
            for category in scalp_root.GetChildren():
                cat_name = category.GetName()
                attr = category.GetAttribute("blacklistedTextures")
                if not attr:
                    results[cat_name] = []
                    continue
                try:
                    values = attr.Get() or []
                    parsed = []
                    for v in values:
                        try:
                            parsed.append(str(v.path) if hasattr(v, "path") else str(v))
                        except Exception:
                            parsed.append(str(v))
                    results[cat_name] = parsed
                except Exception:
                    results[cat_name] = []
            return results
        except Exception:
            return results


class USDStyleUtils:
    """Style USD operations (module references and cross-module rules)."""

    @staticmethod
    def read_module_references(stage, modules_root: str = StandardPrimPaths.STYLE_MODULES_ROOT) -> Dict[str, str]:
        """Return mapping of module slot (Scalp/Crown/Tail/Bang) → referenced asset path.

        Prefers explicit references, falls back to payloads if present.
        """
        results: Dict[str, str] = {}
        if stage is None:
            return results
        try:
            root = stage.GetPrimAtPath(modules_root)
            if not root or not root.IsValid():
                return results
            for child in root.GetChildren():
                slot = child.GetName()
                asset_path: Optional[str] = None
                try:
                    # Try references first
                    refs = child.GetReferences()
                    if refs:
                        for ref in refs.GetAddedReferences():
                            if ref and getattr(ref, "assetPath", None):
                                asset_path = str(ref.assetPath)
                                break
                    if not asset_path:
                        # Try payloads
                        payloads = child.GetPayloads()
                        if payloads:
                            for pl in payloads.GetAddedPayloads():
                                if pl and getattr(pl, "assetPath", None):
                                    asset_path = str(pl.assetPath)
                                    break
                except Exception:
                    asset_path = None
                if asset_path:
                    results[slot] = asset_path
            return results
        except Exception:
            return results

    @staticmethod
    def read_cross_module_exclusions(stage, exclusions_root: str = StandardPrimPaths.STYLE_EXCLUSIONS_ROOT) -> List[CrossModuleExclusion]:
        entries: List[CrossModuleExclusion] = []
        if stage is None:
            return entries
        try:
            root = stage.GetPrimAtPath(exclusions_root)
            if not root or not root.IsValid():
                return entries
            for child in root.GetChildren():
                name = child.GetName()
                rel = child.GetRelationship("excludedBlendshapes")
                targets: List[str] = []
                if rel:
                    try:
                        for t in rel.GetTargets():
                            targets.append(str(t.pathString) if hasattr(t, "pathString") else str(t))
                    except Exception:
                        targets = []
                entries.append(CrossModuleExclusion(name=name, target_prim_paths=targets))
            return entries
        except Exception:
            return entries

    @staticmethod
    def write_cross_module_exclusions(stage, exclusions: List[CrossModuleExclusion], exclusions_root: str = StandardPrimPaths.STYLE_EXCLUSIONS_ROOT) -> bool:
        if stage is None or Sdf is None:
            return False
        try:
            root = USDStageManager.get_or_define_prim(stage, exclusions_root, "Xform")
            if root is None:
                return False
            # Create/overwrite children
            for entry in exclusions:
                child_path = f"{exclusions_root}/{entry.name}"
                child = USDStageManager.get_or_define_prim(stage, child_path, "Xform")
                if child is None:
                    continue
                rel = child.CreateRelationship("excludedBlendshapes", False)
                targets = []
                for p in entry.target_prim_paths:
                    try:
                        targets.append(Sdf.Path(p))
                    except Exception:
                        continue
                rel.SetTargets(targets)
            return True
        except Exception:
            return False

    # ----------------------
    # Animation Rules (BlendshapeRules + TimelineMetadata)
    # ----------------------
    @staticmethod
    def read_animation_rules(stage, rules_root: str = f"{StandardPrimPaths.STYLE_ROOT}/AnimationRules") -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "ruleDescriptions": [],
            "customRules": {},
            "timeline": {},
        }
        if stage is None:
            return data
        try:
            root = stage.GetPrimAtPath(rules_root)
            if not root or not root.IsValid():
                return data
            # BlendshapeRules
            bsr = stage.GetPrimAtPath(f"{rules_root}/BlendshapeRules")
            if bsr and bsr.IsValid():
                desc_attr = bsr.GetAttribute("ruleDescriptions")
                if desc_attr:
                    try:
                        data["ruleDescriptions"] = list(desc_attr.Get() or [])
                    except Exception:
                        data["ruleDescriptions"] = []
                # Collect any other custom attributes
                try:
                    custom: Dict[str, Any] = {}
                    for attr in bsr.GetAttributes():
                        name = attr.GetName()
                        if name == "ruleDescriptions":
                            continue
                        try:
                            custom[name] = attr.Get()
                        except Exception:
                            custom[name] = None
                    data["customRules"] = custom
                except Exception:
                    data["customRules"] = {}
            # TimelineMetadata
            tmeta = stage.GetPrimAtPath(f"{rules_root}/TimelineMetadata")
            if tmeta and tmeta.IsValid():
                tl: Dict[str, Any] = {}
                for key in ("frameRate", "timeUnit", "looping", "keyframes", "keyframeLabels"):
                    try:
                        attr = tmeta.GetAttribute(key)
                        tl[key] = attr.Get() if attr else None
                    except Exception:
                        tl[key] = None
                data["timeline"] = tl
            return data
        except Exception:
            get_logger(__name__).warning("Failed to read AnimationRules")
            return data

    @staticmethod
    def write_animation_rules(
        stage,
        rule_descriptions: Optional[List[str]] = None,
        custom_rules: Optional[Dict[str, Any]] = None,
        timeline: Optional[Dict[str, Any]] = None,
        rules_root: str = f"{StandardPrimPaths.STYLE_ROOT}/AnimationRules",
    ) -> bool:
        if stage is None or Sdf is None:
            return False
        try:
            # Ensure root and subprims exist
            _ = USDStageManager.get_or_define_prim(stage, rules_root, "Xform")
            bsr = USDStageManager.get_or_define_prim(stage, f"{rules_root}/BlendshapeRules", "Xform")
            tmd = USDStageManager.get_or_define_prim(stage, f"{rules_root}/TimelineMetadata", "Xform")

            if bsr and rule_descriptions is not None:
                attr = bsr.CreateAttribute("ruleDescriptions", Sdf.ValueTypeNames.StringArray)
                try:
                    attr.Set(list(rule_descriptions))
                except Exception:
                    attr.Set([])
            if bsr and custom_rules:
                for key, value in custom_rules.items():
                    # Best-effort typing
                    if isinstance(value, str):
                        attr = bsr.CreateAttribute(key, Sdf.ValueTypeNames.String)
                        attr.Set(value)
                    elif isinstance(value, (list, tuple)) and all(isinstance(v, str) for v in value):
                        attr = bsr.CreateAttribute(key, Sdf.ValueTypeNames.StringArray)
                        attr.Set(list(value))
                    elif isinstance(value, int):
                        attr = bsr.CreateAttribute(key, Sdf.ValueTypeNames.Int)
                        attr.Set(value)
                    elif isinstance(value, float):
                        attr = bsr.CreateAttribute(key, Sdf.ValueTypeNames.Float)
                        attr.Set(value)
                    elif isinstance(value, bool):
                        attr = bsr.CreateAttribute(key, Sdf.ValueTypeNames.Bool)
                        attr.Set(bool(value))
                    else:
                        attr = bsr.CreateAttribute(key, Sdf.ValueTypeNames.String)
                        attr.Set(str(value))

            if tmd and timeline is not None:
                key_types = {
                    "frameRate": Sdf.ValueTypeNames.Int,
                    "timeUnit": Sdf.ValueTypeNames.String,
                    "looping": Sdf.ValueTypeNames.Bool,
                    "keyframes": Sdf.ValueTypeNames.IntArray,
                    "keyframeLabels": Sdf.ValueTypeNames.StringArray,
                }
                for key, vtype in key_types.items():
                    if key not in timeline:
                        continue
                    value = timeline.get(key)
                    attr = tmd.CreateAttribute(key, vtype)
                    try:
                        if vtype == Sdf.ValueTypeNames.IntArray:
                            attr.Set([int(v) for v in value])
                        elif vtype == Sdf.ValueTypeNames.StringArray:
                            attr.Set([str(v) for v in value])
                        elif vtype == Sdf.ValueTypeNames.Int:
                            attr.Set(int(value))
                        elif vtype == Sdf.ValueTypeNames.Bool:
                            attr.Set(bool(value))
                        elif vtype == Sdf.ValueTypeNames.String:
                            attr.Set(str(value))
                        else:
                            attr.Set(value)
                    except Exception:
                        pass
            return True
        except Exception:
            get_logger(__name__).warning("Failed to write AnimationRules")
            return False

    @staticmethod
    def read_blendshape_constraints(stage, constraints_root: str = StandardPrimPaths.STYLE_CONSTRAINTS_ROOT) -> List[BlendshapeConstraint]:
        entries: List[BlendshapeConstraint] = []
        if stage is None:
            return entries
        try:
            root = stage.GetPrimAtPath(constraints_root)
            if not root or not root.IsValid():
                return entries
            for child in root.GetChildren():
                name = child.GetName()
                rel = child.GetRelationship("constrainedBlendshapes")
                paths: List[str] = []
                if rel:
                    try:
                        for t in rel.GetTargets():
                            paths.append(str(t.pathString) if hasattr(t, "pathString") else str(t))
                    except Exception:
                        paths = []
                attr = child.GetAttribute("maxWeights")
                weights: List[float] = []
                if attr:
                    try:
                        values = attr.Get() or []
                        weights = [float(v) for v in values]
                    except Exception:
                        weights = []
                entries.append(BlendshapeConstraint(name=name, constrained_prim_paths=paths, max_weights=weights))
            return entries
        except Exception:
            return entries

    @staticmethod
    def write_blendshape_constraints(stage, constraints: List[BlendshapeConstraint], constraints_root: str = StandardPrimPaths.STYLE_CONSTRAINTS_ROOT) -> bool:
        if stage is None or Sdf is None:
            return False
        try:
            root = USDStageManager.get_or_define_prim(stage, constraints_root, "Xform")
            if root is None:
                return False
            for entry in constraints:
                child_path = f"{constraints_root}/{entry.name}"
                child = USDStageManager.get_or_define_prim(stage, child_path, "Xform")
                if child is None:
                    continue
                rel = child.CreateRelationship("constrainedBlendshapes", False)
                rel.SetTargets([Sdf.Path(p) for p in entry.constrained_prim_paths if p])
                attr = child.CreateAttribute("maxWeights", Sdf.ValueTypeNames.FloatArray)
                try:
                    attr.Set([float(v) for v in entry.max_weights])
                except Exception:
                    attr.Set([])
            return True
        except Exception:
            return False

