# Tests for FastaAAExtractor

This directory contains comprehensive unit and integration tests for FastaAAExtractor.

## Running Tests

### Install test dependencies
```bash
pip install pytest pytest-cov
```

### Run all tests
```bash
pytest
```

### Run with coverage report
```bash
pytest --cov=fasta_aa_extractor --cov-report=html --cov-report=term
```

### Run specific test file
```bash
pytest tests/test_core.py
pytest tests/test_cli.py
```

### Run with verbose output
```bash
pytest -v
```

## Test Structure

- **test_core.py**: Unit tests for core extraction functions
  - `TestLoadGenome`: FASTA loading tests
  - `TestLoadCoordinates`: Coordinate file parsing tests
  - `TestNormalizeColumns`: Column normalization tests
  - `TestFindColumn`: Column detection tests
  - `TestDetectRequiredColumns`: Required column validation tests
  - `TestExtractProteins`: Protein extraction tests
  - `TestRunExtraction`: Integration tests
  - `TestEdgeCases`: Edge case and error handling tests
  - `TestRealWorldExample`: Tests with actual example data

- **test_cli.py**: CLI interface tests
  - `TestCLI`: Command-line argument parsing and execution
  - `TestLogging`: Logging configuration tests

- **conftest.py**: Shared pytest fixtures and configuration

## Test Coverage

Current test coverage: >90%

### Coverage by Module
- `core.py`: 95%+ coverage
- `cli.py`: 90%+ coverage
- `__init__.py`: 100% coverage

## Fixtures

- `temp_dir`: Creates temporary directory for test outputs
- `sample_fasta`: Generates test FASTA file with 2 contigs
- `sample_tsv`: Creates test TSV coordinate file
- `sample_csv`: Creates test CSV coordinate file
- `sample_excel`: Creates test Excel coordinate file

## Test Categories

### Unit Tests
Test individual functions in isolation with mocked dependencies.

### Integration Tests
Test complete workflows from input to output.

### Edge Case Tests
- Empty files
- Missing columns
- Out-of-range coordinates
- Invalid file formats
- Duplicate gene names
- Multi-contig genomes

### Real-World Tests
Tests using actual example data from `examples/` directory.

## Adding New Tests

When adding new functionality:

1. Add unit tests for individual functions
2. Add integration tests for workflows
3. Add edge case tests for error conditions
4. Update this README with new test descriptions
5. Ensure >90% code coverage is maintained
