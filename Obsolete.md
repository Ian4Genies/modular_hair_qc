# Obsolete Code and Scripts

This document identifies code, methods, and scripts that are no longer used or important to the streamlined operation of the Hair QC Tool.

## Root-Level Scripts (Obsolete)

### Development Testing Scripts
These scripts were used during development but are now superseded by the integrated hot-reload system:

- **`simple_reload_test.py`** - OBSOLETE
  - Purpose: Manual module reloading and testing
  - Replaced by: `hair_qc_tool/utils/reloader.py` and Developer menu
  - Contains hardcoded paths and manual test procedures
  - Status: Can be deleted

- **`force_reload_and_test.py`** - OBSOLETE  
  - Purpose: Force reload modules with comprehensive testing
  - Replaced by: Built-in Developer → Reload Code functionality
  - Contains hardcoded USD file paths specific to test environment
  - Status: Can be deleted

## Development Tools (Mixed Status)

### Debugging Scripts (Mostly Obsolete)

#### Obsolete Debugging Scripts
- **`dev_tools/debugging/force_reload_modules.py`** - OBSOLETE
  - Purpose: Manual module reloading
  - Replaced by: `hair_qc_tool/utils/reloader.py`
  - Duplicates functionality now built into the tool
  - Status: Can be deleted

- **`dev_tools/debugging/verify_methods.py`** - OBSOLETE
  - Purpose: Verify USDModuleUtils methods after API changes
  - Was used to check for old method names during refactoring
  - No longer needed as API is stable
  - Status: Can be deleted

- **`dev_tools/debugging/cleanup_temp_files.py`** - OBSOLETE
  - Purpose: Clean up temp USD files
  - Contains broken import (`get_config` doesn't exist)
  - Minimal utility that can be done manually
  - Status: Can be deleted

- **`dev_tools/debugging/check_code_changes.py`** - OBSOLETE
  - Purpose: Verify code changes are applied
  - Used during development debugging
  - No longer needed with stable codebase
  - Status: Can be deleted

#### Potentially Useful Debugging Scripts
- **`dev_tools/debugging/debug_geometry_*.py`** - REVIEW NEEDED
  - Purpose: Debug geometry import/save operations
  - May be useful for future debugging
  - Status: Keep but document as development-only

- **`dev_tools/debugging/debug_module_list*.py`** - REVIEW NEEDED  
  - Purpose: Debug module listing functionality
  - May be useful for troubleshooting
  - Status: Keep but document as development-only

- **`dev_tools/debugging/inspect_*.py`** - REVIEW NEEDED
  - Purpose: Inspect Maya/USD components
  - Useful for debugging complex issues
  - Status: Keep but document as development-only

### Maya Testing Scripts (Keep)
Most scripts in `dev_tools/maya_testing/` should be kept as they provide valuable testing capabilities:

- **Keep**: All `test_*.py` files - provide regression testing
- **Keep**: Integration tests for UI components
- **Keep**: Blendshape and geometry testing scripts

## Code Methods and Features

### Obsolete Methods in Core Code

#### In `hair_qc_tool/ui/main_window.py`
- **Line 1496**: `load_geometry_to_scene()` method marked as "legacy method"
  - Redirects to `load_module_in_viewport()`
  - Should be removed and callers updated

#### In `hair_qc_tool/managers/module_manager.py`
- **Lines 192, 198**: Fallback to "old method for compatibility"
  - Blendshape loading fallbacks for old USD format
  - Should be removed once all USD files use new format

#### In `hair_qc_tool/utils/usd_utils.py`
- **Line 171**: `module_type` parameter marked as deprecated
- **Line 249**: `set_module_whitelist()` marked as "legacy method"
- **Line 916**: `SkelAnimation` method marked as deprecated
- **Lines 823-874**: Migration code for old UsdSkel.BlendShape format
  - Should be removed once all files are migrated

### TODO Items (Future Implementation)

#### High Priority TODOs
- Module renaming functionality (main_window.py:1210)
- Module type changing (main_window.py:1239) 
- Module deletion (main_window.py:1381)
- Style generation system (main_window.py:1520-1540)

#### Low Priority TODOs
- Settings/preferences dialog (main_window.py:1678)
- Style validation in data manager (data_manager.py:484)

## Configuration and Logs

### Obsolete Configuration References
- **`cleanup_temp_files.py`**: References non-existent `get_config()` function
- **Old log handling**: Some scripts have manual log cleanup that's now handled by `logging_utils.py`

## Recommendations

### Immediate Cleanup (Safe to Delete)
1. `simple_reload_test.py`
2. `force_reload_and_test.py` 
3. `dev_tools/debugging/force_reload_modules.py`
4. `dev_tools/debugging/verify_methods.py`
5. `dev_tools/debugging/cleanup_temp_files.py`
6. `dev_tools/debugging/check_code_changes.py`

### Code Cleanup (Requires Testing)
1. Remove legacy method `load_geometry_to_scene()` in main_window.py
2. Remove blendshape loading fallbacks in module_manager.py
3. Remove deprecated USD utility methods
4. Clean up migration code for old USD formats

### Documentation Needed
1. Mark remaining debug scripts as development-only
2. Document which test scripts are for regression testing
3. Update README files to reflect current tool state

## Migration Strategy

When cleaning up obsolete code:

1. **Test thoroughly** - Ensure no production code depends on obsolete methods
2. **Update imports** - Check for any remaining imports of removed functions
3. **Update documentation** - Remove references to deleted scripts
4. **Preserve git history** - Use `git rm` for proper deletion tracking

## Notes

The hot-reload system (`hair_qc_tool/utils/reloader.py`) and Developer menu have made most manual reload scripts obsolete. The integrated logging system has also eliminated the need for manual cleanup scripts.

Focus should be on completing the TODO items for missing functionality rather than maintaining obsolete debugging scripts.
