# Proceeding with step 2 tasks
_Exported on 8/8/2025 at 18:21:54 CDT from Cursor (1.4.2)_

---

**User**

Ok we have completed step one, we should proceded with step 2 in task_list.md. Please review the docs folder, and adhere to the usd prim path and viewport loading outlined in usd_rules. Please keep track of tasking for this step as described in task.mdc, and feel free to create a task_step2 doc to keep track of this step with more granular tasks. 


---

**Cursor**

I'll scan the task list and USD docs to understand Step 2, the prim path conventions, and viewport loading rules, then outline granular tasks and create a `docs/task_step2.md`. Proceeding to read the relevant files in parallel.

I reviewed the task list and USD docs and will implement Step 2 utilities following the documented prim paths and minimal viewport loading. I’ll add new USD helper classes to `hair_qc_tool/utils/usd_utils.py` and create `docs/task_step2.md` to track granular tasks. Proceeding with edits and then will run a linter check on the modified file.

```python
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
from typing import Optional, Tuple, List, Dict

import maya.cmds as cmds
import mayaUsd.lib as maya_usd_lib

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

    @staticmethod
    def open_stage(usd_file_path: str):
        if Usd is None:
            return None
        try:
            return Usd.Stage.Open(str(usd_file_path))
        except Exception:
            return None

    @staticmethod
    def create_new_stage(usd_file_path: str):
        if Usd is None:
            return None
        try:
            return Usd.Stage.CreateNew(str(usd_file_path))
        except Exception:
            return None

    @staticmethod
    def save_stage(stage) -> bool:
        if stage is None:
            return False
        try:
            stage.GetRootLayer().Save()
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


```

```markdown
*** Begin Patch
*** Add File: docs/task_step2.md
+# Step 2 — USD Utility System (Work Log)

This document tracks granular tasks for Step 2 from `task_list.md`. Follow USD prim paths and minimal viewport loading as per `docs/USD_paths.md` and `docs/USD_reference.md`.

## Scope
- Group utilities (whitelists, discovery)
- Module utilities (blendshapes, alpha blacklist)
- Style utilities (module refs, cross-module exclusions, weight constraints)
- Stage management helpers
- Viewport (USD proxy) minimal-load operations

## Checklist

- [x] Define canonical prim paths constants in `hair_qc_tool/utils/usd_utils.py`
  - `StandardPrimPaths` for Group, Module, Style, Exclusions, Constraints
- [x] Stage management helpers
  - `USDStageManager.open_stage`, `create_new_stage`, `save_stage`, `get_or_define_prim`
- [x] Group utilities
  - `USDGroupUtils.list_groups`
  - `USDGroupUtils.read_module_whitelist`
  - `USDGroupUtils.read_alpha_whitelist`
- [x] Module utilities
  - `USDModuleUtils.list_blendshape_names`
  - `USDModuleUtils.read_alpha_blacklist`
- [x] Style utilities
  - Read module references: `USDStyleUtils.read_module_references`
  - Cross-module exclusions: `read_cross_module_exclusions`, `write_cross_module_exclusions`
  - Weight constraints: `read_blendshape_constraints`, `write_blendshape_constraints`
- [x] Viewport minimal-load ops (proxy-based)
  - Create proxy, load/unload prims, set USD blendshape weights
- [ ] Blendshape rules serialization (AnimationRules)
  - Read/write of `/HairStyle/AnimationRules` contents
- [ ] Stage caching layer (avoid reopening stages repeatedly)
- [ ] Error handling & logging integration
- [ ] Unit tests (where feasible) / smoke tests in Maya
- [ ] Wire to UI data refresh (non-blocking)

## Notes
- All reading functions tolerate absent prims/attrs and return empty structures.
- Asset path values are normalized to strings (handling `Sdf.AssetPath`).
- Write APIs create container prims when missing and overwrite entries idempotently.

## Follow-ups
- Implement `AnimationRules` serialization API for blendshape rule descriptions and timeline metadata.
- Add convenience functions to resolve physical file paths from `@module/...@` references if needed by validators.
*** End Patch
```

I added the Step 2 utility classes and helpers into `hair_qc_tool/utils/usd_utils.py` following the USD prim paths and minimal viewport loading rules. Next, I’ll create `docs/task_step2.md` to track granular progress for Step 2.

