# Word Formatter Test Suite

Comprehensive test suite for the Word Formatter system that converts documents to properly formatted Word files using AI-enhanced text analysis.

## Overview

This test suite provides comprehensive coverage of the Word Formatter system, including:

- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end workflow testing  
- **Performance Tests**: Large file and scalability testing
- **Edge Case Tests**: Error handling and boundary conditions
- **Claude AI Integration Tests**: AI text analysis functionality

## Test Structure

```
tests/
├── conftest.py              # Pytest configuration and shared fixtures
├── pytest.ini              # Pytest settings and markers
├── test_runner.py           # Comprehensive test runner
├── test_performance.py      # Performance and scalability tests
├── test_edge_cases.py       # Edge cases and error conditions
├── unit/                    # Unit tests
│   ├── test_document_converter.py     # Core converter tests
│   ├── test_document_converter_ai.py  # AI converter tests
│   └── test_document_converter_simple.py  # Simple converter tests
├── integration/             # Integration tests
│   └── test_full_pipeline.py          # End-to-end workflow tests
├── fixtures/                # Test data and samples
│   ├── test_documents.py               # Document generators
│   └── sample_docs/                    # Sample test files
└── utils/                   # Testing utilities
    └── mock_helpers.py                 # Mock objects and helpers
```

## Running Tests

### Quick Start

For rapid feedback during development:

```bash
# Run essential tests (fastest)
python tests/test_runner.py --suite quick

# Run all tests without slow performance tests
python tests/test_runner.py --suite all

# Run all tests including performance tests
python tests/test_runner.py --suite all --include-slow
```

### Test Suites

Run specific test suites:

```bash
# Unit tests only
python tests/test_runner.py --suite unit

# Integration tests only  
python tests/test_runner.py --suite integration

# Performance tests only
python tests/test_runner.py --suite performance

# Edge case tests only
python tests/test_runner.py --suite edge

# Claude AI integration tests only
python tests/test_runner.py --suite claude

# Slow tests only (performance + large file tests)
python tests/test_runner.py --suite slow

# Coverage analysis
python tests/test_runner.py --suite coverage
```

### Direct Pytest Usage

You can also run pytest directly:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_document_converter.py

# Run tests with specific markers
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m claude        # Claude AI tests only
pytest -m performance   # Performance tests only
pytest -m slow          # Slow tests only

# Run tests with coverage
pytest --cov=document_converter --cov=document_converter_ai --cov-report=html

# Stop on first failure
pytest -x

# Run specific test by name
pytest -k "test_style_extraction"
```

## Test Categories

### Unit Tests (`-m unit`)

Test individual components in isolation:
- **StyleExtractor**: Reference document style extraction
- **DocumentConverter**: Core conversion logic  
- **AIDocumentConverter**: AI-enhanced conversion
- **Simple converter**: Fallback conversion logic

### Integration Tests (`-m integration`)

Test complete workflows:
- Text to Word conversion pipeline
- Markdown to Word conversion
- RTF file processing
- AI-enhanced conversion with chunking
- Error recovery and fallback mechanisms
- Shell script integration

### Performance Tests (`-m performance`)

Test system performance and scalability:
- Large file processing (500KB+)
- Memory usage optimization
- Concurrent processing
- Chunking efficiency
- Progressive scaling analysis

### Edge Case Tests

Test boundary conditions and error handling:
- Empty files and minimal content
- Unicode and international text
- Malformed input files
- Special characters and symbols
- File system edge cases
- Extremely long content

### Claude AI Tests (`-m claude`)

Test AI integration functionality:
- Claude CLI interaction
- Text analysis and structuring
- Non-English text italicization
- Chunking for large files
- Timeout and error handling
- Fallback mechanisms

## Test Configuration

### Environment Variables

Control test behavior with environment variables:

```bash
# Enable debug logging during tests
export WORD_FORMATTER_DEBUG=1

# Disable notifications during testing (recommended)
export ENABLE_NOTIFICATIONS=0

# Set custom Claude model for testing
export CLAUDE_MODEL=haiku

# Set custom timeout for Claude calls
export CLAUDE_TIMEOUT=300

