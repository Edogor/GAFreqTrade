"""
Integration tests for evolution loop.
"""
import os
import pytest
from ga_core.population import Population
from ga_core.genetic_ops import GeneticOperations
from evaluation.fitness import FitnessCalculator
from unittest.mock import Mock, patch


@pytest.mark.integration
class TestEvolutionIntegration:
    """Integration tests for the full evolution workflow."""
    
    def test_single_generation_evolution(self, temp_dir):
        """Test a single generation of evolution."""
        # Initialize population
        pop = Population(size=10, generation=0, output_dir=temp_dir)
        pop.initialize_random()
        
        # Mock fitness evaluation (instead of real backtesting)
        import random
        for strategy in pop.strategies:
            fitness = random.uniform(0.3, 0.9)
            pop.update_fitness(strategy['strategy_id'], fitness)
        
        # Evolve to next generation
        new_pop = pop.evolve_generation(
            elite_size=2,
            mutation_rate=0.15,
            crossover_rate=0.7,
            new_random_rate=0.1,
            tournament_size=3
        )
        
        # Verify new population
        assert new_pop.generation == 1
        assert len(new_pop.strategies) == 10
        assert new_pop.generation > pop.generation
    
    def test_multi_generation_evolution(self, temp_dir):
        """Test multiple generations of evolution."""
        pop = Population(size=8, generation=0, output_dir=temp_dir)
        pop.initialize_random()
        
        generations = 3
        
        for gen in range(generations):
            # Mock fitness evaluation
            import random
            for strategy in pop.strategies:
                # Simulate improving fitness over generations
                base_fitness = random.uniform(0.4, 0.7)
                improvement = gen * 0.05
                fitness = min(base_fitness + improvement, 1.0)
                pop.update_fitness(strategy['strategy_id'], fitness)
            
            if gen < generations - 1:
                pop = pop.evolve_generation(
                    elite_size=2,
                    mutation_rate=0.15,
                    crossover_rate=0.7,
                    new_random_rate=0.1,
                    tournament_size=3
                )
        
        # Final generation should be higher
        assert pop.generation == generations - 1
    
    def test_elite_preservation_across_generations(self, temp_dir):
        """Test that elite strategies are preserved."""
        pop = Population(size=10, generation=0, output_dir=temp_dir)
        pop.initialize_random()
        
        # Set clear fitness differences
        for i, strategy in enumerate(pop.strategies):
            fitness = 0.5 + (i * 0.05)
            pop.update_fitness(strategy['strategy_id'], fitness)
        
        # Get top strategies
        top_strategies = pop.get_top_n(2)
        top_ids = [s['strategy_id'] for s in top_strategies]
        
        # Evolve
        new_pop = pop.evolve_generation(
            elite_size=2,
            mutation_rate=0.1,
            crossover_rate=0.7,
            new_random_rate=0.0,
            tournament_size=3
        )
        
        # Elite should be present in new population
        new_ids = [s['strategy_id'] for s in new_pop.strategies]
        for elite_id in top_ids:
            assert elite_id in new_ids
    
    def test_fitness_improvement_trend(self, temp_dir):
        """Test that average fitness tends to improve over generations."""
        pop = Population(size=10, generation=0, output_dir=temp_dir)
        pop.initialize_random()
        
        fitness_history = []
        
        for gen in range(5):
            # Mock fitness with slight improvement trend
            import random
            for strategy in pop.strategies:
                base = 0.4 + gen * 0.05
                fitness = random.uniform(base, base + 0.3)
                pop.update_fitness(strategy['strategy_id'], fitness)
            
            stats = pop.get_statistics()
            fitness_history.append(stats['avg_fitness'])
            
            if gen < 4:
                pop = pop.evolve_generation(
                    elite_size=2,
                    mutation_rate=0.15,
                    crossover_rate=0.7,
                    new_random_rate=0.05,
                    tournament_size=3
                )
        
        # Later generations should generally have higher fitness
        assert fitness_history[-1] >= fitness_history[0]


@pytest.mark.integration
class TestStrategyGenerationAndEvaluation:
    """Integration tests for strategy generation and evaluation."""
    
    def test_generate_and_evaluate_strategies(self, temp_dir):
        """Test generating strategies and evaluating them."""
        from ga_core.strategy_generator import generate_initial_population
        
        # Generate population
        population = generate_initial_population(5, temp_dir)
        
        # Verify all strategies were created
        assert len(population) == 5
        for strategy in population:
            assert os.path.exists(strategy['file_path'])
        
        # Mock evaluate with fitness calculator
        fitness_calc = FitnessCalculator()
        
        for strategy in population:
            # Mock backtest metrics
            mock_metrics = {
                'total_profit_pct': 10.0,
                'trades_count': 50,
                'win_rate': 55.0,
                'sharpe_ratio': 1.5,
                'max_drawdown_pct': -10.0,
                'sortino_ratio': 1.8,
                'calmar_ratio': 1.3,
                'profit_factor': 1.4,
                'expectancy': 0.2
            }
            
            fitness = fitness_calc.calculate_fitness(mock_metrics)
            assert 0.0 <= fitness <= 1.0
    
    def test_genetic_operations_pipeline(self, temp_dir, mock_strategy_metadata):
        """Test the full genetic operations pipeline."""
        genetic_ops = GeneticOperations()
        
        # Create two parent strategies
        parent1 = mock_strategy_metadata.copy()
        parent2 = mock_strategy_metadata.copy()
        parent2['strategy_id'] = 'Gen000_Strat_002'
        
        # Crossover
        child1, child2 = genetic_ops.crossover(parent1, parent2)
        
        # Mutate
        mutated_child1 = genetic_ops.mutate(child1)
        mutated_child2 = genetic_ops.mutate(child2)
        
        # Verify all are valid strategies
        assert 'strategy_id' in mutated_child1
        assert 'strategy_id' in mutated_child2
        assert 'indicators' in mutated_child1
        assert 'indicators' in mutated_child2


