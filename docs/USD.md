# Improved USD Data Structure for Modular Hair QC

## Overview
This document outlines an improved USD-based data structure for a modular hair quality control system, leveraging USD's built-in schemas and composition features for better performance, maintainability, and industry standard compliance.

## Case Study: Blendshape Sample
This document uses the following blendshape configuration as examples throughout:

- **Scalp**: `hairline_fix`
- **Crown**: `lengthen`, `curly`, `volumeOut`, `volumeIn`, `hairline`  
- **Tail**: `lengthen`, `wavy`, `spread`
- **Bang**: `lengthen`, `frizzle`, `spread`

**Note**: The `scalp.hairline_fix` blendshape fires automatically with any `hairline` blendshape from other modules. This is handled implicitly and doesn't require special USD tracking.

## File Organization

**Critical**: Each module and style is stored as a **separate .usd file**. This is not a single large USD with multiple prims, but individual USD files that reference each other:

### **Module Files** (Individual .usd files)
```
module/scalp/scalp.usd                          # Single scalp module
module/crown/short_crown_smallAfro.usd          # Specific crown variation  
module/crown/short_crown_medAfro.usd            # Another crown variation
module/crown/Long_crown_braided.usd             # Long crown variation
module/tail/long_tail_braided.usd               # Specific tail variation
module/bang/long_bang_messy.usd                 # Specific bang variation
```

### **Style Files** (Individual .usd files)
```
style/short_medAfro.usd                         # References specific modules
style/long_braided_beaded_messy.usd             # References different modules  
style/long_simple_pony_parted.usd               # Another combination
```

### **Texture Organization** (PNG files in module subdirectories)
```  
module/scalp/alpha/fade/lineUp.png              # Alpha textures within modules
module/scalp/normal/ripple.png                  # Normal maps within modules
module/crown/alpha/[texture files]              # Crown-specific textures
```

**Each style .usd file contains USD references to the specific module .usd files it needs.**

## Complete Module Examples

The following sections show how each module type would be structured using the case study blendshapes:

### Scalp Module Example (`scalp.usd`)
```usd
def "HairModule" (
    variants = {
        string moduleType = "scalp"
    }
) {
    def Mesh "BaseMesh" {
        # Scalp geometry data
    }
    
    def BlendShape "BlendShapes" {
        def "hairline_fix" {
            point3f[] offsets = [...]  # Fires automatically with Crown.hairline
        }
    }
    
    # No exclusions needed for scalp (only one blendshape)
}
```

### Crown Module Example (`short_crown_smallAfro.usd`)
```usd
def "HairModule" (
    variants = {
        string moduleType = "crown"
    }
) {
    def Mesh "BaseMesh" {
        # Small afro crown geometry data
    }
    
    def BlendShape "BlendShapes" {
        def "lengthen" {
            point3f[] offsets = [...]
        }
        def "curly" {
            point3f[] offsets = [...]
        }
        def "volumeOut" {
            point3f[] offsets = [...]
        }
        def "volumeIn" {
            point3f[] offsets = [...]
        }
        def "hairline" {
            point3f[] offsets = [...]  # Triggers Scalp.hairline_fix
        }
    }
    
    def "BlendshapeExclusions" {
        def "VolumeExclusion" {
            rel excludedBlendshapes = [
                </BlendShapes/volumeOut>,
                </BlendShapes/volumeIn>
            ]
        }
    }
}
```

### Tail Module Example (`long_tail_braided.usd`)
```usd
def "HairModule" (
    variants = {
        string moduleType = "tail"
    }
) {
    def Mesh "BaseMesh" {
        # Long braided tail geometry data
    }
    
    def BlendShape "BlendShapes" {
        def "lengthen" {
            point3f[] offsets = [...]
        }
        def "wavy" {
            point3f[] offsets = [...]
        }
        def "spread" {
            point3f[] offsets = [...]
        }
    }
    
    # No internal exclusions needed for this example
}
```

### Bang Module Example (`long_bang_messy.usd`)
```usd
def "HairModule" (
    variants = {
        string moduleType = "bang"
    }
) {
    def Mesh "BaseMesh" {
        # Long messy bang geometry data
    }
    
    def BlendShape "BlendShapes" {
        def "lengthen" {
            point3f[] offsets = [...]
        }
        def "frizzle" {
            point3f[] offsets = [...]
        }
        def "spread" {
            point3f[] offsets = [...]
        }
    }
    
    # No internal exclusions needed for this example
}
```

