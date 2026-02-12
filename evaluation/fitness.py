"""
Fitness Function for GAFreqTrade

This module calculates fitness scores for trading strategies based on
multiple performance metrics.
"""

import math
from typing import Dict, Optional
import logging

try:
    from utils.logger import get_logger
    logger = get_logger()
except (ImportError, ModuleNotFoundError):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class FitnessCalculator:
    """
    Calculate fitness scores for trading strategies
    
    Fitness is calculated as a weighted sum of normalized metrics.
    """
    
    DEFAULT_WEIGHTS = {
        'profit': 0.30,
        'sharpe': 0.10,
        'drawdown': 0.25,
        'winrate': 0.15,
        'stability': 0.15,
        'trade_count': 0.05,
    }
    
    # Normalization ranges for metrics
    METRIC_RANGES = {
        'profit': (-50, 100),        # Total profit % range
        'sharpe': (-2, 4),            # Sharpe ratio range
        'drawdown': (0, 1),           # Max drawdown (0-1)
        'winrate': (0, 100),          # Win rate %
        'trade_count': (0, 1000),     # Number of trades
        'sortino': (-2, 4),           # Sortino ratio range
        'calmar': (-2, 4),            # Calmar ratio range
        'profit_factor': (0, 3),      # Profit factor range
        'expectancy': (-1, 1),        # Expectancy range
    }
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """
        Initialize fitness calculator
        
        Args:
            weights: Custom weights for fitness components (must sum to ~1.0)
        """
        self.weights = weights if weights else self.DEFAULT_WEIGHTS.copy()
        
        # Validate weights
        weight_sum = sum(self.weights.values())
        if not (0.95 <= weight_sum <= 1.05):
            logger.warning(f"Weights sum to {weight_sum:.3f}, should be close to 1.0")
    
    def calculate_fitness(self, backtest_metrics: Dict) -> float:
        """
        Calculate fitness score from backtest metrics
        
        Args:
            backtest_metrics: Dictionary of backtest metrics
            
        Returns:
            Fitness score (0.0 to 1.0, higher is better)
        """
        if not backtest_metrics or backtest_metrics.get('trades_count', 0) == 0:
            return 0.0
        
        # Calculate individual fitness components
        components = {
            'profit': self._fitness_profit(backtest_metrics),
            'sharpe': self._fitness_sharpe(backtest_metrics),
            'drawdown': self._fitness_drawdown(backtest_metrics),
            'winrate': self._fitness_winrate(backtest_metrics),
            'stability': self._fitness_stability(backtest_metrics),
            'trade_count': self._fitness_trade_count(backtest_metrics),
        }
        
        # Calculate weighted fitness
        fitness = sum(
            self.weights.get(key, 0) * value 
            for key, value in components.items()
        )
        
        # Apply penalties
        fitness = self._apply_penalties(fitness, backtest_metrics)
        
        # Clamp to [0, 1]
        fitness = max(0.0, min(1.0, fitness))
        
        logger.debug(f"Fitness: {fitness:.4f}, Components: {components}")
        
        return fitness
    
    def _normalize(self, value: float, metric_key: str, invert: bool = False) -> float:
        """
        Normalize a metric value to 0-1 range
        
        Args:
            value: Raw metric value
            metric_key: Key to get normalization range
            invert: If True, invert the normalized value (for metrics where lower is better)
            
        Returns:
            Normalized value (0.0 to 1.0)
        """
        min_val, max_val = self.METRIC_RANGES.get(metric_key, (0, 1))
        
        # Clamp value to range
        value = max(min_val, min(max_val, value))
        
        # Normalize to 0-1
        if max_val != min_val:
            normalized = (value - min_val) / (max_val - min_val)
        else:
            normalized = 0.5
        
        # Invert if needed (for metrics where lower is better)
        if invert:
            normalized = 1.0 - normalized
        
        return normalized
    
    def _fitness_profit(self, metrics: Dict) -> float:
        """Calculate profit component of fitness"""
        total_profit = metrics.get('total_profit_pct', 0.0)
        return self._normalize(total_profit, 'profit')
    
    def _fitness_sharpe(self, metrics: Dict) -> float:
        """Calculate Sharpe ratio component of fitness"""
        sharpe = metrics.get('sharpe_ratio', 0.0)
        return self._normalize(sharpe, 'sharpe')
    
    def _fitness_drawdown(self, metrics: Dict) -> float:
        """Calculate drawdown component of fitness (lower drawdown is better)"""
        drawdown = abs(metrics.get('max_drawdown_pct', 0.0)) / 100.0
        return self._normalize(drawdown, 'drawdown', invert=True)
    
    def _fitness_winrate(self, metrics: Dict) -> float:
        """Calculate win rate component of fitness"""
        winrate = metrics.get('win_rate', 0.0)
        return self._normalize(winrate, 'winrate')
    
    def _fitness_stability(self, metrics: Dict) -> float:
        """
        Calculate stability component of fitness
        
        Stability is a composite metric based on:
        - Sortino ratio (downside risk)
        - Calmar ratio (drawdown-adjusted returns)
        - Profit factor
        """
        sortino = metrics.get('sortino_ratio', 0.0)
        calmar = metrics.get('calmar_ratio', 0.0)
        profit_factor = metrics.get('profit_factor', 0.0)
        
        # Normalize each component
        norm_sortino = self._normalize(sortino, 'sortino')
        norm_calmar = self._normalize(calmar, 'calmar')
        norm_profit_factor = self._normalize(profit_factor, 'profit_factor')
        
        # Average them
        stability = (norm_sortino + norm_calmar + norm_profit_factor) / 3.0
        
        return stability
    
    def _fitness_trade_count(self, metrics: Dict) -> float:
        """
        Calculate trade count component of fitness
        
        Too few trades = unreliable statistics
        Too many trades = overtrading / high transaction costs
        Optimal range: 50-200 trades
        """
        trade_count = metrics.get('trades_count', 0)
        
        if trade_count < 10:
            # Very few trades - heavily penalize
            return 0.0
        elif trade_count < 30:
            # Few trades - some penalty
            return 0.3
        elif 30 <= trade_count <= 200:
            # Good range
            return 1.0
        elif trade_count <= 500:
            # Many trades - slight penalty for transaction costs
            return 0.8
        else:
            # Too many trades - overtrading
            return 0.5
    
    def _apply_penalties(self, fitness: float, metrics: Dict) -> float:
        """
        Apply penalties for undesirable characteristics
        
        Args:
            fitness: Base fitness score
            metrics: Backtest metrics
            
        Returns:
            Penalized fitness score
        """
        penalty_multiplier = 1.0
        
        # Penalty for negative profit
        total_profit = metrics.get('total_profit_pct', 0.0)
        if total_profit < 0:
            # Heavy penalty for losing strategies
            penalty_multiplier *= 0.3
        
        # Penalty for very high drawdown (>50%)
        drawdown = abs(metrics.get('max_drawdown_pct', 0.0))
        if drawdown > 50:
            penalty_multiplier *= 0.5
        elif drawdown > 30:
            penalty_multiplier *= 0.7
        
        # Penalty for very low win rate (<30%)
        winrate = metrics.get('win_rate', 0.0)
        if winrate < 30:
            penalty_multiplier *= 0.7
        
        # Penalty for very few trades (<10)
        trade_count = metrics.get('trades_count', 0)
        if trade_count < 10:
            penalty_multiplier *= 0.4
        elif trade_count < 20:
            penalty_multiplier *= 0.7
        
        # Apply penalty
        return fitness * penalty_multiplier
    
    def calculate_multi_objective_fitness(self, metrics: Dict) -> Dict[str, float]:
        """
        Calculate multiple fitness objectives separately
        
        This is useful for multi-objective optimization algorithms.
        
        Args:
            metrics: Backtest metrics
            
        Returns:
            Dictionary of individual fitness objectives
        """
        return {
            'profit': self._fitness_profit(metrics),
            'sharpe': self._fitness_sharpe(metrics),
            'drawdown': self._fitness_drawdown(metrics),
            'winrate': self._fitness_winrate(metrics),
            'stability': self._fitness_stability(metrics),
            'trade_count': self._fitness_trade_count(metrics),
        }
    
    def compare_strategies(self, metrics1: Dict, metrics2: Dict) -> int:
        """
        Compare two strategies
        
        Args:
            metrics1: Metrics for strategy 1
            metrics2: Metrics for strategy 2
            
        Returns:
            1 if strategy1 is better, -1 if strategy2 is better, 0 if equal
        """
        fitness1 = self.calculate_fitness(metrics1)
        fitness2 = self.calculate_fitness(metrics2)
        
        if fitness1 > fitness2:
            return 1
        elif fitness1 < fitness2:
            return -1
        else:
            return 0


