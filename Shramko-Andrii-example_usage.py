#!/usr/bin/env python3
"""
Example usage of PLY to COLMAP converter
Shows different ways to use the converter
"""

from Shramko_Andrii_ply_to_colmap_converter import convert_ply_to_colmap

def example_1_basic_usage():
    """Basic usage with default paths"""
    print("Example 1: Basic usage")
    print("-" * 30)
    
    # This will look for 6/sparse/0/points3D.ply and create 6/sparse/0/points3D.txt
    success = convert_ply_to_colmap("6/sparse/0/points3D.ply")
    
    if success:
        print("✅ Conversion successful!")
    else:
        print("❌ Conversion failed!")

def example_2_custom_paths():
    """Usage with custom input and output paths"""
    print("\nExample 2: Custom paths")
    print("-" * 30)
    
    # Custom input and output files
    input_file = "my_dense_cloud.ply"
    output_file = "my_colmap_points.txt"
    
    success = convert_ply_to_colmap(input_file, output_file)
    
    if success:
        print("✅ Conversion successful!")
    else:
        print("❌ Conversion failed!")

def example_3_batch_processing():
    """Process multiple PLY files"""
    print("\nExample 3: Batch processing")
    print("-" * 30)
    
    ply_files = [
        "scene1/sparse/0/points3D.ply",
        "scene2/sparse/0/points3D.ply", 
        "scene3/sparse/0/points3D.ply"
    ]
    
    for ply_file in ply_files:
        print(f"\nProcessing: {ply_file}")
        success = convert_ply_to_colmap(ply_file)
        
        if success:
            print(f"✅ {ply_file} converted successfully!")
        else:
            print(f"❌ {ply_file} conversion failed!")

if __name__ == "__main__":
    print("PLY to COLMAP Converter - Examples")
    print("=" * 50)
    
    # Run examples
    example_1_basic_usage()
    example_2_custom_paths()
    example_3_batch_processing()
    
    print("\n" + "=" * 50)
    print("Examples completed!")
