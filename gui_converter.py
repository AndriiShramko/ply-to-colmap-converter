#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI application for converting PLY to COLMAP format
With automatic backup and result display
"""

import os
import sys
import json
import shutil
import threading
import io
import contextlib
import webbrowser
import time
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from pathlib import Path
from datetime import datetime
from Shramko_Andrii_ply_to_colmap_converter import convert_ply_to_colmap

# Configuration file name
CONFIG_FILE = "config.json"
GITHUB_URL = "https://github.com/AndriiShramko/ply-to-colmap-converter"

def load_config():
    """Loads configuration from file"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading configuration: {e}")
    return {"last_path": ""}

def save_config(config):
    """Saves configuration to file"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving configuration: {e}")

def create_backup(file_path):
    """Creates backup of file with timestamp"""
    if not os.path.exists(file_path):
        return None
    
    file_path_obj = Path(file_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = file_path_obj.parent / f"{file_path_obj.stem}_backup_{timestamp}{file_path_obj.suffix}"
    
    try:
        shutil.copy2(file_path, backup_path)
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
        return str(backup_path), file_size
    except Exception as e:
        raise Exception(f"Error creating backup: {e}")

def convert_ply_file_gui(ply_file_path, output_name="points3D.txt", log_callback=None, progress_callback=None):
    """
    Converts PLY file to COLMAP format with backup (GUI version)
    
    Args:
        ply_file_path (str): Path to input PLY file
        output_name (str): Output file name
        log_callback (callable): Function for logging (optional)
        progress_callback (callable): Function for progress updates (optional)
    
    Returns:
        dict: Conversion result with success/error information
    """
    result = {
        "success": False,
        "backup_path": None,
        "output_path": None,
        "error": None,
        "file_size_input": 0,
        "file_size_output": 0,
        "points_count": 0
    }
    
    try:
        if log_callback:
            log_callback("=" * 70 + "\n")
            log_callback("PLY to COLMAP Converter with Backup\n")
            log_callback("=" * 70 + "\n\n")
        
        # Check if file exists
        ply_path = Path(ply_file_path)
        if not ply_path.exists():
            error_msg = f"❌ Error: File '{ply_file_path}' not found!"
            result["error"] = error_msg
            if log_callback:
                log_callback(error_msg + "\n")
            return result
        
        if not ply_path.suffix.lower() == '.ply':
            if log_callback:
                log_callback(f"⚠️  Warning: File does not have .ply extension\n")
        
        result["file_size_input"] = os.path.getsize(ply_file_path) / (1024 * 1024)  # MB
        
        # Create backup
        if log_callback:
            log_callback("📦 Creating backup of source file...\n")
        
        try:
            backup_path, backup_size = create_backup(ply_file_path)
            result["backup_path"] = backup_path
            if log_callback:
                log_callback(f"✅ Backup created: {backup_path}\n")
                log_callback(f"   Size: {backup_size:.1f} MB\n\n")
        except Exception as e:
            error_msg = f"❌ Error creating backup: {e}\n"
            result["error"] = error_msg
            if log_callback:
                log_callback(error_msg)
            return result
        
        # Determine output file path
        output_path = ply_path.parent / output_name
        result["output_path"] = str(output_path)
        
        # Conversion
        if log_callback:
            log_callback("🔄 Starting conversion...\n\n")
        
        # Create wrapper that captures output and calls progress_callback in real-time
        class ProgressWriter:
            def __init__(self, log_callback, progress_callback):
                self.log_callback = log_callback
                self.progress_callback = progress_callback
                self.buffer = ""
            
            def write(self, text):
                if not text:
                    return
                    
                self.buffer += text
                # Flush on newline
                if '\n' in text:
                    lines = self.buffer.split('\n')
                    self.buffer = lines[-1]  # Keep incomplete line
                    for line in lines[:-1]:
                        if line.strip():  # Only process non-empty lines
                            if self.log_callback:
                                self.log_callback(line + '\n')
                            
                            # Parse progress in real-time
                            if self.progress_callback and "Progress:" in line:
                                try:
                                    parts = line.split("Progress:")
                                    if len(parts) > 1:
                                        percent_part = parts[1].split("%")[0].strip()
                                        percent = float(percent_part)
                                        
                                        # Extract counts
                                        processed = None
                                        unique = None
                                        if "Processed:" in line and "Unique:" in line:
                                            try:
                                                proc_part = line.split("Processed:")[1].split(",")[0].strip()
                                                unique_part = line.split("Unique:")[1].split()[0].strip()
                                                processed = int(proc_part.replace(',', ''))
                                                unique = int(unique_part.replace(',', ''))
                                            except:
                                                pass
                                        
                                        self.progress_callback(percent, processed, None, unique)
                                except:
                                    pass
            
            def flush(self):
                pass  # No-op for flush
        
        stderr_capture = io.StringIO()
        progress_writer = ProgressWriter(log_callback, progress_callback)
        
        try:
            with contextlib.redirect_stdout(progress_writer), contextlib.redirect_stderr(stderr_capture):
                success = convert_ply_to_colmap(str(ply_path), str(output_path))
            
            # Flush remaining buffer
            if progress_writer.buffer and log_callback:
                log_callback(progress_writer.buffer)
            
            # Output stderr if any
            stderr_output = stderr_capture.getvalue()
            if log_callback and stderr_output:
                log_callback(stderr_output)
        except Exception as e:
            if log_callback:
                log_callback(f"Error during conversion: {e}\n")
            raise
        
        if success:
            result["success"] = True
            result["file_size_output"] = os.path.getsize(output_path) / (1024 * 1024)  # MB
            
            # Count points from output file (approximate)
            try:
                with open(output_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    # First line with point count in header
                    for line in lines:
                        if "Number of points:" in line:
                            parts = line.split("Number of points:")
                            if len(parts) > 1:
                                result["points_count"] = int(parts[1].split(",")[0].strip())
                                break
            except:
                pass
            
            if log_callback:
                log_callback("\n" + "=" * 70 + "\n")
                log_callback("✅ CONVERSION COMPLETED SUCCESSFULLY!\n")
                log_callback("=" * 70 + "\n")
                if result["backup_path"]:
                    log_callback(f"📦 Backup of source file: {result['backup_path']}\n")
                log_callback(f"📄 Output file: {result['output_path']}\n")
                log_callback(f"📊 Input file size: {result['file_size_input']:.1f} MB\n")
                log_callback(f"📊 Output file size: {result['file_size_output']:.1f} MB\n")
                if result["points_count"] > 0:
                    log_callback(f"📊 Number of points: {result['points_count']:,}\n")
                log_callback("\n")
        else:
            result["error"] = "Error during conversion. Check logs above."
            if log_callback:
                log_callback("\n" + "=" * 70 + "\n")
                log_callback("❌ CONVERSION ERROR\n")
                log_callback("=" * 70 + "\n")
                if result["backup_path"]:
                    log_callback(f"📦 Backup of source file saved: {result['backup_path']}\n")
                    log_callback("💡 You can restore the original file from backup\n")
                log_callback("\n")
        
    except Exception as e:
        result["error"] = str(e)
        if log_callback:
            log_callback(f"\n❌ CRITICAL ERROR: {e}\n")
    
    return result

class HelpWindow:
    """Help window with CloudCompare instructions"""
    
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Help - How to Prepare PLY File in CloudCompare")
        self.window.geometry("700x650")
        self.window.resizable(True, True)
        
        # Make window modal
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()
        
        # Center window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")
    
    def create_widgets(self):
        """Creates help window widgets"""
        # Main frame with padding
        main_frame = tk.Frame(self.window, padx=15, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="How to Prepare PLY File in CloudCompare",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(0, 15))
        
        # Scrollable text area
        text_frame = tk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        help_text = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            font=("Arial", 10),
            bg="#ffffff",
            fg="#333333",
            padx=10,
            pady=10
        )
        help_text.pack(fill=tk.BOTH, expand=True)
        
        # Help content
        help_content = """
