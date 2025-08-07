#!/usr/bin/env python3
"""
Test script to verify the List import fix without Maya dependencies
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Mock Maya modules for testing
class MockMayaCmds:
    """Mock maya.cmds for testing"""
    @staticmethod
    def ls(*args, **kwargs):
        return []
    
    @staticmethod
    def objExists(*args):
        return False
    
    @staticmethod
    def listHistory(*args, **kwargs):
        return []

class MockMayaOM:
    """Mock maya.api.OpenMaya for testing"""
    pass

# Create proper mock modules
maya_module = type('MockMaya', (), {})()
maya_module.cmds = MockMayaCmds
maya_api_module = type('MockMayaAPI', (), {})()
maya_api_module.OpenMaya = MockMayaOM

# Inject mocks into sys.modules
sys.modules['maya'] = maya_module
sys.modules['maya.cmds'] = MockMayaCmds
sys.modules['maya.api'] = maya_api_module
sys.modules['maya.api.OpenMaya'] = MockMayaOM

try:
    # Now try to import the fixed module
    from hair_qc_tool.utils.maya_utils import MayaUtils
    
    print("✅ SUCCESS: MayaUtils imported successfully!")
    print("✅ SUCCESS: List type hint issue resolved!")
    
    # Check if the import_usd_as_maya_geometry method exists and has proper type hints
    import inspect
    method = getattr(MayaUtils, 'import_usd_as_maya_geometry', None)
    if method:
        print("✅ SUCCESS: import_usd_as_maya_geometry method exists")
        
        # Check the method signature
        sig = inspect.signature(method)
        print(f"Method signature: {sig}")
        
        # Check return annotation
        return_annotation = sig.return_annotation
        print(f"Return type annotation: {return_annotation}")
        
        if str(return_annotation) == "<class 'typing.List[str]'>":
            print("✅ SUCCESS: Correct List[str] return type annotation")
        else:
            print(f"❌ WARNING: Return type annotation is {return_annotation}, expected List[str]")
    else:
        print("❌ ERROR: import_usd_as_maya_geometry method not found")
    
    # List available methods
    methods = [method for method in dir(MayaUtils) if not method.startswith('_')]
    print(f"Available methods ({len(methods)}): {methods}")
    
except ImportError as e:
    print(f"❌ ERROR: Import failed: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ ERROR: Unexpected error: {e}")
    import traceback
    traceback.print_exc()
