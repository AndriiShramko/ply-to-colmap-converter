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
import struct
from pathlib import Path

def read_ply_header(file_handle):
    """Reads PLY file header and returns metadata"""
    format_type = None
    vertex_count = 0
    vertex_properties = []
    in_vertex_element = False
    data_start_pos = 0
    
    # Read header line by line
    for line in file_handle:
        line = line.decode('ascii', errors='ignore').strip()
        
        if line.startswith('format'):
            parts = line.split()
            if len(parts) >= 2:
                format_type = parts[1]  # 'ascii', 'binary_little_endian', 'binary_big_endian'
        
        elif line.startswith('element vertex'):
            parts = line.split()
            if len(parts) >= 3:
                vertex_count = int(parts[2])
                in_vertex_element = True
                vertex_properties = []  # Reset properties for new element
        
        elif line.startswith('element'):
            # We're in a different element, not vertex
            in_vertex_element = False
        
        elif line.startswith('property') and in_vertex_element:
            parts = line.split()
            if len(parts) >= 3:
                prop_type = parts[1]
                prop_name = parts[2]
                vertex_properties.append((prop_type, prop_name))
        
        elif line == 'end_header':
            data_start_pos = file_handle.tell()
            break
    
    return {
        'format': format_type,
        'vertex_count': vertex_count,
        'properties': vertex_properties,
        'data_start': data_start_pos
    }

def find_property_index(properties, name):
    """Finds index of property by name"""
    for i, (prop_type, prop_name) in enumerate(properties):
        if prop_name.lower() == name.lower():
            return i, prop_type
    return None, None

def parse_binary_vertex(data, properties, byte_order='<'):
    """Parses a single vertex from binary PLY data"""
    vertex_data = {}
    offset = 0
    
    for prop_type, prop_name in properties:
        if prop_type == 'float' or prop_type == 'float32':
            value = struct.unpack(f'{byte_order}f', data[offset:offset+4])[0]
            offset += 4
        elif prop_type == 'double' or prop_type == 'float64':
            value = struct.unpack(f'{byte_order}d', data[offset:offset+8])[0]
            offset += 8
        elif prop_type == 'uchar' or prop_type == 'uint8':
            value = struct.unpack('B', data[offset:offset+1])[0]
            offset += 1
        elif prop_type == 'ushort' or prop_type == 'uint16':
            value = struct.unpack(f'{byte_order}H', data[offset:offset+2])[0]
            offset += 2
        elif prop_type == 'uint' or prop_type == 'uint32':
            value = struct.unpack(f'{byte_order}I', data[offset:offset+4])[0]
            offset += 4
        elif prop_type == 'char' or prop_type == 'int8':
            value = struct.unpack('b', data[offset:offset+1])[0]
            offset += 1
        elif prop_type == 'short' or prop_type == 'int16':
            value = struct.unpack(f'{byte_order}h', data[offset:offset+2])[0]
            offset += 2
        elif prop_type == 'int' or prop_type == 'int32':
            value = struct.unpack(f'{byte_order}i', data[offset:offset+4])[0]
            offset += 4
        else:
            # Default to float32 if unknown
            value = struct.unpack(f'{byte_order}f', data[offset:offset+4])[0]
            offset += 4
        
        vertex_data[prop_name] = value
    
    return vertex_data, offset

