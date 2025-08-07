#!/usr/bin/env python3
"""
Cleanup script to remove leftover temp USD files
"""

def cleanup_temp_files():
    """Remove any leftover temp_*.usd files"""
    
    try:
        from pathlib import Path
        from hair_qc_tool.config import get_config
        
        config = get_config()
        usd_dir = Path(config.get('usd_directory', ''))
        
        if not usd_dir.exists():
            print("USD directory not found")
            return
        
        # Find all temp files
        temp_files = list(usd_dir.rglob('temp_*.usd'))
        
        print(f"Found {len(temp_files)} temp files to clean up")
        
        for temp_file in temp_files:
            try:
                temp_file.unlink()
                print(f"Deleted: {temp_file}")
            except Exception as e:
                print(f"Could not delete {temp_file}: {e}")
        
        print("Cleanup complete")
        
    except Exception as e:
        print(f"Error during cleanup: {e}")

if __name__ == "__main__":
    cleanup_temp_files()