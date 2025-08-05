# USD System Summary

## Overview
This document outlines a USD-based data structure for a modular hair combination and quality control system, leveraging USD's built-in schemas and composition features for better performance, maintainability, and industry standard compliance.

## Case Study: Blendshape Sample
This document uses the following blendshape configuration as examples throughout, organized by module type [[memory:4977069]]:

- **Scalp**: `hairline_fix`
- **Crown**: `lengthen`, `curly`, `volumeOut`, `volumeIn`, `hairline`  
- **Tail**: `lengthen`, `wavy`, `spread`
- **Bang**: `lengthen`, `frizzle`, `spread`

**Note**: The `scalp.hairline_fix` blendshape fires automatically with any `hairline` blendshape from other module types. This is handled implicitly and doesn't require special USD tracking.

## File Organization

**Critical**: Each group, style, and module is stored as a **separate .usd file** [[memory:4977072]]. This is not a single large USD with multiple prims, but individual USD files that reference each other in a hierarchy:

**Group > Style > Module** relationship:
- **Groups** define default module sets and QC boundaries  
- **Styles** reference specific modules from their group
- **Modules** contain actual geometry and blendshapes

**Note:** See [[USD_directory]] for an explanation on how these .usd and dependent files should be organized.
### Group Files (Individual .usd files)
```
Group/short.usd                                # Short group definition (module whitelists + alpha whitelists)
Group/long.usd                                 # Long group definition (module whitelists + alpha whitelists)
```

### Module Files (Individual .usd files)
```
module/scalp/scalp.usd                          # Single scalp module
module/crown/short_crown_smallAfro.usd          # Specific crown variation  
module/crown/short_crown_medAfro.usd            # Another crown variation
module/crown/Long_crown_braided.usd             # Long crown variation
module/tail/long_tail_braided.usd               # Specific tail variation
module/bang/long_bang_messy.usd                 # Specific bang variation
```

### Style Files (Individual .usd files)
```
style/short_medAfro.usd                         # References specific modules
style/long_braided_beaded_messy.usd             # References different modules  
style/long_simple_pony_parted.usd               # Another combination
```

### Texture Organization (PNG files in module subdirectories)
```  
module/scalp/alpha/fade/lineUp.png              # Alpha textures within modules
module/scalp/normal/ripple.png                  # Normal maps within modules
module/crown/alpha/[texture files]              # Crown-specific textures
```

**Hierarchy**: Groups define default whitelists→ Styles reference specific modules from their group → Modules contain actual assets.

## System Architecture

### USD File Structure
The system is organized into three main layers:

1. **Groups** - Define delivery buckets of modules meant to work together by default for QC purposes.
2. **Styles** - Lean data containers with references only, no texture/material data
3. **Modules** - Contain all actual assets: geometry, blendshapes, and materials data

### Key Design Principles
- **Separation of Concerns**: Each USD file has a specific role and responsibility
- **Reference-Based Composition**: Styles reference modules, avoiding data duplication
- **Whitelisting System**: Groups define approved module combinations and textures
- **QC Boundaries**: Modules within the same group are tested together by default

## Two-Level Alpha Texture System

**Alpha textures use a two-level whitelist/blacklist system:**

1. **Group Level Whitelist**: Default approved alpha textures (defined in Group USD)
2. **Module Level Blacklist**: Optional restrictions for specific modules (defined in Module USD)

**Logic**: Alpha textures are allowed if they are:
- ✅ Whitelisted at the group level **AND**
- ❌ **NOT** blacklisted at the module level

This system allows for flexible texture management while maintaining quality control boundaries.

## Group System

**Groups** are delivery buckets of modules meant to work together by default for QC purposes. Each group defines:
- **Module Whitelists**: Which modules are included in this group
- **Alpha Texture Whitelists**: Which scalp alpha textures are approved for this group
- **Default QC Boundaries**: Modules in the same group are tested together

### Group Files (Individual .usd files)
```
Group/short.usd                                # Short group instance  
Group/long.usd                                 # Long group instance
```

Groups provide the foundation for the quality control system by establishing which combinations of modules and textures are validated together.

## Style System

**Key Principle**: Style USDs are lean data containers with **references only** [[memory:4977078]]. All mesh and texture/material data lives in Module USDs.

### What Style USD Contains:
- ✅ Module references (`@modules/scalp.usd@`)
- ✅ Cross-module exclusions (blendshapes that conflict between modules)  
- ✅ Weight constraints (max weight rules between modules)
- ✅ Animation data (blendshape weight timelines)
- ❌ **NO texture connections, materials, or TextureAssets**

### What Module USD Contains:
- ✅ All geometry and blendshapes
- ✅ All materials, basic shaders, and texture references
- ✅ Whitelisted texture collections
- ✅ Internal exclusions (within-module blendshape conflicts)

## Module System

Modules are the core building blocks containing actual assets. Each module type [[memory:4977069]] serves a specific purpose:

- **Scalp**: Base hair module (required for all styles)
- **Crown**: Top/center hair variations
- **Tail**: Back/length hair elements  
- **Bang**: Front/fringe hair elements

### Module Features:
- **USD Native**: Uses standard USD schemas for geometry, materials, and blendshapes
- **Self-Contained**: Each module includes all its required assets, excluding textures, wich are stored as directory paths. 
- **Variant Support**: Modules can have multiple variations (e.g., different crown styles)
- **Quality Control**: Optional blacklists for incompatible textures

## Animation and Constraints

The system supports sophisticated animation and constraint systems:

### Cross-Module Exclusions
- Binary on/off relationships between blendshapes across different modules
- Prevents conflicting combinations (e.g., Crown volume vs Bang spread)

### Weight Constraints  
- Maximum weight limitations when blendshapes are used together
- Allows fine-grained control over blendshape interactions

### Animation System
- USD-native animation support with time sampling
- Module-specific animation data organization
- Timeline metadata for external tool integration

## Asset Resolution

The system uses USD's native asset resolution for portable, relative path-based references:

- **Module references**: `@modules/scalp_v001.usd@</HairModule>`
- **Texture paths**: `@module/scalp/normal/ripple.png`
- **Flexible**: Works across different directory structures without hardcoded paths

This approach ensures the data structure remains portable and maintainable across different environments and workflows.

## Quality Control Integration

The USD structure is designed to support comprehensive quality control:

- **Group-level validation**: Modules in the same group are tested together
- **Texture compatibility**: Two-level whitelist/blacklist system prevents incompatible combinations
- **Constraint validation**: Cross-module weight and exclusion rules are enforced
- **Automated testing**: Structure supports programmatic validation of all combinations

## Performance Considerations

- **Lazy Loading**: USD's payload system allows selective loading of module data
- **Efficient Composition**: Reference-based system avoids data duplication
- **Scalable**: Individual files can be updated without affecting the entire system
- **Industry Standard**: Leverages USD's proven performance characteristics

This summary provides the conceptual framework for understanding the modular hair QC system without getting into the detailed USD code implementation.