## Module USD Structure

### Core Components

#### 1. Mesh and Deformation
```usd
def "HairModule" (
    variants = {
        string moduleType = "scalp"
    }
) {
    # Base mesh using USD's native mesh schema
    def Mesh "BaseMesh" {
        # Standard UsdGeom.Mesh attributes
        # point3f[] points
        # int[] faceVertexCounts
        # int[] faceVertexIndices
    }
    
    # Blendshapes using USD's native blendshape system
    def BlendShape "BlendShapes" {
        # UsdSkel.BlendShape schema
        # point3f[] offsets (per blendshape target)
        # int[] pointIndices (sparse blendshapes supported)
        
        def "lengthen" {
            point3f[] offsets = [...]
        }
        def "curly" {
            point3f[] offsets = [...]
        }
        def "volumeOut" {
            point3f[] offsets = [...]
        }
        def "volumeIn" {
            point3f[] offsets = [...]
        }
        def "hairline" {
            point3f[] offsets = [...]
        }
    }
}
```

#### 2. Module Type Classification (Using USD Variants)
```usd
def "HairModule" (
    variants = {
        string moduleType = "scalp"
    }
) {
    # Variant set for module types
    variantSet "moduleType" = {
        "scalp" {
            # Scalp-specific geometry and properties
            custom string description = "Base scalp hair module"
        }
        "crown" {
            # Crown-specific geometry and properties  
            custom string description = "Crown hair module"
        }
        "tail" {
            # Tail-specific geometry and properties
            custom string description = "Hair tail module"
        }
        "bang" {
            # Bang-specific geometry and properties
            custom string description = "Bang hair module"
        }
    }
}
```

#### 3. Shader System (USD Native Shading)

Note: this is usefull only in so much it helps recreate the shader params in blender, but texture connections will need to be procedurally assigned in blender. 
```usd
def "Materials" {
    def Material "HairMaterial" {
        token outputs:surface.connect = </Materials/HairMaterial/HairShader.outputs:surface>
        
        def Shader "HairShader" {
            uniform token info:id = "UsdPreviewSurface"
            
            # Shader parameters as inputs
            color3f inputs:diffuseColor = (0.8, 0.6, 0.4)
            float inputs:roughness = 0.7
            float inputs:metallic = 0.0
            
            # Connect textures
            color3f inputs:diffuseColor.connect = </Materials/HairMaterial/DiffuseTexture.outputs:rgb>
        }
        
                  def Shader "DiffuseTexture" {
              uniform token info:id = "UsdUVTexture"
              asset inputs:file = @module/scalp/normal/ripple.png
              float2 inputs:st.connect = </Materials/HairMaterial/Primvar.outputs:result>
          }
        
        def Shader "Primvar" {
            uniform token info:id = "UsdPrimvarReader_float2"
            string inputs:varname = "st"
        }
    }
}
```

#### 4. Texture Management 
```usd
def "TextureAssets" {
    # Whitelisted texture collections using USD Collections
    def "WhitelistedTextures" (
        apiSchemas = ["CollectionAPI:diffuseTextures", "CollectionAPI:alphaTextures"]
    ) {
        # Diffuse texture slot configuration
        def "DiffuseSlots" {
            def "Slot1" {
                asset[] texturePaths = [
                    @module/scalp/normal/ripple.png,
                    @module/scalp/normal/wavy.png
                ]
            }
            def "Slot2" {
                asset[] texturePaths = [
                    @module/crown/normal/texture1.png, 
                    @module/crown/normal/texture2.png
                ]
            }
        }
        
        # Alpha texture slot configuration
        def "AlphaSlots" {
            def "Slot1" {
                asset[] texturePaths = [
                    @module/scalp/alpha/fade/lineUp.png,
                    @module/scalp/alpha/fade/midFade.png
                ]
            }
            def "Slot2" {
                asset[] texturePaths = [
                    @module/crown/alpha/fade1.png,
                    @module/crown/alpha/fade2.png
                ]
            }
        }
    }
}
```

