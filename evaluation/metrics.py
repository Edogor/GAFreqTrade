"""
Metrics Module for GAFreqTrade

This module provides utilities for collecting, normalizing, and analyzing
performance metrics across strategies and generations.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import statistics
import logging

try:
    from utils.logger import get_logger
    logger = get_logger()
except (ImportError, ModuleNotFoundError):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


@dataclass
class StrategyMetrics:
    """Container for strategy performance metrics"""
    strategy_id: str
    generation: int
    fitness: float
    total_profit_pct: float
    total_profit_abs: float
    trades_count: int
    win_rate: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown_pct: float
    avg_profit: float
    avg_duration: float
    profit_factor: float
    expectancy: float
    calmar_ratio: float
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_backtest_result(cls, strategy_id: str, generation: int, 
                           fitness: float, backtest_metrics: Dict) -> 'StrategyMetrics':
        """Create from backtest result"""
        return cls(
            strategy_id=strategy_id,
            generation=generation,
            fitness=fitness,
            total_profit_pct=backtest_metrics.get('total_profit_pct', 0.0),
            total_profit_abs=backtest_metrics.get('total_profit_abs', 0.0),
            trades_count=backtest_metrics.get('trades_count', 0),
            win_rate=backtest_metrics.get('win_rate', 0.0),
            sharpe_ratio=backtest_metrics.get('sharpe_ratio', 0.0),
            sortino_ratio=backtest_metrics.get('sortino_ratio', 0.0),
            max_drawdown_pct=backtest_metrics.get('max_drawdown_pct', 0.0),
            avg_profit=backtest_metrics.get('avg_profit', 0.0),
            avg_duration=backtest_metrics.get('avg_duration', 0.0),
            profit_factor=backtest_metrics.get('profit_factor', 0.0),
            expectancy=backtest_metrics.get('expectancy', 0.0),
            calmar_ratio=backtest_metrics.get('calmar_ratio', 0.0),
        )


@dataclass
class GenerationMetrics:
    """Container for generation-level metrics"""
    generation: int
    population_size: int
    best_fitness: float
    avg_fitness: float
    worst_fitness: float
    std_fitness: float
    best_profit: float
    avg_profit: float
    diversity_score: float
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


class MetricsCollector:
    """Collect and aggregate metrics across strategies and generations"""
    
    def __init__(self):
        self.strategy_metrics: List[StrategyMetrics] = []
        self.generation_metrics: List[GenerationMetrics] = []
    
    def add_strategy_metrics(self, metrics: StrategyMetrics):
        """Add metrics for a strategy"""
        self.strategy_metrics.append(metrics)
    
    def calculate_generation_metrics(self, generation: int) -> GenerationMetrics:
        """
        Calculate metrics for a generation
        
        Args:
            generation: Generation number
            
        Returns:
            GenerationMetrics object
        """
        # Get all metrics for this generation
        gen_metrics = [m for m in self.strategy_metrics if m.generation == generation]
        
        if not gen_metrics:
            return GenerationMetrics(
                generation=generation,
                population_size=0,
                best_fitness=0.0,
                avg_fitness=0.0,
                worst_fitness=0.0,
                std_fitness=0.0,
                best_profit=0.0,
                avg_profit=0.0,
                diversity_score=0.0
            )
        
        fitnesses = [m.fitness for m in gen_metrics]
        profits = [m.total_profit_pct for m in gen_metrics]
        
        metrics = GenerationMetrics(
            generation=generation,
            population_size=len(gen_metrics),
            best_fitness=max(fitnesses),
            avg_fitness=statistics.mean(fitnesses),
            worst_fitness=min(fitnesses),
            std_fitness=statistics.stdev(fitnesses) if len(fitnesses) > 1 else 0.0,
            best_profit=max(profits),
            avg_profit=statistics.mean(profits),
            diversity_score=self._calculate_diversity(gen_metrics)
        )
        
        self.generation_metrics.append(metrics)
        return metrics
    
    def _calculate_diversity(self, metrics: List[StrategyMetrics]) -> float:
        """
        Calculate diversity score for a generation
        
        Higher diversity = more varied strategies
        
        Returns:
            Diversity score (0.0 to 1.0)
        """
        if len(metrics) < 2:
            return 0.0
        
        # Calculate coefficient of variation for key metrics
        def cv(values):
            """Coefficient of variation"""
            if not values or statistics.mean(values) == 0:
                return 0.0
            return statistics.stdev(values) / abs(statistics.mean(values))
        
        fitnesses = [m.fitness for m in metrics]
        profits = [m.total_profit_pct for m in metrics]
        winrates = [m.win_rate for m in metrics]
        drawdowns = [abs(m.max_drawdown_pct) for m in metrics]
        
        # Average CV across metrics
        cvs = [
            cv(fitnesses),
            cv(profits),
            cv(winrates),
            cv(drawdowns)
        ]
        
        # Normalize to 0-1 range (CV of 0.5 or higher = high diversity)
        diversity = min(1.0, statistics.mean(cvs) / 0.5)
        
        return diversity
    
    def get_top_strategies(self, n: int = 10, 
                          generation: Optional[int] = None) -> List[StrategyMetrics]:
        """
        Get top N strategies by fitness
        
        Args:
            n: Number of strategies to return
            generation: If specified, only return strategies from this generation
            
        Returns:
            List of top strategies
        """
        metrics = self.strategy_metrics
        
        if generation is not None:
            metrics = [m for m in metrics if m.generation == generation]
        
        # Sort by fitness (descending)
        sorted_metrics = sorted(metrics, key=lambda m: m.fitness, reverse=True)
        
        return sorted_metrics[:n]
    
    def get_generation_summary(self, generation: int) -> Dict:
        """
        Get summary statistics for a generation
        
        Args:
            generation: Generation number
            
        Returns:
            Dictionary with summary statistics
        """
        gen_metrics = [m for m in self.strategy_metrics if m.generation == generation]
        
        if not gen_metrics:
            return {
                'generation': generation,
                'count': 0,
                'error': 'No metrics found'
            }
        
        fitnesses = [m.fitness for m in gen_metrics]
        profits = [m.total_profit_pct for m in gen_metrics]
        trade_counts = [m.trades_count for m in gen_metrics]
        
        return {
            'generation': generation,
            'count': len(gen_metrics),
            'fitness': {
                'best': max(fitnesses),
                'avg': statistics.mean(fitnesses),
                'worst': min(fitnesses),
                'std': statistics.stdev(fitnesses) if len(fitnesses) > 1 else 0.0
            },
            'profit': {
                'best': max(profits),
                'avg': statistics.mean(profits),
                'worst': min(profits),
                'std': statistics.stdev(profits) if len(profits) > 1 else 0.0
            },
            'trades': {
                'avg': statistics.mean(trade_counts),
                'min': min(trade_counts),
                'max': max(trade_counts)
            }
        }
    
    def get_evolution_trend(self) -> List[Dict]:
        """
        Get evolution trend across generations
        
        Returns:
            List of generation summaries
        """
        if not self.generation_metrics:
            # Calculate if not already done
            generations = set(m.generation for m in self.strategy_metrics)
            for gen in sorted(generations):
                self.calculate_generation_metrics(gen)
        
        return [m.to_dict() for m in self.generation_metrics]
    
    def calculate_improvement(self, generation1: int, generation2: int) -> Dict[str, float]:
        """
        Calculate improvement between two generations
        
        Args:
            generation1: Earlier generation
            generation2: Later generation
            
        Returns:
            Dictionary with improvement metrics
        """
        summary1 = self.get_generation_summary(generation1)
        summary2 = self.get_generation_summary(generation2)
        
        if 'error' in summary1 or 'error' in summary2:
            return {'error': 'Invalid generations'}
        
        return {
            'fitness_improvement': summary2['fitness']['best'] - summary1['fitness']['best'],
            'avg_fitness_improvement': summary2['fitness']['avg'] - summary1['fitness']['avg'],
            'profit_improvement': summary2['profit']['best'] - summary1['profit']['best'],
            'avg_profit_improvement': summary2['profit']['avg'] - summary1['profit']['avg'],
        }


class MetricsNormalizer:
    """Normalize metrics for comparison across different time periods or datasets"""
    
    @staticmethod
    def normalize_by_timeframe(metrics: Dict, days: int) -> Dict:
        """
        Normalize metrics by timeframe
        
        Adjust metrics to a standard timeframe for fair comparison.
        
        Args:
            metrics: Raw metrics
            days: Number of days in backtest
            
        Returns:
            Normalized metrics
        """
        if days <= 0:
            return metrics
        
        normalized = metrics.copy()
        
        # Annualize profit
        if 'total_profit_pct' in metrics:
            annual_factor = 365.0 / days
            normalized['annualized_profit_pct'] = metrics['total_profit_pct'] * annual_factor
        
        # Normalize trade count to per-month rate
        if 'trades_count' in metrics:
            month_factor = 30.0 / days
            normalized['trades_per_month'] = metrics['trades_count'] * month_factor
        
        return normalized
    
    @staticmethod
    def normalize_by_exposure(metrics: Dict, max_open_trades: int) -> Dict:
        """
        Normalize metrics by exposure (number of concurrent trades)
        
        Args:
            metrics: Raw metrics
            max_open_trades: Maximum number of open trades
            
        Returns:
            Normalized metrics
        """
        if max_open_trades <= 0:
            return metrics
        
        normalized = metrics.copy()
        
        # Adjust profit by exposure
        if 'total_profit_pct' in metrics:
            normalized['profit_per_exposure'] = metrics['total_profit_pct'] / max_open_trades
        
        return normalized


if __name__ == "__main__":
    # Test metrics collector
    print("Testing Metrics Collector...")
    
    collector = MetricsCollector()
    
    # Add some test metrics
    for gen in range(3):
        for i in range(10):
            metrics = StrategyMetrics(
                strategy_id=f"Gen{gen:03d}_Strat_{i:03d}",
                generation=gen,
                fitness=0.5 + (gen * 0.1) + (i * 0.01),
                total_profit_pct=10.0 + (gen * 5) + (i * 0.5),
                total_profit_abs=100.0 + (gen * 50),
                trades_count=100 + (i * 10),
                win_rate=50.0 + (i * 2),
                sharpe_ratio=1.5 + (gen * 0.2),
                sortino_ratio=2.0 + (gen * 0.2),
                max_drawdown_pct=-15.0 + (i * 0.5),
                avg_profit=0.5 + (i * 0.05),
                avg_duration=120.0,
                profit_factor=1.5,
                expectancy=0.3,
                calmar_ratio=1.2
            )
            collector.add_strategy_metrics(metrics)
    
    # Calculate generation metrics
    for gen in range(3):
        gen_metrics = collector.calculate_generation_metrics(gen)
        print(f"\nGeneration {gen}:")
        print(f"  Best Fitness: {gen_metrics.best_fitness:.4f}")
        print(f"  Avg Fitness: {gen_metrics.avg_fitness:.4f}")
        print(f"  Best Profit: {gen_metrics.best_profit:.2f}%")
        print(f"  Diversity: {gen_metrics.diversity_score:.4f}")
    
    # Get top strategies
    print("\n\nTop 5 Strategies:")
    top_strategies = collector.get_top_strategies(5)
    for i, strategy in enumerate(top_strategies, 1):
        print(f"{i}. {strategy.strategy_id}: Fitness={strategy.fitness:.4f}, "
              f"Profit={strategy.total_profit_pct:.2f}%")
    
    # Calculate improvement
    improvement = collector.calculate_improvement(0, 2)
    print(f"\n\nImprovement from Gen 0 to Gen 2:")
    print(f"  Best Fitness: +{improvement['fitness_improvement']:.4f}")
    print(f"  Avg Fitness: +{improvement['avg_fitness_improvement']:.4f}")
    print(f"  Best Profit: +{improvement['profit_improvement']:.2f}%")
