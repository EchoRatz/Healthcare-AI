# Healthcare AI - Clean Architecture

Thai Healthcare Q&A System with Clean Architecture principles.

## Features

- Clean Architecture implementation
- Thai language support
- Multiple answer services (Simple rule-based, AI-powered)
- Batch CSV processing
- Knowledge caching system
- Vector database support

## Quick Start

```bash
# Install dependencies
pip install -e .

# Setup environment
cp .env.example .env

# Run quick test
python scripts/quick_test.py

# Run batch processing
python scripts/batch_processor.py data/input/test.csv