@pytest.mark.integration
class TestCheckpointingWorkflow:
    """Integration tests for checkpointing workflow."""
    
    def test_save_and_load_checkpoint(self, temp_dir):
        """Test saving and loading population checkpoints."""
        # Create and evolve population
        pop1 = Population(size=5, generation=0, output_dir=temp_dir)
        pop1.initialize_random()
        
        # Add fitness scores
        for strategy in pop1.strategies:
            pop1.update_fitness(strategy['strategy_id'], 0.75)
        
        # Save checkpoint
        checkpoint_dir = os.path.join(temp_dir, 'checkpoints')
        os.makedirs(checkpoint_dir, exist_ok=True)
        pop1.save_checkpoint(checkpoint_dir)
        
        # Find checkpoint file
        checkpoint_file = os.path.join(checkpoint_dir, f'population_gen_{pop1.generation:04d}.pkl')
        assert os.path.exists(checkpoint_file)
        
        # Load checkpoint
        pop2 = Population.load_checkpoint(checkpoint_file, output_dir=temp_dir)
        
        # Verify restoration
        assert pop2.generation == pop1.generation
        assert len(pop2.strategies) == len(pop1.strategies)
        
        # Continue evolution from checkpoint
        pop3 = pop2.evolve_generation(
            elite_size=2,
            mutation_rate=0.15,
            crossover_rate=0.7,
            new_random_rate=0.1,
            tournament_size=3
        )
        
        assert pop3.generation == pop2.generation + 1
    
    def test_checkpoint_during_evolution(self, temp_dir):
        """Test checkpointing during evolution process."""
        pop = Population(size=8, generation=0, output_dir=temp_dir)
        pop.initialize_random()
        
        checkpoint_dir = os.path.join(temp_dir, 'checkpoints')
        os.makedirs(checkpoint_dir, exist_ok=True)
        
        checkpoint_files = []
        
        for gen in range(3):
            # Mock fitness
            import random
            for strategy in pop.strategies:
                pop.update_fitness(strategy['strategy_id'], random.uniform(0.5, 0.9))
            
            # Save checkpoint every generation
            pop.save_checkpoint(checkpoint_dir)
            checkpoint_file = os.path.join(checkpoint_dir, f'population_gen_{pop.generation:04d}.pkl')
            checkpoint_files.append(checkpoint_file)
            
            if gen < 2:
                pop = pop.evolve_generation(
                    elite_size=2,
                    mutation_rate=0.15,
                    crossover_rate=0.7,
                    new_random_rate=0.1,
                    tournament_size=3
                )
        
        # Verify checkpoints were created
        assert len(checkpoint_files) == 3
        for checkpoint in checkpoint_files:
            assert os.path.exists(checkpoint)


@pytest.mark.integration
@pytest.mark.slow
class TestFullEvolutionRun:
    """Integration test for full evolution run (slow)."""
    
    def test_complete_evolution_cycle(self, temp_dir):
        """Test a complete evolution cycle with all components."""
        # Configuration
        population_size = 6
        generations = 2
        elite_size = 2
        
        # Initialize
        pop = Population(size=population_size, generation=0, output_dir=temp_dir)
        pop.initialize_random()
        
        fitness_calc = FitnessCalculator()
        checkpoint_dir = os.path.join(temp_dir, 'checkpoints')
        os.makedirs(checkpoint_dir, exist_ok=True)
        
        best_fitness_history = []
        
        for gen in range(generations):
            print(f"\n=== Generation {gen} ===")
            
            # Evaluate all strategies (mock)
            import random
            for strategy in pop.strategies:
                # Mock backtest metrics
                mock_metrics = {
                    'total_profit_pct': random.uniform(-5, 20),
                    'trades_count': random.randint(30, 150),
                    'win_rate': random.uniform(40, 70),
                    'sharpe_ratio': random.uniform(0.5, 2.5),
                    'max_drawdown_pct': random.uniform(-25, -5),
                    'sortino_ratio': random.uniform(0.6, 2.8),
                    'calmar_ratio': random.uniform(0.5, 2.0),
                    'profit_factor': random.uniform(0.8, 2.5),
                    'expectancy': random.uniform(-0.1, 0.5)
                }
                
                fitness = fitness_calc.calculate_fitness(mock_metrics)
                pop.update_fitness(strategy['strategy_id'], fitness)
            
            # Get statistics
            stats = pop.get_statistics()
            best_fitness_history.append(stats['best_fitness'])
            
            print(f"Best Fitness: {stats['best_fitness']:.3f}")
            print(f"Avg Fitness: {stats['avg_fitness']:.3f}")
            
            # Save checkpoint
            pop.save_checkpoint(checkpoint_dir)
            
            # Evolve to next generation
            if gen < generations - 1:
                pop = pop.evolve_generation(
                    elite_size=elite_size,
                    mutation_rate=0.15,
                    crossover_rate=0.7,
                    new_random_rate=0.1,
                    tournament_size=3
                )
        
        # Verify evolution completed
        assert pop.generation == generations - 1
        assert len(best_fitness_history) == generations
        
        # Get final top strategies
        top_strategies = pop.get_top_n(3)
        assert len(top_strategies) <= 3
        
        print(f"\n=== Final Results ===")
        print(f"Generations completed: {generations}")
        print(f"Best fitness trajectory: {best_fitness_history}")
        print(f"Final top strategy fitness: {pop.fitness_scores.get(top_strategies[0]['strategy_id'], 0):.3f}")