def calculate_fitness(backtest_metrics: Dict, 
                     weights: Optional[Dict[str, float]] = None) -> float:
    """
    Convenience function to calculate fitness
    
    Args:
        backtest_metrics: Dictionary of backtest metrics
        weights: Optional custom weights
        
    Returns:
        Fitness score (0.0 to 1.0)
    """
    calculator = FitnessCalculator(weights)
    return calculator.calculate_fitness(backtest_metrics)


if __name__ == "__main__":
    # Test fitness calculator
    print("Testing Fitness Calculator...")
    
    # Example metrics
    test_metrics = {
        'total_profit_pct': 15.5,
        'trades_count': 120,
        'wins': 72,
        'losses': 48,
        'win_rate': 60.0,
        'sharpe_ratio': 1.8,
        'sortino_ratio': 2.2,
        'calmar_ratio': 1.5,
        'max_drawdown_pct': -12.3,
        'profit_factor': 1.6,
    }
    
    calculator = FitnessCalculator()
    fitness = calculator.calculate_fitness(test_metrics)
    
    print(f"\nTest Metrics: {test_metrics}")
    print(f"Fitness Score: {fitness:.4f}")
    
    # Test multi-objective
    multi_fitness = calculator.calculate_multi_objective_fitness(test_metrics)
    print(f"\nMulti-Objective Fitness:")
    for key, value in multi_fitness.items():
        print(f"  {key}: {value:.4f}")
    
    # Test with poor strategy
    poor_metrics = {
        'total_profit_pct': -5.0,
        'trades_count': 5,
        'wins': 2,
        'losses': 3,
        'win_rate': 40.0,
        'sharpe_ratio': -0.5,
        'max_drawdown_pct': -30.0,
    }
    
    poor_fitness = calculator.calculate_fitness(poor_metrics)
    print(f"\nPoor Strategy Fitness: {poor_fitness:.4f}")
