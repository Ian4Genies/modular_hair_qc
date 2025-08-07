#!/usr/bin/env python
"""
Inspect USD proxy shape attributes to find blendshape controls

This script helps identify what attributes are available on Maya USD proxy shapes
for direct blendshape control, avoiding the need for USD stage updates.
"""

import maya.cmds as cmds


def inspect_proxy_shape_attributes():
    """Inspect all USD proxy shapes in the scene"""
    print("=== USD Proxy Shape Attribute Inspector ===")
    
    # Find all USD proxy shapes
    proxy_shapes = cmds.ls(type="mayaUsdProxyShape") or []
    
    if not proxy_shapes:
        print("No USD proxy shapes found in scene")
        return
    
    for proxy_shape in proxy_shapes:
        print(f"\n--- Proxy Shape: {proxy_shape} ---")
        
        # Get the transform parent
        transform = cmds.listRelatives(proxy_shape, parent=True)
        if transform:
            print(f"Transform: {transform[0]}")
        
        # Get the USD file path
        try:
            file_path = cmds.getAttr(f"{proxy_shape}.filePath")
            print(f"USD File: {file_path}")
        except:
            print("USD File: <not set>")
        
        # Get all attributes
        all_attrs = cmds.listAttr(proxy_shape) or []
        print(f"Total attributes: {len(all_attrs)}")
        
        # Look for blendshape-related attributes
        blendshape_attrs = []
        weight_attrs = []
        animation_attrs = []
        
        for attr in all_attrs:
            attr_lower = attr.lower()
            if any(keyword in attr_lower for keyword in ['blend', 'shape']):
                blendshape_attrs.append(attr)
            elif 'weight' in attr_lower:
                weight_attrs.append(attr)
            elif any(keyword in attr_lower for keyword in ['anim', 'time', 'frame']):
                animation_attrs.append(attr)
        
        if blendshape_attrs:
            print(f"Blendshape-related attributes: {blendshape_attrs}")
        else:
            print("No blendshape-related attributes found")
        
        if weight_attrs:
            print(f"Weight-related attributes: {weight_attrs}")
        
        if animation_attrs:
            print(f"Animation-related attributes: {animation_attrs}")
        
        # Check for dynamic attributes (user-added)
        try:
            user_attrs = cmds.listAttr(proxy_shape, userDefined=True) or []
            if user_attrs:
                print(f"User-defined attributes: {user_attrs}")
        except:
            pass
        
        # Check for keyable attributes
        try:
            keyable_attrs = cmds.listAttr(proxy_shape, keyable=True) or []
            keyable_relevant = [attr for attr in keyable_attrs if any(keyword in attr.lower() for keyword in ['blend', 'shape', 'weight'])]
            if keyable_relevant:
                print(f"Keyable blendshape/weight attributes: {keyable_relevant}")
        except:
            pass


def inspect_usd_stage_info():
    """Try to get USD stage information from proxy shapes"""
    print("\n=== USD Stage Information ===")
    
    proxy_shapes = cmds.ls(type="mayaUsdProxyShape") or []
    
    for proxy_shape in proxy_shapes:
        print(f"\n--- Stage Info for {proxy_shape} ---")
        
        try:
            # Try to get stage information via mayaUsd
            import mayaUsd.lib as mayaUsdLib
            
            # Get the stage
            proxy_path = f"|{cmds.listRelatives(proxy_shape, parent=True)[0]}|{proxy_shape}"
            stage = mayaUsdLib.GetPrim(proxy_path).GetStage()
            
            if stage:
                print("USD Stage found")
                
                # Look for blendshape-related prims
                for prim in stage.Traverse():
                    prim_name = prim.GetName()
                    prim_type = prim.GetTypeName()
                    
                    if any(keyword in prim_name.lower() for keyword in ['blend', 'shape', 'anim']):
                        print(f"  Relevant prim: {prim.GetPath()} (type: {prim_type})")
                        
                        # List attributes
                        attrs = prim.GetAttributes()
                        for attr in attrs:
                            attr_name = attr.GetName()
                            if any(keyword in attr_name.lower() for keyword in ['weight', 'blend']):
                                try:
                                    value = attr.Get()
                                    print(f"    Attribute: {attr_name} = {value}")
                                except:
                                    print(f"    Attribute: {attr_name} = <could not read>")
            
        except ImportError:
            print("mayaUsd.lib not available")
        except Exception as e:
            print(f"Error getting stage info: {e}")


def test_direct_attribute_control():
    """Test if we can directly control blendshape weights via proxy attributes"""
    print("\n=== Testing Direct Attribute Control ===")
    
    proxy_shapes = cmds.ls(type="mayaUsdProxyShape") or []
    
    for proxy_shape in proxy_shapes:
        print(f"\n--- Testing {proxy_shape} ---")
        
        # Try to add a custom attribute for blendshape control
        test_attr_name = f"{proxy_shape}.test_blendshape_weight"
        
        try:
            if not cmds.objExists(test_attr_name):
                cmds.addAttr(proxy_shape, longName="test_blendshape_weight", 
                           attributeType="double", min=0, max=1, defaultValue=0, keyable=True)
                print("Added test blendshape weight attribute")
            
            # Try to set it
            cmds.setAttr(test_attr_name, 0.5)
            value = cmds.getAttr(test_attr_name)
            print(f"Test attribute value: {value}")
            
            # Clean up
            cmds.deleteAttr(test_attr_name)
            print("Cleaned up test attribute")
            
        except Exception as e:
            print(f"Test attribute control failed: {e}")


if __name__ == "__main__":
    print("=== Maya USD Proxy Shape Inspector ===")
    print("This script inspects USD proxy shapes to find blendshape control options")
    
    try:
        inspect_proxy_shape_attributes()
        inspect_usd_stage_info()
        test_direct_attribute_control()
        
        print("\n=== Inspection Complete ===")
        print("Use this information to determine the best approach for blendshape control")
        
    except Exception as e:
        print(f"Error during inspection: {e}")
        import traceback
        traceback.print_exc()
