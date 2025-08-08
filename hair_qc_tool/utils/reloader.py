import importlib
import sys
from dataclasses import dataclass, field
from typing import List


@dataclass
class ReloadResult:
    reloaded_modules: List[str] = field(default_factory=list)
    skipped_modules: List[str] = field(default_factory=list)
    failed_modules: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def summary(self) -> str:
        return (
            f"Reloaded: {len(self.reloaded_modules)}, "
            f"Skipped: {len(self.skipped_modules)}, "
            f"Failed: {len(self.failed_modules)}"
        )


MODULE_DEP_ORDER = [
    'hair_qc_tool.config',
    'hair_qc_tool.utils.file_utils',
    'hair_qc_tool.utils.rules_utils',
    'hair_qc_tool.utils.usd_utils',
    'hair_qc_tool.utils.maya_utils',
    'hair_qc_tool.utils',
    'hair_qc_tool.managers.group_manager',
    'hair_qc_tool.managers.module_manager',
    'hair_qc_tool.managers.data_manager',
    'hair_qc_tool.managers',
    'hair_qc_tool.ui.main_window',
    'hair_qc_tool.ui',
    'hair_qc_tool.main',
    'hair_qc_tool'
]


def reload_hair_qc_modules() -> ReloadResult:
    result = ReloadResult()

    for module_name in MODULE_DEP_ORDER:
        if module_name in sys.modules:
            try:
                importlib.reload(sys.modules[module_name])
                result.reloaded_modules.append(module_name)
            except Exception as e:
                result.failed_modules.append(module_name)
                result.errors.append(f"{module_name}: {e}")
        else:
            result.skipped_modules.append(module_name)

    return result