#### 5. Internal Blendshape Exclusions
```usd
# USD-native approach for mutually exclusive blendshapes within a module
def "BlendshapeExclusions" {
    # Mutually exclusive blendshape pairs (binary on/off)
    def "VolumeExclusion" {
        rel excludedBlendshapes = [
            </BlendShapes/volumeOut>,
            </BlendShapes/volumeIn>
        ]
    }
    
    # Additional exclusion pairs can be added as needed
    # def "AnotherExclusion" {
    #     rel excludedBlendshapes = [...]
    # }
}
```

## Style USD Structure

**Key Principle**: Style USDs are lean data containers with **references only**. All texture/material data lives in Module USDs.

### **What Style USD Contains:**
- ✅ Module references (`@modules/scalp.usd@`)
- ✅ Cross-module exclusions (blendshapes that conflict between modules)  
- ✅ Weight constraints (max weight rules between modules)
- ✅ Animation data (blendshape weight timelines)
- ❌ **NO texture connections, materials, or TextureAssets**

### **What Module USD Contains:**
- ✅ All geometry and blendshapes
- ✅ All materials, shaders, and texture connections
- ✅ whitelisted texture collections
- ✅ Internal exclusions (within-module blendshape conflicts)

### 1. Module Composition (USD References & Payloads)

**Example Style File**: `style/short_medAfro.usd`

```usd
def "HairStyle" (
    variants = {
        string styleType = "casual"
    }
) {
    # Module references with lazy loading capability
    def "Modules" {
        def "Scalp" (
            references = @module/scalp/scalp.usd@</HairModule>
            payload = @module/scalp/scalp.usd@</HairModule>
        ) {
            # No overrides - all material/texture data comes from module
        }
        
        def "Crown" (
            references = @module/crown/short_crown_smallAfro.usd@</HairModule>
            payload = @module/crown/short_crown_smallAfro.usd@</HairModule>
            variants = {
                string moduleType = "crown"
            }
        ) {
            # No material overrides - all texture data comes from module
        }
        
        def "Tail" (
            references = @module/tail/long_tail_braided.usd@</HairModule>
            payload = @module/tail/long_tail_braided.usd@</HairModule>
        ) {
            # No material overrides - all texture data comes from module
        }
        
        def "Bang" (
            references = @module/bang/long_bang_messy.usd@</HairModule>
            payload = @module/bang/long_bang_messy.usd@</HairModule>
        ) {
            # No material overrides - all texture data comes from module
        }
    }
}
```

### 2. Cross-Module Exclusions and Constraints

#### Cross-Module Exclusions (Binary On/Off)
```usd
def "CrossModuleExclusions" {
    # Mutually exclusive blendshapes between different modules
    def "CrownBangVolumeConflict" {
        rel excludedBlendshapes = [
            </Modules/Crown/BlendShapes/volumeOut>,
            </Modules/Bang/BlendShapes/spread>
        ]
    }
    
    def "TailBangLengthConflict" {
        rel excludedBlendshapes = [
            </Modules/Tail/BlendShapes/lengthen>,
            </Modules/Bang/BlendShapes/lengthen>
        ]
    }
}
```

#### Weight Constraints (Max Weight Limitations)
```usd
def "BlendshapeConstraints" {
    # Weight limitations when blendshapes are used together
    def "CrownTailLengthConstraint" {
        rel constrainedBlendshapes = [
            </Modules/Crown/BlendShapes/lengthen>,
            </Modules/Tail/BlendShapes/lengthen>
        ]
        float[] maxWeights = [0.7, 0.5]  # Crown max=0.7, Tail max=0.5 when both fire
    }
    
    def "CrownBangCurlyConstraint" {
        rel constrainedBlendshapes = [
            </Modules/Crown/BlendShapes/curly>,
            </Modules/Bang/BlendShapes/frizzle>
        ]
        float[] maxWeights = [0.8, 0.6]  # Crown max=0.8, Bang max=0.6 when both fire
    }
}
```

### 3. Animation System (USD Native)

