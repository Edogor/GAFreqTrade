"""
Backtester Module for GAFreqTrade

This module provides a wrapper around Freqtrade's backtesting functionality
to evaluate generated strategies.
"""

import subprocess
import json
import os
import time
from typing import Dict, Optional, List
from datetime import datetime
import logging


# Use utils logger if available
try:
    from utils.logger import get_logger
    logger = get_logger()
except (ImportError, ModuleNotFoundError):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class BacktestResult:
    """Container for backtest results"""
    
    def __init__(self, strategy_name: str, raw_results: Dict):
        self.strategy_name = strategy_name
        self.raw_results = raw_results
        self.metrics = self._parse_metrics(raw_results)
    
    def _parse_metrics(self, results: Dict) -> Dict:
        """Extract key metrics from backtest results"""
        if not results:
            return self._default_metrics()
        
        try:
            # Freqtrade backtest results structure
            strategy_results = results.get('strategy', {})
            
            # Extract main metrics
            metrics = {
                'total_profit_pct': float(strategy_results.get('profit_total', 0.0)),
                'total_profit_abs': float(strategy_results.get('profit_total_abs', 0.0)),
                'trades_count': int(strategy_results.get('total_trades', 0)),
                'wins': int(strategy_results.get('wins', 0)),
                'losses': int(strategy_results.get('losses', 0)),
                'draws': int(strategy_results.get('draws', 0)),
                'win_rate': float(strategy_results.get('winrate', 0.0)),
                'avg_profit': float(strategy_results.get('avg_profit', 0.0)),
                'avg_duration': float(strategy_results.get('avg_duration', 0.0)),
                'max_drawdown_pct': float(strategy_results.get('max_drawdown', 0.0)),
                'max_drawdown_abs': float(strategy_results.get('max_drawdown_abs', 0.0)),
                'sharpe_ratio': float(strategy_results.get('sharpe', 0.0)),
                'sortino_ratio': float(strategy_results.get('sortino', 0.0)),
                'calmar_ratio': float(strategy_results.get('calmar', 0.0)),
                'profit_factor': float(strategy_results.get('profit_factor', 0.0)),
                'expectancy': float(strategy_results.get('expectancy', 0.0)),
                'backtest_start': strategy_results.get('backtest_start', ''),
                'backtest_end': strategy_results.get('backtest_end', ''),
                'duration_days': strategy_results.get('backtest_days', 0),
            }
            
            return metrics
        except Exception as e:
            logger.error(f"Error parsing backtest metrics: {e}")
            return self._default_metrics()
    
    def _default_metrics(self) -> Dict:
        """Return default metrics (for failed backtests)"""
        return {
            'total_profit_pct': 0.0,
            'total_profit_abs': 0.0,
            'trades_count': 0,
            'wins': 0,
            'losses': 0,
            'draws': 0,
            'win_rate': 0.0,
            'avg_profit': 0.0,
            'avg_duration': 0.0,
            'max_drawdown_pct': 0.0,
            'max_drawdown_abs': 0.0,
            'sharpe_ratio': 0.0,
            'sortino_ratio': 0.0,
            'calmar_ratio': 0.0,
            'profit_factor': 0.0,
            'expectancy': 0.0,
            'backtest_start': '',
            'backtest_end': '',
            'duration_days': 0,
        }
    
    def get_metric(self, key: str, default=0.0):
        """Get a specific metric"""
        return self.metrics.get(key, default)
    
    def is_valid(self) -> bool:
        """Check if backtest produced valid results"""
        return self.metrics['trades_count'] > 0
    
    def __repr__(self):
        return (f"BacktestResult({self.strategy_name}: "
                f"Profit={self.metrics['total_profit_pct']:.2f}%, "
                f"Trades={self.metrics['trades_count']}, "
                f"WinRate={self.metrics['win_rate']:.2f}%)")