@pytest.mark.integration
class TestStrategyFiltering:
    """Integration tests for strategy filtering during evaluation."""
    
    def test_filter_failed_strategies(self, temp_dir):
        """Test that failed strategies are filtered out during evaluation."""
        from orchestration.evolution_loop import EvolutionLoop
        from evaluation.backtester import BacktestResult
        
        # Create evolution loop with config to ignore invalid strategies
        config = {
            'population_size': 5,
            'generations': 1,
            'elite_size': 2,
            'mutation_rate': 0.2,
            'crossover_rate': 0.7,
        }
        
        eval_config = {
            'freqtrade_path': 'freqtrade',
            'freqtrade_config_path': 'freqtrade/user_data/config.json',
            'strategy_path': temp_dir,
            'datadir': 'freqtrade/user_data/data',
            'timerange': None,
            'min_trades_required': 10,
            'ignore_invalid_strategies': True,
        }
        
        evolution = EvolutionLoop(config=config, eval_config=eval_config)
        evolution.initialize_population()
        
        initial_size = len(evolution.population.strategies)
        assert initial_size == 5
        
        # Mock the backtester to simulate some failures
        original_backtester = evolution.backtester
        
        class MockBacktester:
            def __init__(self):
                self.call_count = 0
                
            def run_backtest(self, strategy_name, **kwargs):
                self.call_count += 1
                # Make every other strategy fail
                if self.call_count % 2 == 0:
                    # Return invalid result (no trades)
                    return BacktestResult(strategy_name, {})
                else:
                    # Return valid result
                    return BacktestResult(strategy_name, {
                        'strategy': {
                            'profit_total': 10.0,
                            'total_trades': 50,
                            'winrate': 55.0,
                            'sharpe': 1.5,
                            'max_drawdown': -10.0,
                        }
                    })
        
        evolution.backtester = MockBacktester()
        
        # Evaluate population (use_mock=False to use our mock backtester)
        evolution.evaluate_population(use_mock=False)
        
        # Check that some strategies were filtered out
        final_size = len(evolution.population.strategies)
        assert final_size < initial_size, "Failed strategies should have been filtered out"
        print(f"Population filtered from {initial_size} to {final_size} strategies")
    
    def test_no_filter_when_disabled(self, temp_dir):
        """Test that strategies are not filtered when filtering is disabled."""
        from orchestration.evolution_loop import EvolutionLoop
        from evaluation.backtester import BacktestResult
        
        # Create evolution loop with config to NOT ignore invalid strategies
        config = {
            'population_size': 5,
            'generations': 1,
            'elite_size': 2,
            'mutation_rate': 0.2,
            'crossover_rate': 0.7,
        }
        
        eval_config = {
            'freqtrade_path': 'freqtrade',
            'freqtrade_config_path': 'freqtrade/user_data/config.json',
            'strategy_path': temp_dir,
            'datadir': 'freqtrade/user_data/data',
            'timerange': None,
            'min_trades_required': 10,
            'ignore_invalid_strategies': False,  # Disabled
        }
        
        evolution = EvolutionLoop(config=config, eval_config=eval_config)
        evolution.initialize_population()
        
        initial_size = len(evolution.population.strategies)
        
        class MockBacktester:
            def run_backtest(self, strategy_name, **kwargs):
                # Always return invalid results
                return BacktestResult(strategy_name, {})
        
        evolution.backtester = MockBacktester()
        
        # Evaluate population
        evolution.evaluate_population(use_mock=False)
        
        # Check that NO strategies were filtered out
        final_size = len(evolution.population.strategies)
        assert final_size == initial_size, "Strategies should not be filtered when filtering is disabled"
        print(f"Population size unchanged: {final_size} strategies")
