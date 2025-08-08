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
**Status**: In Progress
- [x] Set up Python package structure with utils folder
- [x] Create Maya shelf tool entry point
- [x] Set up USD Python API integration
- [x] Create base configuration system for USD directory paths
- [x] Set up logging and error handling framework

### 2. USD Utility System
**Status**: Pending  
- [ ] Create `USDGroupUtils` class for Group USD operations
- [ ] Create `USDModuleUtils` class for Module USD operations  
- [ ] Create `USDStyleUtils` class for Style USD operations
- [ ] Implement custom data serialization for BlendshapeRules
- [ ] Implement custom data serialization for CrossModuleExclusions
- [ ] Create USD stage management utilities

### 3. Group Management System
**Status**: Pending
- [ ] Implement group discovery and loading from USD directory
- [ ] Create group creation/deletion functionality
- [ ] Implement alpha texture whitelist management
- [ ] Create group-level rule storage and retrieval
- [ ] Implement module whitelist management per group

### 4. Module Management System  
**Status**: Pending
- [ ] Implement module USD file creation and loading
- [ ] Create geometry import from Maya scene to USD
- [ ] Implement blendshape import and management
- [ ] Create internal module exclusions system
- [ ] Implement alpha texture blacklist functionality
- [ ] Add module validation (geometry, blendshapes exist)

### 5. Style Management System
**Status**: Pending
- [ ] Implement style combinatorics generation from group modules
- [ ] Create style USD file creation with module references  
- [ ] Implement style validation (references exist, blendshapes exist)
- [ ] Create style loading and composition in Maya
- [ ] Implement cross-module rule inheritance from group level

### 6. Main UI Framework
**Status**: In Progress
- [x] Create main window with scrollable sections
- [ ] Implement group selection UI with alpha whitelist expansion
- [ ] Create module/style tab switching system
- [ ] Implement module selection and editing UI
- [ ] Create style selection and editing UI
- [ ] Add hotkey reference widget at top of tool

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
**Status**: Pending
- [ ] Create "Hair QC" menu in Maya's main menu bar
- [ ] Implement keyboard shortcuts (Tab, F5, Ctrl+R, etc.)
- [ ] Integrate with Maya's hotkey editor system
- [ ] Create shelf button for tool launch
- [ ] Implement Maya scene geometry loading for modules

### 11. Timeline Visualization
**Status**: Pending
- [ ] Implement timeline color-coding for invalid combinations (red)
- [ ] Create visual indicators for rule-affected regions
- [ ] Add timeline navigation and frame selection
- [ ] Implement blendshape weight slider integration
- [ ] Create timeline regeneration progress indicators

### 12. File Management & Utilities
**Status**: Pending
- [ ] Implement naming validation (no spaces, auto-convert to underscores)
- [ ] Create file path utilities for USD directory structure
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

## Current Status: Ready to Begin Implementation
All design questions resolved. Starting with project setup and foundation systems.