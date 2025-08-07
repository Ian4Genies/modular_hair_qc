#!/usr/bin/env python3
"""
Debug script to test geometry saving to USD
"""

def debug_geometry_save():
    """Debug why geometry isn't being saved to USD"""
    
    print("="*60)
    print("DEBUGGING GEOMETRY SAVE TO USD")
    print("="*60)
    
    try:
        import maya.cmds as cmds
        from hair_qc_tool.utils.usd_utils import USDModuleUtils
        from pathlib import Path
        
        # Check selection
        selected = cmds.ls(selection=True)
        if not selected:
            print("ERROR: Please select a mesh object first")
            return False
        
        mesh_name = selected[0]
        print(f"Testing with: {mesh_name}")
        
        # Test file path
        test_file = Path("docs/TestDirectory/module/crown/Test_GEO.usd")
        print(f"Target USD file: {test_file}")
        
        if not test_file.exists():
            print("ERROR: Test USD file doesn't exist")
            return False
        
        # Create module utils
        module_utils = USDModuleUtils(test_file)
        
        # Check initial state
        print("\n" + "-"*40)
        print("BEFORE IMPORT:")
        print("-"*40)
        
        has_geometry_before = module_utils.has_geometry_data()
        print(f"Has geometry before: {has_geometry_before}")
        
        # Try to import geometry
        print("\n" + "-"*40)
        print("IMPORTING GEOMETRY:")
        print("-"*40)
        
        success = module_utils.import_geometry_from_maya(mesh_name)
        print(f"Import result: {success}")
        
        if not success:
            print("ERROR: Import failed")
            return False
        
        # Check state immediately after import
        print("\n" + "-"*40)
        print("IMMEDIATELY AFTER IMPORT:")
        print("-"*40)
        
        has_geometry_after = module_utils.has_geometry_data()
        print(f"Has geometry after: {has_geometry_after}")
        
        # Force save and reload to test persistence
        print("\n" + "-"*40)
        print("TESTING PERSISTENCE:")
        print("-"*40)
        
        print("Saving stage...")
        save_success = module_utils.save_stage()
        print(f"Save result: {save_success}")
        
        # Create a new instance to test if data persists
        print("Creating new module utils instance...")
        module_utils2 = USDModuleUtils(test_file)
        
        has_geometry_reloaded = module_utils2.has_geometry_data()
        print(f"Has geometry after reload: {has_geometry_reloaded}")
        
        # Get detailed info
        module_info = module_utils2.get_module_info()
        print(f"Module info after reload: {module_info}")
        
        # Inspect the USD stage directly
        print("\n" + "-"*40)
        print("DIRECT USD INSPECTION:")
        print("-"*40)
        
        from pxr import Usd, UsdGeom
        
        stage = Usd.Stage.Open(str(test_file))
        if stage:
            base_mesh_prim = stage.GetPrimAtPath("/HairModule/BaseMesh")
            if base_mesh_prim and base_mesh_prim.IsA(UsdGeom.Mesh):
                mesh = UsdGeom.Mesh(base_mesh_prim)
                
                points_attr = mesh.GetPointsAttr()
                if points_attr.HasValue():
                    points = points_attr.Get()
                    print(f"✓ Points in USD: {len(points)}")
                else:
                    print("✗ No points in USD")
                
                indices_attr = mesh.GetFaceVertexIndicesAttr()
                if indices_attr.HasValue():
                    indices = indices_attr.Get()
                    print(f"✓ Indices in USD: {len(indices)}")
                else:
                    print("✗ No indices in USD")
                
                counts_attr = mesh.GetFaceVertexCountsAttr()
                if counts_attr.HasValue():
                    counts = counts_attr.Get()
                    print(f"✓ Face counts in USD: {len(counts)}")
                else:
                    print("✗ No face counts in USD")
            else:
                print("✗ BaseMesh prim not found or not a mesh")
        else:
            print("✗ Could not open USD stage")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_geometry_save()