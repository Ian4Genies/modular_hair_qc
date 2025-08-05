# USD Internal Paths Reference

This document provides a complete reference of all internal USD paths used in the modular hair QC system, organized by file type and hierarchy level.

## Complete Path Hierarchy Examples

These examples show the most important path structures for understanding how the system is organized.

### Style USD Complete Hierarchy Example

Here's how a complete hairstyle would look when all modules are loaded:

```
/HairStyle                                    # ROOT: Main hairstyle
├── /HairStyle/Modules                        # Module container (references only)
│   ├── /HairStyle/Modules/Scalp              # REQUIRED: Scalp module reference
│   │   # All geometry, materials come from @modules/scalp.usd@ reference
│   │   # Style USD does not store material/texture data directly
│   │   # Textures stored as directory paths within modules
│   │
│   ├── /HairStyle/Modules/Crown              # OPTIONAL: Crown module reference
│   │   # All geometry, materials come from @modules/crown.usd@ reference
│   │
│   ├── /HairStyle/Modules/Tail               # OPTIONAL: Tail module reference
│   │   # All geometry, materials come from @modules/tail.usd@ reference
│   │
│   └── /HairStyle/Modules/Bang               # OPTIONAL: Bang module reference
│       # All geometry, materials come from @modules/bang.usd@ reference
│
├── /HairStyle/CrossModuleExclusions          # Cross-module exclusion rules
├── /HairStyle/BlendshapeConstraints          # Weight constraint rules
├── /HairStyle/HairRig                        # Animation system
│   ├── /HairStyle/HairRig/HairSkeleton
│   └── /HairStyle/HairRig/HairAnimation
│       └── /HairStyle/HairRig/HairAnimation/ModuleAnimations
│           ├── /HairStyle/HairRig/HairAnimation/ModuleAnimations/Scalp
│           ├── /HairStyle/HairRig/HairAnimation/ModuleAnimations/Crown
│           ├── /HairStyle/HairRig/HairAnimation/ModuleAnimations/Tail
│           └── /HairStyle/HairRig/HairAnimation/ModuleAnimations/Bang
│
├── /HairStyle/AnimationRules                 # Timeline metadata
│   └── /HairStyle/AnimationRules/TimelineMetadata
│
└── /HairStyle/QualityControl                 # QC validation & metadata
```

### Group USD Complete Hierarchy Example

Here's how a Group USD (e.g., `Group/short.usd`) is structured:

```
/HairGroup                                    # ROOT: Group definition
├── /HairGroup/ModuleWhitelist                # Available modules for this group
│   ├── /HairGroup/ModuleWhitelist/Scalp      # Scalp modules (always required)
│   │   └── moduleFiles = [@module/scalp/scalp.usd@]
│   │
│   ├── /HairGroup/ModuleWhitelist/Crown      # Crown module options
│   │   └── moduleFiles = [
│   │       @module/crown/short_crown_smallAfro.usd@,
│   │       @module/crown/short_crown_medAfro.usd@,
│   │       @module/crown/short_crown_slicked.usd@
│   │   ]
│   │
│   ├── /HairGroup/ModuleWhitelist/Tail       # Tail module options (may be empty)
│   │   └── moduleFiles = []
│   │
│   └── /HairGroup/ModuleWhitelist/Bang       # Bang module options
│       └── moduleFiles = [@module/bang/short_bang_trim.usd@]
│
└── /HairGroup/AlphaWhitelist                 # Approved textures for this group
    └── /HairGroup/AlphaWhitelist/Scalp       # Scalp texture categories
        ├── /HairGroup/AlphaWhitelist/Scalp/fade
        │   └── whitelistedTextures = [
        │       @module/scalp/alpha/fade/lineUp.png@,
        │       @module/scalp/alpha/fade/midFade.png@
        │   ]
        │
        ├── /HairGroup/AlphaWhitelist/Scalp/hairline
        │   └── whitelistedTextures = [
        │       @module/scalp/alpha/hairline/natural.png@,
        │       @module/scalp/alpha/hairline/sharp.png@
        │   ]
        │
        └── /HairGroup/AlphaWhitelist/Scalp/sideburn
            └── whitelistedTextures = [
                @module/scalp/alpha/sideburn/short.png@,
                @module/scalp/alpha/sideburn/trimmed.png@
            ]
```

### Module USD Complete Hierarchy Example

Here's how a Module USD (e.g., `module/crown/short_crown_smallAfro.usd`) is structured:

