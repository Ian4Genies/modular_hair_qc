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
from typing import Optional, Tuple, List

import maya.cmds as cmds
import mayaUsd.lib as maya_usd_lib

try:
    # pxr is typically available in the Maya USD environment
    from pxr import Usd
except Exception:  # pragma: no cover - runtime environment dependent
    Usd = None  # type: ignore


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


