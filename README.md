# PLY to COLMAP Converter

Convert PLY dense point clouds from CloudCompare to COLMAP format for Postshot 3D Gaussian Splatting.

A community contribution to advance 3D/4D Gaussian Splatting technology. Developed through extensive research when no existing solutions were found.

## 🚀 Features

- ✅ **GUI Application** - User-friendly graphical interface
- ✅ **Portable Executable** - Standalone Windows 10/11 executable (no installation required)
- ✅ **Binary PLY Support** - Handles both ASCII and Binary PLY formats from CloudCompare
- ✅ **Automatic Backup** - Creates timestamped backups before conversion
- ✅ **Real-time Progress** - Shows conversion progress with ETA (estimated time remaining)
- ✅ **Duplicate Removal** - Automatically removes duplicate points
- ✅ **Settings Persistence** - Remembers last selected file path

## 📦 Portable Version

**Ready-to-use executable:** `dist/PLY_to_COLMAP_Converter.exe`

- **Size:** ~10 MB
- **Requirements:** Windows 10 or Windows 11 only
- **No installation needed** - Just run the exe file
- **No Python required** - All dependencies included
- **Fully self-contained** - Works on any Windows 10/11 computer

Simply download `PLY_to_COLMAP_Converter.exe` and run it. No additional software needed!

## 🖥️ GUI Application

Run the GUI version:
```bash
python gui_converter.py
```

### GUI Features:
- File selection dialog
- Real-time conversion progress with progress bar
- ETA (Estimated Time to Arrival) display
- Detailed conversion log
- Help section with CloudCompare instructions
- About section with GitHub link

## 📋 Command Line Usage

### Simple conversion:
```bash
python convert.py "path/to/your/file.ply"
```

### With custom output name:
```bash
python convert_ply_with_backup.py "input.ply" "output.txt"
```

## 🔧 Building Portable Version

To build your own portable executable:

### Windows (Recommended):
```bash
build_portable.bat
```

### Or using Python:
```bash
python build_portable.py
```

This will create `dist/PLY_to_COLMAP_Converter.exe` - a fully portable executable.

## 📖 Preparing PLY File in CloudCompare

1. Open CloudCompare
2. Load your dense point cloud
3. **File → Save As → PLY**
4. Configure export settings:
   - ✅ **Binary encoding:** Yes (enabled)
   - ✅ **Include colors:** Yes (enabled)
   - ❌ **Include normals:** No (not needed for COLMAP)
   - ❌ **Include scalar fields:** No (not needed)

## 🔄 What Changed in Latest Version

### Version 2.0 - Major Updates

#### ✨ New Features:
1. **Professional GUI Application**
   - Modern graphical interface built with tkinter
   - Real-time progress tracking with progress bar
   - ETA (Estimated Time to Arrival) calculation
   - Detailed conversion log window
   - Help section with CloudCompare instructions
   - About section with creator information and GitHub link

2. **Binary PLY Format Support**
   - Full support for binary little-endian PLY files
   - Full support for binary big-endian PLY files
   - Automatic format detection (ASCII/Binary)
   - Proper parsing of vertex properties (x, y, z, colors)
   - Handles various data types (float, double, uchar, int, etc.)

3. **Portable Executable**
   - Standalone Windows executable (no Python needed)
   - All dependencies included (~10 MB)
   - Works on Windows 10/11 without installation
   - Self-contained - copy and run anywhere

4. **Enhanced Progress Tracking**
   - Visual progress bar
   - Percentage display
   - ETA calculation based on processing speed
   - Progress updates every 500,000 vertices

5. **Settings Persistence**
   - Remembers last selected file path
   - Saves configuration in `config.json`
   - Automatic restoration on next launch

#### 🐛 Bug Fixes:
- Fixed binary PLY file reading (was causing UTF-8 decode errors)
- Fixed progress writer stream handling
- Improved error handling and reporting
- Better handling of files without color information

#### 🔧 Technical Improvements:
- Refactored code for better maintainability
- Added comprehensive error handling
- Improved memory efficiency for large files
- Better duplicate detection algorithm
- Optimized binary data parsing

### How It Works:

1. **File Format Detection:**
   - Reads PLY header to determine format (ASCII/Binary)
   - Parses vertex properties and counts
   - Detects color information (red/green/blue or r/g/b)

2. **Processing:**
   - For ASCII: Reads line by line, extracts coordinates and colors
   - For Binary: Parses binary data using struct module with proper byte order
   - Removes duplicates by creating unique keys from coordinates + colors
   - Shows progress every 500,000 vertices

3. **Output:**
   - Creates COLMAP points3D.txt format
   - Assigns unique IDs to each point
   - Sets ERROR = 0 for dense clouds
   - Saves in same directory as input file

4. **Backup:**
   - Automatically creates timestamped backup before conversion
   - Format: `[filename]_backup_[YYYYMMDD_HHMMSS].ply`
   - Original file is never modified

## 📊 Performance

- Handles files **2+ GB** in size
- Processes **millions of points** efficiently
- Shows progress every **500,000 vertices**
- Removes duplicates in memory
- Typical conversion time: **2-5 minutes** for large files

## 💡 Usage Example

```
Input: dense_point_cloud.ply (2.1 GB, 28.5M points)
Output: points3D.txt (947 MB, 18.5M unique points)
Processing time: ~3 minutes
Duplicates removed: ~35%
```

## 🛠️ Requirements

### For running Python version:
- Python 3.6+
- tkinter (included with Python)
- No external dependencies (uses only standard library)

### For portable executable:
- Windows 10 or Windows 11
- Nothing else needed!

## 📝 Files Structure

```
├── gui_converter.py                          # Main GUI application
├── Shramko_Andrii_ply_to_colmap_converter.py # Core conversion engine
├── convert.py                                # Simple CLI wrapper
├── convert_ply_with_backup.py               # CLI with backup
├── build_portable.py                        # Build script for exe
├── build_portable.bat                       # Windows build script
├── PLY_Converter.spec                       # PyInstaller spec file
├── dist/
│   └── PLY_to_COLMAP_Converter.exe         # Portable executable
└── README.md                                # This file
```

## 🐛 Troubleshooting

### "File not found" error
- Check that the PLY file path is correct
- Ensure file has `.ply` extension

### "No color information" warning
- File will be converted with default gray colors (128, 128, 128)
- To get colors, export PLY from CloudCompare with "Include colors: Yes"

### Binary file errors
- Ensure file was exported with "Binary encoding: Yes" from CloudCompare
- File should contain vertex positions (x, y, z) and colors (r, g, b)

### Exe file won't run
- Ensure Windows 10 or 11
- Check antivirus isn't blocking it
- Try running as administrator

## 📚 Based On

Solution from Agisoft Forum:
https://www.agisoft.com/forum/index.php?topic=16518.15

> "This altered Colmap points3D.txt file (without projections data) imports into Jawset Postshot for Gaussian Splatting processing with no issue and produces far greater accuracy than using just the tie points alone."

## 👨‍💻 Author

**Andrii Shramko**

GitHub: https://github.com/AndriiShramko/ply-to-colmap-converter

## 📄 License

**MIT License** - Free for community use

This tool is shared freely to advance 3D/4D Gaussian Splatting research and development. Use for personal and commercial projects without restrictions.

## 🙏 Community Support

**Need help?** Consult AI assistants (ChatGPT, Claude, etc.) - they can help troubleshoot and configure everything properly. The tool works perfectly on my system, and AI can guide you through any setup challenges.

---

**A community contribution to advance 3D/4D Gaussian Splatting technology**