```
/HairModule                                   # ROOT: Module definition
├── /HairModule/BaseMesh                      # Geometry data
│   # Standard UsdGeom.Mesh with points, faces, etc.
│
├── /HairModule/BlendShapes                   # All blendshapes for this module
│   ├── /HairModule/BlendShapes/lengthen      # Lengthen blendshape
│   ├── /HairModule/BlendShapes/curly         # Curly blendshape
│   ├── /HairModule/BlendShapes/volumeOut     # Volume out blendshape
│   ├── /HairModule/BlendShapes/volumeIn      # Volume in blendshape
│   └── /HairModule/BlendShapes/hairline      # Hairline blendshape
│
├── /HairModule/Materials                     # Material definitions
│   └── /HairModule/Materials/HairMaterial    # Main hair material
│       ├── /HairModule/Materials/HairMaterial/HairShader  # Basic shader
│       └── /HairModule/Materials/HairMaterial/Primvar     # UV reader
│
├── /HairModule/TextureAssets                 # Texture path references
│   └── /HairModule/TextureAssets/WhitelistedTextures
│       ├── /HairModule/TextureAssets/WhitelistedTextures/NormalTextures
│       │   └── texturePaths = [
│       │       @module/crown/normal/texture1.png,
│       │       @module/crown/normal/texture2.png
│       │   ]
│       │
│       └── /HairModule/TextureAssets/WhitelistedTextures/AlphaSlots
│           ├── /HairModule/TextureAssets/WhitelistedTextures/AlphaSlots/Slot1
│           └── /HairModule/TextureAssets/WhitelistedTextures/AlphaSlots/Slot2
│
├── /HairModule/BlendshapeExclusions          # Internal exclusions
│   └── /HairModule/BlendshapeExclusions/VolumeExclusion
│       └── excludedBlendshapes = [
│           </BlendShapes/volumeOut>,
│           </BlendShapes/volumeIn>
│       ]
│
└── /HairModule/AlphaBlacklist                # Optional texture restrictions
    └── /HairModule/AlphaBlacklist/Scalp      # Scalp texture restrictions
        ├── /HairModule/AlphaBlacklist/Scalp/fade
        │   └── blacklistedTextures = [@module/scalp/alpha/fade/highFade.png@]
        │
        ├── /HairModule/AlphaBlacklist/Scalp/hairline
        │   └── blacklistedTextures = [@module/scalp/alpha/hairline/receding.png@]
        │
        └── /HairModule/AlphaBlacklist/Scalp/sideburn
            └── blacklistedTextures = []
```

## Directory Structure to USD Path Mapping

This section shows how USD asset paths map to the actual file system directory structure:

### USD References to Physical Files
```
# Group USD Reference Path             →    Physical File Location
@Group/short.usd@                       →    modular_hair/Group/short.usd
@Group/long.usd@                        →    modular_hair/Group/long.usd

# Module USD Reference Path            →    Physical File Location  
@module/scalp/scalp.usd@                →    modular_hair/module/scalp/scalp.usd
@module/crown/short_crown_smallAfro.usd@ →   modular_hair/module/crown/short_crown_smallAfro.usd
@module/tail/long_tail_braided.usd@     →    modular_hair/module/tail/long_tail_braided.usd
@module/bang/long_bang_messy.usd@       →    modular_hair/module/bang/long_bang_messy.usd
```

### USD Texture Paths to Physical Files
```
# USD Asset Path                       →    Physical File Location
@module/scalp/alpha/fade/lineUp.png    →    modular_hair/module/scalp/alpha/fade/lineUp.png
@module/scalp/normal/ripple.png        →    modular_hair/module/scalp/normal/ripple.png
@module/crown/alpha/fade1.png          →    modular_hair/module/crown/alpha/fade1.png
@module/tail/normal/texture.png        →    modular_hair/module/tail/normal/texture.png
```

### Group and Style Files in Directory Structure
```
# Group USD File                       →    Physical File Location
Group/short.usd                        →    modular_hair/Group/short.usd  
Group/long.usd                         →    modular_hair/Group/long.usd

# Style USD File                       →    Physical File Location
style/short_medAfro.usd                →    modular_hair/style/short_medAfro.usd
style/long_braided_beaded_messy.usd    →    modular_hair/style/long_braided_beaded_messy.usd
style/long_simple_pony_parted.usd      →    modular_hair/style/long_simple_pony_parted.usd
```

**Key Points:**
- USD `@` syntax creates relative asset paths
- USD resolver maps these to actual file system paths
- **Hierarchy**: Groups define whitelists → Styles reference modules → Modules contain assets
- Groups provide module whitelists and alpha texture whitelists for QC boundaries
- Each style `.usd` file references specific module `.usd` files from their group
- Texture paths are relative to the module that contains them
- Alpha textures use two-level system: Group whitelist + Module blacklist
- No absolute paths are stored in USD files

