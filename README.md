# Hair QC Tool

A comprehensive Maya tool for managing modular hair assets using USD-based data structures. Supports group-based organization, cross-module blendshape rules, and automated QC workflows.

## Features

- **USD-Based Data Management**: Organized hierarchy of Groups, Styles, and Modules
- **Modular Hair System**: Support for scalp, crown, tail, and bang module types
- **Blendshape QC**: Automated combination generation and rule-based validation
- **Cross-Module Rules**: Weight constraints and exclusions between different modules
- **Maya Integration**: Native timeline, blendshape controls, and geometry import
- **Group-Based Workflow**: Organize modules by delivery buckets for efficient QC

## Installation

### Option 1: Direct Installation (Recommended)
1. Copy the entire project folder to your desired location
2. In Maya's Script Editor (Python tab), run:
   ```python
   exec(open(r'C:\path\to\your\project\install_direct.py').read())
   ```
3. The script will automatically detect the project location and install the tool
4. Choose "Launch Tool" to start using it immediately

### Option 2: Manual Installation
```python
import sys
sys.path.insert(0, r'C:\path\to\your\project')
from hair_qc_tool.main import install_maya_menu, create_shelf_button
from hair_qc_tool import launch_hair_qc_tool

install_maya_menu()
create_shelf_button()
launch_hair_qc_tool()
```

### Installation Features
- **Automatic Path Detection**: No need to edit installation scripts
- **USD Directory Initialization**: Automatically creates proper directory structure
- **Maya Integration**: Menu bar and shelf button installation
- **Error Handling**: Clear feedback and troubleshooting

## Quick Start

1. **Set USD Directory**: First launch will prompt you to select your USD directory
2. **Select Group**: Choose a group from the list to work with its modules and styles
3. **Create/Edit Modules**: Use the Module tab to manage individual hair modules
4. **Generate Styles**: Use the Style tab to create combinations and set up QC rules
5. **QC Timeline**: Review generated blendshape combinations in Maya's timeline

## Directory Structure

The tool expects a USD directory with the following structure:

```
usd_directory/
├── Group/
│   ├── short.usd
│   ├── long.usd
│   └── ...
├── module/
│   ├── scalp/
│   │   ├── scalp.usd
│   │   └── alpha/
│   │       ├── fade/
│   │       ├── hairline/
│   │       └── sideburn/
│   ├── crown/
│   │   ├── short_crown_smallAfro.usd
│   │   └── ...
│   ├── tail/
│   │   └── ...
│   └── bang/
│       └── ...
└── style/
    ├── short_medAfro.usd
    ├── long_braided_beaded_messy.usd
    └── ...
```

## Usage

### Module Management
- **Add Module**: Create new hair modules with geometry and blendshapes
- **Edit Blendshapes**: Add, remove, and configure blendshape targets
- **Set Exclusions**: Define which blendshapes cannot be used together

### Style Management
- **Generate Combinations**: Create all possible module combinations for a group
- **QC Rules**: Set weight constraints and exclusions between modules
- **Timeline Generation**: Create animation timeline with all blendshape combinations

### Keyboard Shortcuts
- **Tab**: Switch between Module/Style tabs
- **F5**: Refresh data from USD files
- **Ctrl+R**: Regenerate timeline
- **Ctrl+S**: Save current module or timeline

## Technical Details

- **USD Version**: Compatible with USD 20.11+
- **Maya Version**: 2022+
- **Python**: 3.7+
- **Dependencies**: PySide2, Maya USD plugin

## Configuration

Settings are stored in `~/.hair_qc_tool_config.json`:

```json
{
  "usd_directory": "/path/to/usd/directory",
  "max_timeline_frames": 6000,
  "frames_per_combination": 10,
  "auto_save_enabled": true,
  "lazy_loading_enabled": true
}
```

## Development Status

This is version 1.0 of the Hair QC Tool. Current implementation includes:

✅ **Completed**:
- Project structure and Maya integration
- Configuration system
- Main UI framework
- Basic USD utilities

🚧 **In Progress**:
- USD data management
- Blendshape combination system
- Rule validation system

📋 **Planned**:
- Advanced timeline visualization
- Performance optimizations
- Extended validation features

## Support

For issues, questions, or feature requests, please refer to the project documentation in the `docs/` folder or contact the development team.