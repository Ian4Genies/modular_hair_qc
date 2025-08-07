# USD-Backed Maya Display Geometry System

## Overview

This system replaces USD proxy shapes with native Maya DAG nodes (display geometry) for interactive blendshape editing while maintaining full USD pipeline compatibility.

## Key Features

### 1. Display Geometry Management
- **Module Groups**: Each module creates a clean Maya group (`{module_name}_DisplayGeo`)
- **Exclusive Loading**: Only one module's display geometry is loaded at a time
- **Auto Cleanup**: Previous geometry is automatically cleared when switching modules
- **Organized Scene**: All display geometry is properly grouped for clean Maya scenes

### 2. Lazy Loading
- **Fast USD Import**: Quick conversion from USD to Maya DAG nodes
- **Cached USD Stages**: USD stages remain loaded for rapid data access
- **On-Demand Loading**: Geometry only imported when needed for editing

### 3. Dual Blendshape System
- **Maya Blendshapes**: Native Maya blendShape nodes for real-time viewport updates
- **USD Blendshapes**: Industry-standard USD blendshape schema for pipeline compatibility
- **Synchronized Updates**: Changes update both Maya and USD simultaneously

### 4. Interactive Control
- **Real-Time Updates**: Maya blendshape sliders update viewport immediately
- **Native Maya Workflow**: Standard Maya blendshape tools work normally
- **No Viewport Refresh Issues**: Maya handles viewport updates automatically

## Workflow

### Loading a Module
1. Clear previous display geometry
2. Import USD as Maya DAG nodes
3. Create module group and organize nodes
4. Set up Maya blendshape controls
5. Map blendshape attributes for UI control

### Adding a Blendshape
1. Add blendshape to USD file (for pipeline)
2. Add blendshape to Maya display geometry (for interaction)
3. Update module info
4. Refresh display geometry to show changes

### Setting Blendshape Weights
1. Update Maya blendshape attribute directly
2. Viewport updates automatically (no refresh needed)
3. Store weight in module info for saving later

### Saving Module
1. Sync current Maya blendshape weights to USD
2. Save USD file with updated weights
3. Maintain pipeline compatibility

## Technical Implementation

### Module Manager Changes
- `display_geometry`: Dict mapping module names to Maya group names
- `maya_blendshapes`: Dict mapping blendshape names to Maya attributes
- `_import_usd_as_maya_geometry()`: Convert USD to Maya DAG nodes
- `_setup_maya_blendshape_controls()`: Map Maya blendshape attributes
- `_add_blendshape_to_maya_geometry()`: Add blendshapes to Maya
- `_refresh_display_geometry()`: Reload geometry from USD

### Maya Utils Extension
- `import_usd_as_maya_geometry()`: Import USD as native Maya nodes
- Support for blendshape import
- Proper node tracking and organization

### Data Manager Updates
- `clear_module_display_geometry()`: Updated terminology
- Maintains same API for UI compatibility

## Benefits

### For Artists
- **Immediate Feedback**: Blendshape sliders work like native Maya
- **Familiar Workflow**: Standard Maya tools and interactions
- **No Lag**: No viewport refresh delays or lockups
- **Clean Scene**: Organized geometry groups

### For Pipeline
- **USD Compatibility**: Full industry-standard USD blendshape support
- **Interchange**: USD files work correctly in other tools
- **Data Integrity**: Proper UsdSkel schema implementation
- **Scalability**: Supports complex module hierarchies

### For Performance
- **Lazy Loading**: Fast module switching
- **Memory Efficient**: Only current module geometry in scene
- **No Refresh Overhead**: Maya handles updates natively
- **Cached Stages**: USD data remains accessible for rapid operations

## Migration from Proxy Shapes

### What Changed
- ❌ `proxy_shapes` → ✅ `display_geometry`
- ❌ `clear_all_proxy_shapes()` → ✅ `clear_all_display_geometry()`
- ❌ USD proxy shape viewport refresh → ✅ Native Maya blendshape updates
- ❌ Complex refresh mechanisms → ✅ Automatic Maya viewport updates

### What Stayed the Same
- Module loading API
- Blendshape control API
- USD file format and schema
- Group/style management
- Pipeline compatibility

## File Structure

```
ModuleName_DisplayGeo/          # Maya group
├── HairModule_BaseMesh         # Imported geometry
├── HairModule_BlendShape1      # Maya blendShape node
└── ...                         # Other imported nodes
```

## Console Output

```
[Module Manager] Imported 3 nodes from USD: ['HairModule_BaseMesh', ...]
[Module Manager] Found blendshape control: hairline -> blendShape1.hairline
[Module Manager] Set up 2 blendshape controls for module midAfro
[Module Manager] Set Maya blendshape: blendShape1.hairline = 0.75
```

## Future Enhancements

1. **Multi-Module Loading**: Support multiple modules simultaneously
2. **Instancing Support**: Efficient handling of repeated modules
3. **Animation Timeline**: Time-based blendshape animation
4. **Advanced Caching**: Smarter USD stage management
5. **Viewport Optimization**: Level-of-detail for complex modules

This system provides the best of both worlds: interactive Maya editing with full USD pipeline compatibility.