## Group USD Files (e.g., `short.usd`, `long.usd`)

### Root Level Paths
```
/HairGroup                                    # Root group prim with variants
```

### Module Whitelist Paths
```
/HairGroup/ModuleWhitelist                    # Module whitelists container
/HairGroup/ModuleWhitelist/Crown              # Crown module whitelist
/HairGroup/ModuleWhitelist/Tail               # Tail module whitelist  
/HairGroup/ModuleWhitelist/Bang               # Bang module whitelist
/HairGroup/ModuleWhitelist/Scalp              # Scalp module whitelist (required)
```

### Alpha Whitelist Paths  
```
/HairGroup/AlphaWhitelist                     # Alpha texture whitelists container
/HairGroup/AlphaWhitelist/Scalp               # Scalp alpha whitelists
/HairGroup/AlphaWhitelist/Scalp/fade          # Fade alpha whitelist
/HairGroup/AlphaWhitelist/Scalp/hairline      # Hairline alpha whitelist  
/HairGroup/AlphaWhitelist/Scalp/sideburn      # Sideburn alpha whitelist
```

## Module USD Files (e.g., `scalp.usd`, `short_crown_smallAfro.usd`, `long_tail_braided.usd`, `long_bang_messy.usd`)

### Root Level Paths
```
/HairModule                                    # Root module prim with variants
```

### Geometry Paths
```
/HairModule/BaseMesh                          # Main mesh geometry
```

### Blendshape Paths
```
/HairModule/BlendShapes                       # Blendshape container

# Crown module example:
/HairModule/BlendShapes/lengthen              # Lengthen blendshape
/HairModule/BlendShapes/curly                 # Curly blendshape
/HairModule/BlendShapes/volumeOut             # Volume out blendshape
/HairModule/BlendShapes/volumeIn              # Volume in blendshape
/HairModule/BlendShapes/hairline              # Hairline blendshape

# Scalp module example:
/HairModule/BlendShapes/hairline_fix          # Hairline fix blendshape (fires automatically with hairline)

# Tail module example:
/HairModule/BlendShapes/lengthen              # Lengthen blendshape
/HairModule/BlendShapes/wavy                  # Wavy blendshape
/HairModule/BlendShapes/spread                # Spread blendshape

# Bang module example:
/HairModule/BlendShapes/lengthen              # Lengthen blendshape
/HairModule/BlendShapes/frizzle               # Frizzle blendshape
/HairModule/BlendShapes/spread                # Spread blendshape
```

### Material and Shading Paths
```
/HairModule/Materials                         # Materials container
/HairModule/Materials/HairMaterial            # Main hair material
/HairModule/Materials/HairMaterial/HairShader # Main shader node (basic parameters only)
/HairModule/Materials/HairMaterial/Primvar    # UV coordinate reader
```

### Texture Asset Paths
```
/HairModule/TextureAssets                     # Texture assets container
/HairModule/TextureAssets/WhitelistedTextures # Whitelisted texture collections
/HairModule/TextureAssets/WhitelistedTextures/NormalTextures # Normal texture references
/HairModule/TextureAssets/WhitelistedTextures/AlphaSlots # Alpha texture slots (whitelisted at group level)
/HairModule/TextureAssets/WhitelistedTextures/AlphaSlots/Slot1 # First alpha slot
/HairModule/TextureAssets/WhitelistedTextures/AlphaSlots/Slot2 # Second alpha slot
```

### Exclusion Paths
```
/HairModule/BlendshapeExclusions              # Internal blendshape exclusions container
/HairModule/BlendshapeExclusions/VolumeExclusion # Volume exclusion (volumeOut ↔ volumeIn)
```

### Alpha Blacklist Paths (Optional)
```
/HairModule/AlphaBlacklist                    # Alpha texture blacklists container (optional)
/HairModule/AlphaBlacklist/Scalp              # Scalp alpha blacklists
/HairModule/AlphaBlacklist/Scalp/fade         # Fade alpha blacklist
/HairModule/AlphaBlacklist/Scalp/hairline     # Hairline alpha blacklist
/HairModule/AlphaBlacklist/Scalp/sideburn     # Sideburn alpha blacklist
```

## Style USD Files (e.g., `hairstyle_casual.usd`, `hairstyle_formal.usd`)

### Root Level Paths
```
/HairStyle                                    # Root style prim with variants
```

