"""
Pytest configuration and shared fixtures for GAFreqTrade tests.
"""
import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List

import pytest

# Add parent directory to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    # Cleanup after test
    if os.path.exists(temp_path):
        shutil.rmtree(temp_path)


@pytest.fixture
def mock_strategy_metadata():
    """Generate mock strategy metadata for testing."""
    return {
        'strategy_id': 'Gen000_Strat_001',
        'class_name': 'Strategy_Gen000_Strat_001',
        'generation': 0,
        'strategy_num': 1,
        'indicators': ['rsi', 'macd', 'ema'],  # String list, not dicts
        'buy_conditions': [
            "(dataframe['rsi'] < buy_rsi_threshold)",
            "(dataframe['macd'] > dataframe['macdsignal'])"
        ],
        'sell_conditions': [
            "(dataframe['rsi'] > sell_rsi_threshold)",
            "(dataframe['macd'] < dataframe['macdsignal'])"
        ],
        'num_buy_conditions': 2,
        'num_sell_conditions': 2,
        'timeframe': '5m',
        'stoploss': -0.10,
        'trailing_stop': True,
        'trailing_stop_positive': 0.01,
        'trailing_stop_positive_offset': 0.02,
        'trailing_only_offset_is_reached': True,
        'hyperopt_params': ['buy_rsi_threshold', 'sell_rsi_threshold'],  # String list
        'file_path': '/tmp/strategies/Strategy_Gen000_Strat_001.py',
        'created_at': '2024-01-01T00:00:00'
    }


@pytest.fixture
def mock_backtest_metrics():
    """Generate mock backtest metrics for testing."""
    return {
        'total_profit_pct': 15.5,
        'total_profit_abs': 155.0,
        'trades_count': 120,
        'wins': 72,
        'losses': 48,
        'win_rate': 60.0,
        'avg_profit_pct': 0.129,
        'avg_loss_pct': -0.086,
        'sharpe_ratio': 1.8,
        'sortino_ratio': 2.1,
        'calmar_ratio': 1.5,
        'max_drawdown_pct': -12.3,
        'max_drawdown_abs': -123.0,
        'profit_factor': 1.6,
        'expectancy': 0.043,
        'starting_balance': 1000.0,
        'final_balance': 1155.0
    }


@pytest.fixture
def mock_population_data():
    """Generate mock population data with multiple strategies."""
    strategies = []
    for i in range(5):
        strategies.append({
            'strategy_id': f'Gen000_Strat_{i+1:03d}',
            'class_name': f'Strategy_Gen000_Strat_{i+1:03d}',
            'generation': 0,
            'strategy_num': i + 1,
            'indicators': ['rsi', 'macd'],  # String list
            'buy_conditions': ["(dataframe['rsi'] < 30)"],
            'sell_conditions': ["(dataframe['rsi'] > 70)"],
            'num_buy_conditions': 1,
            'num_sell_conditions': 1,
            'timeframe': '5m',
            'stoploss': -0.10,
            'trailing_stop': True,
            'hyperopt_params': [],  # String list
            'file_path': f'/tmp/strategies/Strategy_Gen000_Strat_{i+1:03d}.py',
            'created_at': '2024-01-01T00:00:00'
        })
    return strategies


@pytest.fixture
def mock_fitness_scores():
    """Generate mock fitness scores for testing."""
    return {
        'Gen000_Strat_001': 0.85,
        'Gen000_Strat_002': 0.72,
        'Gen000_Strat_003': 0.91,
        'Gen000_Strat_004': 0.68,
        'Gen000_Strat_005': 0.79
    }


@pytest.fixture
def sample_freqtrade_output():
    """Sample Freqtrade backtest output for parsing tests."""
    return """
==================== BACKTESTING REPORT ============================
|     Pair |   Buys |   Avg Profit % |   Cum Profit % |   Tot Profit USDT |   Tot Profit % |   Avg Duration |   Win  Draw  Loss  Win% |
|----------+--------+----------------+----------------+-------------------+----------------+----------------+-------------------------|
| BTC/USDT |     45 |           0.32 |          14.40 |            144.00 |          14.40 |        2:15:00 |    27     0    18  60.0 |
| ETH/USDT |     38 |           0.28 |          10.64 |            106.40 |          10.64 |        2:30:00 |    23     0    15  60.5 |
|    TOTAL |     83 |           0.30 |          25.04 |            250.40 |          25.04 |        2:22:00 |    50     0    33  60.2 |

SUMMARY METRICS
=======================================
Backtesting from 2024-01-01 to 2024-03-31
Total/Daily Avg Trades                : 83 / 0.92
Starting balance                      : 1000.00 USDT
Final balance                         : 1250.40 USDT
Absolute profit                       : 250.40 USDT
Total profit %                        : 25.04%
Avg. stake amount                     : 100.00 USDT
Total trade volume                    : 8300.00 USDT
Best Pair                             : BTC/USDT 14.40%
Worst Pair                            : ETH/USDT 10.64%
Best Trade                            : 3.20% 
Worst Trade                           : -2.10%
Max Drawdown                          : -8.5%
Sharpe Ratio                          : 1.85
Sortino Ratio                         : 2.15
Calmar Ratio                          : 2.95
Profit Factor                         : 1.75
Expectancy                            : 0.301
"""


@pytest.fixture
def config_dict():
    """Sample configuration dictionary."""
    return {
        'ga': {
            'population_size': 50,
            'max_generations': 100,
            'mutation_rate': 0.15,
            'crossover_rate': 0.7,
            'elite_size': 5,
            'tournament_size': 3,
            'new_random_rate': 0.05
        },
        'strategy': {
            'min_indicators': 3,
            'max_indicators': 7,
            'min_buy_conditions': 1,
            'max_buy_conditions': 4,
            'min_sell_conditions': 1,
            'max_sell_conditions': 4
        },
        'evaluation': {
            'timerange': '20240101-20240331',
            'pairs': ['BTC/USDT', 'ETH/USDT'],
            'starting_balance': 1000,
            'stake_amount': 100,
            'max_open_trades': 3
        },
        'fitness_weights': {
            'profit': 0.30,
            'sharpe': 0.10,
            'drawdown': 0.25,
            'winrate': 0.15,
            'stability': 0.15,
            'trade_count': 0.05
        }
    }
