"""
Code signing utilities for the Images-Deduplicator installers.
This script handles code signing for Windows, macOS, and Linux platforms.
"""
import os
import sys
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, List, Dict, Any
import json
import shutil
from datetime import datetime, timedelta

class CodeSigner:
    """Base class for code signing operations."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.platform = sys.platform
        self.cert_info = self._load_certificate_info()
    
    def _load_certificate_info(self) -> Dict[str, Any]:
        """Load certificate information from config or environment."""
        cert_info = self.config.get('code_signing', {})
        
        # Check for environment variables
        env_mapping = {
            'windows': {
                'cert_path': 'WINDOWS_SIGNING_CERT_PATH',
                'cert_password': 'WINDOWS_SIGNING_CERT_PASSWORD',
                'timestamp_url': 'WINDOWS_TIMESTAMP_URL',
            },
            'darwin': {
                'identity': 'MACOS_SIGNING_IDENTITY',
                'keychain': 'MACOS_KEYCHAIN_PATH',
                'keychain_password': 'MACOS_KEYCHAIN_PASSWORD',
            },
            'linux': {
                'gpg_key': 'GPG_SIGNING_KEY',
                'gpg_password': 'GPG_PASSPHRASE',
            }
        }
        
        # Update with environment variables if available
        for key, env_var in env_mapping.get(sys.platform, {}).items():
            if os.environ.get(env_var):
                cert_info[key] = os.environ[env_var]
        
        return cert_info
    
    def sign(self, file_path: Path) -> bool:
        """Sign a file using the appropriate method for the platform."""
        if not file_path.exists():
            print(f"Error: File not found: {file_path}")
            return False
        
        sign_methods = {
            'win32': self._sign_windows,
            'darwin': self._sign_macos,
            'linux': self._sign_linux
        }
        
        sign_method = sign_methods.get(sys.platform)
        if not sign_method:
            print(f"Error: Unsupported platform: {sys.platform}")
            return False
        
        print(f"Signing {file_path}...")
        return sign_method(file_path)
    
    def _sign_windows(self, file_path: Path) -> bool:
        """Sign a Windows executable or installer."""
        if not self.cert_info.get('cert_path'):
            print("Error: Windows signing certificate path not configured")
            return False
        
        signtool = self._find_signtool()
        if not signtool:
            print("Error: Could not find signtool.exe")
            return False
        
        cmd = [
            str(signtool), 'sign',
            '/fd', 'SHA256',
            '/td', 'SHA256',
            '/tr', self.cert_info.get('timestamp_url', 'http://timestamp.digicert.com'),
            '/d', 'Images Deduplicator',
            '/du', 'https://github.com/Nsfr750/Images-Deduplicator',
        ]
        
        # Add certificate information
        if self.cert_info.get('cert_password'):
            cmd.extend(['/p', self.cert_info['cert_password']])
        
        # Add file to sign
        cmd.append(str(file_path))
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"Successfully signed {file_path}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error signing {file_path}: {e.stderr}")
            return False
    
    def _sign_macos(self, file_path: Path) -> bool:
        """Sign a macOS application bundle or installer."""
        identity = self.cert_info.get('identity')
        if not identity:
            print("Error: macOS signing identity not configured")
            return False
        
        # For .app bundles, sign with --deep
        if file_path.suffix == '.app':
            args = ['codesign', '--deep', '--force', '--verify', '--verbose']
        else:
            args = ['codesign', '--force', '--verify', '--verbose']
        
        # Add entitlements if specified
        entitlements = self.config.get('entitlements_file')
        if entitlements and Path(entitlements).exists():
            args.extend(['--entitlements', entitlements])
        
        # Add signature arguments
        args.extend([
            '--sign', identity,
            '--options', 'runtime',
            '--timestamp',
            str(file_path)
        ])
        
        try:
            subprocess.run(args, check=True, capture_output=True, text=True)
            print(f"Successfully signed {file_path}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error signing {file_path}: {e.stderr}")
            return False
    
    def _sign_linux(self, file_path: Path) -> bool:
        """Sign a Linux executable or package."""
        gpg_key = self.cert_info.get('gpg_key')
        if not gpg_key:
            print("Error: GPG key not configured")
            return False
        
        # For AppImage, use appimagetool for signing
        if file_path.suffix.lower() == '.appimage':
            return self._sign_appimage(file_path, gpg_key)
        
        # For DEB packages, use dpkg-sig
        if file_path.suffix.lower() == '.deb':
            return self._sign_deb(file_path, gpg_key)
        
        # For other files, use GPG
        return self._sign_with_gpg(file_path, gpg_key)
    
    def _sign_appimage(self, file_path: Path, gpg_key: str) -> bool:
        """Sign an AppImage file."""
        try:
            cmd = ['appimagetool', '--sign', '--sign-key', gpg_key, str(file_path)]
            if self.cert_info.get('gpg_password'):
                # Use gpg-preset-passphrase if available
                cmd = ['gpg-preset-passphrase', '--preset', '--passphrase', 
                      self.cert_info['gpg_password']] + cmd
            
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"Successfully signed {file_path}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error signing AppImage: {e.stderr}")
            return False
    
    def _sign_deb(self, file_path: Path, gpg_key: str) -> bool:
        """Sign a DEB package."""
        try:
            # First, sign the .changes file
            changes_file = file_path.with_suffix('.changes')
            if not changes_file.exists():
                # Create a temporary changes file
                with tempfile.NamedTemporaryFile(suffix='.changes', delete=False) as f:
                    changes_file = Path(f.name)
                    f.write(f"Format: 1.0\n\n")
                    f.write(f"Images-Deduplicator ({self.config.get('version', '1.6.0')}) stable; urgency=medium\n")
                    f.write(f"  * New release\n\n")
                    f.write(f" -- {self.config.get('author', 'Nsfr750')} <{self.config.get('email', 'nsfr750@yandex.com')}>  {datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000')}\n".encode())
            
            # Sign the package
            cmd = ['dpkg-sig', '--sign', 'builder', '-k', gpg_key, str(file_path)]
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            # Clean up temporary changes file if we created one
            if changes_file.exists() and not changes_file.with_suffix('.changes').exists():
                changes_file.unlink()
                
            print(f"Successfully signed {file_path}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error signing DEB package: {e.stderr}")
            return False
    
    def _sign_with_gpg(self, file_path: Path, gpg_key: str) -> bool:
        """Sign a file with GPG."""
        try:
            cmd = ['gpg', '--detach-sign', '--armor', '--local-user', gpg_key]
            if self.cert_info.get('gpg_password'):
                cmd.extend(['--batch', '--pinentry-mode', 'loopback', '--passphrase', self.cert_info['gpg_password']])
            cmd.append(str(file_path))
            
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"Successfully signed {file_path}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error signing with GPG: {e.stderr}")
            return False
    
    def _find_signtool(self) -> Optional[Path]:
        """Find the Windows SDK signtool.exe."""
        # Common locations for signtool.exe
        program_files = os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)')
        sdk_paths = [
            f"{program_files}\\Windows Kits\\10\\bin\\10.0.*\\x64",
            f"{program_files}\\Windows Kits\\10\\bin\\10.0.*\\x86",
            f"{program_files}\\Windows Kits\\8.1\\bin\\x64",
            f"{program_files}\\Windows Kits\\8.1\\bin\\x86",
        ]
        
        for path_pattern in sdk_paths:
            try:
                # Find the latest version if there are multiple
                matches = sorted(Path().glob(path_pattern), reverse=True)
                for path in matches:
                    signtool = path / 'signtool.exe'
                    if signtool.exists():
                        return signtool
            except Exception as e:
                continue
        
        return None

def setup_code_signing():
    """Set up code signing environment."""
    print("Setting up code signing environment...")
    
    # Create a sample configuration file if it doesn't exist
    config_path = Path('code_signing.json')
    if not config_path.exists():
        config = {
            "code_signing": {
                "windows": {
                    "cert_path": "path/to/certificate.pfx",
                    "cert_password": "your_password",
                    "timestamp_url": "http://timestamp.digicert.com"
                },
                "darwin": {
                    "identity": "Developer ID Application: Your Name (TEAMID)",
                    "keychain": "path/to/keychain"
                },
                "linux": {
                    "gpg_key": "your-gpg-key-id"
                }
            },
            "author": "Nsfr750",
            "email": "nsfr750@yandex.com",
            "version": "1.6.0"
        }
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"Created sample configuration at {config_path}")
        print("Please update it with your signing information.")
    else:
        print(f"Configuration file exists at {config_path}")
    
    print("\nCode signing setup complete!")
    print("Make sure to set up the following environment variables for CI/CD:")
    print("  - Windows: WINDOWS_SIGNING_CERT_PATH, WINDOWS_SIGNING_CERT_PASSWORD")
    print("  - macOS: MACOS_SIGNING_IDENTITY, MACOS_KEYCHAIN_PATH, MACOS_KEYCHAIN_PASSWORD")
    print("  - Linux: GPG_SIGNING_KEY, GPG_PASSPHRASE")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Code signing utility for Images-Deduplicator')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Set up code signing environment')
    
    # Sign command
    sign_parser = subparsers.add_parser('sign', help='Sign a file')
    sign_parser.add_argument('file', help='File to sign')
    sign_parser.add_argument('--config', default='code_signing.json', 
                           help='Path to configuration file')
    
    args = parser.parse_args()
    
    if args.command == 'setup':
        setup_code_signing()
    elif args.command == 'sign':
        if not Path(args.config).exists():
            print(f"Error: Configuration file not found: {args.config}")
            print("Run 'python scripts/code_signing.py setup' to create a configuration file.")
            sys.exit(1)
        
        with open(args.config) as f:
            config = json.load(f)
        
        signer = CodeSigner(config)
        if not signer.sign(Path(args.file)):
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)
