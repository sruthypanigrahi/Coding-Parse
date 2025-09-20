# Architecture Documentation

## Design Patterns

### Strategy Pattern
- **Location**: `patterns/strategy.py`
- **Purpose**: Different processing strategies (parallel/sequential)
- **Implementation**: `ProcessingStrategy` interface with concrete implementations

### Observer Pattern  
- **Location**: `patterns/observer.py`
- **Purpose**: Progress tracking and notifications
- **Implementation**: `Subject` and `Observer` classes with event notifications

### Factory Pattern
- **Location**: `factories/`
- **Purpose**: Create processors and services
- **Implementation**: Abstract factories with concrete implementations

### Builder Pattern
- **Location**: `core/builders.py`
- **Purpose**: Complex pipeline construction
- **Implementation**: `ProcessingBuilder` with fluent interface

### Singleton Pattern
- **Location**: `patterns/singleton.py`
- **Purpose**: Configuration management
- **Implementation**: Thread-safe singleton metaclass

## SOLID Principles

### Single Responsibility
Each class has one clear purpose:
- `PDFProcessor` - PDF file operations
- `TOCParser` - Table of contents parsing
- `ContentExtractor` - Content extraction
- `FileExporter` - File export operations

### Open/Closed
Classes are open for extension, closed for modification:
- Strategy pattern allows new processing strategies
- Factory pattern allows new processor types
- Observer pattern allows new notification handlers

### Liskov Substitution
All implementations are substitutable:
- All processors implement `Processable` interface
- All exporters implement `Exportable` interface
- All strategies implement `ProcessingStrategy` interface

### Interface Segregation
Focused, specific interfaces:
- `Parseable` - Only parsing methods
- `Extractable` - Only extraction methods
- `Exportable` - Only export methods

### Dependency Inversion
Depends on abstractions, not concretions:
- Services depend on interfaces, not concrete classes
- Factory pattern provides dependency injection
- Configuration through interfaces