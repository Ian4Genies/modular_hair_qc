# Hair QC Tool - Task List

## Project Overview
Creating a Maya tool for modular hair quality control using USD-based data management system.

## High-Level Architecture
- **USD System**: Group-level rules, Style-level animation, Module-level assets
- **Maya Integration**: Shelf tool, imported geometry, native timeline with color coding  
- **Performance**: 6000 frame limit, lazy loading by group
- **UI**: Single-selection lists, Maya menu bar + hotkey widget, manual regeneration
- **Validation**: Real-time USD reference and blendshape validation

## Task Breakdown

### 1. Project Setup & Foundation
**Status**: ✅ **COMPLETED**
- [x] Set up Python package structure with utils folder
- [x] Create Maya shelf tool entry point
- [x] Set up USD Python API integration
- [x] Create base configuration system for USD directory paths
- [x] Set up logging and error handling framework

### 2. USD Utility System
**Status**: ✅ **COMPLETED**  
- [x] Create `USDGroupUtils` class for Group USD operations
- [x] Create `USDModuleUtils` class for Module USD operations  
- [x] Create `USDStyleUtils` class for Style USD operations
- [x] Implement custom data serialization for BlendshapeRules
- [x] Implement custom data serialization for CrossModuleExclusions
- [x] Create USD stage management utilities

### 3. Group Management System
**Status**: ✅ **COMPLETED**
- [x] Implement group discovery and loading from USD directory
- [x] Create group creation/deletion functionality
- [x] Implement alpha texture whitelist management
- [x] Create group-level rule storage and retrieval
- [x] Implement module whitelist management per group

### 4. Module Management System  
**Status**: ✅ **COMPLETED**
- [x] Implement module USD file creation and loading
- [x] Create geometry import from Maya scene to USD
- [x] Implement blendshape import and management
- [x] Create internal module exclusions system
- [x] Implement alpha texture blacklist functionality
- [x] Add module validation (geometry, blendshapes exist)

### 5. Style Management System
**Status**: Pending
- [ ] Implement style combinatorics generation from group modules
- [ ] Create style USD file creation with module references  
- [ ] Implement style validation (references exist, blendshapes exist)
- [ ] Create style loading and composition in Maya
- [ ] Implement cross-module rule inheritance from group level

### 6. Main UI Framework
**Status**: 🟡 **PARTIALLY COMPLETED**
- [x] Create main window with scrollable sections
- [x] Implement group selection UI with alpha whitelist expansion
- [x] Create module/style tab switching system
- [x] Implement module selection and editing UI *(placeholder functionality)*
- [x] Create style selection and editing UI *(placeholder functionality)*
- [x] Add hotkey reference widget at top of tool

### 7. Blendshape Combination System
**Status**: Pending
- [ ] Implement combination generation algorithm (from Python reference)
- [ ] Create timeline generation with 10 frames per combination
- [ ] Implement 6000 frame limit with overflow warnings
- [ ] Create blendshape weight animation keyframe system
- [ ] Integrate with Maya's native timeline system

### 8. Rules & Exclusions System
**Status**: Pending
- [ ] Implement cross-module exclusion creation and editing
- [ ] Create weight constraint system for blendshape interactions
- [ ] Implement rule propagation from group to all applicable styles
- [ ] Create rule validation and conflict detection
- [ ] Add manual timeline regeneration with rule application

### 9. Validation & Error Handling
**Status**: Pending
- [ ] Implement real-time USD reference validation
- [ ] Create blendshape existence validation across modules
- [ ] Implement broken reference detection and UI display
- [ ] Create "remove invalid data" functionality
- [ ] Add external file change detection and warnings

### 10. Maya Integration
**Status**: 🟡 **PARTIALLY COMPLETED**
- [x] Create "Hair QC" menu in Maya's main menu bar
- [x] Implement keyboard shortcuts (Tab, F5, Ctrl+R, Ctrl+S, Ctrl+O)
- [ ] Integrate with Maya's hotkey editor system
- [x] Create shelf button for tool launch
- [ ] Implement Maya scene geometry loading for modules

### 11. Timeline Visualization
**Status**: Pending
- [ ] Implement timeline color-coding for invalid combinations (red)
- [ ] Create visual indicators for rule-affected regions
- [ ] Add timeline navigation and frame selection
- [ ] Implement blendshape weight slider integration
- [ ] Create timeline regeneration progress indicators

### 12. File Management & Utilities
**Status**: 🟡 **PARTIALLY COMPLETED**
- [x] Implement naming validation (no spaces, auto-convert to underscores)
- [x] Create file path utilities for USD directory structure
- [ ] Add external change detection for USD files
- [ ] Implement clean removal of invalid references
- [ ] Create backup and recovery utilities (if needed)

### 13. Testing & Polish
**Status**: Pending
- [ ] Create test USD directory structure with sample data
- [ ] Test all UI workflows end-to-end
- [ ] Performance testing with large datasets
- [ ] Bug fixes and error handling improvements
- [ ] Documentation and user guide creation

## Technical Notes

### Key Design Decisions
- **Geometry Loading**: Import USD to Maya geometry for better blendshape manipulation
- **Rule Storage**: Group-level storage with style inheritance
- **Timeline**: Maya native timeline with 6000 frame limit
- **Validation**: Real-time with manual refresh options
- **UI**: Single-selection only, no batch operations

### Performance Considerations
- Lazy loading by group (max ~20 modules per group)
- USD stage caching and reuse
- Batch save operations to minimize disk I/O
- 6000 frame limit prevents Maya timeline overload

### Integration Points
- Maya shelf tool as primary entry point
- Maya menu bar integration for discoverability
- USD Python APIs for all file operations
- Maya's native blendshape and animation systems

## Current Status: Module Management Completed ✅

### ✅ **COMPLETED SYSTEMS:**
1. **Project Setup & Foundation** - Full Python package, Maya integration, USD API setup
2. **USD Utility System** - Complete USD utils for Groups, Modules, Styles with serialization
3. **Group Management System** - Full group CRUD, alpha whitelist, rule storage
4. **Module Management System** - Full module CRUD, geometry import/export, blendshape management

### 🟡 **PARTIALLY COMPLETED:**
- **Main UI Framework** - Core UI done, module/style functionality placeholders
- **Maya Integration** - Menu, shortcuts, shelf button done; geometry loading pending
- **File Management** - Naming validation and path utilities done

### 🎯 **NEXT PRIORITY:**
**Step 5: Style Management System** - Implement style combinatorics generation, USD file creation with module references, and style validation.

### 📊 **Progress Summary:**
- **4 systems fully completed** (Foundation, USD Utils, Group Management, Module Management)
- **3 systems partially completed** (UI Framework, Maya Integration, File Management) 
- **6 systems pending** (Style, Blendshape, Rules, Validation, Timeline, Testing)
- **Overall Progress: ~45% complete**