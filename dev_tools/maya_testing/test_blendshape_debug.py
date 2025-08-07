#!/usr/bin/env python
"""
Debug script to test blendshape weight setting functionality

This script helps debug the TokenArray issue with blendshape weights.
"""

import sys
from pathlib import Path

# Add the hair_qc_tool to Python path for testing
sys.path.insert(0, str(Path(__file__).parent / "hair_qc_tool"))

try:
    from pxr import Usd, UsdSkel, UsdGeom
    USD_AVAILABLE = True
    print("[Debug] USD Python API is available")
except ImportError as e:
    USD_AVAILABLE = False
    print(f"[Debug] USD Python API not available: {e}")
    print("[Debug] This script requires USD Python API to run")
    sys.exit(1)

from hair_qc_tool.utils.usd_utils import USDModuleUtils


def test_tokenarray_conversion():
    """Test TokenArray to list conversion"""
    print("\n=== Testing TokenArray Conversion ===")
    
    # Create a test USD file
    test_file = Path("test_module_debug.usd")
    
    try:
        # Create a minimal module structure
        stage = Usd.Stage.CreateNew(str(test_file))
        
        # Create basic structure
        root_prim = stage.DefinePrim("/HairModule")
        anim_prim = UsdSkel.Animation.Define(stage, "/HairModule/Animation")
        
        # Create test blendshape names (this will be a TokenArray)
        test_names = ["smile", "frown", "blink"]
        test_weights = [0.0, 0.5, 1.0]
        
        # Set blendshape data
        blend_shapes_attr = anim_prim.CreateBlendShapesAttr()
        blend_weights_attr = anim_prim.CreateBlendShapeWeightsAttr()
        
        blend_shapes_attr.Set(test_names)
        blend_weights_attr.Set(test_weights)
        
        stage.Save()
        print(f"[Debug] Created test file: {test_file}")
        
        # Now test reading it back
        stage = Usd.Stage.Open(str(test_file))
        anim_prim = stage.GetPrimAtPath("/HairModule/Animation")
        skel_anim = UsdSkel.Animation(anim_prim)
        
        blend_shapes_attr = skel_anim.GetBlendShapesAttr()
        blend_weights_attr = skel_anim.GetBlendShapeWeightsAttr()
        
        if blend_shapes_attr and blend_weights_attr:
            blendshape_names = blend_shapes_attr.Get()
            blendshape_weights = blend_weights_attr.Get()
            
            print(f"[Debug] Raw blendshape_names type: {type(blendshape_names)}")
            print(f"[Debug] Raw blendshape_names: {blendshape_names}")
            print(f"[Debug] Raw blendshape_weights type: {type(blendshape_weights)}")
            print(f"[Debug] Raw blendshape_weights: {blendshape_weights}")
            
            # Test conversion to list
            try:
                names_list = list(blendshape_names)
                print(f"[Debug] Converted names to list: {names_list}")
                print(f"[Debug] List type: {type(names_list)}")
                
                # Test index() method
                try:
                    smile_index = names_list.index("smile")
                    print(f"[Debug] Found 'smile' at index: {smile_index}")
                except ValueError as e:
                    print(f"[Debug] ERROR: Could not find 'smile': {e}")
                
                # Test direct TokenArray index() method (this should fail)
                try:
                    direct_index = blendshape_names.index("smile")
                    print(f"[Debug] Direct TokenArray index worked: {direct_index}")
                except AttributeError as e:
                    print(f"[Debug] Expected error - TokenArray has no index method: {e}")
                
            except Exception as e:
                print(f"[Debug] ERROR converting to list: {e}")
        
        # Clean up
        test_file.unlink(missing_ok=True)
        print(f"[Debug] Cleaned up test file")
        
    except Exception as e:
        print(f"[Debug] ERROR in test: {e}")
        import traceback
        traceback.print_exc()
        # Clean up on error
        test_file.unlink(missing_ok=True)


def test_module_utils_blendshape_setting():
    """Test the actual module utils blendshape setting"""
    print("\n=== Testing Module Utils Blendshape Setting ===")
    
    test_file = Path("test_module_utils.usd")
    
    try:
        # Create a test module file
        utils = USDModuleUtils(test_file)
        success = utils.create_module_structure("test_module", "scalp")
        
        if not success:
            print("[Debug] ERROR: Could not create test module structure")
            return
        
        print("[Debug] Created test module structure")
        
        # Simulate adding a blendshape by creating the structure manually
        utils.open_stage()
        
        # Create a test blendshape
        from pxr import UsdSkel, Sdf
        blendshape_prim = UsdSkel.BlendShape.Define(utils.stage, "/HairModule/BlendShapes/test_smile")
        
        # Create weight attribute
        prim = blendshape_prim.GetPrim()
        weight_attr = prim.CreateAttribute("weight", Sdf.ValueTypeNames.Float)
        weight_attr.Set(0.0)
        
        # Update the SkelAnimation
        utils._update_skel_animation_blendshapes()
        utils.save_stage()
        
        print("[Debug] Created test blendshape")
        
        # Now test setting the weight
        print("[Debug] Testing weight setting...")
        success = utils.set_blendshape_weight_via_animation("test_smile", 0.75)
        
        if success:
            print("[Debug] SUCCESS: Weight setting worked!")
        else:
            print("[Debug] ERROR: Weight setting failed")
        
        # Clean up
        test_file.unlink(missing_ok=True)
        print("[Debug] Cleaned up test file")
        
    except Exception as e:
        print(f"[Debug] ERROR in module utils test: {e}")
        import traceback
        traceback.print_exc()
        # Clean up on error
        test_file.unlink(missing_ok=True)


if __name__ == "__main__":
    print("=== Blendshape Debug Script ===")
    print("Testing TokenArray conversion and blendshape weight setting...")
    
    test_tokenarray_conversion()
    test_module_utils_blendshape_setting()
    
    print("\n=== Debug Complete ===")


