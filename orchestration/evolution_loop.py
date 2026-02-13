"""
Evolution Loop for GAFreqTrade

This is the main orchestration module that runs the genetic algorithm evolution loop.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from typing import Dict, Optional
from datetime import datetime
import logging

try:
    from ga_core.population import Population
    from evaluation.backtester import Backtester
    from evaluation.fitness import FitnessCalculator
    from evaluation.metrics import MetricsCollector, StrategyMetrics
    from storage.strategy_db import StrategyDB
    from storage.leaderboard import Leaderboard
    from utils.config_loader import GAConfig, load_config
    from utils.logger import get_logger
    logger = get_logger()
except (ImportError, ModuleNotFoundError):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    # Simplified imports for testing
    from ga_core.population import Population
    from evaluation.fitness import FitnessCalculator
    from evaluation.metrics import MetricsCollector, StrategyMetrics
    from storage.strategy_db import StrategyDB
    from storage.leaderboard import Leaderboard


class EvolutionLoop:
    """
    Main evolution loop for genetic algorithm
    
    Coordinates:
    - Population initialization
    - Strategy evaluation (backtesting)
    - Fitness calculation
    - Evolution (selection, crossover, mutation)
    - Checkpoint saving
    - Statistics tracking
    """
    
    def __init__(self, config: Optional[Dict] = None, eval_config: Optional[Dict] = None):
        """
        Initialize evolution loop
        
        Args:
            config: Configuration dictionary (or GAConfig object)
            eval_config: Evaluation configuration dictionary
        """
        if config is None:
            # Use default config
            config = {
                'population_size': 20,
                'generations': 100,
                'elite_size': 4,
                'mutation_rate': 0.20,
                'crossover_rate': 0.70,
                'new_random_rate': 0.10,
                'tournament_size': 5,
                'checkpoint_interval': 10,
                'fitness_weights': {
                    'profit': 0.30,
                    'sharpe': 0.10,
                    'drawdown': 0.25,
                    'winrate': 0.15,
                    'stability': 0.15,
                    'trade_count': 0.05,
                }
            }
        
        self.config = config
        
        # Load eval config if not provided
        if eval_config is None:
            eval_config = self._load_eval_config()
        self.eval_config = eval_config
        
        # Initialize components
        try:
            # Get freqtrade settings from eval_config
            freqtrade_path = self.eval_config.get('freqtrade_path', 'freqtrade')
            config_path = self.eval_config.get('freqtrade_config_path', 'freqtrade/user_data/config.json')
            strategy_dir = self.eval_config.get('strategy_path', 'strategies/generated')
            
            self.backtester = Backtester(
                freqtrade_path=freqtrade_path,
                config_path=config_path,
                strategy_dir=strategy_dir
            )
        except Exception as e:
            logger.warning(f"Could not initialize backtester: {e}")
            self.backtester = None
        
        self.fitness_calculator = FitnessCalculator(
            weights=self.config.get('fitness_weights')
        )
        self.metrics_collector = MetricsCollector()
        
        # Initialize database and leaderboard
        try:
            self.db = StrategyDB()
            self.leaderboard = Leaderboard(self.db)
            logger.info("Database initialized")
        except Exception as e:
            logger.warning(f"Could not initialize database: {e}")
            self.db = None
            self.leaderboard = None
        
        self.population: Optional[Population] = None
        self.current_generation = 0
        self.start_time = None
    
    def _load_eval_config(self) -> Dict:
        """Load evaluation configuration from file"""
        try:
            from utils.config_loader import ConfigLoader
            from pathlib import Path
            import os
            
            # Get absolute path to the config file
            script_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            config_path = script_dir / 'config' / 'eval_config.yaml'
            
            loader = ConfigLoader(base_dir=script_dir)
            eval_config_obj = loader.load_eval_config(str(config_path))
            
            # Convert to dict for easier use
            return {
                'freqtrade_path': 'freqtrade',  # Keep as command, not path
                'freqtrade_config_path': eval_config_obj.freqtrade_config_path,
                'strategy_path': eval_config_obj.strategy_path,
                'datadir': eval_config_obj.datadir,
                'timerange': None,  # Will be set later
                'min_trades_required': eval_config_obj.min_trades_required,
                'ignore_invalid_strategies': eval_config_obj.ignore_invalid_strategies,
            }
        except Exception as e:
            logger.warning(f"Failed to load eval_config.yaml: {e}, using defaults")
            return {
                'freqtrade_path': 'freqtrade',
                'freqtrade_config_path': 'freqtrade/user_data/config.json',
                'strategy_path': 'strategies/generated',
                'datadir': 'freqtrade/user_data/data',
                'timerange': None,
                'min_trades_required': 10,
                'ignore_invalid_strategies': True,
            }
    
    def initialize_population(self):
        """Initialize the population"""
        logger.info("Initializing population...")
        
        self.population = Population(
            size=self.config.get('population_size', 20),
            generation=0,
            output_dir="strategies/generated"
        )
        
        self.population.initialize_random()
        self.current_generation = 0
        
        logger.info(f"Population initialized with {len(self.population.strategies)} strategies")
    
    def evaluate_population(self, use_mock: bool = True):
        """
        Evaluate all strategies in the current population
        
        Args:
            use_mock: If True, use mock fitness scores (for testing without Freqtrade)
        """
        logger.info(f"Evaluating generation {self.current_generation}...")
        
        evaluated_count = 0
        failed_strategies = []  # Track strategies that failed evaluation
        
        for strategy in self.population.strategies:
            strategy_id = strategy['strategy_id']
            class_name = strategy['class_name']
            
            logger.info(f"Evaluating {strategy_id}...")
            
            if use_mock or self.backtester is None:
                # Mock evaluation for testing
                import random
                backtest_metrics = {
                    'total_profit_pct': random.uniform(-10, 30),
                    'trades_count': random.randint(50, 200),
                    'wins': random.randint(20, 100),
                    'losses': random.randint(20, 100),
                    'win_rate': random.uniform(40, 70),
                    'sharpe_ratio': random.uniform(0.5, 2.5),
                    'sortino_ratio': random.uniform(0.5, 3.0),
                    'calmar_ratio': random.uniform(0.5, 2.0),
                    'max_drawdown_pct': random.uniform(-30, -5),
                    'profit_factor': random.uniform(1.0, 2.5),
                    'avg_profit': random.uniform(0.1, 1.0),
                    'avg_duration': random.uniform(30, 300),
                    'expectancy': random.uniform(0.0, 0.5),
                }
            else:
                # Real backtesting
                try:
                    result = self.backtester.run_backtest(
                        strategy_name=class_name,
                        timerange="20240101-20240630"  # Example timerange
                    )
                    
                    if not result.is_valid():
                        logger.warning(f"Backtest for {strategy_id} produced no valid trades")
                        # Check if we should ignore invalid strategies
                        if self.eval_config.get('ignore_invalid_strategies', True):
                            logger.warning(f"Marking {strategy_id} for removal (no valid trades)")
                            failed_strategies.append(strategy_id)
                            continue
                        else:
                            backtest_metrics = result._default_metrics()
                    else:
                        backtest_metrics = result.metrics
                        
                except Exception as e:
                    logger.error(f"Error backtesting {strategy_id}: {e}")
                    # Mark strategy as failed if it throws an error
                    if self.eval_config.get('ignore_invalid_strategies', True):
                        logger.warning(f"Marking {strategy_id} for removal (backtest error)")
                        failed_strategies.append(strategy_id)
                        continue
                    else:
                        # Use default metrics for failed strategies when filtering is disabled
                        backtest_metrics = {}
            
            # Calculate fitness
            fitness = self.fitness_calculator.calculate_fitness(backtest_metrics)
            
            # Update population
            self.population.update_fitness(strategy_id, fitness)
            
            # Save to database
            if self.db:
                # Prepare strategy data for DB
                strategy_data = {
                    'name': strategy_id,
                    'generation': self.current_generation,
                    'parent1': strategy.get('parent1'),
                    'parent2': strategy.get('parent2'),
                    'indicators': strategy.get('indicators', []),
                    'parameters': strategy.get('parameters', {}),
                    'code': ''  # Code is saved to files
                }
                self.db.save_strategy(strategy_data)
                self.db.save_result(
                    strategy_name=strategy_id,
                    generation=self.current_generation,
                    fitness=fitness,
                    metrics=backtest_metrics
                )
            
            # Collect metrics
            strategy_metrics = StrategyMetrics.from_backtest_result(
                strategy_id=strategy_id,
                generation=self.current_generation,
                fitness=fitness,
                backtest_metrics=backtest_metrics
            )
            self.metrics_collector.add_strategy_metrics(strategy_metrics)
            
            evaluated_count += 1
            logger.info(f"  Fitness: {fitness:.4f}, Profit: {backtest_metrics.get('total_profit_pct', 0):.2f}%")
        
        # Remove failed strategies from population
        if failed_strategies:
            logger.warning(f"Removing {len(failed_strategies)} failed strategies from population")
            self.population.strategies = [
                s for s in self.population.strategies 
                if s['strategy_id'] not in failed_strategies
            ]
            # Also remove from fitness scores
            for strategy_id in failed_strategies:
                if strategy_id in self.population.fitness_scores:
                    del self.population.fitness_scores[strategy_id]
            
            logger.info(f"Population size after filtering: {len(self.population.strategies)}")
        
        logger.info(f"Evaluated {evaluated_count} strategies")
        
        # Calculate generation metrics
        gen_metrics = self.metrics_collector.calculate_generation_metrics(self.current_generation)
        logger.info(f"Generation {self.current_generation} Statistics:")
        logger.info(f"  Best Fitness: {gen_metrics.best_fitness:.4f}")
        logger.info(f"  Avg Fitness: {gen_metrics.avg_fitness:.4f}")
        logger.info(f"  Best Profit: {gen_metrics.best_profit:.2f}%")
        logger.info(f"  Diversity: {gen_metrics.diversity_score:.4f}")
        
        # Save generation stats to database
        if self.db:
            self.db.save_generation(
                generation=self.current_generation,
                stats={
                    'best_fitness': gen_metrics.best_fitness,
                    'avg_fitness': gen_metrics.avg_fitness,
                    'best_profit': gen_metrics.best_profit,
                    'population_size': len(self.population.strategies),
                    'diversity': gen_metrics.diversity_score
                }
            )
    
    def evolve_to_next_generation(self):
        """Evolve the population to the next generation"""
        logger.info(f"Evolving from generation {self.current_generation} to {self.current_generation + 1}...")
        
        self.population = self.population.evolve_generation(
            elite_size=self.config.get('elite_size', 4),
            mutation_rate=self.config.get('mutation_rate', 0.20),
            crossover_rate=self.config.get('crossover_rate', 0.70),
            new_random_rate=self.config.get('new_random_rate', 0.10),
            tournament_size=self.config.get('tournament_size', 5)
        )
        
        self.current_generation += 1
        logger.info(f"Evolved to generation {self.current_generation}")
    
    def save_checkpoint(self):
        """Save current state as checkpoint"""
        logger.info(f"Saving checkpoint for generation {self.current_generation}...")
        self.population.save_checkpoint("checkpoints")
        logger.info("Checkpoint saved")
    
    def run(self, 
            max_generations: Optional[int] = None,
            use_mock_evaluation: bool = True,
            checkpoint_interval: Optional[int] = None):
        """
        Run the evolution loop
        
        Args:
            max_generations: Maximum number of generations (None = use config)
            use_mock_evaluation: Use mock fitness scores (for testing)
            checkpoint_interval: Save checkpoint every N generations (None = use config)
        """
        if max_generations is None:
            max_generations = self.config.get('generations', 100)
        
        if checkpoint_interval is None:
            checkpoint_interval = self.config.get('checkpoint_interval', 10)
        
        logger.info("=" * 60)
        logger.info("Starting GAFreqTrade Evolution")
        logger.info("=" * 60)
        logger.info(f"Configuration:")
        logger.info(f"  Population Size: {self.config.get('population_size')}")
        logger.info(f"  Max Generations: {max_generations}")
        logger.info(f"  Elite Size: {self.config.get('elite_size')}")
        logger.info(f"  Mutation Rate: {self.config.get('mutation_rate')}")
        logger.info(f"  Crossover Rate: {self.config.get('crossover_rate')}")
        logger.info(f"  Mock Evaluation: {use_mock_evaluation}")
        logger.info("=" * 60)
        
        self.start_time = time.time()
        
        # Initialize population
        if self.population is None:
            self.initialize_population()
        
        # Main evolution loop
        for generation in range(max_generations):
            gen_start_time = time.time()
            
            logger.info("")
            logger.info("=" * 60)
            logger.info(f"GENERATION {self.current_generation}")
            logger.info("=" * 60)
            
            # Evaluate population
            self.evaluate_population(use_mock=use_mock_evaluation)
            
            # Show top strategies
            top_5 = self.population.get_top_n(5)
            logger.info("\nTop 5 Strategies:")
            for i, strategy in enumerate(top_5, 1):
                fitness = self.population.fitness_scores[strategy['strategy_id']]
                logger.info(f"  {i}. {strategy['strategy_id']}: Fitness={fitness:.4f}")
            
            # Save checkpoint
            if (self.current_generation % checkpoint_interval == 0) or (self.current_generation == max_generations - 1):
                self.save_checkpoint()
            
            # Check if we've reached the end
            if self.current_generation >= max_generations - 1:
                break
            
            # Evolve to next generation
            self.evolve_to_next_generation()
            
            gen_duration = time.time() - gen_start_time
            logger.info(f"Generation {self.current_generation - 1} completed in {gen_duration:.2f}s")
        
        # Final statistics
        total_duration = time.time() - self.start_time
        
        logger.info("")
        logger.info("=" * 60)
        logger.info("EVOLUTION COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Total Generations: {self.current_generation + 1}")
        logger.info(f"Total Time: {total_duration:.2f}s ({total_duration/60:.2f} minutes)")
        logger.info(f"Avg Time per Generation: {total_duration/(self.current_generation + 1):.2f}s")
        
        # Final top strategies
        final_top_10 = self.population.get_top_n(10)
        logger.info("\n\nFINAL TOP 10 STRATEGIES:")
        for i, strategy in enumerate(final_top_10, 1):
            fitness = self.population.fitness_scores[strategy['strategy_id']]
            indicators = strategy.get('indicators', [])
            logger.info(f"  {i}. {strategy['strategy_id']}")
            logger.info(f"     Fitness: {fitness:.4f}")
            logger.info(f"     Indicators: {', '.join(indicators)}")
        
        # Evolution trend
        logger.info("\n\nEVOLUTION TREND:")
        for gen_metrics in self.metrics_collector.generation_metrics:
            logger.info(f"  Gen {gen_metrics.generation}: "
                       f"Best={gen_metrics.best_fitness:.4f}, "
                       f"Avg={gen_metrics.avg_fitness:.4f}, "
                       f"Profit={gen_metrics.best_profit:.2f}%")
        
        logger.info("\n" + "=" * 60)
        logger.info("Evolution results saved in:")
        logger.info("  - strategies/generated/")
        logger.info("  - checkpoints/")
        logger.info("=" * 60)
        
        return self.population


def run_evolution(config: Optional[Dict] = None, 
                 resume_checkpoint: Optional[str] = None,
                 max_generations: int = 10,
                 use_mock: bool = True):
    """
    Convenience function to run evolution
    
    Args:
        config: Configuration dictionary
        resume_checkpoint: Path to checkpoint file to resume from
        max_generations: Maximum number of generations
        use_mock: Use mock evaluation (for testing without Freqtrade)
        
    Returns:
        Final population
    """
    # Create evolution loop
    evolution = EvolutionLoop(config)
    
    # Resume from checkpoint if provided
    if resume_checkpoint:
        try:
            evolution.population = Population.load_checkpoint(resume_checkpoint)
            evolution.current_generation = evolution.population.generation
            logger.info(f"Resumed from checkpoint: generation {evolution.current_generation}")
        except Exception as e:
            logger.error(f"Failed to load checkpoint: {e}")
            logger.info("Starting fresh evolution")
    
    # Run evolution
    final_population = evolution.run(
        max_generations=max_generations,
        use_mock_evaluation=use_mock
    )
    
    return final_population


if __name__ == "__main__":
    # Test evolution loop
    print("\n" + "=" * 60)
    print("TESTING EVOLUTION LOOP")
    print("=" * 60 + "\n")
    
    # Run a small test evolution
    final_pop = run_evolution(
        max_generations=5,
        use_mock=True
    )
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
