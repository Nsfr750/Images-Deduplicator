#!/usr/bin/env python3
# setup/comp.py
import os
import sys
import shutil
import platform
import subprocess
from pathlib import Path
from PNG_ICO import convert_png_to_ico

def convert_icon():
    """Convert app-icon.png to app-icon.ico if needed."""
    try:
        base_dir = Path(__file__).parent.parent
        png_path = base_dir / "assets" / "app-icon.png"
        ico_path = base_dir / "assets" / "app-icon.ico"
        
        # Check if conversion is needed
        if png_path.exists() and (not ico_path.exists() or 
                                 png_path.stat().st_mtime > ico_path.stat().st_mtime):
            print("Converting app icon...")
            
            # Import the conversion function
            sys.path.append(str(Path(__file__).parent))
            from convert_icon import convert_png_to_ico
            if not convert_png_to_ico(str(png_path), str(ico_path)):
                print("Warning: Could not convert app icon")
        return True
    except Exception as e:
        print(f"Error converting icon: {e}")
        return False

def main():
    """Main function to handle the build process."""
    # Clean build directories
    clean_build()
    
    # Convert icon if needed
    if not convert_icon():
        print("Warning: Could not convert app icon, using default")
    
    # Install dependencies
    install_dependencies()
    
    # Run Nuitka
    if not run_nuitka():
        sys.exit(1)
    
    # Sign the executable
    sign_executable()
    
    print(f"\n{APP_NAME} {VERSION} has been built successfully!")
    print(f"Output: {DIST_DIR / APP_NAME}.exe")

# Clear build directory
build_dir = Path("build")
if build_dir.exists():
    print(f"Clearing build directory: {build_dir}")
    try:
        shutil.rmtree(build_dir)
        print("Build directory cleared successfully")
    except Exception as e:
        print(f"Error clearing build directory: {e}")
else:
    print("Build directory does not exist")

# Clear dist directory
dist_dir = Path("dist")
if dist_dir.exists():
    print(f"Clearing dist directory: {dist_dir}")
    try:
        shutil.rmtree(dist_dir)
        print("Dist directory cleared successfully")
    except Exception as e:
        print(f"Error clearing dist directory: {e}")
else:
    print("Dist directory does not exist")

# Clear spec directory
spec_dir = Path("spec")
if spec_dir.exists():
    print(f"Clearing spec directory: {spec_dir}")
    try:
        shutil.rmtree(spec_dir)
        print("Spec directory cleared successfully")
    except Exception as e:
        print(f"Error clearing spec directory: {e}")
else:
    print("Spec directory does not exist")    

# Project information
APP_NAME = "Image-Deduplicator"
VERSION = "1.7.0"
AUTHOR = "Nsfr750"
DESCRIPTION = "An image deduplicator with enhanced encryption, key management, and security features."
ENTRY_POINT = "main.py"

# Directories
BASE_DIR = Path(__file__).parent.parent
DIST_DIR = BASE_DIR / "dist"
BUILD_DIR = BASE_DIR / "build"
SPEC_DIR = BASE_DIR / "spec"

# Nuitka options
NUITKA_OPTIONS = [
    "--mingw64",  # Use MinGW64 for compilation
    "--standalone",  # Create a standalone distribution
    "--onefile",  # Create a single executable file
    "--jobs=4",  # Number of jobs for parallel compilation
    #"--windows-console-mode=disable",  # Disable console window for GUI apps
    "--enable-plugin=pyqt6",  # Enable PySide6 plugin
    "--include-package=script",  # Include gui package
    "--include-package=logs",  # Include logs files
    "--include-package=assets",  # Include assets
    "--include-data-dir=assets=assets",  # Include assets directory
    "--windows-console-mode=force",  # Enable console for debugging
    "--windows-icon-from-ico=assets/app-icon.ico",  # Application icon
    #"--windows-uac-admin",  # Request admin privileges if needed
    "--follow-imports",  # Follow all imports
    "--remove-output",  # Remove build directory after compilation
    "--assume-yes-for-downloads",  # Auto-confirm downloads
    f"--output-filename={APP_NAME}",  # Output filename
    f"--output-dir={DIST_DIR}",  # Output directory
    f"--company-name={AUTHOR}",  # Company name
    f"--file-version={VERSION}",  # File version
    f"--product-version={VERSION}",  # Product version
    f"--file-description={DESCRIPTION}",  # File description
    f"--product-name={APP_NAME}",  # Product name
    f"--copyright=© 2024-2025 {AUTHOR} - All Rights Reserved",  # Copyright notice
    "--windows-company-name=Tuxxle",  # Company name for Windows
    "--windows-file-version=1.7.0",  # Windows file version
    "--windows-product-version=1.7.0",  # Windows product version
]

def clean_build():
    """Clean up build and dist directories."""
    print("Cleaning build directories...")
    for directory in [DIST_DIR, BUILD_DIR, SPEC_DIR]:
        if directory.exists():
            shutil.rmtree(directory, ignore_errors=True)
        directory.mkdir(parents=True, exist_ok=True)

def run_nuitka():
    """Run Nuitka to compile the application."""
    print(f"Compiling {APP_NAME} with Nuitka...")
    
    cmd = [
        sys.executable,
        "-m", "nuitka",
        *NUITKA_OPTIONS,
        str(BASE_DIR / ENTRY_POINT)
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"\nSuccessfully compiled {APP_NAME}!")
        print(f"Executable location: {DIST_DIR / f'{APP_NAME}.exe'}")
    except subprocess.CalledProcessError as e:
        print(f"Error during compilation: {e}", file=sys.stderr)
        sys.exit(1)

def sign_executable():
    """Sign the compiled executable."""
    executable = DIST_DIR / f"{APP_NAME}.exe"
    if not executable.exists():
        print("Executable not found for signing.", file=sys.stderr)
        return

    print("\nSigning the executable...")
    sign_script = BASE_DIR / "setup" / "firma.bat"
    if sign_script.exists():
        try:
            subprocess.run(str(sign_script), shell=True, check=True)
            print("Executable signed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"Error during signing: {e}", file=sys.stderr)
    else:
        print("Signing script not found. Skipping signing.", file=sys.stderr)

def install_dependencies():
    """Install required dependencies."""
    print("Installing/updating dependencies...")
    requirements = [
        "nuitka",
        "PySide6>=6.4.0",
        "PGPy>=0.6.0",
        "cryptography>=3.4.0",
        "pyperclip>=1.8.2",
        "wand>=0.6.10",
        "python-gnupg>=0.5.0",
        "pycryptodome>=3.12.0",
        "argon2-cffi>=21.3.0"
    ]
    
    for package in requirements:
        print(f"Checking {package}...")
        try:
            __import__(package.split('>=')[0].split('==')[0])
        except ImportError:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def main():
    """Main function to handle the build process."""
    print(f"Building {APP_NAME} v{VERSION}")
    print("=" * 50)
    
    # Install/update dependencies
    install_dependencies()
    
    # Check if Nuitka is installed
    try:
        import nuitka
    except ImportError:
        print("Nuitka installation failed. Please install it manually.")
        sys.exit(1)
    
    clean_build()
    run_nuitka()
    sign_executable()

if __name__ == "__main__":
    main()