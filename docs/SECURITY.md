# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 2.2.x   | :white_check_mark: |
| < 2.2   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in Image Deduplicator, please follow these steps:

1. **Do not** create a public GitHub issue

2. Email the security team at [Nsfr750](mailto:nsfr750@yandex.com) with:
   - A clear description of the vulnerability
   - Steps to reproduce the issue
   - Any relevant logs or screenshots
   - Your contact information

We will respond to your report within 48 hours and keep you updated on our progress.

## Security Considerations

### Data Protection

- Image hashes are stored locally in the cache directory
- No image data is transmitted over the network
- Temporary files are securely deleted after processing

### File Operations

- All file operations are performed with appropriate permissions
- File deletions can be undone using the built-in undo functionality
- Users are prompted for confirmation before performing destructive actions

### Dependencies

- All third-party dependencies are regularly updated
- Dependencies are verified for known vulnerabilities

## Best Practices

1. **Keep the Application Updated**

   - Always use the latest version of Image Deduplicator
   - Regularly check for updates

2. **File Permissions**

   - Run the application with the minimum required permissions
   - Be cautious when granting write access to system directories

3. **Data Backup**

   - Always maintain backups of important files
   - Consider using the "Preview" feature before deleting duplicates

## Security Features

- **Progress Saving**: Progress is saved securely and can be resumed

- **Undo Functionality**: Accidental deletions can be undone

- **Memory Safety**: Safe memory management for large image collections

## Known Issues

For a list of known security issues, please check our [GitHub Security Advisories](https://github.com/Nsfr750/Images-Deduplicator/security/advisories).
