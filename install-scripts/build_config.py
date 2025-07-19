"""
Build configuration for platform-specific installers.
"""
from pathlib import Path
import sys

# Project information
PROJECT_NAME = "Images-Deduplicator"
VERSION = "1.6.0"
AUTHOR = "Nsfr750"
DESCRIPTION = "A tool for finding and removing duplicate images."
COPYRIGHT = f"(c) 2025 {AUTHOR}"

# Paths
ROOT_DIR = Path(__file__).parent
ASSETS_DIR = ROOT_DIR / "assets"
DIST_DIR = ROOT_DIR / "dist"
BUILD_DIR = ROOT_DIR / "build"

# Platform-specific configurations
PLATFORMS = {
    "Windows": {
        "name": "Windows",
        "executable": f"{PROJECT_NAME}.exe",
        "installer": {
            "type": "nsis",
            "extension": "exe",
            "extra_args": [
                "--windowed",
                "--onefile",
                "--noconsole",
                "--name", f"{PROJECT_NAME}-{VERSION}-Windows",
                "--icon", str(ASSETS_DIR / "icon.ico"),
                "--version-file", str(ASSETS_DIR / "version_info.txt"),
            ],
            "nsis": {
                "install_icon": str(ASSETS_DIR / "installer.ico"),
                "uninstall_icon": str(ASSETS_DIR / "uninstaller.ico"),
                "header_image": str(ASSETS_DIR / "nsis-header.bmp"),
                "wizard_image": str(ASSETS_DIR / "nsis-wizard.bmp"),
                "sidebar_image": str(ASSETS_DIR / "nsis-sidebar.bmp"),
                "installer_name": f"{PROJECT_NAME}-{VERSION}-Setup"
            }
        },
        "archive": {
            "formats": ["zip", "7z"],
            "include": ["*.exe", "*.dll", "*.pyd", "LICENSE", "README.md"]
        }
    },
    "Darwin": {
        "name": "macOS",
        "executable": f"{PROJECT_NAME}.app",
        "installer": {
            "type": "dmg",
            "extension": "dmg",
            "extra_args": [
                "--windowed",
                "--osx-bundle-identifier", f"com.{AUTHOR.lower()}.{PROJECT_NAME.lower()}",
                "--icon", str(ASSETS_DIR / "icon.icns"),
                "--name", f"{PROJECT_NAME}-{VERSION}-macOS",
                "--osx-entitlements-file", str(ASSETS_DIR / "entitlements.plist"),
            ],
            "dmg": {
                "volume_name": f"{PROJECT_NAME} {VERSION}",
                "background": str(ASSETS_DIR / "dmg-background.png"),
                "icon_size": 80,
                "text_size": 12,
                "window_rect": {"x": 100, "y": 100, "width": 500, "height": 300}
            }
        },
        "archive": {
            "formats": ["tar.gz", "zip"],
            "include": ["*.app", "LICENSE", "README.md"]
        }
    },
    "Linux": {
        "name": "Linux",
        "executable": PROJECT_NAME,
        "installer": {
            "type": "appimage",
            "extension": "AppImage",
            "extra_args": [
                "--windowed",
                "--name", f"{PROJECT_NAME}-{VERSION}-Linux",
                "--icon", str(ASSETS_DIR / "icon.png"),
                "--runtime-tmpdir", "/tmp"
            ],
            "appimage": {
                "update-information": None,
                "sign": True,
                "sign-args": ["--sign"],
                "runtime-file": "appruntime"
            }
        },
        "archive": {
            "formats": ["tar.gz", "zip"],
            "include": ["*.AppImage", "*.desktop", "LICENSE", "README.md"]
        },
        "deb": {
            "enabled": True,
            "dependencies": ["python3", "python3-pip"],
            "maintainer": f"{AUTHOR} <nsfr750@yandex.com>",
            "section": "utils",
            "architecture": "amd64",
            "description": DESCRIPTION,
            "pre_install_script": "preinst",
            "post_install_script": "postinst",
            "pre_uninstall_script": "prerm",
            "post_uninstall_script": "postrm"
        }
    }
}

# Common PyInstaller configurations
PYINSTALLER_CONFIG = {
    "hidden_imports": [
        'PyQt6',
        'qrcode',
        'numpy',
        'wand',
        'imagehash',
        'requests',
        'pywin32',
        'psutil',
        'send2trash',
        'win32timezone' if sys.platform == 'win32' else ''
    ],
    "data_files": [
        (str(ASSETS_DIR), "assets"),
        (str(ROOT_DIR / "config"), "config"),
        (str(ROOT_DIR / "script"), "script"),
        (str(ROOT_DIR / "README.md"), "."),
        (str(ROOT_DIR / "LICENSE"), "."),
        (str(ROOT_DIR / "CHANGELOG.md"), ".")
    ],
    "excludes": [
        'tkinter',
        'pillow',
        'PIL',
        'unittest',
        'email',
        'http',
        'xml',
        'pydoc',
        'pdb',
        'doctest',
        'pdb'
    ],
    "upx": True,
    "upx_exclude": [],
    "no_compress": False,
    "optimize": 1,
    "strip": True,
    "console": False,
    "debug": False
}
