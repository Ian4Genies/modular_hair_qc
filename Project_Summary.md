# Hair QC Tool - Project Summary

## Overview
The Hair QC Tool is a comprehensive Maya plugin for managing modular hair assets using USD-based data structures. It provides a streamlined workflow for creating, editing, and quality controlling hair modules with blendshape combinations and cross-module rules.

## Core Architecture

### Data Flow Architecture
```
USD Directory (File System)
    ↓
Config Manager (config.py)
    ↓
Data Manager (Coordinator)
    ↓
├── Group Manager ← → Group USD Files
├── Module Manager ← → Module USD Files  
└── Style Manager ← → Style USD Files
    ↓
Main Window UI (PySide2)
    ↓
Maya Scene Integration
```

### Primary Components

#### 1. Entry Point & Tool Management
- **`main.py`**: Tool lifecycle, Maya menu/shelf integration, launch logic
- **`config.py`**: USD directory management, user preferences, validation

#### 2. Data Management Layer (Managers)
- **`DataManager`**: Central coordinator that unifies access to all data types
- **`GroupManager`**: Handles Group USD files (alpha whitelists, cross-module rules)
- **`ModuleManager`**: Handles Module USD files (geometry, blendshapes, exclusions)

#### 3. User Interface
- **`main_window.py`**: Primary UI with tabbed interface
  - Group selection and alpha whitelist management
  - Module creation/editing with blendshape controls
  - Style generation and timeline management (planned)

#### 4. Utility Layer
- **`usd_utils.py`**: USD file operations, validation, creation
- **`maya_utils.py`**: Maya scene integration, geometry import/export
- **`file_utils.py`**: Directory management, file validation
- **`rules_utils.py`**: Blendshape rules and constraint management
- **`logging_utils.py`**: Session logging and debugging support
- **`reloader.py`**: Hot-reload for development

## Data Structure

### USD Directory Organization
```
<USD_DIRECTORY>/
├── Group/           # Group definitions with module collections
│   ├── short.usd    # Sample group file
│   └── long.usd     # Sample group file
├── module/          # Individual hair modules by type
│   ├── scalp/       # Scalp modules with alpha textures
│   │   ├── alpha/   # Alpha texture subdirectories
│   │   │   ├── fade/, hairline/, sideburn/
│   │   └── normal/  # Standard modules
│   ├── crown/       # Crown hair modules
│   ├── tail/        # Tail/ponytail modules
│   └── bang/        # Bang/fringe modules
├── style/           # Style combinations (future)
└── logs/            # Session logs for debugging
    └── hair_qc_tool/
```

### Module Types [[memory:4977069]]
- **Scalp**: Base hair with alpha texture support
- **Crown**: Crown area hair
- **Tail**: Ponytail/tail hair
- **Bang**: Fringe/bang hair

## Key Features

### 1. Module Management
- Create/edit hair modules with geometry and blendshapes
- Import geometry from Maya scene to USD
- Real-time blendshape weight preview in Maya viewport
- Internal exclusion rules between blendshapes
- Module type organization and validation

### 2. Group Management
- Group-level alpha texture whitelisting
- Module collections for different hair styles
- Cross-module rules and constraints
- Group validation and structure checking

### 3. Maya Integration
- USD proxy shape display for interactive editing
- Hot-reload development workflow
- Maya blendshape control mapping
- Geometry import/export pipeline

### 4. USD Data Management [[memory:4977078]]
- Simple USD containers without embedded logic
- System-level uniform rules implementation
- Separate .usd files for each module/style [[memory:4977072]]
- Path-based texture references

## Development Workflow

### 1. Hot-Reload Development
- Developer menu with code reload functionality
- Persistent logging to USD directory
- Module reloading without Maya restart
- Session-based log files with rotation

### 2. Maya Integration
- Menu installation in Maya main menu bar
- Shelf button support for quick access
- USD stage management and cleanup
- Cross-platform file browser integration

### 3. Data Validation
- USD file structure validation
- Module/group consistency checking
- Texture path validation
- Change tracking for unsaved modifications

## Current Status & Limitations

### Implemented Features
- ✅ Core module creation and editing
- ✅ Group management with alpha whitelists
- ✅ Maya geometry import/export
- ✅ Real-time blendshape preview
- ✅ Hot-reload development system
- ✅ USD directory initialization

### Planned Features
- 🔄 Style generation and combination system
- 🔄 Timeline export for animation testing
- 🔄 Cross-module constraint validation
- 🔄 Module renaming and type changing
- 🔄 Module deletion functionality

### Known Limitations
- Style management is placeholder (UI exists but not functional)
- Module renaming/deletion not implemented
- Limited cross-module rule enforcement
- No batch operations for multiple modules

## File Organization Philosophy

The project follows a clean separation of concerns:
- **Core Logic**: Managers handle data operations
- **UI Layer**: Main window coordinates user interactions
- **Utility Layer**: Reusable functions for USD/Maya operations
- **Development Tools**: Separate debugging and testing utilities

This architecture enables maintainable code with clear data flow from USD files through managers to the UI, with Maya integration handled transparently by the utility layer.