PREPARING PLY FILE IN CLOUDCOMPARE

This converter requires a PLY file exported from CloudCompare with specific settings.
Follow these steps to prepare your file:

STEP 1: Open Your Point Cloud in CloudCompare
─────────────────────────────────────────────
1. Open CloudCompare
2. Go to File → Open
3. Select your dense point cloud file (supports formats like .e57, .las, .pts, etc.)

STEP 2: Edit and Process Your Point Cloud (Optional)
─────────────────────────────────────────────────────
• Use Edit → Subsample to reduce point count if needed
• Apply Tools → Noise filter to clean the data
• Perform any necessary editing operations

STEP 3: Export as PLY File
───────────────────────────
1. Go to File → Save As
2. Select PLY format from the file type dropdown
3. Configure PLY export settings:

   REQUIRED SETTINGS:
   ✅ Binary encoding: Yes (enabled)
   ✅ Include colors: Yes (enabled)
   ❌ Include normals: No (disabled - not needed for COLMAP)
   ❌ Include scalar fields: No (disabled)

4. Click Save and choose your file location

IMPORTANT NOTES:
────────────────
• The PLY file must contain vertex positions (X, Y, Z) and colors (R, G, B)
• Binary encoding is recommended for better performance
• Normals and scalar fields are not required and will be ignored
• The converter will automatically remove duplicate points
• Original file will be backed up before conversion

