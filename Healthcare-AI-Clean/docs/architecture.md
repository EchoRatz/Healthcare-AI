# Healthcare AI - Clean Architecture

## Overview

This project implements a Thai Healthcare Q&A system using Clean Architecture principles.

## Architecture Layers

### Domain Layer (`src/domain/`)
- **Entities**: Core business objects (Question, Answer, CacheEntry, etc.)
- **Repositories**: Data access interfaces
- **Services**: Business logic interfaces

### Core Layer (`src/core/`)
- **Use Cases**: Application business rules
- **Services**: Application services and parsers

### Infrastructure Layer (`src/infrastructure/`)
- **Repositories**: Data access implementations
- **Services**: External service implementations
- **Config**: Configuration management

### Presentation Layer (`scripts/`)
- **CLI**: Command-line interfaces
- **Entry Points**: Application entry points

## Dependency Flow

```
Scripts → Core → Domain ← Infrastructure
```

## Key Features

1. **Clean Architecture**: Separation of concerns with clear boundaries
2. **Thai Language Support**: Specialized parsing for Thai questions
3. **Multiple Answer Services**: Rule-based and AI-powered options
4. **Caching System**: Knowledge extraction and storage
5. **Batch Processing**: Efficient CSV processing
6. **Extensible Design**: Easy to add new services and features