#!/usr/bin/env python3
"""
PLY Dense Point Cloud to COLMAP Converter for Postshot
Converts PLY files from CloudCompare to proper COLMAP points3D.txt format

A community contribution to advance 3D/4D Gaussian Splatting technology.
Developed through extensive research when no existing solutions were found.

Based on solution from Agisoft Forum:
https://www.agisoft.com/forum/index.php?topic=16518.15

Author: Community Developer
Date: 2025-01-06
License: MIT - Free for community use
"""

import os
import sys
import argparse
from pathlib import Path

def convert_ply_to_colmap(ply_file, output_file=None):
    """
    Convert PLY file to COLMAP points3D.txt format
    
    Args:
        ply_file (str): Path to input PLY file
        output_file (str): Path to output COLMAP file (optional)
    """
    
    # Set default output file if not provided
    if output_file is None:
        ply_path = Path(ply_file)
        output_file = ply_path.parent / "points3D.txt"
    
    print("=" * 60)
    print("PLY to COLMAP Converter for Postshot")
    print("Community contribution to 3D/4D Gaussian Splatting")
    print("=" * 60)
    print(f"Input file: {ply_file}")
    print(f"Output file: {output_file}")
    print()
    
    # Check if input file exists
    if not os.path.exists(ply_file):
        print(f"ERROR: Input file '{ply_file}' not found!")
        return False
    
    try:
        # First, count total lines for progress tracking
        print("Counting lines in PLY file...")
        with open(ply_file, 'r', encoding='utf-8') as f:
            total_lines = sum(1 for _ in f)
        
        print(f"Total lines in PLY file: {total_lines:,}")
        
        # Process file and remove duplicates
        unique_points = {}
        processed = 0
        
        print("\nProcessing file and removing duplicates...")
        print("Progress will be shown every 500,000 lines")
        print("-" * 40)
        
        with open(ply_file, 'r', encoding='utf-8') as f:
            # Skip PLY header (first 16 lines)
            for i in range(16):
                next(f)
                processed += 1
            
            # Process data lines
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split()
                    if len(parts) >= 6:
                        # Create unique key from coordinates and colors
                        # Format: X Y Z R G B (normal values are ignored)
                        key = f"{parts[0]}_{parts[1]}_{parts[2]}_{parts[3]}_{parts[4]}_{parts[5]}"
                        if key not in unique_points:
                            unique_points[key] = line
                
                processed += 1
                if processed % 500000 == 0:
                    progress = (processed / total_lines) * 100
                    print(f"Progress: {progress:.1f}% - Processed: {processed:,}, Unique: {len(unique_points):,}")
        
        print("-" * 40)
        print(f"Processing completed!")
        print(f"Total unique points found: {len(unique_points):,}")
        
        # Calculate compression ratio
        original_points = total_lines - 16  # Subtract header lines
        compression_ratio = (original_points - len(unique_points)) / original_points * 100
        print(f"Duplicates removed: {compression_ratio:.1f}%")
        
        # Write COLMAP format
        print(f"\nWriting COLMAP format to: {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            # Write COLMAP header
            f.write("# 3D point list with one line of data per point:\n")
            f.write("#   POINT3D_ID, X, Y, Z, R, G, B, ERROR, TRACK[] as (IMAGE_ID, POINT2D_IDX)\n")
            f.write(f"# Number of points: {len(unique_points)}, mean track length: 0.0\n")
            
            # Write points in COLMAP format
            point_id = 1
            for line in unique_points.values():
                parts = line.split()
                if len(parts) >= 6:
                    x, y, z, r, g, b = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5]
                    # COLMAP format: POINT3D_ID X Y Z R G B ERROR TRACK[]
                    # For dense cloud: ERROR = 0, TRACK[] is empty
                    f.write(f"{point_id} {x} {y} {z} {r} {g} {b} 0\n")
                    point_id += 1
        
        # Get file sizes
        input_size = os.path.getsize(ply_file) / (1024 * 1024)  # MB
        output_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
        
        print("=" * 60)
        print("CONVERSION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"Input file size:  {input_size:.1f} MB")
        print(f"Output file size: {output_size:.1f} MB")
        print(f"Points created:   {point_id-1:,}")
        print(f"Output file:      {output_file}")
        print()
        print("The file is now ready for use in Postshot!")
        print("Place it in your COLMAP sparse/0/ folder and import in Postshot.")
        print()
        print("💡 Need help? Consult AI assistants (ChatGPT, Claude, etc.)")
        print("   They can help troubleshoot any setup issues!")
        print("   This tool works perfectly on my system.")
        
        return True
        
    except Exception as e:
        print(f"ERROR during conversion: {str(e)}")
        return False

def main():
    """Main function with command line interface"""
    
    parser = argparse.ArgumentParser(
        description="Convert PLY dense point cloud to COLMAP format for Postshot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ply_to_colmap_converter.py
  python ply_to_colmap_converter.py input.ply
  python ply_to_colmap_converter.py input.ply output.txt
        """
    )
    
    parser.add_argument(
        'input_file', 
        nargs='?', 
        default='6/sparse/0/points3D.ply',
        help='Input PLY file path (default: 6/sparse/0/points3D.ply)'
    )
    
    parser.add_argument(
        'output_file', 
        nargs='?', 
        default=None,
        help='Output COLMAP file path (default: same directory as input)'
    )
    
    args = parser.parse_args()
    
    # Convert file
    success = convert_ply_to_colmap(args.input_file, args.output_file)
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()