def convert_ply_to_colmap(ply_file, output_file=None):
    """
    Convert PLY file to COLMAP points3D.txt format
    Supports both ASCII and binary PLY formats
    
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
        # Detect file format by reading header
        print("Reading PLY file header...")
        
        with open(ply_file, 'rb') as f:
            # Check if it's PLY file
            first_line = f.readline().decode('ascii', errors='ignore').strip()
            if first_line != 'ply':
                print(f"ERROR: Not a valid PLY file (should start with 'ply')")
                return False
            
            f.seek(0)  # Reset to beginning
            header_info = read_ply_header(f)
        
        format_type = header_info['format']
        vertex_count = header_info['vertex_count']
        properties = header_info['properties']
        data_start = header_info['data_start']
        
        print(f"PLY Format: {format_type}")
        print(f"Number of vertices: {vertex_count:,}")
        print(f"Properties: {', '.join([p[1] for p in properties])}")
        print()
        
        # Find required properties (for ASCII format - we use indices)
        x_idx, _ = find_property_index(properties, 'x')
        y_idx, _ = find_property_index(properties, 'y')
        z_idx, _ = find_property_index(properties, 'z')
        
        # Look for color properties (can be red/green/blue or r/g/b)
        r_idx, r_type = find_property_index(properties, 'red')
        if r_idx is None:
            r_idx, r_type = find_property_index(properties, 'r')
        g_idx, g_type = find_property_index(properties, 'green')
        if g_idx is None:
            g_idx, g_type = find_property_index(properties, 'g')
        b_idx, b_type = find_property_index(properties, 'blue')
        if b_idx is None:
            b_idx, b_type = find_property_index(properties, 'b')
        
        # Also store color property names for binary format
        r_name = None
        if r_idx is not None:
            r_name = properties[r_idx][1]
        g_name = None
        if g_idx is not None:
            g_name = properties[g_idx][1]
        b_name = None
        if b_idx is not None:
            b_name = properties[b_idx][1]
        
        if x_idx is None or y_idx is None or z_idx is None:
            print("ERROR: PLY file must contain x, y, z coordinates")
            return False
        
        has_colors = (r_idx is not None and g_idx is not None and b_idx is not None)
        if not has_colors:
            print("WARNING: PLY file does not contain color information (red/green/blue)")
            print("Points will be converted with default colors (128, 128, 128)")
        
        # Process vertices
        print("Processing vertices and removing duplicates...")
        print("Progress will be shown every 500,000 vertices")
        print("-" * 40)
        
        unique_points = {}
        processed = 0
        
        if format_type == 'ascii':
            # ASCII format processing
            with open(ply_file, 'r', encoding='utf-8') as f:
                # Skip header - read until end_header
                for line in f:
                    if line.strip() == 'end_header':
                        break
                
                # Now read vertex data
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    parts = line.split()
                    if len(parts) < max(x_idx, y_idx, z_idx) + 1:
                        continue
                    
                    try:
                        x, y, z = float(parts[x_idx]), float(parts[y_idx]), float(parts[z_idx])
                        
                        if r_idx is not None and g_idx is not None and b_idx is not None and len(parts) > max(r_idx, g_idx, b_idx):
                            r, g, b = int(float(parts[r_idx])), int(float(parts[g_idx])), int(float(parts[b_idx]))
                        else:
                            r, g, b = 128, 128, 128  # Default gray
                        
                        # Create unique key from coordinates and colors
                        key = f"{x:.6f}_{y:.6f}_{z:.6f}_{r}_{g}_{b}"
                        if key not in unique_points:
                            unique_points[key] = (x, y, z, r, g, b)
                    except (ValueError, IndexError) as e:
                        continue  # Skip invalid lines
                    
                    processed += 1
                    if processed % 500000 == 0:
                        progress = (processed / vertex_count) * 100 if vertex_count > 0 else 0
                        print(f"Progress: {progress:.1f}% - Processed: {processed:,}, Unique: {len(unique_points):,}")
        
        else:
            # Binary format processing
            byte_order = '<' if format_type == 'binary_little_endian' else '>'
            
            with open(ply_file, 'rb') as f:
                f.seek(data_start)  # Skip to data section
                
                # Calculate vertex size
                vertex_size = 0
                for prop_type, prop_name in properties:
                    if prop_type in ['float', 'float32', 'int', 'int32', 'uint', 'uint32']:
                        vertex_size += 4
                    elif prop_type in ['double', 'float64']:
                        vertex_size += 8
                    elif prop_type in ['uchar', 'uint8', 'char', 'int8']:
                        vertex_size += 1
                    elif prop_type in ['ushort', 'uint16', 'short', 'int16']:
                        vertex_size += 2
                    else:
                        vertex_size += 4  # Default to 4 bytes
                
                # Read vertices
                for i in range(vertex_count):
                    vertex_data = f.read(vertex_size)
                    if len(vertex_data) < vertex_size:
                        break
                    
                    parsed_data, _ = parse_binary_vertex(vertex_data, properties, byte_order)
                    
                    # Get coordinates
                    x = parsed_data.get('x', 0.0)
                    y = parsed_data.get('y', 0.0)
                    z = parsed_data.get('z', 0.0)
                    
                    # Get colors
                    if has_colors and r_name and g_name and b_name:
                        r = int(parsed_data.get(r_name, 128))
                        g = int(parsed_data.get(g_name, 128))
                        b = int(parsed_data.get(b_name, 128))
                    else:
                        # Try common color names
                        r = int(parsed_data.get('red', parsed_data.get('r', parsed_data.get('Red', parsed_data.get('R', 128)))))
                        g = int(parsed_data.get('green', parsed_data.get('g', parsed_data.get('Green', parsed_data.get('G', 128)))))
                        b = int(parsed_data.get('blue', parsed_data.get('b', parsed_data.get('Blue', parsed_data.get('B', 128)))))
                    
                    # Create unique key from coordinates and colors
                    key = f"{x:.6f}_{y:.6f}_{z:.6f}_{r}_{g}_{b}"
                    if key not in unique_points:
                        unique_points[key] = (x, y, z, r, g, b)
                    
                    processed += 1
                    if processed % 500000 == 0:
                        progress = (processed / vertex_count) * 100 if vertex_count > 0 else 0
                        print(f"Progress: {progress:.1f}% - Processed: {processed:,}, Unique: {len(unique_points):,}")
        
        print("-" * 40)
        print(f"Processing completed!")
        print(f"Total unique points found: {len(unique_points):,}")
        
        # Calculate compression ratio
        if vertex_count > 0:
            compression_ratio = ((vertex_count - len(unique_points)) / vertex_count) * 100
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
            for x, y, z, r, g, b in unique_points.values():
                # COLMAP format: POINT3D_ID X Y Z R G B ERROR TRACK[]
                # For dense cloud: ERROR = 0, TRACK[] is empty
                f.write(f"{point_id} {x:.6f} {y:.6f} {z:.6f} {r} {g} {b} 0\n")
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
        import traceback
        print(f"ERROR during conversion: {str(e)}")
        print("\nDetailed error:")
        traceback.print_exc()
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
