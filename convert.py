#!/usr/bin/env python3
"""
Простой скрипт для конвертации PLY в COLMAP
Просто передайте путь к файлу как аргумент
"""

from convert_ply_with_backup import convert_ply_file
import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python convert.py <путь_к_ply_файлу>")
        print()
        print("Пример:")
        print('  python convert.py "C:\\path\\to\\file.ply"')
        sys.exit(1)
    
    ply_file = sys.argv[1]
    success = convert_ply_file(ply_file)
    sys.exit(0 if success else 1)