class Backtester:
    """
    Wrapper for Freqtrade backtesting
    
    This class handles running backtests on generated strategies and parsing results.
    """
    
    def __init__(self, 
                 freqtrade_path: str = "freqtrade",
                 config_path: str = "freqtrade/user_data/config.json",
                 data_dir: str = "freqtrade/user_data/data",
                 strategy_dir: str = "strategies/generated",
                 timeout: int = 300,
                 use_docker: bool = False,
                 docker_image: str = "freqtradeorg/freqtrade:stable",
                 docker_user_data_path: str = "./freqtrade/user_data"):
        """
        Initialize backtester
        
        Args:
            freqtrade_path: Path to freqtrade executable or directory
            config_path: Path to freqtrade config file
            data_dir: Path to data directory
            strategy_dir: Directory containing strategies
            timeout: Timeout in seconds for each backtest
            use_docker: Whether to use Docker to run Freqtrade
            docker_image: Docker image to use (if use_docker is True)
            docker_user_data_path: Local path to user_data directory for Docker volume mount
        """
        self.freqtrade_path = freqtrade_path
        self.config_path = config_path
        self.data_dir = data_dir
        self.strategy_dir = strategy_dir
        self.timeout = timeout
        self.use_docker = use_docker
        self.docker_image = docker_image
        self.docker_user_data_path = docker_user_data_path
        
        # Verify freqtrade is available
        self._verify_freqtrade()
    
    def _verify_freqtrade(self):
        """Verify that freqtrade is accessible"""
        try:
            # Try to run freqtrade version command
            cmd = self._build_freqtrade_command(['--version'])
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version_output = result.stdout.strip() if result.stdout else result.stderr.strip()
                logger.info(f"Freqtrade found: {version_output}")
            else:
                logger.warning("Freqtrade command returned non-zero exit code")
        except Exception as e:
            logger.warning(f"Could not verify freqtrade: {e}")
    
    def _build_freqtrade_command(self, args: List[str]) -> List[str]:
        """Build freqtrade command (supports both native and Docker execution)"""
        if self.use_docker:
            # Build Docker command
            cmd = [
                'docker', 'run', '--rm',
                '-v', f'{self.docker_user_data_path}:/freqtrade/user_data',
                self.docker_image
            ]
            cmd.extend(args)
            return cmd
        else:
            # Native execution
            cmd = ['freqtrade']
            cmd.extend(args)
            return cmd
    
    def run_backtest(self, 
                     strategy_name: str,
                     timerange: Optional[str] = None,
                     pairs: Optional[List[str]] = None,
                     starting_balance: float = 1000,
                     stake_amount: str = "unlimited",
                     max_open_trades: int = 3) -> BacktestResult:
        """
        Run backtest for a strategy
        
        Args:
            strategy_name: Name of the strategy class
            timerange: Time range for backtest (e.g., "20230101-20231231")
            pairs: List of trading pairs to test
            starting_balance: Starting balance for backtest
            stake_amount: Stake amount per trade
            max_open_trades: Maximum number of open trades
            
        Returns:
            BacktestResult object with metrics
        """
        logger.info(f"Running backtest for strategy: {strategy_name}")
        
        # Adjust paths for Docker if needed
        if self.use_docker:
            # Convert local paths to Docker container paths
            config_path = "user_data/config.json"
            data_dir = "user_data/data"
            strategy_dir = "user_data/strategies"
        else:
            config_path = self.config_path
            data_dir = self.data_dir
            strategy_dir = self.strategy_dir
        
        # Build backtest command
        cmd = self._build_freqtrade_command([
            'backtesting',
            '--strategy', strategy_name,
            '--config', config_path,
            '--datadir', data_dir,
            '--strategy-path', strategy_dir,
            '--export', 'none',  # Don't export trades to save space
            '--breakdown', 'day',  # Daily breakdown for better stats
        ])
        
        # Add optional parameters
        if timerange:
            cmd.extend(['--timerange', timerange])
        
        if pairs:
            cmd.extend(['--pairs'] + pairs)
        
        # Add trading parameters
        env = os.environ.copy()
        env['FREQTRADE_STARTING_BALANCE'] = str(starting_balance)
        env['FREQTRADE_STAKE_AMOUNT'] = stake_amount
        env['FREQTRADE_MAX_OPEN_TRADES'] = str(max_open_trades)
        
        # Run backtest
        start_time = time.time()
        try:
            # For Docker, we don't need to change working directory
            work_dir = None
            if not self.use_docker and os.path.isdir(self.freqtrade_path):
                work_dir = self.freqtrade_path
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                env=env,
                cwd=work_dir
            )
            
            duration = time.time() - start_time
            logger.info(f"Backtest completed in {duration:.2f}s")
            
            if result.returncode != 0:
                logger.error(f"Backtest failed with return code {result.returncode}")
                logger.error(f"Error output: {result.stderr}")
                return BacktestResult(strategy_name, {})
            
            # Parse results
            parsed_results = self._parse_backtest_output(result.stdout, result.stderr)
            return BacktestResult(strategy_name, parsed_results)
            
        except subprocess.TimeoutExpired:
            logger.error(f"Backtest timed out after {self.timeout}s")
            return BacktestResult(strategy_name, {})
        except Exception as e:
            logger.error(f"Error running backtest: {e}")
            return BacktestResult(strategy_name, {})
    
    def _parse_backtest_output(self, stdout: str, stderr: str) -> Dict:
        """
        Parse backtest output to extract results
        
        Freqtrade outputs results in various formats. This tries to parse them.
        """
        results = {}
        
        try:
            # Try to find JSON output in stdout
            lines = stdout.split('\n')
            for line in lines:
                if line.strip().startswith('{') and 'strategy' in line:
                    try:
                        results = json.loads(line)
                        break
                    except json.JSONDecodeError:
                        continue
            
            # If no JSON found, try to parse text output
            if not results:
                results = self._parse_text_output(stdout)
            
            return results
            
        except Exception as e:
            logger.error(f"Error parsing backtest output: {e}")
            return {}
    
    def _parse_text_output(self, output: str) -> Dict:
        """
        Parse text-based backtest output
        
        This is a fallback parser for when JSON output is not available.
        """
        results = {'strategy': {}}
        lines = output.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Extract key metrics from text output
            if 'Total profit' in line:
                try:
                    # Example: "Total profit:  5.23%"
                    profit = float(line.split(':')[1].strip().replace('%', ''))
                    results['strategy']['profit_total'] = profit
                except:
                    pass
            
            elif 'Total trades' in line:
                try:
                    trades = int(line.split(':')[1].strip())
                    results['strategy']['total_trades'] = trades
                except:
                    pass
            
            elif 'Win rate' in line or 'Winrate' in line:
                try:
                    winrate = float(line.split(':')[1].strip().replace('%', ''))
                    results['strategy']['winrate'] = winrate
                except:
                    pass
            
            elif 'Max drawdown' in line:
                try:
                    drawdown = float(line.split(':')[1].strip().replace('%', ''))
                    results['strategy']['max_drawdown'] = drawdown
                except:
                    pass
            
            elif 'Sharpe' in line:
                try:
                    sharpe = float(line.split(':')[1].strip())
                    results['strategy']['sharpe'] = sharpe
                except:
                    pass
        
        return results
    
    def run_batch_backtests(self, 
                          strategy_names: List[str],
                          parallel: bool = False,
                          max_workers: int = 4,
                          **backtest_kwargs) -> Dict[str, BacktestResult]:
        """
        Run backtests for multiple strategies
        
        Args:
            strategy_names: List of strategy names
            parallel: Whether to run in parallel (not yet implemented)
            max_workers: Max parallel workers
            **backtest_kwargs: Additional arguments for run_backtest
            
        Returns:
            Dictionary mapping strategy names to BacktestResults
        """
        results = {}
        
        if parallel:
            logger.warning("Parallel backtesting not yet implemented, running sequentially")
        
        for strategy_name in strategy_names:
            result = self.run_backtest(strategy_name, **backtest_kwargs)
            results[strategy_name] = result
        
        return results


if __name__ == "__main__":
    # Test backtester
    print("Testing Backtester...")
    
    backtester = Backtester(
        freqtrade_path="freqtrade",
        config_path="freqtrade/user_data/config.json",
        strategy_dir="ga_core/strategies/generated"
    )
    
    # Test with a generated strategy
    result = backtester.run_backtest(
        "Strategy_Gen000_Strat_001",
        timerange="20240101-20240131"
    )
    
    print(f"\nBacktest Result: {result}")
    print(f"Valid: {result.is_valid()}")
    print(f"Metrics: {result.metrics}")
