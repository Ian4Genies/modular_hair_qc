# USD Blendshape Viewport Refresh Fix Summary

## Issue
After fixing the TokenArray error, blendshape weights were being set correctly in the USD stage, but the changes weren't visible in Maya's viewport. The USD proxy shape wasn't refreshing to show the blendshape deformations.

## Root Cause
Maya's Hydra viewport renderer doesn't automatically refresh when USD stage data is modified programmatically. The proxy shape needs to be explicitly told to reload the USD data and refresh the viewport display.

## Comprehensive Fix Applied

### 1. Immediate USD Stage Saving
**File:** `hair_qc_tool/utils/usd_utils.py`
**Lines:** 926-931

Added immediate saving of USD stage after blendshape weight changes:
```python
# Save changes immediately for Maya proxy shape to pick up
try:
    self.save_stage()
    print(f"[USD Module Utils] Saved USD stage after blendshape weight change")
except Exception as save_error:
    print(f"[USD Module Utils] Warning: Could not save stage immediately: {save_error}")
```

### 2. Comprehensive Multi-Approach Refresh System
**File:** `hair_qc_tool/managers/module_manager.py`
**Lines:** 775-877

Created `_force_usd_proxy_refresh()` method with 6 different refresh approaches:

#### Approach 1: Save USD Stage to Disk
Ensures the USD file on disk is updated before attempting viewport refresh.

#### Approach 2: File Path Reset
```python
cmds.setAttr(f"{proxy_shape}.filePath", "", type="string")
cmds.refresh(currentView=True, force=True)
cmds.setAttr(f"{proxy_shape}.filePath", current_file_path, type="string")
```

#### Approach 3: USD Stage Cache Clearing
```python
from pxr import Usd
stage_cache = Usd.StageCache.Get()
stage_cache.Clear()
```

#### Approach 4: Hydra Viewport Refresh
```python
import maya.api.OpenMayaRender as omr
renderer = omr.MRenderer.theRenderer()
if renderer:
    renderer.setGeometryDrawDirty(omr.MRenderer.kAllGeometry)
```

#### Approach 5: Proxy Shape Specific Refresh
```python
cmds.dgdirty(proxy_shape)
cmds.dgdirty(allPlugs=True)
```

#### Approach 6: Timeline Scrub
```python
current_time = cmds.currentTime(query=True)
cmds.currentTime(current_time + 0.001)
cmds.refresh(currentView=True, force=True)
cmds.currentTime(current_time)
cmds.refresh(currentView=True, force=True)
```

### 3. Maya USD Notification System
**Lines:** 803-811

Added Maya USD change notification:
```python
import mayaUsd.ufe as mayaUsdUfe
if hasattr(mayaUsdUfe, 'sendNotification'):
    mayaUsdUfe.sendNotification()
```

## Testing Tools

### 1. Viewport Refresh Test Script
**File:** `test_viewport_refresh.py`

Created comprehensive test script to verify different refresh approaches work correctly.

### 2. Debug Output
Enhanced console output to track refresh progress:
- "Saved USD stage after blendshape weight change"
- "Cleared USD stage cache"
- "Marked Hydra geometry as dirty"
- "Performed timeline scrub for blendshape refresh"
- "Completed comprehensive USD proxy refresh"

## Expected Results

After applying this fix, when you move a blendshape slider:

1. **Console Output:** You should see comprehensive refresh messages
2. **Viewport Update:** The geometry should immediately update to show blendshape deformation
3. **Robustness:** If one refresh approach fails, others will be attempted

## Troubleshooting

If blendshapes still don't update visually:

1. **Check Maya Viewport Mode:** Ensure you're using Viewport 2.0 (not Legacy)
2. **Check USD Plugin:** Verify mayaUSD plugin is loaded and working
3. **Manual Refresh:** Try scrubbing the timeline manually
4. **Viewport Renderer:** Switch between different viewport renderers
5. **Console Messages:** Check for any error messages in the refresh process

## Files Modified

1. **`hair_qc_tool/utils/usd_utils.py`** - Added immediate USD stage saving
2. **`hair_qc_tool/managers/module_manager.py`** - Added comprehensive refresh system
3. **`test_viewport_refresh.py`** - Created for testing (can be deleted after verification)
4. **`VIEWPORT_REFRESH_FIX_SUMMARY.md`** - This documentation (can be deleted after verification)

## Performance Considerations

The comprehensive refresh approach may seem heavy, but:
- Each approach is tried with error handling
- Failed approaches are skipped quickly
- The timeline scrub is minimal (0.001 frame)
- Stage saving only happens when needed (`_is_dirty` flag)

This ensures maximum compatibility across different Maya versions and USD plugin configurations while maintaining good performance for interactive blendshape editing.

