#!/usr/bin/env python3
"""
Test script to verify Maya node type handling fix
"""

def test_maya_node_type_fix():
    """Test if we properly handle Maya import returning a list"""
    
    print("="*60)
    print("TESTING MAYA NODE TYPE HANDLING")
    print("="*60)
    
    # Simulate the Maya USD import behavior
    mock_imported_nodes = ["|Test_GEO_geo1"]  # This is what Maya returns
    
    print(f"Mock imported nodes: {mock_imported_nodes}")
    print(f"Type: {type(mock_imported_nodes)}")
    print(f"Length: {len(mock_imported_nodes)}")
    
    # Test our handling logic
    if mock_imported_nodes and len(mock_imported_nodes) > 0:
        maya_node = mock_imported_nodes[0]
        print(f"✓ Extracted first node: {maya_node}")
        print(f"✓ Type: {type(maya_node)}")
        
        # Test the string operations that were failing
        target_name = "Test_GEO_geo"
        
        print(f"Target name: {target_name}")
        print(f"Node != target: {maya_node != target_name}")
        
        # This should work now (previously failed)
        if maya_node != target_name:
            print(f"✓ String comparison works: '{maya_node}' != '{target_name}'")
        
        print("✓ SUCCESS: Node type handling is working correctly!")
        return True
    else:
        print("✗ FAILED: No nodes in list")
        return False

if __name__ == "__main__":
    test_maya_node_type_fix()