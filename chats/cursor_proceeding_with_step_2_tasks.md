# Proceeding with step 2 tasks
_Exported on 8/8/2025 at 19:47:23 CDT from Cursor (1.4.2)_

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

---

**User**

Lets proceded with the step 2 tasks@task_step2.md I have moved task management to its own folder.



---

**Cursor**

I’m going to implement the remaining Step 2 tasks:
- Add AnimationRules read/write to `USDStyleUtils`.
- Add a simple stage cache to the USD helpers.
- Integrate logging for error visibility.
- Wire group loading in the UI to use the new utilities.

Then I’ll update `tasks/task_step2.md` checklist accordingly.

I'll implement the remaining Step 2 items: extend USD style utilities with AnimationRules read/write, add a simple stage cache, integrate logging, and minimally wire UI group loading to use the new utilities. Then I'll update `tasks/task_step2.md` checklist. Proceeding with code edits.

```python
*** Begin Patch
*** Update File: hair_qc_tool/utils/usd_utils.py
@@
-from dataclasses import dataclass
-from typing import Optional, Tuple, List, Dict
+from dataclasses import dataclass
+from typing import Optional, Tuple, List, Dict, Any
+import os
@@
-import maya.cmds as cmds
-import mayaUsd.lib as maya_usd_lib
+import maya.cmds as cmds
+import mayaUsd.lib as maya_usd_lib
+from .logging_utils import get_logger
@@
 Sdf = None  # type: ignore
 
 
 @dataclass(frozen=True)
 class StandardPrimPaths:
@@
 class USDUtils:
     """Utility methods for USD operations in Maya following minimal-load rules."""
+
+    _LOG = get_logger(__name__)
@@
         try:
             stage = USDUtils.get_stage_from_proxy(proxy_shape)
             if stage is None:
                 return False
             try:
                 stage.Load(prim_path)
                 return True
             except Exception:
-            return False
+                USDUtils._LOG.warning(f"Failed to load prim in viewport: {prim_path}")
+                return False
@@
         try:
             stage = USDUtils.get_stage_from_proxy(proxy_shape)
             if stage is None:
                 return False
             try:
                 stage.Unload(prim_path)
                 return True
             except Exception:
-            return False
+                USDUtils._LOG.warning(f"Failed to unload prim in viewport: {prim_path}")
+                return False
@@
         try:
             return stage.GetPrimAtPath(prim_path).IsValid()
         except Exception:
-            return False
+            USDUtils._LOG.warning(f"prim_exists_in_view failed for: {prim_path}")
+            return False
@@
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
-            return False
+            USDUtils._LOG.warning(
+                f"Failed to set blendshape weight: prim={prim_path} shape={shape_name}"
+            )
+            return False
@@
 class USDStageManager:
     """Utilities for opening, creating, and saving USD stages."""
+
+    _cache: Dict[str, Tuple[Any, float]] = {}
@@
-    def open_stage(usd_file_path: str):
+    def open_stage(usd_file_path: str):
         if Usd is None:
             return None
         try:
-            return Usd.Stage.Open(str(usd_file_path))
+            path = str(usd_file_path)
+            mtime = 0.0
+            try:
+                mtime = os.path.getmtime(path)
+            except Exception:
+                mtime = 0.0
+            cached = USDStageManager._cache.get(path)
+            if cached and cached[1] == mtime:
+                return cached[0]
+            stage = Usd.Stage.Open(path)
+            if stage:
+                USDStageManager._cache[path] = (stage, mtime)
+            return stage
         except Exception:
             return None
@@
     def create_new_stage(usd_file_path: str):
         if Usd is None:
             return None
         try:
-            return Usd.Stage.CreateNew(str(usd_file_path))
+            path = str(usd_file_path)
+            stage = Usd.Stage.CreateNew(path)
+            # Refresh cache entry (mtime will be updated after first save)
+            USDStageManager._cache.pop(path, None)
+            return stage
         except Exception:
             return None
@@
     def save_stage(stage) -> bool:
         if stage is None:
             return False
         try:
             stage.GetRootLayer().Save()
+            # Update cache mtime
+            try:
+                path = stage.GetRootLayer().realPath
+                if path:
+                    USDStageManager._cache[path] = (
+                        stage,
+                        os.path.getmtime(path) if os.path.exists(path) else 0.0,
+                    )
+            except Exception:
+                pass
             return True
         except Exception:
             return False
@@
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
+
+    @staticmethod
+    def clear_cache() -> None:
+        USDStageManager._cache.clear()
@@
 class USDGroupUtils:
@@
         try:
             from pathlib import Path
             base = Path(usd_directory) if not isinstance(usd_directory, Path) else usd_directory
             group_dir = base / "Group"
             if not group_dir.exists():
                 return []
             return sorted([p.stem for p in group_dir.glob("*.usd")])
         except Exception:
-            return []
+            from .logging_utils import get_logger as _get_log
+            _get_log(__name__).warning("Failed to list groups from directory")
+            return []
@@
 class USDStyleUtils:
     """Style USD operations (module references and cross-module rules)."""
@@
         except Exception:
             return False
+
+    # ----------------------
+    # Animation Rules (BlendshapeRules + TimelineMetadata)
+    # ----------------------
+    @staticmethod
+    def read_animation_rules(stage, rules_root: str = f"{StandardPrimPaths.STYLE_ROOT}/AnimationRules") -> Dict[str, Any]:
+        data: Dict[str, Any] = {
+            "ruleDescriptions": [],
+            "customRules": {},
+            "timeline": {},
+        }
+        if stage is None:
+            return data
+        try:
+            root = stage.GetPrimAtPath(rules_root)
+            if not root or not root.IsValid():
+                return data
+            # BlendshapeRules
+            bsr = stage.GetPrimAtPath(f"{rules_root}/BlendshapeRules")
+            if bsr and bsr.IsValid():
+                desc_attr = bsr.GetAttribute("ruleDescriptions")
+                if desc_attr:
+                    try:
+                        data["ruleDescriptions"] = list(desc_attr.Get() or [])
+                    except Exception:
+                        data["ruleDescriptions"] = []
+                # Collect any other custom string attributes
+                try:
+                    custom: Dict[str, Any] = {}
+                    for attr in bsr.GetAttributes():
+                        name = attr.GetName()
+                        if name == "ruleDescriptions":
+                            continue
+                        try:
+                            custom[name] = attr.Get()
+                        except Exception:
+                            custom[name] = None
+                    data["customRules"] = custom
+                except Exception:
+                    data["customRules"] = {}
+            # TimelineMetadata
+            tmeta = stage.GetPrimAtPath(f"{rules_root}/TimelineMetadata")
+            if tmeta and tmeta.IsValid():
+                tl: Dict[str, Any] = {}
+                for key in ("frameRate", "timeUnit", "looping", "keyframes", "keyframeLabels"):
+                    try:
+                        attr = tmeta.GetAttribute(key)
+                        tl[key] = attr.Get() if attr else None
+                    except Exception:
+                        tl[key] = None
+                data["timeline"] = tl
+            return data
+        except Exception:
+            from .logging_utils import get_logger as _get_log
+            _get_log(__name__).warning("Failed to read AnimationRules")
+            return data
+
+    @staticmethod
+    def write_animation_rules(
+        stage,
+        rule_descriptions: Optional[List[str]] = None,
+        custom_rules: Optional[Dict[str, Any]] = None,
+        timeline: Optional[Dict[str, Any]] = None,
+        rules_root: str = f"{StandardPrimPaths.STYLE_ROOT}/AnimationRules",
+    ) -> bool:
+        if stage is None or Sdf is None:
+            return False
+        try:
+            # Ensure root and subprims exist
+            _ = USDStageManager.get_or_define_prim(stage, rules_root, "Xform")
+            bsr = USDStageManager.get_or_define_prim(stage, f"{rules_root}/BlendshapeRules", "Xform")
+            tmd = USDStageManager.get_or_define_prim(stage, f"{rules_root}/TimelineMetadata", "Xform")
+
+            if bsr and rule_descriptions is not None:
+                attr = bsr.CreateAttribute("ruleDescriptions", Sdf.ValueTypeNames.StringArray)
+                try:
+                    attr.Set(list(rule_descriptions))
+                except Exception:
+                    attr.Set([])
+            if bsr and custom_rules:
+                for key, value in custom_rules.items():
+                    # Create string attributes for strings, otherwise attempt best-effort set
+                    if isinstance(value, str):
+                        attr = bsr.CreateAttribute(key, Sdf.ValueTypeNames.String)
+                        attr.Set(value)
+                    elif isinstance(value, (list, tuple)) and all(isinstance(v, str) for v in value):
+                        attr = bsr.CreateAttribute(key, Sdf.ValueTypeNames.StringArray)
+                        attr.Set(list(value))
+                    elif isinstance(value, (int, float)):
+                        # choose appropriate type
+                        vtype = Sdf.ValueTypeNames.Int if isinstance(value, int) else Sdf.ValueTypeNames.Float
+                        attr = bsr.CreateAttribute(key, vtype)
+                        attr.Set(value)
+                    elif isinstance(value, bool):
+                        attr = bsr.CreateAttribute(key, Sdf.ValueTypeNames.Bool)
+                        attr.Set(bool(value))
+                    else:
+                        # Fallback: best effort stringification
+                        attr = bsr.CreateAttribute(key, Sdf.ValueTypeNames.String)
+                        attr.Set(str(value))
+
+            if tmd and timeline is not None:
+                # Known keys and their types
+                key_types = {
+                    "frameRate": Sdf.ValueTypeNames.Int,
+                    "timeUnit": Sdf.ValueTypeNames.String,
+                    "looping": Sdf.ValueTypeNames.Bool,
+                    "keyframes": Sdf.ValueTypeNames.IntArray,
+                    "keyframeLabels": Sdf.ValueTypeNames.StringArray,
+                }
+                for key, vtype in key_types.items():
+                    value = timeline.get(key) if isinstance(timeline, dict) else None
+                    if value is None:
+                        continue
+                    attr = tmd.CreateAttribute(key, vtype)
+                    try:
+                        if vtype == Sdf.ValueTypeNames.IntArray:
+                            attr.Set([int(v) for v in value])
+                        elif vtype == Sdf.ValueTypeNames.StringArray:
+                            attr.Set([str(v) for v in value])
+                        elif vtype == Sdf.ValueTypeNames.Int:
+                            attr.Set(int(value))
+                        elif vtype == Sdf.ValueTypeNames.Bool:
+                            attr.Set(bool(value))
+                        elif vtype == Sdf.ValueTypeNames.String:
+                            attr.Set(str(value))
+                        else:
+                            attr.Set(value)
+                    except Exception:
+                        # Ignore bad value types silently
+                        pass
+            return True
+        except Exception:
+            from .logging_utils import get_logger as _get_log
+            _get_log(__name__).warning("Failed to write AnimationRules")
+            return False
*** End Patch
```