#### Blendshape Animation Setup
```usd
def SkelRoot "HairRig" {
    def Skeleton "HairSkeleton" {
        # Optional: if you need skeletal deformation in addition to blendshapes
    }
    
    def SkelAnimation "HairAnimation" (
        apiSchemas = ["SkelBindingAPI"]
    ) {
        # Frame range using USD's native time sampling
        double startTimeCode = 1
        double endTimeCode = 120
        
        # Master blendshape weight animation across all modules
        float[] blendShapeWeights.timeSamples = {
            1: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            30: [0.8, 0.3, 0.0, 0.0, 0.5, 0.8, 0.0, 0.4, 0.6, 0.2, 0.0, 0.0, 0.0],
            60: [0.2, 0.7, 0.4, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.3, 0.4],
            120: [0.0, 0.0, 0.0, 0.0, 0.0, 0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        }
        
        # Blendshape target order reference
        string[] blendShapeTargets = [
            "Scalp.hairline_fix", "Crown.lengthen", "Crown.curly", "Crown.volumeOut", 
            "Crown.volumeIn", "Crown.hairline", "Tail.lengthen", "Tail.wavy", 
            "Tail.spread", "Bang.lengthen", "Bang.frizzle", "Bang.spread"
        ]
        
        # Module-specific animation data
        def "ModuleAnimations" {
            def "Scalp" {
                float[] blendShapeWeights.timeSamples = {
                    1: [0.0],
                    30: [0.8],    # hairline_fix fires with Crown.hairline
                    60: [0.2],    # hairline_fix reduced as Crown.hairline peaks
                    120: [0.0]
                                }
                string[] blendShapeTargets = ["hairline_fix"]
            }
            
            def "Crown" {
                float[] blendShapeWeights.timeSamples = {
                    1: [0.0, 0.0, 0.0, 0.0, 0.0],    # [lengthen, curly, volumeOut, volumeIn, hairline]
                    30: [0.3, 0.0, 0.0, 0.5, 0.8],   # Frame 30
                    60: [0.7, 0.4, 0.0, 0.0, 1.0],   # Frame 60
                    120: [0.0, 0.0, 0.0, 0.0, 0.2]   # Frame 120
                }
                string[] blendShapeTargets = ["lengthen", "curly", "volumeOut", "volumeIn", "hairline"]
            }
            
            def "Tail" {
                float[] blendShapeWeights.timeSamples = {
                    1: [0.0, 0.0, 0.0],
                    45: [0.4, 0.6, 0.2],
                    120: [0.0, 0.0, 0.0]
                }
                string[] blendShapeTargets = ["lengthen", "wavy", "spread"]
            }
            
            def "Bang" {
                float[] blendShapeWeights.timeSamples = {
                    1: [0.0, 0.0, 0.0],
                    60: [0.5, 0.3, 0.4],
                    120: [0.0, 0.0, 0.0]
                }
                string[] blendShapeTargets = ["lengthen", "frizzle", "spread"]
            }
        }
    }
}
```

#### Animation Rules and Timeline
```usd
def "AnimationRules" {
    # Rules for UI and timeline generation
    def "BlendshapeRules" {
        string[] ruleDescriptions = [
            "Crown.lengthen max 0.7 when Tail.lengthen > 0.3",
            "Crown.curly max 0.8 when Bang.frizzle > 0.4", 
            "Cross-module timing: Crown.hairline leads to Scalp.hairline_fix"
        ]
        
        # Rule implementation as relationships or custom attributes
        custom string lengthConstraint = "Crown.lengthen.max = 0.7 when Tail.lengthen > 0.3"
        custom string curlyConstraint = "Crown.curly.max = 0.8 when Bang.frizzle > 0.4"
    }
    
    # Timeline metadata for external tools
    def "TimelineMetadata" {
        custom int frameRate = 24
        custom string timeUnit = "frames"
        custom bool looping = false
        
        # Keyframe markers for external tools
        int[] keyframes = [1, 30, 60, 90, 120]
        string[] keyframeLabels = ["Start", "BuildUp", "Peak", "Decay", "End"]
    }
}
```

## Advanced Features

### Asset Resolution Configuration
```usd
# Configure search paths for textures and modules in your USD resolver context

# Module references use relative paths:
references = @modules/scalp_v001.usd@</HairModule>

# Texture paths in modules use relative paths:
asset inputs:file = @module/scalp/normal/ripple.png
```

