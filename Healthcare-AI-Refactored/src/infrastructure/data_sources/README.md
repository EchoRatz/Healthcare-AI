# Data Sources

This directory contains all the data sources used by the Healthcare AI system.

## Structure

```
data_sources/
├── results_doc/
│   └── direct_extraction_corrected.txt
├── results_doc2/
│   └── direct_extraction_corrected.txt
├── results_doc3/
│   └── direct_extraction_corrected.txt
└── hospital_micro_facts/
    └── hospital_micro_facts.txt
```

## Data Sources Description

### results_doc, results_doc2, results_doc3
- **Content**: Healthcare policy and coverage information
- **Format**: Text files with extracted healthcare data
- **Size**: ~34KB, ~45KB, ~221KB respectively
- **Purpose**: Primary knowledge base for healthcare questions

### hospital_micro_facts
- **Content**: Hospital-specific micro facts and department information
- **Format**: Structured text with department facts, service information
- **Size**: ~15KB
- **Purpose**: Hospital-specific knowledge for detailed healthcare queries

## Integration

The data sources are automatically loaded and indexed by the `DataSourceManager` class when the system starts. Each source is:

1. Loaded as a `Document` entity
2. Indexed in the vector store for semantic search
3. Stored in the document repository for retrieval

## Adding New Data Sources

To add a new data source:

1. Create a new directory under `data_sources/`
2. Add your data file(s)
3. Update the `DataSourceManager.sources` dictionary in `DataSourceManager.py`
4. The system will automatically detect and load the new source

## Testing

Run the test script to verify data source integration:

```bash
python test_data_sources.py
```

This will show:
- Available data sources
- File sizes and status
- Sample content from each source
- Integration verification 