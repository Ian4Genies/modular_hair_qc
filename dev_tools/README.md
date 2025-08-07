# Development Tools

This folder contains development, testing, and debugging utilities for the Maya Hair QC Tool project.

## Folder Structure

### `maya_testing/`
Contains test scripts that require Maya environment to run:
- `test_*.py` - Various test scripts for different components
- Run these scripts from within Maya's Script Editor or as Maya Python scripts

### `debugging/`
Contains debugging and inspection utilities:
- `inspect_*.py` - Scripts to inspect Maya/USD components
- `debug_*.py` - Debugging utilities for specific issues
- `verify_methods.py` - Method verification utilities
- `cleanup_temp_files.py` - Cleanup utilities
- `force_reload_modules.py` - Module reloading utilities
- `check_code_changes.py` - Code change verification

### `requirements-dev.txt`
Development dependencies for IDE support:
- `types-maya` - Type hints for Maya API (VSCode intellisense)
- `debugpy` - Remote debugging support

## Setup for Development

### 1. Install Development Dependencies
```bash
# Create a separate Python environment for development
python -m venv venv_dev
source venv_dev/bin/activate  # On Windows: venv_dev\Scripts\activate

# Install development dependencies
pip install -r dev_tools/requirements-dev.txt
```

### 2. VSCode Setup
- The `types-maya` package provides autocompletion for Maya commands
- This does NOT affect Maya runtime - it's purely for IDE support
- Your Maya tests will continue to work exactly as before

### 3. Running Tests
- **Maya Tests**: Run from Maya's Script Editor or as Maya Python scripts
- **Debugging Scripts**: Can be run from Maya or standalone depending on the script

## Important Notes

- **Maya Compatibility**: The `types-maya` package only provides type hints and doesn't affect Maya's actual behavior
- **Testing**: All existing Maya testing workflows remain unchanged
- **Organization**: This separation keeps development tools organized and separate from the main `hair_qc_tool` package

## Remote Debugging with Maya

To debug Maya scripts from VSCode:

1. In Maya's Script Editor:
```python
import debugpy
debugpy.listen(("localhost", 5678))
debugpy.wait_for_client()
debugpy.breakpoint()
```

2. In VSCode, attach to the debugger (port 5678)
