# GAFreqTrade Testing Framework

## Overview

This directory contains comprehensive tests for the GAFreqTrade genetic algorithm trading system.

## Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Shared fixtures and pytest configuration
├── unit/                    # Unit tests for individual modules
│   ├── test_strategy_generator.py
│   ├── test_genetic_ops.py
│   ├── test_population.py
│   ├── test_fitness.py
│   └── test_backtester.py
└── integration/             # Integration tests for workflows
    └── test_evolution.py
```

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test Categories
```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Run tests with specific markers
pytest -m unit
pytest -m integration
pytest -m mock
```

### Run Specific Test Files
```bash
pytest tests/unit/test_strategy_generator.py
pytest tests/unit/test_genetic_ops.py
pytest tests/unit/test_population.py
```

### Run with Coverage Report
```bash
pytest --cov=ga_core --cov=evaluation --cov-report=html
```

### Run in Verbose Mode
```bash
pytest -v
```

### Run Fast Tests Only (Skip Slow Tests)
```bash
pytest -m "not slow"
```

## Test Categories

### Unit Tests
- **test_strategy_generator.py**: Tests for random strategy generation
  - Indicator library
  - Condition generation
  - Strategy file creation
  - Code validity

- **test_genetic_ops.py**: Tests for genetic operations
  - Mutation (parameters, indicators, conditions)
  - Crossover (single-point, uniform, indicator swap)
  - Selection (tournament, roulette, rank, elite)

- **test_population.py**: Tests for population management
  - Population initialization
  - Strategy management
  - Evolution mechanics
  - Checkpointing

- **test_fitness.py**: Tests for fitness calculation
  - Fitness components
  - Normalization
  - Penalties
  - Multi-objective optimization

- **test_backtester.py**: Tests for backtesting integration
  - Backtest execution
  - Result parsing
  - Mock mode
  - Batch operations

### Integration Tests
- **test_evolution.py**: End-to-end evolution workflow tests
  - Single/multi-generation evolution
  - Elite preservation
  - Checkpointing workflow
  - Complete evolution cycles

## Fixtures

Common test fixtures are defined in `conftest.py`:

- `temp_dir`: Temporary directory for test files
- `mock_strategy_metadata`: Sample strategy metadata
- `mock_backtest_metrics`: Sample backtest results
- `mock_population_data`: Sample population with 5 strategies
- `mock_fitness_scores`: Sample fitness scores
- `sample_freqtrade_output`: Sample Freqtrade output text
- `config_dict`: Sample configuration dictionary

## Test Markers

Tests are marked with the following pytest markers:

- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.slow`: Tests that take longer to run
- `@pytest.mark.mock`: Tests using mock data instead of real backtests

## Writing New Tests

### Basic Test Template
```python
import pytest
from module_name import ClassName

class TestFeature:
    """Tests for specific feature."""
    
    def test_basic_functionality(self):
        """Test basic use case."""
        # Arrange
        obj = ClassName()
        
        # Act
        result = obj.method()
        
        # Assert
        assert result is not None
```

### Using Fixtures
```python
def test_with_fixture(temp_dir, mock_strategy_metadata):
    """Test using fixtures."""
    # temp_dir and mock_strategy_metadata are automatically provided
    strategy = mock_strategy_metadata
    assert strategy['strategy_id'] is not None
```

### Mocking External Dependencies
```python
from unittest.mock import Mock, patch

def test_with_mock():
    """Test with mocked dependencies."""
    with patch('module.external_call') as mock_call:
        mock_call.return_value = {'result': 'success'}
        # Test code here
```

## Coverage Goals

Target coverage for each module:
- **ga_core**: > 80%
- **evaluation**: > 75%
- **orchestration**: > 70%
- **storage**: > 75%
- **utils**: > 80%

Check current coverage:
```bash
pytest --cov --cov-report=term-missing
```

## Continuous Integration

These tests are designed to run in CI/CD pipelines:
```bash
# Quick check (unit tests only, no slow tests)
pytest tests/unit/ -m "not slow"

# Full test suite
pytest --cov --cov-report=xml
```

## Troubleshooting

### Tests Failing Due to Missing Dependencies
```bash
pip install -r requirements.txt
```

### Tests Failing Due to Import Errors
Make sure the project root is in PYTHONPATH:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest
```

### Cleanup After Failed Tests
```bash
# Remove temporary test files
rm -rf /tmp/test_*
rm -rf htmlcov/
rm -rf .pytest_cache/
```

## Best Practices

1. **Keep tests isolated**: Each test should be independent
2. **Use fixtures**: Leverage pytest fixtures for common setup
3. **Mock external calls**: Don't rely on external services
4. **Test edge cases**: Include tests for boundary conditions
5. **Name tests clearly**: Use descriptive test names
6. **Keep tests fast**: Use mocks to avoid slow operations
7. **Document complex tests**: Add comments for non-obvious test logic

## Future Enhancements

- [ ] Add performance benchmarking tests
- [ ] Add stress tests for large populations
- [ ] Add tests for storage/database operations
- [ ] Add tests for monitoring tools
- [ ] Add property-based tests with Hypothesis
- [ ] Add mutation testing with mutmut
