# Contributing to USB Power Delivery PDF Parser

## Development Setup

1. **Clone and Setup**
```bash
git clone https://github.com/usbpdparser/usb-pd-parser.git
cd usb-pd-parser
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .[dev]
```

2. **Install Pre-commit Hooks**
```bash
pre-commit install
```

## Code Quality Standards

### Formatting and Linting
- **Black**: Line length 79 characters
- **Ruff**: Comprehensive linting with security checks
- **MyPy**: Strict type checking required

### Testing Requirements
- **Unit Tests**: All new code must have tests
- **Security Tests**: Path traversal and input validation
- **Performance Tests**: Benchmark critical operations
- **Coverage**: Minimum 90% code coverage

### Security Guidelines
- All file operations must use `SecurePathValidator`
- Input validation required for all user-provided data
- No hardcoded credentials or sensitive data
- Thread-safe operations for concurrent code

## Architecture Principles

### SOLID Principles
- **Single Responsibility**: Each class has one clear purpose
- **Open/Closed**: Extensible without modification
- **Liskov Substitution**: Perfect interface compliance
- **Interface Segregation**: Focused, specific interfaces
- **Dependency Inversion**: Abstractions over concretions

### Design Patterns
Current implementation includes 7 design patterns:
1. Strategy Pattern (processing strategies)
2. Observer Pattern (progress tracking)
3. Factory Pattern (processor creation)
4. Builder Pattern (configuration building)
5. Singleton Pattern (configuration management)
6. Template Method Pattern (processing workflow)
7. State Pattern (processing state management)

## Pull Request Process

1. **Branch Naming**: `feature/description` or `fix/description`
2. **Commit Messages**: Follow conventional commits format
3. **Tests**: All tests must pass in CI
4. **Documentation**: Update relevant documentation
5. **Performance**: Run benchmarks for performance-critical changes

### PR Checklist
- [ ] Code follows style guidelines (black, ruff, mypy)
- [ ] Tests added for new functionality
- [ ] Security considerations addressed
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] Performance impact assessed

## Running Tests

```bash
# All tests
pytest tests/ -v

# Security tests only
pytest tests/test_security.py -v

# With coverage
pytest tests/ --cov=. --cov-report=html

# Performance benchmarks
python benchmarks/performance_benchmark.py
```

## Code Review Guidelines

### What We Look For
- **Security**: Path traversal protection, input validation
- **Performance**: Efficient algorithms, proper caching
- **Maintainability**: Clear code structure, good naming
- **Testing**: Comprehensive test coverage
- **Documentation**: Clear docstrings and comments

### Common Issues
- Missing input validation
- Inefficient file operations
- Poor error handling
- Missing type hints
- Inadequate test coverage

## Release Process

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create release PR
4. Tag release after merge
5. GitHub Actions handles publishing

## Getting Help

- **Issues**: Use GitHub issues for bugs and feature requests
- **Discussions**: Use GitHub discussions for questions
- **Security**: Email security@usbpdparser.com for vulnerabilities

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation