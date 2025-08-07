# Blendshape TokenArray Fix Summary

## Issue
The error `'TokenArray' object has no attribute 'index'` was occurring when trying to set blendshape weights via the USD SkelAnimation approach. The problem was in the `set_blendshape_weight_via_animation` method in `usd_utils.py`.

## Root Cause
USD's `blendShapes` attribute returns a `TokenArray` object, not a Python list. The `TokenArray` type doesn't have the `.index()` method that Python lists have.

## Fix Applied

### 1. Fixed TokenArray Index Error
**File:** `hair_qc_tool/utils/usd_utils.py`
**Lines:** 894-900

**Before:**
```python
try:
    blend_index = blendshape_names.index(blendshape_name)
except ValueError:
    print(f"[USD Module Utils] Blendshape '{blendshape_name}' not found in SkelAnimation")
    return False
```

**After:**
```python
try:
    # Convert TokenArray to list to use index() method
    blendshape_names_list = list(blendshape_names)
    blend_index = blendshape_names_list.index(blendshape_name)
except (ValueError, AttributeError) as e:
    print(f"[USD Module Utils] Blendshape '{blendshape_name}' not found in SkelAnimation or error accessing blendshape names: {e}")
    return False
```

### 2. Added Debug Output
**File:** `hair_qc_tool/utils/usd_utils.py`
**Lines:** 893-896

Added debug output to help troubleshoot blendshape issues:
```python
# Debug output
print(f"[USD Module Utils] Found {len(blendshape_names)} blendshapes in SkelAnimation: {list(blendshape_names)}")
print(f"[USD Module Utils] Current weights: {list(blendshape_weights)}")
print(f"[USD Module Utils] Looking for blendshape: '{blendshape_name}'")
```

### 3. Enhanced Error Handling and Verification
**File:** `hair_qc_tool/utils/usd_utils.py**
**Lines:** 923-930

Added verification step to confirm the weight was set correctly:
```python
# Mark stage as dirty so changes get saved
self._is_dirty = True

# Verify the weight was set correctly
verification_weights = blend_weights_attr.Get()
if verification_weights and len(verification_weights) > blend_index:
    actual_weight = verification_weights[blend_index]
    print(f"[USD Module Utils] Verification: blendshape '{blendshape_name}' weight is now {actual_weight}")
```

### 4. Added Fallback Mechanism
**File:** `hair_qc_tool/managers/module_manager.py`
**Lines:** 653-668

Added a fallback approach when the SkelAnimation method fails:
```python
# Fallback: Try to update the individual blendshape prim weight directly
try:
    module_utils.open_stage()
    blendshape_prim_path = f"/HairModule/BlendShapes/{blendshape_name}"
    blendshape_prim = module_utils.stage.GetPrimAtPath(blendshape_prim_path)
    if blendshape_prim.IsValid():
        weight_attr = blendshape_prim.GetAttribute("weight")
        if weight_attr:
            weight_attr.Set(float(weight))
            module_utils._is_dirty = True
            print(f"[Module Manager] Fallback: Set individual blendshape prim weight: {blendshape_name} = {weight}")
            success = True
except Exception as fallback_error:
    print(f"[Module Manager] Fallback approach also failed: {fallback_error}")
```

## Testing
Created `test_blendshape_debug.py` to test the TokenArray conversion and verify the fix works correctly.

## Expected Result
- The `'TokenArray' object has no attribute 'index'` error should no longer occur
- Blendshape sliders should work properly
- Debug output will help identify any remaining issues
- Fallback mechanism provides additional robustness

## Files Modified
1. `hair_qc_tool/utils/usd_utils.py` - Fixed TokenArray handling and added debug output
2. `hair_qc_tool/managers/module_manager.py` - Added fallback mechanism
3. `test_blendshape_debug.py` - Created for testing (can be deleted after verification)
4. `BLENDSHAPE_FIX_SUMMARY.md` - This documentation (can be deleted after verification)


