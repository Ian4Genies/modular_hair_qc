# USD Technical Reference

This document contains detailed USD code examples and technical implementation details for the modular hair QC system. This is primarily for AI reference and technical implementation.

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
    
    # Optional: Alpha texture blacklist for this specific module  
    # (Crown QC determines what scalp alphas don't work with this crown)
    def "AlphaBlacklist" {
        def "Scalp" {
            def "fade" {
                # Crown-specific restrictions on scalp fade alphas
                asset[] blacklistedTextures = [
                    @module/scalp/alpha/fade/highFade.png@  # High fade conflicts with this crown style
                ]
            }
            
            def "hairline" {
                # Crown-specific restrictions on scalp hairline alphas  
                asset[] blacklistedTextures = [
                    @module/scalp/alpha/hairline/receding.png@  # Receding hairline doesn't work with this crown
                ]
            }
            
            def "sideburn" {
                # Crown-specific restrictions on scalp sideburn alphas
                asset[] blacklistedTextures = []  # No restrictions for this crown
            }
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

Note: this is useful only in so much it helps recreate the shader params in Blender, but texture connections will need to be procedurally assigned in Blender. 
```usd
def "Materials" {
    def Material "HairMaterial" {
        token outputs:surface.connect = </Materials/HairMaterial/HairShader.outputs:surface>
        
                def Shader "HairShader" {
            uniform token info:id = "UsdPreviewSurface"
            
            # Basic shader parameters (no diffuse/metallic/roughness)
            # Additional shader parameters will be set procedurally in Blender
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
        apiSchemas = ["CollectionAPI:alphaTextures", "CollectionAPI:normalTextures"]
    ) {
        # Normal texture references (for procedural shader reconstruction)
        def "NormalTextures" {
            asset[] texturePaths = [
                @module/scalp/normal/ripple.png,
                @module/scalp/normal/wavy.png
            ]
        }
        
        # Alpha texture slot configuration (whitelisted at group level)
        def "AlphaSlots" {
            def "Slot1" {
                asset[] texturePaths = [
                    @module/scalp/alpha/fade/lineUp.png,
                    @module/scalp/alpha/fade/midFade.png
                ]
            }
            def "Slot2" {
                asset[] texturePaths = [
                    @module/scalp/alpha/hairline/texture1.png,
                    @module/scalp/alpha/hairline/texture2.png
                ]
            }
        }
    }
}
```

#### 5. Two-Level Alpha Texture System Implementation

```usd
# Optional: Alpha texture blacklist for this specific module  
def "AlphaBlacklist" {
    def "Scalp" {
        def "fade" {
            asset[] blacklistedTextures = [
                @module/scalp/alpha/fade/highFade.png@  # This crown can't use high fade
            ]
        }
        def "hairline" {
            asset[] blacklistedTextures = [
                @module/scalp/alpha/hairline/receding.png@  # Doesn't work with this crown
            ]
        }
        def "sideburn" {
            asset[] blacklistedTextures = []  # No restrictions
        }
    }
}
```

#### 6. Internal Blendshape Exclusions
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

## Group USD Structure Implementation

### Generic Group USD Format

**Example Group File**: `Group/short.usd`

```usd
def "HairGroup" (
    variants = {
        string groupType = "short"
    }
) {
    # Module whitelist - modules included in this group
    def "ModuleWhitelist" {
        def "Crown" {
            asset[] moduleFiles = [
                @module/crown/short_crown_smallAfro.usd@,
                @module/crown/short_crown_medAfro.usd@,
                @module/crown/short_crown_slicked.usd@,
                @module/crown/short_crown_combed.usd@
            ]
        }
        
        def "Tail" {
            # Note: Short group may have no tail modules
            asset[] moduleFiles = []
        }
        
        def "Bang" {
            # Short group typically has minimal bang options
            asset[] moduleFiles = [
                @module/bang/short_bang_trim.usd@
            ]
        }
        
        def "Scalp" {
            # Scalp is required for all groups
            asset[] moduleFiles = [
                @module/scalp/scalp.usd@
            ]
        }
    }
    
    # Alpha texture whitelist for this group
    def "AlphaWhitelist" {
        def "Scalp" {
            def "fade" {
                asset[] whitelistedTextures = [
                    @module/scalp/alpha/fade/lineUp.png@,
                    @module/scalp/alpha/fade/midFade.png@,
                    @module/scalp/alpha/fade/highFade.png@
                ]
            }
            
            def "hairline" {
                asset[] whitelistedTextures = [
                    @module/scalp/alpha/hairline/natural.png@,
                    @module/scalp/alpha/hairline/sharp.png@
                ]
            }
            
            def "sideburn" {
                asset[] whitelistedTextures = [
                    @module/scalp/alpha/sideburn/short.png@,
                    @module/scalp/alpha/sideburn/trimmed.png@
                ]
            }
        }
    }
}
```

### Long Group Example

**Example Group File**: `Group/long.usd`

```usd
def "HairGroup" (
    variants = {
        string groupType = "long"
    }
) {
    # Module whitelist - modules included in this group
    def "ModuleWhitelist" {
        def "Crown" {
            asset[] moduleFiles = [
                @module/crown/Long_crown_simple.usd@,
                @module/crown/Long_crown_braided.usd@,
                @module/crown/Long_crown_fancy.usd@
            ]
        }
        
        def "Tail" {
            # Long group has extensive tail options
            asset[] moduleFiles = [
                @module/tail/long_tail_braided.usd@,
                @module/tail/long_tail_pony.usd@,
                @module/tail/long_tail_beaded.usd@
            ]
        }
        
        def "Bang" {
            asset[] moduleFiles = [
                @module/bang/long_bang_straightCut.usd@,
                @module/bang/long_bang_messy.usd@,
                @module/bang/long_bang_parted.usd@
            ]
        }
        
        def "Scalp" {
            asset[] moduleFiles = [
                @module/scalp/scalp.usd@
            ]
        }
    }
    
    # Alpha texture whitelist for this group (more permissive for long styles)
    def "AlphaWhitelist" {
        def "Scalp" {
            def "fade" {
                asset[] whitelistedTextures = [
                    @module/scalp/alpha/fade/lineUp.png@,
                    @module/scalp/alpha/fade/midFade.png@,
                    @module/scalp/alpha/fade/lowFade.png@,
                    @module/scalp/alpha/fade/noFade.png@
                ]
            }
            
            def "hairline" {
                asset[] whitelistedTextures = [
                    @module/scalp/alpha/hairline/natural.png@,
                    @module/scalp/alpha/hairline/receding.png@,
                    @module/scalp/alpha/hairline/widows_peak.png@
                ]
            }
            
            def "sideburn" {
                asset[] whitelistedTextures = [
                    @module/scalp/alpha/sideburn/long.png@,
                    @module/scalp/alpha/sideburn/full.png@,
                    @module/scalp/alpha/sideburn/shaped.png@
                ]
            }
        }
    }
}
```

## Style USD Structure Implementation

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

# Normal texture paths in modules use relative paths:
asset inputs:file = @module/scalp/normal/ripple.png
```

**Usage**: This allows your USD files to use relative paths which USD's resolver automatically maps to actual file locations. Essential for portable data containers that work across different directory structures without hardcoded paths.

This technical reference provides all the detailed USD implementation code for building the modular hair QC system.