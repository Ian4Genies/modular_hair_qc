# USD Features Reference

This document provides a concise overview of the data stored in each type of USD file in the modular hair QC system.

## Group USD Files
**Purpose**: Define delivery buckets and QC boundaries for module combinations
**Location**: `Group/short.usd`, `Group/long.usd`

### Data Stored:
- **Module Whitelists**: Approved modules for each module type [[memory:4977069]] (scalp, crown, tail, bangs)
- **Alpha Texture Whitelists**: Group-level approved scalp alpha textures by category (fade, hairline, sideburn)
- **Group Metadata**: Group type variants and descriptions

### Key Paths:
```
/HairGroup/ModuleWhitelist/{Crown|Tail|Bang|Scalp}
/HairGroup/AlphaWhitelist/Scalp/{fade|hairline|sideburn}
```

## Module USD Files  
**Purpose**: Self-contained assets with geometry, materials, and textures
**Location**: `module/{scalp|crown|tail|bang}/*.usd`

### Data Stored:
- **Geometry**: Base mesh using USD native mesh schema
- **Blendshapes**: All deformation targets using USD BlendShape schema
- **Materials**: Basic hair shaders with USD native shading
- **Texture References**: Whitelisted normal and alpha texture collections
- **Internal Exclusions**: Within-module blendshape conflicts
- **Alpha Blacklists**: Optional module-specific texture restrictions
- **Module Type**: Variant classification (scalp, crown, tail, bang)

### Key Paths:
```
/HairModule/BaseMesh
/HairModule/BlendShapes/{blendshape_name}
/HairModule/Materials/HairMaterial
/HairModule/TextureAssets/WhitelistedTextures
/HairModule/BlendshapeExclusions
/HairModule/AlphaBlacklist (optional)
```

## Style USD Files
**Purpose**: Lean composition containers with references only [[memory:4977078]]
**Location**: `style/*.usd`

### Data Stored:
- **Module References**: USD references to specific module files
- **Cross-Module Exclusions**: Binary on/off conflicts between modules
- **Weight Constraints**: Maximum weight rules when blendshapes interact
- **Animation Data**: USD native blendshape weight timelines
- **Animation Rules**: Constraint descriptions and timeline metadata
- **Quality Control**: Validation rules and metadata

### Key Paths:
```
/HairStyle/Modules/{Scalp|Crown|Tail|Bang}
/HairStyle/CrossModuleExclusions
/HairStyle/BlendshapeConstraints  
/HairStyle/HairRig/HairAnimation
/HairStyle/AnimationRules
/HairStyle/QualityControl
```

### What Style USD Does NOT Contain:
- ❌ Texture connections or material data
- ❌ Geometry or mesh data
- ❌ TextureAssets or shader nodes

## Texture Organization
**Purpose**: PNG files referenced by USD paths [[memory:4977072]]
**Location**: Within module subdirectories

### Structure:
```
module/{module_type}/alpha/{category}/{texture}.png
module/{module_type}/normal/{texture}.png
```

### Alpha Texture Logic:
- **Two-level system**: Group whitelist + Module blacklist
- **Allowed if**: Whitelisted at group level AND NOT blacklisted at module level

## Data Flow Summary

1. **Groups** → Define approved module sets and alpha textures for QC boundaries
2. **Modules** → Contain all actual assets (geometry, materials, textures, blendshapes)  
3. **Styles** → Reference specific modules with cross-module rules and animation
4. **Textures** → Stored as path references within USD directory structure

**Key Principle**: Each module and style is a separate .usd file [[memory:4977072]], with uniform rules implemented at the system level rather than embedded in individual USD files [[memory:4977078]].