**Usage**: This allows your USD files to use relative paths which USD's resolver automatically maps to actual file locations. Essential for portable data containers that work across different directory structures without hardcoded paths.

## Directory Structure to USD Path Mapping

This section shows how USD asset paths map to the actual file system directory structure:

### **USD References to Physical Files**
```
# USD Reference Path                    →    Physical File Location
@module/scalp/scalp.usd@                →    modular_hair/module/scalp/scalp.usd
@module/crown/short_crown_smallAfro.usd@ →   modular_hair/module/crown/short_crown_smallAfro.usd
@module/tail/long_tail_braided.usd@     →    modular_hair/module/tail/long_tail_braided.usd
@module/bang/long_bang_messy.usd@       →    modular_hair/module/bang/long_bang_messy.usd
```

### **USD Texture Paths to Physical Files**
```
# USD Asset Path                       →    Physical File Location
@module/scalp/alpha/fade/lineUp.png    →    modular_hair/module/scalp/alpha/fade/lineUp.png
@module/scalp/normal/ripple.png        →    modular_hair/module/scalp/normal/ripple.png
@module/crown/alpha/fade1.png          →    modular_hair/module/crown/alpha/fade1.png
@module/tail/normal/texture.png        →    modular_hair/module/tail/normal/texture.png
```

### **Style Files in Directory Structure**
```
# Style USD File                       →    Physical File Location
style/short_medAfro.usd                →    modular_hair/style/short_medAfro.usd
style/long_braided_beaded_messy.usd    →    modular_hair/style/long_braided_beaded_messy.usd
style/long_simple_pony_parted.usd      →    modular_hair/style/long_simple_pony_parted.usd
```

**Key Points:**
- USD `@` syntax creates relative asset paths
- USD resolver maps these to actual file system paths
- Each style `.usd` file references specific module `.usd` files
- Texture paths are relative to the module that contains them
- No absolute paths are stored in USD files

## USD Path Reference

This section provides a complete reference of all USD paths used in the proposed structure, organized by file and hierarchy level.

### Module USD Files (e.g., `scalp.usd`, `crown.usd`, `tail.usd`, `bang.usd`)

#### Root Level Paths
```
/HairModule                                    # Root module prim with variants
```

#### Geometry Paths
```
/HairModule/BaseMesh                          # Main mesh geometry
```

#### Blendshape Paths
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

#### Material and Shading Paths
```
/HairModule/Materials                         # Materials container
/HairModule/Materials/HairMaterial            # Main hair material
/HairModule/Materials/HairMaterial/HairShader # Main shader node
/HairModule/Materials/HairMaterial/DiffuseTexture # Diffuse texture shader
/HairModule/Materials/HairMaterial/Primvar    # UV coordinate reader
```

#### Texture Asset Paths
```
/HairModule/TextureAssets                     # Texture assets container
/HairModule/TextureAssets/WhitelistedTextures # Whitelisted texture collections
/HairModule/TextureAssets/WhitelistedTextures/DiffuseSlots # Diffuse texture slots
/HairModule/TextureAssets/WhitelistedTextures/DiffuseSlots/Slot1 # First diffuse slot
/HairModule/TextureAssets/WhitelistedTextures/DiffuseSlots/Slot2 # Second diffuse slot
/HairModule/TextureAssets/WhitelistedTextures/AlphaSlots # Alpha texture slots
/HairModule/TextureAssets/WhitelistedTextures/AlphaSlots/Slot1 # First alpha slot
/HairModule/TextureAssets/WhitelistedTextures/AlphaSlots/Slot2 # Second alpha slot
```

#### Exclusion Paths
```
/HairModule/BlendshapeExclusions              # Internal blendshape exclusions container
/HairModule/BlendshapeExclusions/VolumeExclusion # Volume exclusion (volumeOut ↔ volumeIn)
```

### Style USD Files (e.g., `hairstyle_casual.usd`, `hairstyle_formal.usd`)

#### Root Level Paths
```
/HairStyle                                    # Root style prim with variants
```

