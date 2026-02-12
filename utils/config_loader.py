"""
Configuration loader for GAFreqTrade.

Loads and validates YAML configuration files.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class GAConfig:
    """Genetic Algorithm configuration."""
    population_size: int = 100
    elite_size: int = 10
    generations: int = 1000
    initial_random: bool = True
    
    mutation_rate: float = 0.20
    mutation_strength: float = 0.15
    crossover_rate: float = 0.70
    new_random_rate: float = 0.10
    
    selection_method: str = "tournament"
    tournament_size: int = 5
    
    fitness_weights: Dict[str, float] = field(default_factory=lambda: {
        'profit': 0.30,
        'sharpe': 0.10,
        'drawdown': 0.25,
        'winrate': 0.15,
        'stability': 0.20,
        'trade_penalty': 0.05
    })
    
    min_indicators: int = 2
    max_indicators: int = 6
    min_conditions: int = 1
    max_conditions: int = 4
    
    parallel_backtests: int = 4
    backtest_timeout: int = 300
    checkpoint_interval: int = 10
    
    log_level: str = "INFO"
    log_to_file: bool = True
    log_file: str = "logs/evolution.log"
    
    maintain_diversity: bool = True
    diversity_threshold: float = 0.7
    early_stopping: bool = False
    early_stopping_patience: int = 50
    
    use_islands: bool = False
    num_islands: int = 3
    migration_interval: int = 20
    migration_size: int = 3


@dataclass
class EvalConfig:
    """Evaluation configuration."""
    backtest_period: str = "90d"
    timeframe: str = "5m"
    starting_balance: int = 1000
    fee: float = 0.001
    
    freqtrade_config_path: str = "freqtrade/user_data/config.json"
    strategy_path: str = "freqtrade/user_data/strategies"
    datadir: str = "freqtrade/user_data/data"
    max_open_trades: int = 3
    stake_amount: str = "unlimited"
    stake_currency: str = "USDT"
    dry_run: bool = True
    
    min_trades_required: int = 30
    max_drawdown_threshold: float = 0.50
    min_win_rate: float = 0.35
    min_profit: float = -0.10
    max_trade_duration: int = 3600
    
    max_position_size: float = 0.33
    max_drawdown_allowed: float = 0.40
    required_profit_factor: float = 1.1
    
    collect_detailed: bool = True
    save_trades: bool = False
    calculate_sharpe: bool = True
    calculate_sortino: bool = True
    calculate_calmar: bool = True
    
    backtest_only: bool = True
    dry_run_enabled: bool = False
    live_test_enabled: bool = False
    
    min_candles: int = 500
    prefetch_days: int = 100
    update_before_backtest: bool = False
    
    cache_results: bool = True
    cache_ttl: int = 3600
    use_cached_indicators: bool = True
    parallel_downloads: bool = True
    
    retry_on_failure: bool = True
    max_retries: int = 3
    retry_delay: int = 5
    ignore_invalid_strategies: bool = True
    log_errors: bool = True


class ConfigLoader:
    """Configuration loader and validator."""
    
    def __init__(self, base_dir: Optional[Path] = None):
        """
        Initialize config loader.
        
        Args:
            base_dir: Base directory for config files (defaults to current dir)
        """
        self.base_dir = base_dir or Path.cwd()
        self.config_dir = self.base_dir / "config"
        
    def load_yaml(self, file_path: str) -> Dict[str, Any]:
        """
        Load YAML file.
        
        Args:
            file_path: Path to YAML file
            
        Returns:
            Dictionary with configuration
            
        Raises:
            FileNotFoundError: If file doesn't exist
            yaml.YAMLError: If YAML is invalid
        """
        path = Path(file_path)
        if not path.is_absolute():
            path = self.config_dir / path
            
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")
        
        with open(path, 'r') as f:
            config = yaml.safe_load(f)
        
        return config or {}
    
    def load_ga_config(self, file_path: str = "ga_config.yaml") -> GAConfig:
        """
        Load genetic algorithm configuration.
        
        Args:
            file_path: Path to GA config file
            
        Returns:
            GAConfig instance
        """
        config_dict = self.load_yaml(file_path)
        
        # Create GAConfig with loaded values
        ga_config = GAConfig()
        
        # Update with loaded values
        for key, value in config_dict.items():
            if hasattr(ga_config, key):
                setattr(ga_config, key, value)
        
        # Validate
        self._validate_ga_config(ga_config)
        
        return ga_config
    
    def load_eval_config(self, file_path: str = "eval_config.yaml") -> EvalConfig:
        """
        Load evaluation configuration.
        
        Args:
            file_path: Path to eval config file
            
        Returns:
            EvalConfig instance
        """
        config_dict = self.load_yaml(file_path)
        
        # Handle nested structure
        eval_config = EvalConfig()
        
        # Flatten nested config
        if 'backtest' in config_dict:
            for key, value in config_dict['backtest'].items():
                if hasattr(eval_config, key):
                    setattr(eval_config, key, value)
        
        if 'freqtrade' in config_dict:
            for key, value in config_dict['freqtrade'].items():
                # Map some keys
                if key == 'config_path':
                    eval_config.freqtrade_config_path = value
                elif hasattr(eval_config, key):
                    setattr(eval_config, key, value)
        
        if 'validation' in config_dict:
            for key, value in config_dict['validation'].items():
                if hasattr(eval_config, key):
                    setattr(eval_config, key, value)
        
        if 'risk' in config_dict:
            for key, value in config_dict['risk'].items():
                if hasattr(eval_config, key):
                    setattr(eval_config, key, value)
        
        # Other sections
        for section in ['metrics', 'modes', 'data', 'performance', 'error_handling']:
            if section in config_dict:
                for key, value in config_dict[section].items():
                    if hasattr(eval_config, key):
                        setattr(eval_config, key, value)
        
        # Validate
        self._validate_eval_config(eval_config)
        
        return eval_config
    
    def _validate_ga_config(self, config: GAConfig) -> None:
        """
        Validate GA configuration.
        
        Args:
            config: GAConfig to validate
            
        Raises:
            ValueError: If configuration is invalid
        """
        if config.population_size < 1:
            raise ValueError("population_size must be >= 1")
        
        if config.elite_size >= config.population_size:
            raise ValueError("elite_size must be < population_size")
        
        if not 0 <= config.mutation_rate <= 1:
            raise ValueError("mutation_rate must be between 0 and 1")
        
        if not 0 <= config.crossover_rate <= 1:
            raise ValueError("crossover_rate must be between 0 and 1")
        
        if config.selection_method not in ["tournament", "roulette", "rank"]:
            raise ValueError("selection_method must be 'tournament', 'roulette', or 'rank'")
        
        # Validate fitness weights sum to ~1.0
        total_weight = sum(config.fitness_weights.values())
        if not 0.95 <= total_weight <= 1.05:
            raise ValueError(f"fitness_weights should sum to ~1.0 (got {total_weight})")
    
    def _validate_eval_config(self, config: EvalConfig) -> None:
        """
        Validate evaluation configuration.
        
        Args:
            config: EvalConfig to validate
            
        Raises:
            ValueError: If configuration is invalid
        """
        if config.starting_balance <= 0:
            raise ValueError("starting_balance must be > 0")
        
        if not 0 <= config.fee <= 1:
            raise ValueError("fee must be between 0 and 1")
        
        if config.min_trades_required < 0:
            raise ValueError("min_trades_required must be >= 0")
        
        if not 0 <= config.max_drawdown_threshold <= 1:
            raise ValueError("max_drawdown_threshold must be between 0 and 1")


def load_config(
    ga_config_file: str = "ga_config.yaml",
    eval_config_file: str = "eval_config.yaml",
    base_dir: Optional[Path] = None
) -> tuple[GAConfig, EvalConfig]:
    """
    Load both GA and eval configurations.
    
    Args:
        ga_config_file: Path to GA config file
        eval_config_file: Path to eval config file
        base_dir: Base directory for configs
        
    Returns:
        Tuple of (GAConfig, EvalConfig)
    """
    loader = ConfigLoader(base_dir)
    ga_config = loader.load_ga_config(ga_config_file)
    eval_config = loader.load_eval_config(eval_config_file)
    
    return ga_config, eval_config


if __name__ == "__main__":
    # Test config loader
    loader = ConfigLoader()
    
    print("Loading GA config...")
    ga_config = loader.load_ga_config()
    print(f"  Population size: {ga_config.population_size}")
    print(f"  Elite size: {ga_config.elite_size}")
    print(f"  Mutation rate: {ga_config.mutation_rate}")
    print(f"  Fitness weights: {ga_config.fitness_weights}")
    
    print("\nLoading Eval config...")
    eval_config = loader.load_eval_config()
    print(f"  Backtest period: {eval_config.backtest_period}")
    print(f"  Timeframe: {eval_config.timeframe}")
    print(f"  Starting balance: {eval_config.starting_balance}")
    print(f"  Min trades: {eval_config.min_trades_required}")
    
    print("\nConfiguration loaded successfully!")