```markdown
*** Begin Patch
*** Add File: docs/task_step2.md
+# Step 2 — USD Utility System (Work Log)

Track granular tasks for Step 2 from `task_list.md`. Follow prim paths in `docs/USD_paths.md` and technical patterns in `docs/USD_reference.md`. Viewport loading must be minimal (proxy-based).

## Scope
- Group utils: whitelist reading, discovery
- Module utils: blendshapes listing, alpha blacklist reading
- Style utils: module references, cross-module exclusions, weight constraints
- Stage helpers: open/create/save, get-or-define prim
- Viewport ops: proxy creation, load/unload prim, set USD blendshape weights

## Checklist
- [x] Canonical prim paths (`StandardPrimPaths`) for Group/Module/Style
- [x] Stage helpers (`USDStageManager`)
- [x] Group utils (`USDGroupUtils.list_groups`, `read_module_whitelist`, `read_alpha_whitelist`)
- [x] Module utils (`USDModuleUtils.list_blendshape_names`, `read_alpha_blacklist`)
- [x] Style utils (read module refs; read/write exclusions; read/write constraints)
- [x] Viewport minimal-load ops (proxy-based)
- [ ] BlendshapeRules serialization (AnimationRules block)
- [ ] Stage caching layer
- [ ] Logging integration and error surfacing to UI
- [ ] Unit/smoke tests in Maya USD env
- [ ] UI data refresh wiring

## Notes
- Readers are resilient to missing prims/attrs and return empty structures.
- `Sdf.AssetPath` values normalized to strings where applicable.
- Writers create container prims when absent and set relationships/attributes idempotently.

## Follow-ups
- Implement read/write helpers for `/HairStyle/AnimationRules` (rule descriptions, timeline metadata).
- Add asset path resolver helpers if needed for validation workflows.
*** End Patch
```

Creating a granular Step 2 tracking doc and updating `task_list.md` to reflect implemented utilities. Then I’ll summarize what changed.

```markdown
# Step 2 — USD Utility System (Work Log)

Track granular tasks for Step 2 from `task_list.md`. Follow prim paths in `docs/USD_paths.md` and technical patterns in `docs/USD_reference.md`. Viewport loading must be minimal (proxy-based).

## Scope
- Group utils: whitelist reading, discovery
- Module utils: blendshapes listing, alpha blacklist reading
- Style utils: module references, cross-module exclusions, weight constraints
- Stage helpers: open/create/save, get-or-define prim
- Viewport ops: proxy creation, load/unload prim, set USD blendshape weights

## Checklist
- [x] Canonical prim paths (`StandardPrimPaths`) for Group/Module/Style
- [x] Stage helpers (`USDStageManager`)
- [x] Group utils (`USDGroupUtils.list_groups`, `read_module_whitelist`, `read_alpha_whitelist`)
- [x] Module utils (`USDModuleUtils.list_blendshape_names`, `read_alpha_blacklist`)
- [x] Style utils (read module refs; read/write exclusions; read/write constraints)
- [x] Viewport minimal-load ops (proxy-based)
- [ ] BlendshapeRules serialization (AnimationRules block)
- [ ] Stage caching layer
- [ ] Logging integration and error surfacing to UI
- [ ] Unit/smoke tests in Maya USD env
- [ ] UI data refresh wiring

## Notes
- Readers are resilient to missing prims/attrs and return empty structures.
- `Sdf.AssetPath` values normalized to strings where applicable.
- Writers create container prims when absent and set relationships/attributes idempotently.

## Follow-ups
- Implement read/write helpers for `/HairStyle/AnimationRules` (rule descriptions, timeline metadata).
- Add asset path resolver helpers if needed for validation workflows.
```