CONVERSION PROCESS:
───────────────────
1. Select your PLY file using the "Select File" button
2. Click "Convert" to start the conversion
3. A backup of your original file will be created automatically
4. The converted COLMAP points3D.txt file will be saved in the same directory

RESULT:
───────
After conversion, you will get:
• points3D.txt - COLMAP format file ready for Postshot 3D Gaussian Splatting
• [filename]_backup_[timestamp].ply - Backup of your original file

The converted file can be placed in your COLMAP sparse/0/ folder and imported into Postshot.

TROUBLESHOOTING:
───────────────
If you encounter errors:
• Ensure your PLY file has colors (R, G, B values)
• Check that the file is not corrupted
• Verify the file was exported with binary encoding enabled
• Make sure you have sufficient disk space for the backup and output file

Need more help? Consult AI assistants (ChatGPT, Claude, etc.) or check the GitHub repository.
"""
        
        help_text.insert(tk.END, help_content)
        help_text.config(state=tk.DISABLED)  # Make read-only
        
        # Close button
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=(15, 0))
        
        close_button = tk.Button(
            button_frame,
            text="Close",
            command=self.window.destroy,
            font=("Arial", 10),
            bg="#2196F3",
            fg="white",
            relief=tk.RAISED,
            padx=20,
            pady=5
        )
        close_button.pack()

class AboutWindow:
    """About window with creator information and GitHub link"""
    
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("About")
        self.window.geometry("500x350")
        self.window.resizable(False, False)
        
        # Make window modal
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()
        
        # Center window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")
    
    def create_widgets(self):
        """Creates about window widgets"""
        # Main frame
        main_frame = tk.Frame(self.window, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="PLY to COLMAP Converter",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 10))
        
        # Version/Description
        desc_label = tk.Label(
            main_frame,
            text="Converts PLY dense point clouds from CloudCompare\nto COLMAP format for Postshot 3D Gaussian Splatting",
            font=("Arial", 10),
            justify=tk.CENTER
        )
        desc_label.pack(pady=(0, 20))
        
        # Creator info
        creator_frame = tk.Frame(main_frame)
        creator_frame.pack(pady=(0, 20))
        
        tk.Label(
            creator_frame,
            text="Created by:",
            font=("Arial", 9),
            fg="gray"
        ).pack()
        
        tk.Label(
            creator_frame,
            text="Andrii Shramko",
            font=("Arial", 11, "bold")
        ).pack(pady=(5, 0))
        
        # GitHub link
        link_frame = tk.Frame(main_frame)
        link_frame.pack(pady=(0, 20))
        
        tk.Label(
            link_frame,
            text="GitHub Repository:",
            font=("Arial", 9),
            fg="gray"
        ).pack()
        
        github_link = tk.Label(
            link_frame,
            text=GITHUB_URL,
            font=("Arial", 9),
            fg="blue",
            cursor="hand2"
        )
        github_link.pack(pady=(5, 0))
        github_link.bind("<Button-1>", lambda e: webbrowser.open(GITHUB_URL))
        
        # License
        license_label = tk.Label(
            main_frame,
            text="License: MIT - Free for community use",
            font=("Arial", 9),
            fg="gray"
        )
        license_label.pack(pady=(0, 20))
        
        # Description
        info_text = """
A community contribution to advance 3D/4D Gaussian Splatting technology.
Developed through extensive research when no existing solutions were found.