Implementing AnimationRules read/write, stage caching, logging, and minimal UI wiring now. Reading current files to prepare precise edits.

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


```

```python
"""
Main window for Hair QC Tool

Provides the primary user interface with group/module/style management tabs.
"""

from PySide2 import QtWidgets, QtCore, QtGui
import maya.cmds as cmds
from pathlib import Path

from ..config import config
from ..utils.usd_utils import USDGroupUtils


class HairQCMainWindow(QtWidgets.QMainWindow):
    """Main window for Hair QC Tool"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Hair QC Tool v1.0")
        self.setMinimumSize(800, 600)
        self.resize(1400, 1000)
        # Start maximized by default for more vertical space
        self.setWindowState(self.windowState() | QtCore.Qt.WindowMaximized)
        
        # Make window stay on top but not always
        self.setWindowFlags(QtCore.Qt.Window)
        
        self.setup_ui()
        self.setup_shortcuts()
        
        # Initialize with first refresh
        self.refresh_data()
    
    def setup_ui(self):
        """Set up the main UI layout"""
        # Create menu bar first
        self.create_menu_bar()
        
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        # Root layout
        root_layout = QtWidgets.QVBoxLayout(central_widget)
        root_layout.setSpacing(10)
        root_layout.setContentsMargins(10, 10, 10, 10)
        
        # Scroll area wrapping the entire interface content
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(10)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        
        # Hotkey reference widget at top
        self.create_hotkey_widget(scroll_layout)
        
        # Use a vertical splitter so sections are independently resizable
        self.main_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        
        # Group selection section (top of splitter)
        group_frame = self.create_group_section()
        self.main_splitter.addWidget(group_frame)
        
        # Module/Style tab section (bottom of splitter)
        tab_widget = self.create_tab_section()
        self.main_splitter.addWidget(tab_widget)
        
        # Prefer more space to the tab section by default
        self.main_splitter.setStretchFactor(0, 1)
        self.main_splitter.setStretchFactor(1, 3)
        # Give an initial generous size allocation to improve vertical real estate
        self.main_splitter.setSizes([400, 900])
        
        scroll_layout.addWidget(self.main_splitter)
        scroll_area.setWidget(scroll_content)
        root_layout.addWidget(scroll_area)
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def create_hotkey_widget(self, parent_layout):
        """Create hotkey reference widget at top"""
        hotkey_frame = QtWidgets.QFrame()
        hotkey_frame.setFrameStyle(QtWidgets.QFrame.Box)
        hotkey_frame.setStyleSheet("QFrame { background-color: #f0f0f0; }")
        
        hotkey_layout = QtWidgets.QHBoxLayout(hotkey_frame)
        
        hotkey_label = QtWidgets.QLabel("Shortcuts: Tab=Switch Tabs | F5=Refresh | Ctrl+R=Regen Timeline | Ctrl+S=Save | Ctrl+O=Change Directory")
        hotkey_label.setStyleSheet("font-size: 11px; color: #666;")
        
        hotkey_layout.addWidget(hotkey_label)
        hotkey_layout.addStretch()
        
        parent_layout.addWidget(hotkey_frame)
    
    def create_menu_bar(self):
        """Create the menu bar with File menu"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        # Change USD Directory action
        change_dir_action = QtWidgets.QAction('Change USD Directory...', self)
        change_dir_action.setShortcut('Ctrl+O')
        change_dir_action.setStatusTip('Change the USD directory location')
        change_dir_action.triggered.connect(self.change_usd_directory)
        file_menu.addAction(change_dir_action)
        
        # Show current directory action
        show_dir_action = QtWidgets.QAction('Show Current Directory', self)
        show_dir_action.setStatusTip('Show the current USD directory path')
        show_dir_action.triggered.connect(self.show_current_directory)
        file_menu.addAction(show_dir_action)
        
        file_menu.addSeparator()
        
        # Validate directory action
        validate_action = QtWidgets.QAction('Validate Directory Structure', self)
        validate_action.setStatusTip('Check if current directory has valid USD structure')
        validate_action.triggered.connect(self.validate_directory)
        file_menu.addAction(validate_action)
        
        # Initialize directory action
        init_action = QtWidgets.QAction('Initialize Empty Directory...', self)
        init_action.setStatusTip('Initialize an empty directory with USD structure')
        init_action.triggered.connect(self.initialize_directory)
        file_menu.addAction(init_action)
        
        file_menu.addSeparator()
        
        # Refresh action
        refresh_action = QtWidgets.QAction('Refresh Data', self)
        refresh_action.setShortcut('F5')
        refresh_action.setStatusTip('Refresh all data from USD files')
        refresh_action.triggered.connect(self.refresh_data)
        file_menu.addAction(refresh_action)
        
        # Settings menu
        settings_menu = menubar.addMenu('Settings')
        
        # Preferences action
        prefs_action = QtWidgets.QAction('Preferences...', self)
        prefs_action.setStatusTip('Open preferences dialog')
        prefs_action.triggered.connect(self.show_preferences)
        settings_menu.addAction(prefs_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        # About action
        about_action = QtWidgets.QAction('About Hair QC Tool', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_group_section(self):
        """Create group selection section"""
        # Group section frame
        group_frame = QtWidgets.QGroupBox("Select Group")
        group_layout = QtWidgets.QVBoxLayout(group_frame)
        
        # Group list
        self.group_list = QtWidgets.QListWidget()
        # Allow splitter-driven resizing instead of a fixed max height
        self.group_list.setMinimumHeight(120)
        self.group_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.group_list.currentRowChanged.connect(self.on_group_selected)
        group_layout.addWidget(self.group_list)
        
        # Group controls
        group_controls = QtWidgets.QHBoxLayout()
        self.add_group_btn = QtWidgets.QPushButton("Add Group")
        self.add_group_btn.clicked.connect(self.add_group)
        group_controls.addWidget(self.add_group_btn)
        group_controls.addStretch()
        
        group_layout.addLayout(group_controls)
        
        # Alpha whitelist (expandable)
        self.alpha_expander = QtWidgets.QGroupBox("Alpha Whitelist")
        self.alpha_expander.setCheckable(True)
        self.alpha_expander.setChecked(False)
        alpha_layout = QtWidgets.QVBoxLayout(self.alpha_expander)
        
        self.alpha_list = QtWidgets.QTableWidget()
        self.alpha_list.setColumnCount(3)
        self.alpha_list.setHorizontalHeaderLabels(["Whitelisted", "Texture Path", ""]) 
        self.alpha_list.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.alpha_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.alpha_list.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        alpha_layout.addWidget(self.alpha_list)
        
        group_layout.addWidget(self.alpha_expander)
        
        return group_frame
    
    def create_tab_section(self):
        """Create module/style tab section"""
        # Tab widget
        self.tab_widget = QtWidgets.QTabWidget()
        
        # Module tab
        self.module_tab = QtWidgets.QWidget()
        self.setup_module_tab()
        self.tab_widget.addTab(self.module_tab, "Module")
        
        # Style tab
        self.style_tab = QtWidgets.QWidget()
        self.setup_style_tab()
        self.tab_widget.addTab(self.style_tab, "Style")
        
        return self.tab_widget
    
    def setup_module_tab(self):
        """Set up the module management tab"""
        layout = QtWidgets.QVBoxLayout(self.module_tab)
        
        # Module selection
        module_select_frame = QtWidgets.QGroupBox("Module Selection")
        module_select_layout = QtWidgets.QVBoxLayout(module_select_frame)
        
        self.module_list = QtWidgets.QTableWidget()
        self.module_list.setColumnCount(2)
        self.module_list.setHorizontalHeaderLabels(["Type", "Name"]) 
        self.module_list.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.module_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.module_list.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.module_list.cellClicked.connect(self.on_module_row_clicked)
        self.module_list.currentItemChanged.connect(self.on_module_selected)
        module_select_layout.addWidget(self.module_list)
        
        # Module controls
        module_controls = QtWidgets.QHBoxLayout()
        self.add_module_btn = QtWidgets.QPushButton("Add Module")
        self.add_module_btn.clicked.connect(self.add_module)
        module_controls.addWidget(self.add_module_btn)
        module_controls.addStretch()
        
        module_select_layout.addLayout(module_controls)
        
        # Edit Module (expandable)
        self.module_edit_frame = QtWidgets.QGroupBox("Edit Module")
        self.module_edit_frame.setCheckable(True)
        self.module_edit_frame.setChecked(False)
        self.module_edit_frame.setEnabled(False)
        
        module_edit_layout = QtWidgets.QVBoxLayout(self.module_edit_frame)
        
        # Module properties
        # MODULE LIST 
        props_layout = QtWidgets.QFormLayout()
        self.module_name_edit = QtWidgets.QLineEdit()
        self.module_type_combo = QtWidgets.QComboBox()
        self.module_type_combo.addItems(["scalp", "crown", "tail", "bang"])
        
        props_layout.addRow("Name:", self.module_name_edit)
        props_layout.addRow("Type:", self.module_type_combo)
        
        module_edit_layout.addLayout(props_layout)
        
        # Base mesh LOADING 
        mesh_layout = QtWidgets.QHBoxLayout()
        self.base_mesh_label = QtWidgets.QLabel("No mesh loaded")
        self.replace_mesh_btn = QtWidgets.QPushButton("Replace")
        self.replace_mesh_btn.clicked.connect(self.replace_base_mesh)
        
        mesh_layout.addWidget(QtWidgets.QLabel("Base Mesh:"))
        mesh_layout.addWidget(self.base_mesh_label)
        mesh_layout.addWidget(self.replace_mesh_btn)
        mesh_layout.addStretch()
        
        module_edit_layout.addLayout(mesh_layout)
        
        # Blendshapes
        blend_frame = QtWidgets.QGroupBox("Blendshapes")
        blend_layout = QtWidgets.QVBoxLayout(blend_frame)
        #BLENDSHAPE LIST ======================================================
        self.blendshape_list = QtWidgets.QTableWidget()
        self.blendshape_list.setColumnCount(3)
        self.blendshape_list.setHorizontalHeaderLabels(["Name", "Weight", "Excluded"]) 
        self.blendshape_list.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.blendshape_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.blendshape_list.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        blend_layout.addWidget(self.blendshape_list)
        #======================================================================
        # Blendshape controls
        blend_controls = QtWidgets.QHBoxLayout()
        self.add_blendshape_btn = QtWidgets.QPushButton("Add Blendshape")
        self.add_blendshape_btn.clicked.connect(self.add_blendshape)
        blend_controls.addWidget(self.add_blendshape_btn)
        blend_controls.addStretch()
        
        blend_layout.addLayout(blend_controls)
        module_edit_layout.addWidget(blend_frame)
        
        # Save button
        save_layout = QtWidgets.QHBoxLayout()
        self.save_module_btn = QtWidgets.QPushButton("Save Module")
        self.save_module_btn.clicked.connect(self.save_module)
        save_layout.addStretch()
        save_layout.addWidget(self.save_module_btn)
        
        module_edit_layout.addLayout(save_layout)
        
        # Use a vertical splitter so the module list and edit area are resizable
        self.module_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.module_splitter.addWidget(module_select_frame)
        self.module_splitter.addWidget(self.module_edit_frame)
        self.module_splitter.setStretchFactor(0, 3)
        self.module_splitter.setStretchFactor(1, 2)
        # Initial sizes for better visibility
        self.module_splitter.setSizes([500, 700])
        layout.addWidget(self.module_splitter)
    
    def setup_style_tab(self):
        """Set up the style management tab"""
        layout = QtWidgets.QVBoxLayout(self.style_tab)
        
        # Style selection
        style_select_frame = QtWidgets.QGroupBox("Style Selection")
        style_select_layout = QtWidgets.QVBoxLayout(style_select_frame)
        
        # Style controls
        style_controls = QtWidgets.QHBoxLayout()
        self.generate_styles_btn = QtWidgets.QPushButton("Generate")
        self.add_valid_styles_btn = QtWidgets.QPushButton("Add Valid")
        self.cull_invalid_styles_btn = QtWidgets.QPushButton("Cull Invalid")
        
        self.generate_styles_btn.clicked.connect(self.generate_styles)
        self.add_valid_styles_btn.clicked.connect(self.add_valid_styles)
        self.cull_invalid_styles_btn.clicked.connect(self.cull_invalid_styles)
        
        style_controls.addWidget(self.generate_styles_btn)
        style_controls.addWidget(self.add_valid_styles_btn)
        style_controls.addWidget(self.cull_invalid_styles_btn)
        style_controls.addStretch()
        
        style_select_layout.addLayout(style_controls)
        
        # Style list
        self.style_list = QtWidgets.QTableWidget()
        self.style_list.setColumnCount(4)
        self.style_list.setHorizontalHeaderLabels(["Status", "Crown", "Tail", "Bang"]) 
        self.style_list.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.style_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.style_list.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.style_list.cellClicked.connect(self.on_style_row_clicked)
        self.style_list.currentItemChanged.connect(self.on_style_selected)
        style_select_layout.addWidget(self.style_list)
        
        # Edit Style (expandable)
        self.style_edit_frame = QtWidgets.QGroupBox("Edit Style")
        self.style_edit_frame.setCheckable(True)
        self.style_edit_frame.setChecked(False)
        self.style_edit_frame.setEnabled(False)
        
        style_edit_layout = QtWidgets.QVBoxLayout(self.style_edit_frame)
        
        # Timeline controls
        timeline_controls = QtWidgets.QHBoxLayout()
        self.regen_timeline_btn = QtWidgets.QPushButton("Regenerate Timeline")
        self.regen_timeline_btn.clicked.connect(self.regenerate_timeline)
        timeline_controls.addWidget(self.regen_timeline_btn)
        timeline_controls.addStretch()
        
        style_edit_layout.addLayout(timeline_controls)
        
        # Blendshape rules table
        rules_frame = QtWidgets.QGroupBox("Blendshape Rules")
        rules_layout = QtWidgets.QVBoxLayout(rules_frame)
        
        self.rules_list = QtWidgets.QTableWidget()
        self.rules_list.setColumnCount(7)
        self.rules_list.setHorizontalHeaderLabels([
            "Active","Type", "Name", "Blendshape", "Weight", "Max", "Exclude"
        ])
        self.rules_list.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.rules_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.rules_list.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        rules_layout.addWidget(self.rules_list)
        
        style_edit_layout.addWidget(rules_frame)
        
        # Save timeline button
        save_timeline_layout = QtWidgets.QHBoxLayout()
        self.save_timeline_btn = QtWidgets.QPushButton("Save Timeline")
        self.save_timeline_btn.clicked.connect(self.save_timeline)
        save_timeline_layout.addStretch()
        save_timeline_layout.addWidget(self.save_timeline_btn)
        
        style_edit_layout.addLayout(save_timeline_layout)
        
        # Use a vertical splitter so the style list and edit area are resizable
        self.style_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.style_splitter.addWidget(style_select_frame)
        self.style_splitter.addWidget(self.style_edit_frame)
        self.style_splitter.setStretchFactor(0, 3)
        self.style_splitter.setStretchFactor(1, 2)
        # Initial sizes for better visibility
        self.style_splitter.setSizes([500, 700])
        layout.addWidget(self.style_splitter)
    
    def setup_shortcuts(self):
        """Set up keyboard shortcuts"""
        # Tab switching
        tab_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Tab"), self)
        tab_shortcut.activated.connect(self.switch_tab)
        
        # Refresh data
        refresh_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("F5"), self)
        refresh_shortcut.activated.connect(self.refresh_data)
        
        # Regenerate timeline
        regen_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+R"), self)
        regen_shortcut.activated.connect(self.regenerate_timeline)
        
        # Save
        save_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+S"), self)
        save_shortcut.activated.connect(self.save_current)
    
    def switch_tab(self):
        """Switch between Module and Style tabs"""
        current_index = self.tab_widget.currentIndex()
        next_index = (current_index + 1) % self.tab_widget.count()
        self.tab_widget.setCurrentIndex(next_index)
    
    def refresh_data(self):
        """Refresh all data from USD files"""
        self.statusBar().showMessage("Refreshing data...")
        
        # TODO: Implement data refresh
        self.load_groups()
        
        self.statusBar().showMessage("Data refreshed", 2000)
    
    def load_groups(self):
        """Load groups from USD directory"""
        self.group_list.clear()
        
        if not config.usd_directory:
            return
        # Use utility to list groups per Step 2 utilities
        groups = USDGroupUtils.list_groups(config.usd_directory)
        for name in groups:
            self.group_list.addItem(name)
    
    # Event handlers (placeholder implementations)
    def on_group_selected(self, row):
        """Handle group selection change"""
        if row >= 0:
            group_name = self.group_list.item(row).text()
            self.statusBar().showMessage(f"Selected group: {group_name}")
            # TODO: Load modules and styles for this group
    
    def on_module_selected(self, current_item, previous_item):
        """Handle module selection change"""
        if current_item:
            self.module_edit_frame.setEnabled(True)
            # TODO: Load module data into edit form
    
    def on_module_row_clicked(self, row, column):
        """Handle module row click selection"""
        self.module_list.selectRow(row)
        self.module_edit_frame.setEnabled(True)
    
    def on_style_selected(self, current_item, previous_item):
        """Handle style selection change"""
        if current_item:
            self.style_edit_frame.setEnabled(True)
            # TODO: Load style data and timeline
    
    def on_style_row_clicked(self, row, column):
        """Handle style row click selection"""
        self.style_list.selectRow(row)
        self.style_edit_frame.setEnabled(True)
    
    def add_group(self):
        """Add new group"""
        # TODO: Implement group creation
        pass
    
    def add_module(self):
        """Add new module"""
        # TODO: Implement module creation
        pass
    
    def add_blendshape(self):
        """Add blendshape to current module"""
        # TODO: Implement blendshape addition
        pass
    
    def replace_base_mesh(self):
        """Replace base mesh for current module"""
        # TODO: Implement mesh replacement
        pass
    
    def save_module(self):
        """Save current module to USD"""
        # TODO: Implement module saving
        pass
    
    def generate_styles(self):
        """Generate style combinations"""
        # TODO: Implement style generation
        pass
    
    def add_valid_styles(self):
        """Add all valid styles to disk"""
        # TODO: Implement valid style addition
        pass
    
    def cull_invalid_styles(self):
        """Remove all invalid styles"""
        # TODO: Implement invalid style removal
        pass
    
    def regenerate_timeline(self):
        """Regenerate timeline for current style"""
        # TODO: Implement timeline regeneration
        pass
    
    def save_timeline(self):
        """Save timeline to style USD"""
        # TODO: Implement timeline saving
        pass
    
    def save_current(self):
        """Save currently active item"""
        current_tab = self.tab_widget.currentIndex()
        if current_tab == 0:  # Module tab
            self.save_module()
        elif current_tab == 1:  # Style tab
            self.save_timeline()
    
    # Menu action handlers
    def change_usd_directory(self):
        """Change USD directory with validation and initialization"""
        from ..main import HairQCTool
        
        # Create a temporary tool instance to use its directory methods
        temp_tool = HairQCTool()
        temp_tool._browse_usd_directory()
        
        # Refresh data if directory was changed successfully
        self.refresh_data()
    
    def show_current_directory(self):
        """Show current USD directory path"""
        current_dir = config.usd_directory
        if current_dir:
            QtWidgets.QMessageBox.information(
                self,
                "Current USD Directory",
                f"Current USD directory:\n\n{current_dir}"
            )
        else:
            QtWidgets.QMessageBox.warning(
                self,
                "No Directory Set",
                "No USD directory is currently set.\n\nUse 'Change USD Directory' to set one."
            )
    
    def validate_directory(self):
        """Validate current directory structure"""
        validation_result, message = config.validate_usd_directory()
        
        if validation_result == True:
            QtWidgets.QMessageBox.information(
                self,
                "Directory Valid",
                f"Directory structure is valid!\n\n{message}"
            )
        elif validation_result == "empty":
            result = QtWidgets.QMessageBox.question(
                self,
                "Empty Directory",
                f"{message}\n\nWould you like to initialize it now?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            if result == QtWidgets.QMessageBox.Yes:
                self.initialize_current_directory()
        else:
            QtWidgets.QMessageBox.warning(
                self,
                "Directory Invalid",
                f"Directory structure is invalid:\n\n{message}"
            )
    
    def initialize_directory(self):
        """Initialize an empty directory"""
        # Browse for directory first
        directory = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Select Directory to Initialize",
            str(config.usd_directory) if config.usd_directory else ""
        )
        
        if directory:
            # Temporarily set the directory
            old_directory = config.usd_directory
            config.usd_directory = directory
            
            # Check if it's empty and initialize
            validation_result, message = config.validate_usd_directory()
            if validation_result == "empty":
                result = QtWidgets.QMessageBox.question(
                    self,
                    "Initialize Directory",
                    f"Initialize directory with USD structure?\n\n{directory}\n\nThis will create:\n• Group/, module/, style/ directories\n• Sample group files\n• Required subdirectory structure",
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
                )
                
                if result == QtWidgets.QMessageBox.Yes:
                    success, init_message = config.initialize_usd_directory()
                    if success:
                        QtWidgets.QMessageBox.information(
                            self,
                            "Initialization Success",
                            f"Directory initialized successfully!\n\n{init_message}"
                        )
                        self.refresh_data()
                    else:
                        QtWidgets.QMessageBox.critical(
                            self,
                            "Initialization Failed",
                            f"Failed to initialize directory:\n\n{init_message}"
                        )
                        # Restore old directory
                        config.usd_directory = old_directory
                else:
                    # Restore old directory
                    config.usd_directory = old_directory
            else:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Directory Not Empty",
                    f"Selected directory is not empty or has existing USD structure.\n\nUse 'Validate Directory Structure' to check the current directory."
                )
                # Restore old directory
                config.usd_directory = old_directory
    
    def initialize_current_directory(self):
        """Initialize the current USD directory"""
        success, message = config.initialize_usd_directory()
        
        if success:
            QtWidgets.QMessageBox.information(
                self,
                "Initialization Success",
                f"Directory initialized successfully!\n\n{message}"
            )
            self.refresh_data()
        else:
            QtWidgets.QMessageBox.critical(
                self,
                "Initialization Failed",
                f"Failed to initialize directory:\n\n{message}"
            )
    
    def show_preferences(self):
        """Show preferences dialog"""
        # TODO: Implement preferences dialog
        QtWidgets.QMessageBox.information(
            self,
            "Preferences",
            "Preferences dialog not yet implemented.\n\nCurrent settings are stored in:\n~/.hair_qc_tool_config.json"
        )
    
    def show_about(self):
        """Show about dialog"""
        QtWidgets.QMessageBox.about(
            self,
            "About Hair QC Tool",
            """<h3>Hair QC Tool v1.0</h3>
            <p>A comprehensive Maya tool for managing modular hair assets using USD-based data structures.</p>
            
            <p><b>Features:</b></p>
            <ul>
            <li>USD-based data management</li>
            <li>Modular hair system (scalp, crown, tail, bang)</li>
            <li>Blendshape QC and combination generation</li>
            <li>Cross-module rules and constraints</li>
            <li>Maya timeline integration</li>
            </ul>
            
            <p><b>Keyboard Shortcuts:</b></p>
            <ul>
            <li>Tab - Switch tabs</li>
            <li>F5 - Refresh data</li>
            <li>Ctrl+R - Regenerate timeline</li>
            <li>Ctrl+S - Save current</li>
            <li>Ctrl+O - Change directory</li>
            </ul>"""
        )