# Disable markdown saving during tests
export SAVE_MARKDOWN=0
```

### Pytest Markers

Available test markers:

- `unit`: Unit tests
- `integration`: Integration tests
- `performance`: Performance tests
- `slow`: Tests that take >10 seconds
- `claude`: Tests requiring Claude AI
- `network`: Tests requiring network (mocked by default)

### Coverage Configuration

The test suite includes comprehensive coverage analysis:

- **Target Coverage**: 80% minimum
- **Coverage Reports**: Terminal + HTML
- **Excluded Files**: Test files, fixtures
- **HTML Report Location**: `tests/coverage_html/index.html`

## Test Data and Fixtures

### Shared Fixtures (conftest.py)

- **reference_doc_path**: Test reference document
- **temp_dir**: Temporary directory for test files
- **sample_text_file**: Basic text file for testing
- **sample_markdown_file**: Markdown file with various elements
- **sample_rtf_file**: RTF file for format testing
- **large_text_file**: Large file for performance testing
- **sanskrit_text_file**: Non-English text for AI testing

### Mock Objects

Comprehensive mocking for external dependencies:

- **Claude CLI**: Success, error, timeout scenarios
- **Notifications**: System notification mocking
- **File System**: File I/O mocking for edge cases
- **Subprocess**: External command mocking

### Sample Documents

The test suite includes various document types:

- Simple text documents
- Complex structured documents
- Markdown with tables and formatting
- RTF files
- Large documents for performance testing
- Unicode and international text
- Malformed content for error testing

## Writing New Tests

### Test Structure (AAA Pattern)

Follow the Arrange-Act-Assert pattern:

```python
def test_example_functionality():
    # Arrange - Set up test data and conditions
    converter = DocumentConverter(reference_doc_path)
    test_file = create_test_file("sample content")
    
    # Act - Execute the function being tested
    result = converter.convert(test_file, output_path)
    
    # Assert - Verify the expected outcome
    assert result is True
    assert output_path.exists()
```

### Test Naming

Use descriptive test names:

```python
def test_<function>_<scenario>_<expected_result>():
    """Test description explaining what this test validates."""
```

### Using Fixtures

Leverage shared fixtures for consistency:

```python
def test_conversion(reference_doc_path, sample_text_file, temp_dir):
    converter = DocumentConverter(str(reference_doc_path))
    output_path = temp_dir / "output.docx"
    # ... test implementation
```

### Mocking External Dependencies

Use provided mock helpers:

```python
def test_ai_processing(mock_claude_success, mock_notifications):
    converter = AIDocumentConverter(reference_path)
    # Claude and notifications are automatically mocked
    result = converter.convert_with_ai(input_file)
```

### Test Categories

Mark tests appropriately:

```python
@pytest.mark.unit
def test_unit_functionality():
    """Unit test for individual component."""
    pass

@pytest.mark.integration
def test_full_workflow():
    """Integration test for complete workflow."""
    pass

@pytest.mark.performance
@pytest.mark.slow
def test_large_file_processing():
    """Performance test for large files."""
    pass
```

## Continuous Integration

The test suite is designed for CI/CD integration:

### Quick Feedback Loop
```bash
# Fast tests for pull request validation
python tests/test_runner.py --suite quick
```

### Complete Validation
```bash
# Full test suite for main branch
python tests/test_runner.py --suite all --include-slow
```

### Coverage Requirements
- Minimum 80% code coverage
- All new features must include tests
- Critical paths require 100% coverage

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure project root is in Python path
2. **File Not Found**: Check that reference documents exist
3. **Timeout Errors**: Increase Claude timeout for slow systems
4. **Permission Errors**: Ensure test directories are writable
5. **Mock Issues**: Verify mock helpers are properly imported

### Debug Mode

Enable debug mode for detailed test output:

```bash
export WORD_FORMATTER_DEBUG=1
pytest -v -s tests/
```

### Test Environment Validation

Validate test setup:

```bash
python tests/test_runner.py --validate-only
```

## Contributing

When adding new functionality:

1. Write tests first (TDD approach)
2. Include unit and integration tests
3. Add performance tests for new features affecting large files
4. Test edge cases and error conditions
5. Update test documentation
6. Ensure coverage requirements are met

## Dependencies

Test-specific dependencies:

```
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-timeout>=2.1.0
psutil>=5.8.0        # For memory usage tests
python-docx>=0.8.11  # Document processing
beautifulsoup4>=4.9.0 # HTML parsing
striprtf>=0.0.20     # RTF processing
```

Install test dependencies:

```bash
pip install -r requirements.txt
pip install pytest pytest-cov pytest-timeout psutil
```