# Developer Guide

## Architecture Overview

The USB Power Delivery PDF Parser follows a clean architecture with perfect separation of concerns:

### Core Components

- **Parser**: PDF processing and TOC extraction
- **Validator**: Input validation and security checks  
- **Exporter**: JSONL and Excel report generation
- **Search**: Content indexing and query processing

### Design Patterns Implemented

1. **Strategy Pattern** - Processing strategies (parallel/sequential)
2. **Observer Pattern** - Progress tracking with notifications
3. **Factory Pattern** - Component creation and dependency injection
4. **Builder Pattern** - Complex configuration building
5. **Singleton Pattern** - Configuration management
6. **Template Method** - Document processing workflow
7. **State Pattern** - Processing state management

## Development Setup

```bash
# Clone and setup
git clone <repository>
cd coding-parse

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Code formatting
black --line-length=79 .
isort --profile=black --line-length=79 .

# Linting
flake8 . --max-line-length=79
```

## Testing

### Schema Validation
```bash
pytest tests/test_jsonl_schema.py -v
```

### Parsing Correctness
```bash
pytest tests/test_parsing.py -v
```

### Validation Logic
```bash
pytest tests/test_validation.py -v
```

## Code Quality Standards

- **Line Length**: Maximum 79 characters
- **Type Hints**: Required for all functions
- **Docstrings**: Required for all public methods
- **Error Handling**: Specific exceptions with proper logging
- **Security**: Path traversal protection, XSS prevention

## Performance Optimization

- **Parallel Processing**: Multi-threaded content extraction
- **Memory Efficiency**: Generator-based batch processing
- **Caching**: LRU cache for repeated operations
- **String Operations**: Join instead of concatenation

## Security Considerations

- **Path Validation**: All file operations protected
- **Input Sanitization**: HTML escaping for outputs
- **Thread Safety**: Proper locking for shared resources
- **Error Sanitization**: No sensitive data in logs