```

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
- [x] Stage helpers (`USDStageManager`) + simple mtime cache
- [x] Group utils (`USDGroupUtils.list_groups`, `read_module_whitelist`, `read_alpha_whitelist`)
- [x] Module utils (`USDModuleUtils.list_blendshape_names`, `read_alpha_blacklist`)
- [x] Style utils (read module refs; read/write exclusions; read/write constraints)
- [x] Viewport minimal-load ops (proxy-based)
- [x] BlendshapeRules serialization (AnimationRules block) — read/write
- [x] Logging integration for utils
- [ ] Unit/smoke tests in Maya USD env
- [ ] UI data refresh wiring (modules/styles, beyond groups)

## Notes
- Readers are resilient to missing prims/attrs and return empty structures.
- `Sdf.AssetPath` values normalized to strings where applicable.
- Writers create container prims when absent and set relationships/attributes idempotently.

## Follow-ups
- Implement additional UI wiring: load module/style data when group is selected, using the new utils.
- Add asset path resolver helpers if needed for validation workflows.

```

Status: Proceeding with remaining Step 2 tasks as requested, using the new `tasks/task_step2.md`.

Planned and executed edits:
- Extended `hair_qc_tool/utils/usd_utils.py`:
  - Added logging via `get_logger`.
  - Added a simple mtime-based stage cache in `USDStageManager`.
  - Implemented `read_animation_rules` and `write_animation_rules` on `USDStyleUtils` for `/HairStyle/AnimationRules` and `TimelineMetadata`.
  - Hardened proxy viewport load/unload and prim check with warnings.
