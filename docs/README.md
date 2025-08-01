# Healthcare-AI - Clean Architecture

A modular Thai RAG (Retrieval-Augmented Generation) system with clean, maintainable code.

## Features

- **Small, focused classes** - Each class has one responsibility
- **Clean architecture** - Easy to understand and maintain
- **Thai language support** - Optimized for Thai text processing
- **Modular design** - Easy to extend and test
- **Simple setup** - Get started in minutes

## Architecture

```
src/
├── database/          # Vector storage & search
│   ├── vector_store.py      # FAISS operations
│   ├── text_processor.py    # Text processing
│   └── search_engine.py     # Search coordination
├── llm/               # LLM clients
│   ├── base_client.py       # Abstract interface
│   └── mock_client.py       # Testing mock
├── rag/               # RAG pipeline
│   └── rag_pipeline.py      # Orchestration
└── utils/             # Utilities
    ├── logger.py            # Logging
    ├── file_handler.py      # File operations
    └── validators.py        # Input validation
```

## Quick Start

### 1. Setup
```bash
python scripts/setup.py
```

### 2. Run
```bash
python scripts/run.py
```

### 3. Ask Questions
```
Question: What is learning?
Answer: Learning is an important process for self-development...
```

## Project Structure

- **src/** - Main source code (small, focused modules)
- **config/** - Configuration and settings
- **scripts/** - Entry point scripts
- **data/** - Sample data and storage
- **docs/** - Documentation
- **tests/** - Test modules

## Design Principles

1. **Single Responsibility** - Each class does one thing well
2. **Small Classes** - Easy to understand and debug
3. **Clear Dependencies** - Explicit, testable dependencies
4. **Separation of Concerns** - Database, LLM, and RAG logic separated

## Benefits

- Easy to understand - Small, focused classes  
- Easy to test - Each module independent  
- Easy to extend - Add new components easily  
- Easy to maintain - Clear separation of concerns  
- Easy to debug - Isolated components  

This architecture makes the codebase much more maintainable and developer-friendly!