### Module Reference Paths
```
/HairStyle/Modules                            # Modules container
/HairStyle/Modules/Scalp                      # Scalp module reference
/HairStyle/Modules/Crown                      # Crown module reference  
/HairStyle/Modules/Tail                       # Tail module reference
/HairStyle/Modules/Bang                       # Bang module reference
```

### Cross-Module Paths
```
/HairStyle/CrossModuleExclusions              # Cross-module exclusions container
/HairStyle/CrossModuleExclusions/CrownBangVolumeConflict # Crown-Bang volume conflict
/HairStyle/CrossModuleExclusions/TailBangLengthConflict  # Tail-Bang length conflict

/HairStyle/BlendshapeConstraints              # Weight constraints container
/HairStyle/BlendshapeConstraints/CrownTailLengthConstraint # Crown-Tail length constraint
/HairStyle/BlendshapeConstraints/CrownBangCurlyConstraint  # Crown-Bang curly constraint
```

### Animation System Paths
```
/HairStyle/HairRig                            # Skeletal rig root
/HairStyle/HairRig/HairSkeleton               # Skeleton (optional)
/HairStyle/HairRig/HairAnimation              # Main animation container
/HairStyle/HairRig/HairAnimation/ModuleAnimations # Module-specific animations
/HairStyle/HairRig/HairAnimation/ModuleAnimations/Scalp # Scalp animation data
/HairStyle/HairRig/HairAnimation/ModuleAnimations/Crown # Crown animation data
/HairStyle/HairRig/HairAnimation/ModuleAnimations/Tail # Tail animation data
/HairStyle/HairRig/HairAnimation/ModuleAnimations/Bang # Bang animation data
```

### Animation Rules Paths
```
/HairStyle/AnimationRules                     # Animation rules container
/HairStyle/AnimationRules/TimelineMetadata    # Timeline metadata for external tools
```

### Quality Control Paths
```
/HairStyle/QualityControl                     # QC validation rules and metadata
```


## External Asset Reference Paths

These are the asset paths referenced from within USD files:

### Group File References
```
@Group/short.usd@</HairGroup>                                   # Short group reference
@Group/long.usd@</HairGroup>                                    # Long group reference
```

### Module File References
```
@module/scalp/scalp.usd@</HairModule>                           # Scalp module reference
@module/crown/short_crown_smallAfro.usd@</HairModule>           # Crown module reference
@module/tail/long_tail_braided.usd@</HairModule>                # Tail module reference  
@module/bang/long_bang_messy.usd@</HairModule>                  # Bang module reference
```

### Texture File References
```
# Normal textures (for shader reconstruction)
@module/scalp/normal/ripple.png             # Scalp ripple normal texture
@module/scalp/normal/wavy.png               # Scalp wavy normal texture
@module/crown/normal/texture1.png           # Crown normal texture 1
@module/crown/normal/texture2.png           # Crown normal texture 2
@module/tail/normal/texture.png             # Tail normal texture

# Alpha textures (whitelisted at group level, blacklistable at module level)
@module/scalp/alpha/fade/lineUp.png         # Scalp fade alpha texture
@module/scalp/alpha/fade/midFade.png        # Scalp mid fade alpha texture
@module/scalp/alpha/hairline/texture1.png   # Scalp hairline alpha texture
@module/scalp/alpha/sideburn/texture1.png   # Scalp sideburn alpha texture
```

## Path Relationship Examples

### Exclusion and Constraint Relationships
```
# Internal module exclusions (within a single module - binary on/off)
</BlendShapes/volumeOut>                      # Volume out blendshape
</BlendShapes/volumeIn>                       # Volume in blendshape (mutually exclusive)

# Cross-module exclusions (between different modules - binary on/off)
</Modules/Crown/BlendShapes/volumeOut>        # Crown volume out
</Modules/Bang/BlendShapes/spread>            # Bang spread (conflicting combination)

# Cross-module weight constraints (max weight limitations)
</Modules/Crown/BlendShapes/lengthen>         # Crown lengthen (max 0.7 when Tail.lengthen fires)
</Modules/Tail/BlendShapes/lengthen>          # Tail lengthen (max 0.5 when Crown.lengthen fires)
</Modules/Crown/BlendShapes/curly>            # Crown curly (max 0.8 when Bang.frizzle fires)
</Modules/Bang/BlendShapes/frizzle>           # Bang frizzle (max 0.6 when Crown.curly fires)
```

### Material Connection Paths
```
</Materials/HairMaterial/HairShader.outputs:surface>           # Surface output

</Materials/HairMaterial/Primvar.outputs:result>               # UV coordinate output
```

This reference provides a complete roadmap for navigating and understanding the USD structure paths. Each path represents a specific location in the hierarchy where data is stored or referenced.