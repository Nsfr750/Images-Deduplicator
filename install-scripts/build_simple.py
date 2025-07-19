#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple build script for Images-Deduplicator Windows installer.
"""
import os
import sys
import subprocess
import shutil
import time
from pathlib import Path

def clean_directory(dir_path):
    """Remove directory if it exists and recreate it."""
    if dir_path.exists():
        shutil.rmtree(dir_path, ignore_errors=True)
    dir_path.mkdir(parents=True, exist_ok=True)

def run_command(cmd, cwd=None):
    """Run a command and return (success, output)."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.output

def create_portable_archive():
    """Create a portable archive of the built application."""
    print("\n" + "=" * 80)
    print("📦 Creating portable archive")
    print("=" * 80)
    
    import zipfile
    from datetime import datetime
    
    base_dir = Path(__file__).parent
    dist_dir = base_dir / "dist"
    exe_path = dist_dir / "Images-Deduplicator.exe"
    
    if not exe_path.exists():
        print("❌ Executable not found. Please build the application first.")
        return False
    
    # Create a version string for the archive name
    try:
        from script.version import __version__
        version_str = __version__
    except ImportError:
        version_str = datetime.now().strftime("%Y%m%d")
    
    archive_name = f"Images-Deduplicator-Portable-v{version_str}.zip"
    archive_path = dist_dir / archive_name
    
    print(f"📁 Creating archive: {archive_path}")
    
    try:
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add the executable
            zipf.write(exe_path, arcname=exe_path.name)
            
            # Add assets directory if it exists
            assets_src = base_dir / "assets"
            assets_dest = "assets"
            if assets_src.exists():
                for root, _, files in os.walk(assets_src):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = assets_dest / file_path.relative_to(assets_src)
                        zipf.write(file_path, arcname=arcname)
            
            # Add a README.txt
            readme_content = """Images-Deduplicator Portable

This is a portable version of Images-Deduplicator. Simply extract this archive and run Images-Deduplicator.exe.

Version: {}
Build date: {}
""".format(version_str, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            
            zipf.writestr("README.txt", readme_content)
        
        print(f"✅ Successfully created portable archive: {archive_path}")
        print(f"   Archive size: {archive_path.stat().st_size / 1024 / 1024:.2f} MB")
        return True
    except Exception as e:
        print(f"❌ Failed to create portable archive: {e}")
        if archive_path.exists():
            archive_path.unlink()
        return False

def build_installer():
    """Build the Windows installer using PyInstaller."""
    print("=" * 80)
    print("🚀 Building Images-Deduplicator")
    print("=" * 80)
    
    # Set up paths
    base_dir = Path(__file__).parent
    dist_dir = base_dir / "dist"
    build_dir = base_dir / "build"
    
    # Clean previous builds
    print("🧹 Cleaning build directories...")
    clean_directory(build_dir)
    
    # Build PyInstaller command
    # Collect all Python files in the script directory
    script_files = []
    script_dir = base_dir / "script"
    for root, _, files in os.walk(script_dir):
        for file in files:
            if file.endswith('.py'):
                script_files.append((script_dir / file).relative_to(base_dir))
    
    # Build PyInstaller command
    pyinstaller_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--distpath", str(dist_dir),
        "--workpath", str(build_dir),
        "--specpath", str(build_dir),
        "--onefile",
        "--windowed",
        "--noconsole",
        "--name", "Images-Deduplicator",
        "--icon", str(base_dir / "assets" / "icon.ico"),
        "--add-data", f"{base_dir / 'assets'}{os.pathsep}assets",
        "--add-data", f"{base_dir / 'script'}{os.pathsep}script",
        "--hidden-import", "script.about",
        "--hidden-import", "script.help",
        "--hidden-import", "script.log_viewer",
        "--hidden-import", "script.sponsor",
        "--hidden-import", "script.styles",
        "--hidden-import", "script.translations",
        "--hidden-import", "script.updates",
        "--hidden-import", "script.version",
        "--hidden-import", "script.settings_dialog",
        "--hidden-import", "script.menu",
        "--hidden-import", "script.logger",
        "--hidden-import", "script.language_manager",
        "--hidden-import", "script.workers",
        "--hidden-import", "script.image_dialog_preview",
        "--hidden-import", "script.empty_trash",
        "--hidden-import", "script.undo_manager",
        "--hidden-import", "script.update_preview",
        str(base_dir / "main.py")
    ]
    
    print("\n🔨 Running PyInstaller command:")
    print(" ".join(f'"{arg}"' if ' ' in str(arg) else str(arg) for arg in pyinstaller_cmd))
    
    # Run PyInstaller
    print("\n📝 PyInstaller output:")
    print("-" * 80)
    
    process = subprocess.Popen(
        pyinstaller_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    # Print output in real-time
    output_lines = []
    while True:
        line = process.stdout.readline()
        if not line and process.poll() is not None:
            break
        if line:
            print(line, end='')
            output_lines.append(line)
    
    return_code = process.returncode
    output = "\n".join(output_lines)
    
    print("\n" + "-" * 80)
    
    # Check if build was successful
    exe_path = dist_dir / "Images-Deduplicator.exe"
    if return_code == 0 and exe_path.exists():
        print(f"\n✅ Successfully built: {exe_path}")
        print(f"   File size: {exe_path.stat().st_size / 1024 / 1024:.2f} MB")
        
        # Create portable archive after successful build
        create_portable_archive()
        
        return True
    else:
        print("\n❌ Build failed")
        print(f"   Return code: {return_code}")
        print(f"   Executable exists: {exe_path.exists()}")
        
        # Save the full output to a file for debugging
        log_file = base_dir / "build_failure.log"
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"\n📄 Full build output saved to: {log_file}")
        
        return False

if __name__ == "__main__":
    build_installer()
