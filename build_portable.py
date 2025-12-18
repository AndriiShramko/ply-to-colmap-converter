#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Professional build script for portable PLY to COLMAP Converter
Creates standalone executable for Windows 10/11 without any dependencies
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")

def check_pyinstaller():
    """Check if PyInstaller is installed"""
    try:
        import PyInstaller
        version = PyInstaller.__version__
        print(f"✅ PyInstaller {version} is installed")
        return True
    except ImportError:
        print("❌ PyInstaller is not installed")
        response = input("Install PyInstaller? (y/n): ")
        if response.lower() == 'y':
            print("Installing PyInstaller...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print("✅ PyInstaller installed successfully")
                return True
            except subprocess.CalledProcessError:
                print("❌ Failed to install PyInstaller")
                return False
        else:
            print("❌ PyInstaller is required for building")
            return False

def check_required_files():
    """Check if all required files exist"""
    required_files = [
        'gui_converter.py',
        'Shramko_Andrii_ply_to_colmap_converter.py',
        'PLY_Converter.spec'
    ]
    
    missing = []
    for file in required_files:
        if not os.path.exists(file):
            missing.append(file)
    
    if missing:
        print(f"❌ Missing required files: {', '.join(missing)}")
        return False
    
    print("✅ All required files found")
    return True

def clean_build_dirs():
    """Clean previous build directories"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"🧹 Cleaned {dir_name}/")
            except Exception as e:
                print(f"⚠️  Could not clean {dir_name}/: {e}")

def build_executable():
    """Build the executable using PyInstaller"""
    print_header("Building Portable Executable")
    
    # Check if spec file exists
    if not os.path.exists('PLY_Converter.spec'):
        print("❌ PLY_Converter.spec file not found!")
        print("   Building with command line options instead...")
        
        cmd = [
            'pyinstaller',
            '--onefile',
            '--windowed',
            '--name', 'PLY_to_COLMAP_Converter',
            '--add-data', 'Shramko_Andrii_ply_to_colmap_converter.py;.',
            '--hidden-import', 'tkinter',
            '--hidden-import', 'tkinter.filedialog',
            '--hidden-import', 'tkinter.messagebox',
            '--hidden-import', 'tkinter.scrolledtext',
            '--hidden-import', 'tkinter.ttk',
            '--hidden-import', 'Shramko_Andrii_ply_to_colmap_converter',
            '--clean',
            'gui_converter.py'
        ]
    else:
        print("📋 Using PLY_Converter.spec file")
        cmd = [
            'pyinstaller',
            '--clean',
            'PLY_Converter.spec'
        ]
    
    print("🔨 Running PyInstaller...")
    print(f"   Command: {' '.join(cmd)}\n")
    
    try:
        # Run PyInstaller
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=False,
            text=True
        )
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed with error code {e.returncode}")
        return False
    except FileNotFoundError:
        print("\n❌ PyInstaller not found in PATH")
        print("   Make sure PyInstaller is installed and accessible")
        return False

def verify_build():
    """Verify that the executable was created"""
    exe_path = Path('dist') / 'PLY_to_COLMAP_Converter.exe'
    
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"✅ Executable created successfully!")
        print(f"   Location: {exe_path.absolute()}")
        print(f"   Size: {size_mb:.1f} MB")
        return True
    else:
        print(f"❌ Executable not found at {exe_path}")
        return False

def create_readme():
    """Create README for portable version"""
    readme_content = """PLY to COLMAP Converter - Portable Version
==========================================

This is a standalone portable application that requires NO installation.
Simply run PLY_to_COLMAP_Converter.exe on any Windows 10/11 computer.

SYSTEM REQUIREMENTS:
- Windows 10 or Windows 11
- No additional software required
- No Python installation needed
- No internet connection required

USAGE:
1. Double-click PLY_to_COLMAP_Converter.exe
2. Click "Select File..." to choose your PLY file
3. Click "Convert" to start conversion
4. Wait for completion - progress will be shown

FEATURES:
- Automatic backup of original files
- Real-time progress tracking
- Support for ASCII and Binary PLY files
- All-in-one portable executable

For more information, visit:
https://github.com/AndriiShramko/ply-to-colmap-converter

Created by: Andrii Shramko
License: MIT - Free for community use
"""
    
    readme_path = Path('dist') / 'README.txt'
    try:
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print(f"📄 Created README.txt in dist/")
    except Exception as e:
        print(f"⚠️  Could not create README: {e}")

def main():
    """Main build function"""
    print_header("PLY to COLMAP Converter - Portable Build")
    
    print("This script will create a standalone portable executable")
    print("that works on Windows 10/11 without any dependencies.\n")
    
    # Step 1: Check PyInstaller
    if not check_pyinstaller():
        return False
    
    # Step 2: Check required files
    if not check_required_files():
        return False
    
    # Step 3: Clean previous builds
    print("\n🧹 Cleaning previous build directories...")
    clean_build_dirs()
    
    # Step 4: Build executable
    if not build_executable():
        return False
    
    # Step 5: Verify build
    print("\n🔍 Verifying build...")
    if not verify_build():
        return False
    
    # Step 6: Create README
    print("\n📝 Creating documentation...")
    create_readme()
    
    # Success message
    print_header("Build Completed Successfully!")
    
    exe_path = Path('dist') / 'PLY_to_COLMAP_Converter.exe'
    print(f"✅ Portable executable created: {exe_path.absolute()}")
    print()
    print("📦 The executable is ready for distribution!")
    print("   You can copy it to any Windows 10/11 computer and run it directly.")
    print("   No installation or additional software required.")
    print()
    print("💡 Tips:")
    print("   - The executable is self-contained (all dependencies included)")
    print("   - It will create config.json in the same folder for settings")
    print("   - Backup files are created automatically during conversion")
    print()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Build cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

