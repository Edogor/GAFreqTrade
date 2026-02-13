# Changes - Fix Evolution No-Mock Issues

## Summary
Fixed multiple issues preventing the evolution from running properly with `--no-mock` flag and implemented strategy validation to filter out failed strategies.

## Issues Fixed

### 1. Backtester Initialization Error
**Problem:** When running evolution with `--no-mock`, the backtester was initialized with "freqtrade" as the path, but the command building logic would result in an empty command, causing `[Errno 2] No such file or directory: ''` errors.

**Solution:**
- Modified `_build_freqtrade_command()` in `evaluation/backtester.py` to always use 'freqtrade' as a command (assuming it's in PATH)
- Updated the subprocess call to properly handle working directory when freqtrade_path is a directory

**Files Changed:**
- `evaluation/backtester.py`

### 2. Configuration Loading Issues
**Problem:** The `eval_config.yaml` file was not being loaded properly, causing default values to be used instead of configured freqtrade paths and settings.

**Solution:**
- Added `_load_eval_config()` method to `EvolutionLoop` class to properly load evaluation configuration
- Fixed path resolution using Path objects instead of string concatenation
- Updated `EvolutionLoop.__init__()` to accept and use eval_config
- Modified `run_evolution.py` to load config as YAML dict instead of trying to use the complex tuple-returning load_config function
- Updated `run_evolution()` function signature to accept config dict directly

**Files Changed:**
- `orchestration/evolution_loop.py`
- `run_evolution.py`

### 3. Strategy Validation and Filtering
**Problem:** Strategies that failed during backtesting (errors or no trades) were not being filtered out, causing them to be included in the population with zero fitness.

**Solution:**
- Modified `evaluate_population()` to track failed strategies
- Added logic to remove failed strategies from population after evaluation when `ignore_invalid_strategies` is enabled
- Strategies that throw errors or produce no valid trades are marked for removal
- Added proper logging for strategy removal

**Files Changed:**
- `orchestration/evolution_loop.py`

## Configuration
The following configuration options are now properly respected from `eval_config.yaml`:

- `freqtrade_path`: Path to freqtrade installation (defaults to 'freqtrade' command)
- `freqtrade_config_path`: Path to freqtrade configuration file
- `strategy_path`: Directory where strategies are stored
- `datadir`: Directory where market data is stored
- `min_trades_required`: Minimum number of trades for a valid backtest
- `ignore_invalid_strategies`: Whether to filter out failed strategies (default: true)

## Testing
Added comprehensive tests to verify the strategy filtering functionality:

1. **test_filter_failed_strategies**: Verifies that failed strategies are properly filtered out when filtering is enabled
2. **test_no_filter_when_disabled**: Verifies that strategies are kept when filtering is disabled

**Files Changed:**
- `tests/integration/test_evolution.py`

## Usage
The evolution now works correctly with `--no-mock` flag:

```bash
# Run evolution with real backtesting
python3 run_evolution.py --no-mock --generations 20 --population 50

# Run with custom config
python3 run_evolution.py --no-mock --config config/ga_config.yaml

# Quick test with mock mode (default)
python3 run_evolution.py --generations 3 --population 10
```

## Benefits

1. **More Reliable Evolution**: Strategies that fail backtesting are automatically removed, preventing zero-fitness strategies from diluting the gene pool
2. **Better Configuration Management**: Proper loading of eval_config.yaml ensures consistent freqtrade settings
3. **Clearer Error Messages**: Better logging helps identify which strategies are failing and why
4. **Configurable Behavior**: Users can choose whether to filter failed strategies via configuration

## Backwards Compatibility
All changes are backwards compatible. The default behavior is:
- Mock mode is used when `--no-mock` is not specified
- Failed strategies are filtered out by default (can be disabled in eval_config.yaml)
- CLI arguments still override configuration file settings