This tool converts dense point clouds from CloudCompare to COLMAP format,
allowing better quality 3D Gaussian Splatting training in Postshot compared
to using sparse point clouds alone.
"""
        
        info_label = tk.Label(
            main_frame,
            text=info_text.strip(),
            font=("Arial", 9),
            justify=tk.CENTER,
            fg="#555555"
        )
        info_label.pack(pady=(0, 20))
        
        # Close button
        close_button = tk.Button(
            main_frame,
            text="Close",
            command=self.window.destroy,
            font=("Arial", 10),
            bg="#2196F3",
            fg="white",
            relief=tk.RAISED,
            padx=20,
            pady=5
        )
        close_button.pack()

class PLYConverterGUI:
    """Main GUI application class"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("PLY to COLMAP Converter")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Load configuration
        self.config = load_config()
        self.current_file_path = self.config.get("last_path", "")
        
        # Create interface
        self.create_menu()
        self.create_widgets()
        
        # Update interface with loaded path
        if self.current_file_path:
            self.file_path_var.set(self.current_file_path)
    
    def create_menu(self):
        """Creates menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="How to Prepare PLY File...", command=self.show_help)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self.show_about)
    
    def create_widgets(self):
        """Creates interface elements"""
        
        # Main frame
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="PLY to COLMAP Converter",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # File selection frame
        file_frame = tk.Frame(main_frame)
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(file_frame, text="PLY File:", font=("Arial", 10)).pack(side=tk.LEFT, padx=(0, 10))
        
        self.file_path_var = tk.StringVar()
        file_entry = tk.Entry(file_frame, textvariable=self.file_path_var, font=("Arial", 10))
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        select_button = tk.Button(
            file_frame,
            text="Select File...",
            command=self.select_file,
            font=("Arial", 10),
            bg="#4CAF50",
            fg="white",
            relief=tk.RAISED,
            padx=10,
            pady=5
        )
        select_button.pack(side=tk.LEFT)
        
        # Convert button
        convert_button = tk.Button(
            main_frame,
            text="Convert",
            command=self.start_conversion,
            font=("Arial", 12, "bold"),
            bg="#2196F3",
            fg="white",
            relief=tk.RAISED,
            padx=20,
            pady=10,
            state=tk.NORMAL
        )
        convert_button.pack(pady=(0, 10))
        
        self.convert_button = convert_button
        
        # Progress frame
        progress_frame = tk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            length=400,
            mode='determinate'
        )
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Progress label
        self.progress_label_var = tk.StringVar(value="")
        progress_label = tk.Label(
            progress_frame,
            textvariable=self.progress_label_var,
            font=("Arial", 9),
            fg="#2196F3",
            width=15
        )
        progress_label.pack(side=tk.RIGHT)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_label = tk.Label(
            main_frame,
            textvariable=self.status_var,
            font=("Arial", 9),
            fg="gray",
            anchor=tk.W
        )
        status_label.pack(fill=tk.X, pady=(0, 10))
        
        # Initialize progress tracking
        self.progress_start_time = None
        self.last_progress_update = 0
        
        # Log text area
        log_label = tk.Label(main_frame, text="Conversion Log:", font=("Arial", 10, "bold"))
        log_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.log_text = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            font=("Consolas", 9),
            bg="#f5f5f5",
            fg="#333",
            height=20
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Initial message
        self.log_text.insert(tk.END, "Welcome to PLY to COLMAP Converter!\n")
        self.log_text.insert(tk.END, "Select a PLY file to convert.\n\n")
    
    def show_help(self):
        """Shows help window"""
        HelpWindow(self.root)
    
    def show_about(self):
        """Shows about window"""
        AboutWindow(self.root)
    
    def select_file(self):
        """Opens file selection dialog"""
        initial_dir = ""
        if self.current_file_path:
            initial_dir = str(Path(self.current_file_path).parent)
        
        file_path = filedialog.askopenfilename(
            title="Select PLY File",
            initialdir=initial_dir,
            filetypes=[("PLY files", "*.ply"), ("All files", "*.*")]
        )
        
        if file_path:
            self.current_file_path = file_path
            self.file_path_var.set(file_path)
            
            # Save path to configuration
            self.config["last_path"] = file_path
            save_config(self.config)
            
            self.log_text.insert(tk.END, f"File selected: {file_path}\n")
            self.log_text.see(tk.END)
            self.status_var.set(f"File selected: {Path(file_path).name}")
    
    def log_message(self, message):
        """Adds message to log (thread-safe)"""
        self.root.after(0, self._log_message_safe, message)
    
    def _log_message_safe(self, message):
        """Safe message addition to log from main thread"""
        self.log_text.insert(tk.END, message)
        self.log_text.see(tk.END)
        
        # Try to extract progress from message
        if "Progress:" in message:
            try:
                # Extract percentage from "Progress: 45.2%"
                parts = message.split("Progress:")
                if len(parts) > 1:
                    percent_str = parts[1].split("%")[0].strip()
                    percent = float(percent_str)
                    self.update_progress(percent)
            except:
                pass
    
    def update_progress(self, percent, processed=None, total=None, unique=None):
        """Updates progress bar (thread-safe)"""
        self.root.after(0, self._update_progress_safe, percent, processed, total, unique)
    
    def _update_progress_safe(self, percent, processed, total, unique):
        """Safe progress update from main thread"""
        self.progress_var.set(percent)
        
        # Update progress label
        if processed is not None and total is not None:
            # Calculate ETA
            if self.progress_start_time is None:
                self.progress_start_time = time.time()
                self.last_progress_update = percent
            
            if percent > 0 and percent > self.last_progress_update:
                elapsed = time.time() - self.progress_start_time
                if percent > 0:
                    estimated_total = elapsed / (percent / 100.0)
                    remaining = estimated_total - elapsed
                    
                    if remaining > 60:
                        eta_str = f"{int(remaining / 60)}m {int(remaining % 60)}s"
                    else:
                        eta_str = f"{int(remaining)}s"
                    
                    self.progress_label_var.set(f"{percent:.1f}% | ETA: {eta_str}")
                    self.last_progress_update = percent
                else:
                    self.progress_label_var.set(f"{percent:.1f}%")
            else:
                self.progress_label_var.set(f"{percent:.1f}%")
        else:
            self.progress_label_var.set(f"{percent:.1f}%")
    
    def reset_progress(self):
        """Resets progress bar"""
        self.progress_var.set(0)
        self.progress_label_var.set("")
        self.progress_start_time = None
        self.last_progress_update = 0
    
    def start_conversion(self):
        """Starts conversion in separate thread"""
        file_path = self.file_path_var.get().strip().strip('"')
        
        if not file_path:
            messagebox.showerror("Error", "Please select a file to convert!")
            return
        
        if not os.path.exists(file_path):
            messagebox.showerror("Error", f"File not found:\n{file_path}")
            return
        
        # Clear logs
        self.log_text.delete(1.0, tk.END)
        
        # Reset progress
        self.reset_progress()
        
        # Disable convert button
        self.convert_button.config(state=tk.DISABLED)
        self.status_var.set("Conversion in progress...")
        
        # Start conversion in separate thread
        thread = threading.Thread(target=self.convert_thread, args=(file_path,), daemon=True)
        thread.start()
    
    def convert_thread(self, file_path):
        """Executes conversion in separate thread"""
        try:
            # Execute conversion with progress callback
            result = convert_ply_file_gui(
                file_path, 
                "points3D.txt", 
                log_callback=self.log_message,
                progress_callback=self.update_progress
            )
            
            # Update UI from main thread
            self.root.after(0, self.conversion_complete, result)
            
        except Exception as e:
            self.root.after(0, self.conversion_error, str(e))
    
    def conversion_complete(self, result):
        """Handles conversion completion"""
        self.convert_button.config(state=tk.NORMAL)
        
        # Set progress to 100% on completion
        if result["success"]:
            self.update_progress(100.0)
            self.progress_label_var.set("100% | Complete")
            self.status_var.set("✅ Conversion completed successfully!")
            messagebox.showinfo(
                "Success",
                f"Conversion completed successfully!\n\n"
                f"Output file: {result['output_path']}\n"
                f"Backup: {Path(result['backup_path']).name if result['backup_path'] else 'Not created'}\n"
                f"Input file size: {result['file_size_input']:.1f} MB\n"
                f"Output file size: {result['file_size_output']:.1f} MB"
            )
        else:
            self.progress_label_var.set("Failed")
            self.status_var.set("❌ Conversion error")
            error_msg = result.get("error", "Unknown error")
            messagebox.showerror("Error", f"Error during conversion:\n\n{error_msg}")
    
    def conversion_error(self, error_msg):
        """Handles critical error"""
        self.convert_button.config(state=tk.NORMAL)
        self.status_var.set("❌ Critical error")
        messagebox.showerror("Critical Error", f"An error occurred:\n\n{error_msg}")

def main():
    """Main function to start GUI"""
    root = tk.Tk()
    app = PLYConverterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
