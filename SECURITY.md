# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Security Features

### Path Traversal Protection (CWE-22)
- **SecurePathValidator**: Centralized validation preventing `../` attacks
- **Filename Sanitization**: Removes dangerous characters and sequences
- **Path Resolution**: Validates all file operations against working directory

### Input Validation
- **PDF Validation**: Verifies file format and structure before processing
- **Query Sanitization**: Prevents injection attacks in search functionality
- **File Extension Validation**: Restricts processing to safe file types

### Error Handling
- **Information Disclosure Prevention**: Generic error messages to external users
- **Detailed Logging**: Comprehensive internal logging for debugging
- **Graceful Degradation**: Safe fallbacks for all error conditions

## Security Testing

Run security tests:
```bash
pytest tests/test_security.py -v
```

Test path traversal protection:
```bash
python -m pytest tests/test_security.py::test_path_traversal_prevention -v
```

## Reporting a Vulnerability

Please report security vulnerabilities to security@usbpdparser.com

- **Response Time**: 24 hours acknowledgment
- **Fix Timeline**: Critical issues patched within 7 days
- **Disclosure**: Coordinated disclosure after fix deployment

## Security Checklist

- [x] Path traversal protection (CWE-22)
- [x] Input validation and sanitization
- [x] Secure file operations
- [x] Error message sanitization
- [x] Resource management with context managers
- [x] Thread-safe operations
- [x] Dependency pinning for reproducible builds