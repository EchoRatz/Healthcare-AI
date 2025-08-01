# API Documentation

## Core Use Cases

### ProcessSingleQuestion
Process a single healthcare question.

```python
from core.use_cases.ProcessSingleQuestion import ProcessSingleQuestion

processor = ProcessSingleQuestion(answer_service)
result = processor.execute(question)
```

### ProcessCsvBatch
Process multiple questions from CSV file.

```python
from core.use_cases.ProcessCsvBatch import ProcessCsvBatch

processor = ProcessCsvBatch(question_repo, answer_service)
result = processor.execute(input_file, output_file, batch_size=10)
```

## Services

### Answer Services
- `SimpleAnswerService`: Rule-based answering
- `OllamaAnswerService`: AI-powered answering

### Repositories
- `CsvQuestionRepository`: CSV file operations
- `JsonCacheRepository`: JSON-based caching
- `RedisCacheRepository`: Redis-based caching