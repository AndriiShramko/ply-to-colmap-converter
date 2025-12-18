#!/usr/bin/env python3
"""
Обертка для конвертации PLY в COLMAP с автоматическим бэкапом
Конвертирует PLY файл в COLMAP формат с сохранением бэкапа исходного файла
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime
from Shramko_Andrii_ply_to_colmap_converter import convert_ply_to_colmap

def create_backup(file_path):
    """
    Создает бэкап файла с временной меткой
    
    Args:
        file_path (str): Путь к файлу для бэкапа
        
    Returns:
        str: Путь к бэкап файлу или None в случае ошибки
    """
    if not os.path.exists(file_path):
        print(f"⚠️  Файл {file_path} не существует, бэкап не требуется")
        return None
    
    file_path_obj = Path(file_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = file_path_obj.parent / f"{file_path_obj.stem}_backup_{timestamp}{file_path_obj.suffix}"
    
    try:
        shutil.copy2(file_path, backup_path)
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
        print(f"✅ Бэкап создан: {backup_path}")
        print(f"   Размер: {file_size:.1f} MB")
        return str(backup_path)
    except Exception as e:
        print(f"❌ Ошибка при создании бэкапа: {e}")
        return None

def convert_ply_file(ply_file_path, output_name="points3D.txt"):
    """
    Конвертирует PLY файл в COLMAP формат с бэкапом
    
    Args:
        ply_file_path (str): Путь к входному PLY файлу
        output_name (str): Имя выходного файла (по умолчанию points3D.txt)
    
    Returns:
        bool: True если конвертация успешна, False иначе
    """
    print("=" * 70)
    print("PLY to COLMAP Converter with Backup")
    print("=" * 70)
    print()
    
    # Проверка существования файла
    ply_path = Path(ply_file_path)
    if not ply_path.exists():
        print(f"❌ Ошибка: Файл '{ply_file_path}' не найден!")
        return False
    
    if not ply_path.suffix.lower() == '.ply':
        print(f"⚠️  Предупреждение: Файл не имеет расширения .ply")
    
    # Создание бэкапа
    print("📦 Создание бэкапа исходного файла...")
    backup_path = create_backup(ply_file_path)
    
    if backup_path is None and os.path.exists(ply_file_path):
        response = input("Бэкап не создан. Продолжить? (y/n): ")
        if response.lower() != 'y':
            print("❌ Операция отменена пользователем")
            return False
    
    print()
    
    # Определение пути выходного файла
    output_path = ply_path.parent / output_name
    
    # Конвертация
    print("🔄 Начало конвертации...")
    print()
    success = convert_ply_to_colmap(str(ply_path), str(output_path))
    
    if success:
        print()
        print("=" * 70)
        print("✅ КОНВЕРТАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
        print("=" * 70)
        if backup_path:
            print(f"📦 Бэкап исходного файла: {backup_path}")
        print(f"📄 Выходной файл: {output_path}")
        print()
        return True
    else:
        print()
        print("=" * 70)
        print("❌ ОШИБКА ПРИ КОНВЕРТАЦИИ")
        print("=" * 70)
        if backup_path:
            print(f"📦 Бэкап исходного файла сохранен: {backup_path}")
            print("💡 Вы можете восстановить исходный файл из бэкапа")
        print()
        return False

def main():
    """Главная функция с интерфейсом командной строки"""
    
    if len(sys.argv) < 2:
        print("Использование: python convert_ply_with_backup.py <путь_к_ply_файлу> [имя_выходного_файла]")
        print()
        print("Примеры:")
        print("  python convert_ply_with_backup.py input.ply")
        print("  python convert_ply_with_backup.py input.ply points3D.txt")
        print("  python convert_ply_with_backup.py C:\\path\\to\\file.ply")
        print()
        
        # Интерактивный режим
        ply_path = input("Введите путь к PLY файлу: ").strip().strip('"')
        if not ply_path:
            print("❌ Путь не указан")
            sys.exit(1)
        
        output_name = input("Имя выходного файла [points3D.txt]: ").strip()
        if not output_name:
            output_name = "points3D.txt"
    else:
        ply_path = sys.argv[1].strip().strip('"')
        output_name = sys.argv[2] if len(sys.argv) > 2 else "points3D.txt"
    
    success = convert_ply_file(ply_path, output_name)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