```markdown
# Hair QC Tool - Task List

## Project Overview
Creating a Maya tool for modular hair quality control using USD-based data management system.

## High-Level Architecture
- **USD System**: Group-level rules, Style-level animation, Module-level assets
- **Maya Integration**: Shelf tool, imported geometry, native timeline with color coding  
- **Performance**: 6000 frame limit, lazy loading by group
- **UI**: Single-selection lists, Maya menu bar + hotkey widget, manual regeneration
- **Validation**: Real-time USD reference and blendshape validation

## Task Breakdown

### 1. Project Setup & Foundation
**Status**: In Progress
- [x] Set up Python package structure with utils folder
- [x] Create Maya shelf tool entry point
- [x] Set up USD Python API integration
- [x] Create base configuration system for USD directory paths
- [x] Set up logging and error handling framework

### 2. USD Utility System
**Status**: In Progress  
- [x] Create `USDGroupUtils` class for Group USD operations
- [x] Create `USDModuleUtils` class for Module USD operations  
- [x] Create `USDStyleUtils` class for Style USD operations
- [ ] Implement custom data serialization for BlendshapeRules
- [x] Implement custom data serialization for CrossModuleExclusions
- [x] Create USD stage management utilities

### 3. Group Management System
**Status**: Pending
- [ ] Implement group discovery and loading from USD directory
- [ ] Create group creation/deletion functionality
- [ ] Implement alpha texture whitelist management
- [ ] Create group-level rule storage and retrieval
- [ ] Implement module whitelist management per group

### 4. Module Management System  
**Status**: Pending
- [ ] Implement module USD file creation and loading
- [ ] Create geometry import from Maya scene to USD
- [ ] Implement blendshape import and management
- [ ] Create internal module exclusions system
- [ ] Implement alpha texture blacklist functionality
- [ ] Add module validation (geometry, blendshapes exist)

### 5. Style Management System
**Status**: Pending
- [ ] Implement style combinatorics generation from group modules
- [ ] Create style USD file creation with module references  
- [ ] Implement style validation (references exist, blendshapes exist)
- [ ] Create style loading and composition in Maya
- [ ] Implement cross-module rule inheritance from group level

### 6. Main UI Framework
**Status**: In Progress
- [x] Create main window with scrollable sections
- [ ] Implement group selection UI with alpha whitelist expansion
- [ ] Create module/style tab switching system
- [ ] Implement module selection and editing UI
- [ ] Create style selection and editing UI
- [ ] Add hotkey reference widget at top of tool

### 7. Blendshape Combination System
**Status**: Pending
- [ ] Implement combination generation algorithm (from Python reference)
- [ ] Create timeline generation with 10 frames per combination
- [ ] Implement 6000 frame limit with overflow warnings
- [ ] Create blendshape weight animation keyframe system
- [ ] Integrate with Maya's native timeline system

### 8. Rules & Exclusions System
**Status**: Pending
- [ ] Implement cross-module exclusion creation and editing
- [ ] Create weight constraint system for blendshape interactions
- [ ] Implement rule propagation from group to all applicable styles
- [ ] Create rule validation and conflict detection
- [ ] Add manual timeline regeneration with rule application

### 9. Validation & Error Handling
**Status**: Pending
- [ ] Implement real-time USD reference validation
- [ ] Create blendshape existence validation across modules
- [ ] Implement broken reference detection and UI display
- [ ] Create "remove invalid data" functionality
- [ ] Add external file change detection and warnings

### 10. Maya Integration
**Status**: Pending
- [ ] Create "Hair QC" menu in Maya's main menu bar
- [ ] Implement keyboard shortcuts (Tab, F5, Ctrl+R, etc.)
- [ ] Integrate with Maya's hotkey editor system
- [ ] Create shelf button for tool launch
- [ ] Implement Maya scene geometry loading for modules

### 11. Timeline Visualization
**Status**: Pending
- [ ] Implement timeline color-coding for invalid combinations (red)
- [ ] Create visual indicators for rule-affected regions
- [ ] Add timeline navigation and frame selection
- [ ] Implement blendshape weight slider integration
- [ ] Create timeline regeneration progress indicators

### 12. File Management & Utilities
**Status**: Pending
- [ ] Implement naming validation (no spaces, auto-convert to underscores)
- [ ] Create file path utilities for USD directory structure
- [ ] Add external change detection for USD files
- [ ] Implement clean removal of invalid references
- [ ] Create backup and recovery utilities (if needed)

### 13. Testing & Polish
**Status**: Pending
- [ ] Create test USD directory structure with sample data
- [ ] Test all UI workflows end-to-end
- [ ] Performance testing with large datasets
- [ ] Bug fixes and error handling improvements
- [ ] Documentation and user guide creation

## Technical Notes

### Key Design Decisions
- **Geometry Loading**: Import USD to Maya geometry for better blendshape manipulation
- **Rule Storage**: Group-level storage with style inheritance
- **Timeline**: Maya native timeline with 6000 frame limit
- **Validation**: Real-time with manual refresh options
- **UI**: Single-selection only, no batch operations

### Performance Considerations
- Lazy loading by group (max ~20 modules per group)
- USD stage caching and reuse
- Batch save operations to minimize disk I/O
- 6000 frame limit prevents Maya timeline overload

### Integration Points
- Maya shelf tool as primary entry point
- Maya menu bar integration for discoverability
- USD Python APIs for all file operations
- Maya's native blendshape and animation systems

## Current Status: Ready to Begin Implementation
All design questions resolved. Starting with project setup and foundation systems.
```

Status: Reviewed USD docs and implemented Step 2 utilities adhering to documented prim paths and minimal viewport loading. Added granular tracking doc and updated the task list.

What I did:
- Implemented Group/Module/Style utilities and stage helpers in `hair_qc_tool/utils/usd_utils.py`, following `docs/USD_paths.md` and `docs/USD_reference.md`.
- Created `docs/task_step2.md` to track granular Step 2 tasks.
- Updated `task_list.md` Step 2: marked In Progress and checked off completed utility items.

Notes:
- Lint check shows only Maya USD import warnings (expected in non-Maya env).
- BlendshapeRules (AnimationRules) serialization, stage caching, and UI wiring are noted as follow-ups in `docs/task_step2.md`.

Next I can wire these utilities into `ui/main_window.py` refresh/load flows, or proceed to implement the BlendshapeRules read/write per the tracking doc.

Summary
- Added `USDStageManager`, `USDGroupUtils`, `USDModuleUtils`, `USDStyleUtils`, and new prim path constants in `hair_qc_tool/utils/usd_utils.py`.
- Created `docs/task_step2.md` for Step 2 work log and checklist.
- Updated `task_list.md` Step 2 items to reflect progress.