#### Module Reference Paths
```
/HairStyle/Modules                            # Modules container
/HairStyle/Modules/Scalp                      # Scalp module reference
/HairStyle/Modules/Crown                      # Crown module reference  
/HairStyle/Modules/Tail                       # Tail module reference
/HairStyle/Modules/Bang                       # Bang module reference
```

#### Style Override Paths (Examples)
```
# No material/texture overrides at style level
# All texture connections are stored at module level only
# Overrides would only be for cross-module data or animation
```

#### Cross-Module Paths
```
/HairStyle/CrossModuleExclusions              # Cross-module exclusions container
/HairStyle/CrossModuleExclusions/CrownBangVolumeConflict # Crown-Bang volume conflict
/HairStyle/CrossModuleExclusions/TailBangLengthConflict  # Tail-Bang length conflict

/HairStyle/BlendshapeConstraints              # Weight constraints container
/HairStyle/BlendshapeConstraints/CrownTailLengthConstraint # Crown-Tail length constraint
/HairStyle/BlendshapeConstraints/CrownBangCurlyConstraint  # Crown-Bang curly constraint
```

#### Animation System Paths
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

#### Animation Rules Paths
```
/HairStyle/AnimationRules                     # Animation rules container
/HairStyle/AnimationRules/TimelineMetadata    # Timeline metadata for external tools
```

#### Quality Control Paths
```
/HairStyle/QualityControl                     # QC validation rules and metadata
```

### User Override Layer Files (e.g., `user_overrides.usd`)

#### Override Paths (Examples)
```
# Note: This document covers data storage structure
# User override layers are not part of the core data pipeline
# All texture connections remain at module level
```

### Complete Path Hierarchy Example

Here's how a complete hairstyle would look when all modules are loaded:

```
/HairStyle                                    # ROOT: Main hairstyle
├── /HairStyle/Modules                        # Module container (references only)
│   ├── /HairStyle/Modules/Scalp              # REQUIRED: Scalp module reference
│   │   # All geometry, materials, textures come from @modules/scalp.usd@ reference
│   │   # Style USD does not store material/texture data directly
│   │
│   ├── /HairStyle/Modules/Crown              # OPTIONAL: Crown module reference
│   │   # All geometry, materials, textures come from @modules/crown.usd@ reference
│   │
│   ├── /HairStyle/Modules/Tail               # OPTIONAL: Tail module reference
│   │   # All geometry, materials, textures come from @modules/tail.usd@ reference
│   │
│   └── /HairStyle/Modules/Bang               # OPTIONAL: Bang module reference
│       # All geometry, materials, textures come from @modules/bang.usd@ reference
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

### External Asset Reference Paths

These are the asset paths referenced from within USD files:

#### Module File References
```
@module/scalp/scalp.usd@</HairModule>                           # Scalp module reference
@module/crown/short_crown_smallAfro.usd@</HairModule>           # Crown module reference
@module/tail/long_tail_braided.usd@</HairModule>                # Tail module reference  
@module/bang/long_bang_messy.usd@</HairModule>                  # Bang module reference
```

#### Texture File References
```
@module/scalp/normal/ripple.png             # Main diffuse texture
@module/scalp/normal/wavy.png               # Scalp wavy normal texture
@module/crown/normal/texture1.png           # Crown normal texture 1
@module/crown/normal/texture2.png           # Crown normal texture 2
@module/scalp/alpha/fade/lineUp.png         # Scalp fade alpha texture
@module/scalp/alpha/fade/midFade.png        # Scalp mid fade alpha texture
@module/crown/alpha/fade1.png               # Crown alpha texture 1
@module/crown/alpha/fade2.png               # Crown alpha texture 2
@module/tail/normal/texture.png             # Tail normal texture
@module/bang/alpha/texture.png              # Bang alpha texture
```

### Path Relationship Examples

#### Exclusion and Constraint Relationships
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

#### Material Connection Paths
```
</Materials/HairMaterial/HairShader.outputs:surface>           # Surface output
</Materials/HairMaterial/DiffuseTexture.outputs:rgb>           # Diffuse texture output  
</Materials/HairMaterial/Primvar.outputs:result>               # UV coordinate output
```

This reference provides a complete roadmap for navigating and understanding the proposed USD structure. Each path represents a specific location in the hierarchy where data is stored or referenced.