- Wired UI group listing to new utilities:
  - `hair_qc_tool/ui/main_window.py` `load_groups` now uses `USDGroupUtils.list_groups`.
- Updated `tasks/task_step2.md`:
  - Marked AnimationRules read/write, stage cache, and logging as done.
  - Noted next items (UI wiring for modules/styles and smoke tests).

Next steps I can do now:
- Wire module/style data loading when a group is selected, leveraging `USDGroupUtils` and `USDStyleUtils`.
- Add minimal smoke tests or a debug command to exercise the new read/write APIs.

Summary
- Implemented AnimationRules serialization, stage caching, and logging in `usd_utils.py`.
- UI now lists groups using the new utils in `main_window.py`.
- Updated `tasks/task_step2.md` checklist to reflect progress.

---

**User**

can you describe what both of these are?

Next steps I can do now:
Wire module/style data loading when a group is selected, leveraging USDGroupUtils and USDStyleUtils.
Add minimal smoke tests or a debug command to exercise the new read/write APIs.

---

**Cursor**

### What these two next steps are

- Wire module/style data loading on group selection:
  - When a user clicks a group in the UI, immediately read that group’s USD using `USDGroupUtils` and populate:
    - Module UI: list module types and available module files from the group’s ModuleWhitelist; prep data for showing a selected module in the viewport.
    - Style UI: list existing styles for the group and/or prepare valid combinations; later use `USDStyleUtils` to read style module refs, exclusions, constraints, and animation rules for the selected style.
  - Goal: the UI reflects the selected group’s data without manual refresh, following the documented USD prim paths.

