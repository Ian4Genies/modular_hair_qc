#!/usr/bin/env python3
"""
Test script to check geometry status detection
"""

def test_geometry_status():
    """Test if geometry status is correctly detected"""
    
    try:
        from hair_qc_tool.utils.usd_utils import USDModuleUtils
        from pathlib import Path
        
        # Test with a module that should not have geometry
        test_module_path = Path("C:/Users/woske/Documents/Genies/01_working/05_SyntheticData/03_Directory/01_ModularHair/module/scalp/test.usd")
        
        if test_module_path.exists():
            print(f"Testing geometry status for: {test_module_path}")
            
            module_utils = USDModuleUtils(test_module_path)
            has_geometry = module_utils.has_geometry_data()
            
            print(f"Has geometry data: {has_geometry}")
            
            # Get detailed info
            module_info = module_utils.get_module_info()
            print(f"Module info: {module_info}")
            
            return has_geometry
        else:
            print(f"Test module not found: {test_module_path}")
            return None
            
    except Exception as e:
        print(f"Error testing geometry status: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_geometry_status()