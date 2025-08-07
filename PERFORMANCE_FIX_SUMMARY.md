# Performance Fix for USD Blendshape Sliders

## Problem
The comprehensive viewport refresh approach was causing Maya to lock up because it was:
- Saving USD stages to disk on every slider movement
- Running 6 different refresh approaches simultaneously
- Causing "Failed verification" errors in Maya's USD system
- Creating a feedback loop of constant file I/O operations

## Solution: Lightweight Interactive Approach

### 1. Two-Tier Strategy

**Interactive Mode (Slider Movement):**
- Try direct proxy shape attribute control first (fastest)
- If that fails, do in-memory USD updates only (no disk saves)
- Minimal refresh (just timeline scrub)

**Save Mode (When User Saves Module):**
- Write all blendshape weights to USD stage
- Save to disk once

### 2. Direct Proxy Shape Control (Approach 1)

**File:** `hair_qc_tool/managers/module_manager.py`
**Lines:** 628-644

Try to find and control proxy shape attributes directly:
```python
proxy_attr_names = [
    f"{proxy_shape}.{blendshape_name}",  # Direct name
    f"{proxy_shape}.blendShape_{blendshape_name}",  # With prefix
    f"{proxy_shape}.{blendshape_name}_weight",  # With suffix
    f"{proxy_shape}.blendShapeWeights_{blendshape_name}",  # Alternative format
]

for attr_name in proxy_attr_names:
    if cmds.objExists(attr_name):
        cmds.setAttr(attr_name, weight)
        success = True
        break
```

### 3. Lightweight USD Updates (Approach 2)

**File:** `hair_qc_tool/managers/module_manager.py`
**Lines:** 646-670

If direct control fails:
- Update USD stage in memory only
- No disk saving during interaction
- Minimal refresh (timeline scrub only)

### 4. Removed Heavy Operations

**What was removed:**
- ❌ Immediate USD stage saving on every slider change
- ❌ File path reset refresh
- ❌ USD stage cache clearing
- ❌ Complex Hydra geometry dirty marking
- ❌ Multiple simultaneous refresh approaches

**What was kept:**
- ✅ In-memory USD updates
- ✅ Simple timeline scrub refresh
- ✅ Error handling and fallbacks

### 5. Save-Time USD Updates

**File:** `hair_qc_tool/managers/module_manager.py`
**Lines:** 299-306

When user explicitly saves the module:
```python
# Save current blendshape weights from UI to USD
if module_info.blendshapes:
    for bs_name, weight in module_info.blendshapes.items():
        module_utils.set_blendshape_weight_via_animation(bs_name, weight)

# Save changes to disk
module_utils.save_stage()
```

## Diagnostic Tools

### 1. Proxy Shape Inspector
**File:** `inspect_proxy_attributes.py`

Run this script to discover what attributes are available on your USD proxy shapes:
- Lists all attributes on proxy shapes
- Identifies blendshape/weight-related attributes
- Tests direct attribute control
- Inspects USD stage structure

### 2. Reduced Console Output

Instead of overwhelming output, you'll now see:
```
[Module Manager] Set proxy attribute: proxyShape1.hairline_weight = 0.5
[Module Manager] Applied minimal refresh
```

Or if direct control isn't available:
```
[USD Module Utils] Set blendshape 'hairline' weight to 0.5 (in-memory)
[Module Manager] Applied minimal refresh
```

## Expected Performance Improvement

- **Interactive slider movement:** Near-instant response
- **No disk I/O during interaction:** Prevents file system bottlenecks
- **No Maya lockups:** Eliminated heavy refresh operations
- **Smooth animation:** Minimal viewport refresh only when needed

## Troubleshooting

1. **Run the inspector script** to see what proxy attributes are available
2. **Check console output** to see which approach is being used
3. **If neither approach works,** the blendshapes may need to be set up differently in the USD structure

## Files Modified

1. **`hair_qc_tool/managers/module_manager.py`** - Lightweight interactive approach
2. **`hair_qc_tool/utils/usd_utils.py`** - Removed immediate saving
3. **`inspect_proxy_attributes.py`** - Diagnostic tool
4. **`PERFORMANCE_FIX_SUMMARY.md`** - This documentation

The system now prioritizes interactive performance over immediate USD persistence, with proper saving only when explicitly requested by the user.
