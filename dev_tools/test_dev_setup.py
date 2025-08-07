#!/usr/bin/env python
"""
Test script to verify the development setup works correctly
This can be run both in VSCode (for type checking) and in Maya (for actual testing)
"""

def test_type_hints_and_imports():
    """Test that we can import Maya modules and get type hints"""
    print("=== Testing Development Setup ===")
    
    try:
        # This should work with type hints in VSCode
        import maya.cmds as cmds
        print("✓ maya.cmds imported successfully")
        
        # Test some basic cmds functions (these will only work in Maya)
        try:
            # This will fail outside Maya but should show proper type hints in VSCode
            scene_name = cmds.file(query=True, sceneName=True)
            print(f"✓ Maya scene query successful: {scene_name}")
            
            # Test selection
            selection = cmds.ls(selection=True)
            print(f"✓ Selection query successful: {selection}")
            
            print("✓ Running in Maya environment - full functionality available")
            return True
            
        except RuntimeError as e:
            if "Maya command engine is not yet initialized" in str(e):
                print("ℹ  Running outside Maya - type hints available but commands disabled")
                print("ℹ  This is expected when running in VSCode")
                return True
            else:
                print(f"✗ Unexpected Maya error: {e}")
                return False
                
    except ImportError as e:
        print(f"✗ Failed to import Maya modules: {e}")
        print("ℹ  Install 'types-maya' for development type hints")
        return False


def test_project_imports():
    """Test that we can import our project modules"""
    print("\n=== Testing Project Imports ===")
    
    try:
        # Add the project to path if needed
        import sys
        from pathlib import Path
        
        project_root = Path(__file__).parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        
        # Test importing our modules
        from hair_qc_tool.config import config
        print("✓ hair_qc_tool.config imported successfully")
        
        from hair_qc_tool.managers import ModuleManager
        print("✓ hair_qc_tool.managers.ModuleManager imported successfully")
        
        from hair_qc_tool.utils import file_utils
        print("✓ hair_qc_tool.utils.file_utils imported successfully")
        
        print("✓ All project imports successful")
        return True
        
    except ImportError as e:
        print(f"✗ Failed to import project modules: {e}")
        return False


def test_development_workflow():
    """Test the complete development workflow"""
    print("\n=== Testing Development Workflow ===")
    
    # Test type hints availability
    try:
        import maya.cmds as cmds
        
        # In VSCode with types-maya, this should show proper autocompletion
        # Test some common functions to verify type hints
        functions_to_test = [
            'ls', 'select', 'file', 'getAttr', 'setAttr', 
            'polyCube', 'move', 'rotate', 'scale'
        ]
        
        for func_name in functions_to_test:
            if hasattr(cmds, func_name):
                func = getattr(cmds, func_name)
                print(f"✓ {func_name} available: {func}")
            else:
                print(f"✗ {func_name} not found")
        
        print("✓ Maya functions accessible for type checking")
        return True
        
    except Exception as e:
        print(f"✗ Development workflow test failed: {e}")
        return False


if __name__ == "__main__":
    print("Maya Hair QC Tool - Development Setup Test")
    print("=" * 50)
    
    # Run all tests
    results = []
    results.append(test_type_hints_and_imports())
    results.append(test_project_imports())
    results.append(test_development_workflow())
    
    # Summary
    print("\n" + "=" * 50)
    if all(results):
        print("✓ ALL TESTS PASSED - Development setup is working correctly!")
        print("\nNext steps:")
        print("1. Install dev dependencies: pip install -r dev_tools/requirements-dev.txt")
        print("2. Open project in VSCode for full type hint support")
        print("3. Run Maya tests from Maya's Script Editor")
        print("4. Use VSCode debugger to attach to Maya for debugging")
    else:
        print("✗ Some tests failed - check the output above")
        print("\nTroubleshooting:")
        print("1. Make sure you're in the correct directory")
        print("2. Install types-maya: pip install types-maya")
        print("3. Check that hair_qc_tool is in your Python path")
