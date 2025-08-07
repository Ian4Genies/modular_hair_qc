#!/usr/bin/env python3
"""
Script to inspect the Test_GEO.usd file and check for geometry data
"""

def inspect_test_geo():
    """Inspect the Test_GEO.usd file"""
    
    try:
        from pathlib import Path
        from pxr import Usd, UsdGeom
        
        # Path to the test file
        test_file = Path("docs/TestDirectory/module/crown/Test_GEO.usd")
        
        if not test_file.exists():
            print(f"File not found: {test_file}")
            return False
        
        print(f"Inspecting: {test_file}")
        print("="*50)
        
        # Open the USD stage
        stage = Usd.Stage.Open(str(test_file))
        if not stage:
            print("Failed to open USD stage")
            return False
        
        print("✓ USD stage opened successfully")
        
        # Check the root structure
        print("\nStage structure:")
        for prim in stage.Traverse():
            print(f"  {prim.GetPath()} [{prim.GetTypeName()}]")
            
            # If it's a mesh, check for geometry data
            if prim.IsA(UsdGeom.Mesh):
                mesh = UsdGeom.Mesh(prim)
                
                print(f"    Mesh details:")
                
                # Check points
                points_attr = mesh.GetPointsAttr()
                if points_attr.HasValue():
                    points = points_attr.Get()
                    print(f"    - Points: {len(points)} vertices")
                else:
                    print(f"    - Points: NO DATA")
                
                # Check face vertex indices
                indices_attr = mesh.GetFaceVertexIndicesAttr()
                if indices_attr.HasValue():
                    indices = indices_attr.Get()
                    print(f"    - Face Vertex Indices: {len(indices)} indices")
                else:
                    print(f"    - Face Vertex Indices: NO DATA")
                
                # Check face vertex counts
                counts_attr = mesh.GetFaceVertexCountsAttr()
                if counts_attr.HasValue():
                    counts = counts_attr.Get()
                    print(f"    - Face Vertex Counts: {len(counts)} faces")
                else:
                    print(f"    - Face Vertex Counts: NO DATA")
        
        # Now test our has_geometry_data function
        print("\n" + "="*50)
        print("Testing has_geometry_data function:")
        
        from hair_qc_tool.utils.usd_utils import USDModuleUtils
        
        module_utils = USDModuleUtils(test_file)
        has_geometry = module_utils.has_geometry_data()
        
        print(f"has_geometry_data() result: {has_geometry}")
        
        # Get module info
        module_info = module_utils.get_module_info()
        print(f"Module info: {module_info}")
        
        return True
        
    except Exception as e:
        print(f"Error inspecting USD file: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    inspect_test_geo()