- Add minimal smoke tests or a debug command:
  - Lightweight checks to prove the new APIs work in your environment (Maya USD or headless):
    - Open a stage, call `USDGroupUtils.read_module_whitelist` / `read_alpha_whitelist`.
    - For a style file: call `USDStyleUtils.read_module_references`, `read/write_cross_module_exclusions`, `read/write_blendshape_constraints`, `read/write_animation_rules`, then re-read to confirm persistence.
    - Exercise `USDStageManager` cache by re-opening the same file and checking it doesn’t thrash.
  - Delivered as a small script or menu/debug action that prints results and returns pass/fail, without requiring a full test framework.

- Clarified both items and their intent:
  - Group selection wiring = make the UI data reactive to the selected group via the new utils.
  - Smoke tests/debug = quick operational validation of read/write APIs and stage caching.

---

**User**

why would we do this 
For a style file: call USDStyleUtils.read_module_references, read/write_cross_module_exclusions, read/write_blendshape_constraints, read/write_animation_rules, then re-read to confirm persistence.
Exercise USDStageManager cache by re-opening the same file and checking it doesn’t thrash.

---

**Cursor**

### Why do quick read/write + re-read checks on Style utils?

- **Validate round-trip correctness**: Ensures our write APIs produce USD data that our read APIs (and other tools) can parse back exactly, confirming paths and types match `docs/USD_paths.md`.
- **Catch schema mismatches early**: If we typo an attr name (e.g., maxWeights vs. weights) or a relationship target path, the re-read will expose it immediately.
- **Protect real data**: Smoke tests on a sample stage verify we won’t corrupt actual `.usd` files when wiring into the UI later.
- **Unblock UI wiring**: Once reads/writes are proven, we can safely hook the UI to these APIs without debugging both UI and IO simultaneously.

### Why exercise the stage cache?

- **Prevent performance thrash**: Reopening the same stage repeatedly (e.g., on selection changes) can be slow; the cache confirms we reuse the same stage when the file hasn’t changed.
- **Stability under load**: Validates cache invalidation on save and avoids stale-stage bugs when files update on disk.
- **Baseline perf signal**: Quick check that Step 2’s caching achieves the lazy-loading/performance aims before more complex features are layered on.

Summary
- Read/write + re-read: verifies data integrity, schema adherence, and safety before UI integration.
- Stage cache test: confirms performance and correctness of the caching layer to support responsive UI.

