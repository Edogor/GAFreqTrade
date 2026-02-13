"""
Unit tests for ga_core.population module.
"""
import os
import pytest
from ga_core.population import Population


class TestPopulationInitialization:
    """Tests for Population initialization."""
    
    def test_population_init(self, temp_dir):
        """Test Population initialization."""
        pop = Population(size=10, generation=0, output_dir=temp_dir)
        
        assert pop.size == 10
        assert pop.generation == 0
        assert pop.output_dir == temp_dir
        assert len(pop.strategies) == 0
    
    def test_population_init_default_generation(self, temp_dir):
        """Test Population with default generation."""
        pop = Population(size=20, output_dir=temp_dir)
        
        assert pop.generation == 0


class TestPopulationRandomInitialization:
    """Tests for random population initialization."""
    
    def test_initialize_random_creates_strategies(self, temp_dir):
        """Test that initialize_random creates strategies."""
        pop = Population(size=5, generation=0, output_dir=temp_dir)
        pop.initialize_random()
        
        assert len(pop.strategies) == 5
    
    def test_initialize_random_all_valid(self, temp_dir):
        """Test that all randomly initialized strategies are valid."""
        pop = Population(size=3, generation=0, output_dir=temp_dir)
        pop.initialize_random()
        
        for strategy in pop.strategies:
            assert 'strategy_id' in strategy
            assert 'file_path' in strategy
            assert os.path.exists(strategy['file_path'])
    
    def test_initialize_random_unique_ids(self, temp_dir):
        """Test that all strategies have unique IDs."""
        pop = Population(size=10, generation=0, output_dir=temp_dir)
        pop.initialize_random()
        
        strategy_ids = [s['strategy_id'] for s in pop.strategies]
        assert len(strategy_ids) == len(set(strategy_ids))


class TestPopulationManagement:
    """Tests for population management methods."""
    
    def test_add_strategy(self, temp_dir, mock_strategy_metadata):
        """Test adding a strategy to population."""
        pop = Population(size=10, generation=0, output_dir=temp_dir)
        pop.add_strategy(mock_strategy_metadata, fitness=0.85, parents=None)
        
        assert len(pop.strategies) == 1
        assert pop.strategies[0]['strategy_id'] == mock_strategy_metadata['strategy_id']
    
    def test_add_strategy_with_fitness(self, temp_dir, mock_strategy_metadata):
        """Test adding strategy with fitness score."""
        pop = Population(size=10, generation=0, output_dir=temp_dir)
        pop.add_strategy(mock_strategy_metadata, fitness=0.75)
        
        assert pop.fitness_scores[mock_strategy_metadata['strategy_id']] == 0.75
    
    def test_update_fitness(self, temp_dir, mock_strategy_metadata):
        """Test updating fitness score."""
        pop = Population(size=10, generation=0, output_dir=temp_dir)
        pop.add_strategy(mock_strategy_metadata, fitness=0.5)
        
        pop.update_fitness(mock_strategy_metadata['strategy_id'], 0.9)
        
        assert pop.fitness_scores[mock_strategy_metadata['strategy_id']] == 0.9
    
    def test_get_strategy(self, temp_dir, mock_strategy_metadata):
        """Test retrieving a strategy by ID."""
        pop = Population(size=10, generation=0, output_dir=temp_dir)
        pop.add_strategy(mock_strategy_metadata, fitness=0.8)
        
        retrieved = pop.get_strategy(mock_strategy_metadata['strategy_id'])
        
        assert retrieved is not None
        assert retrieved['strategy_id'] == mock_strategy_metadata['strategy_id']
    
    def test_get_strategy_not_found(self, temp_dir):
        """Test retrieving non-existent strategy."""
        pop = Population(size=10, generation=0, output_dir=temp_dir)
        
        retrieved = pop.get_strategy('NonExistent_ID')
        
        assert retrieved is None
    
    def test_get_top_n(self, temp_dir, mock_population_data, mock_fitness_scores):
        """Test getting top N strategies."""
        pop = Population(size=10, generation=0, output_dir=temp_dir)
        
        for strategy in mock_population_data:
            pop.add_strategy(
                strategy,
                fitness=mock_fitness_scores[strategy['strategy_id']]
            )
        
        top_3 = pop.get_top_n(3)
        
        assert len(top_3) == 3
        # Should be sorted by fitness (descending)
        assert top_3[0]['strategy_id'] == 'Gen000_Strat_003'  # fitness 0.91
        assert top_3[1]['strategy_id'] == 'Gen000_Strat_001'  # fitness 0.85
        assert top_3[2]['strategy_id'] == 'Gen000_Strat_005'  # fitness 0.79
    
    def test_get_top_n_exceeds_population(self, temp_dir, mock_population_data, mock_fitness_scores):
        """Test getting more strategies than population size."""
        pop = Population(size=10, generation=0, output_dir=temp_dir)
        
        for strategy in mock_population_data:
            pop.add_strategy(
                strategy,
                fitness=mock_fitness_scores[strategy['strategy_id']]
            )
        
        top_10 = pop.get_top_n(10)
        
        # Should return all available strategies
        assert len(top_10) == 5


class TestPopulationStatistics:
    """Tests for population statistics."""
    
    def test_get_statistics_empty(self, temp_dir):
        """Test statistics for empty population."""
        pop = Population(size=10, generation=0, output_dir=temp_dir)
        stats = pop.get_statistics()
        
        assert stats['generation'] == 0
        assert stats['size'] == 0  # size reflects actual strategies count, not max
        assert stats['evaluated'] == 0
        assert stats.get('best_fitness') is None
        assert stats.get('avg_fitness') is None
    
    def test_get_statistics_with_strategies(self, temp_dir, mock_population_data, mock_fitness_scores):
        """Test statistics with strategies."""
        pop = Population(size=10, generation=2, output_dir=temp_dir)
        
        for strategy in mock_population_data:
            pop.add_strategy(
                strategy,
                fitness=mock_fitness_scores[strategy['strategy_id']]
            )
        
        stats = pop.get_statistics()
        
        assert stats['generation'] == 2
        assert stats['size'] == 5  # 5 strategies were added
        assert stats['evaluated'] == 5
        assert stats['best_fitness'] == 0.91  # Max fitness
        assert 0.7 < stats['avg_fitness'] < 0.8  # Average of fitness scores
        assert stats['worst_fitness'] == 0.68  # Min fitness


class TestPopulationEvolution:
    """Tests for population evolution."""
    
    def test_evolve_generation_creates_new_population(self, temp_dir):
        """Test that evolve_generation creates a new population."""
        pop = Population(size=10, generation=0, output_dir=temp_dir)
        pop.initialize_random()
        
        # Add fitness scores
        for strategy in pop.strategies:
            pop.update_fitness(strategy['strategy_id'], 0.5)
        
        new_pop = pop.evolve_generation(
            elite_size=2,
            mutation_rate=0.1,
            crossover_rate=0.7,
            new_random_rate=0.1,
            tournament_size=3
        )
        
        assert isinstance(new_pop, Population)
        assert new_pop.generation == pop.generation + 1
        assert len(new_pop.strategies) == pop.size
    
    def test_evolve_generation_preserves_elite(self, temp_dir, mock_population_data, mock_fitness_scores):
        """Test that elite strategies are preserved."""
        pop = Population(size=10, generation=0, output_dir=temp_dir)
        
        for strategy in mock_population_data:
            pop.add_strategy(
                strategy,
                fitness=mock_fitness_scores[strategy['strategy_id']]
            )
        
        # Get top strategies before evolution
        top_before = pop.get_top_n(2)
        top_ids_before = set([s['strategy_id'] for s in top_before])
        
        new_pop = pop.evolve_generation(
            elite_size=2,
            mutation_rate=0.1,
            crossover_rate=0.7,
            new_random_rate=0.0,  # No random to make test deterministic
            tournament_size=3
        )
        
        # Elite should be in new population
        new_ids = set([s['strategy_id'] for s in new_pop.strategies])
        # At least one elite should be preserved
        assert len(top_ids_before & new_ids) >= 1


class TestPopulationCheckpointing:
    """Tests for population checkpointing."""
    
    def test_save_checkpoint_creates_files(self, temp_dir):
        """Test that save_checkpoint creates files."""
        pop = Population(size=5, generation=0, output_dir=temp_dir)
        pop.initialize_random()
        
        checkpoint_dir = os.path.join(temp_dir, 'checkpoints')
        os.makedirs(checkpoint_dir, exist_ok=True)
        
        pop.save_checkpoint(checkpoint_dir)
        
        # Should create checkpoint files
        assert len(os.listdir(checkpoint_dir)) > 0
    
    def test_load_checkpoint_restores_population(self, temp_dir):
        """Test that load_checkpoint restores population."""
        # Create and save a population
        pop1 = Population(size=5, generation=3, output_dir=temp_dir)
        pop1.initialize_random()
        
        for strategy in pop1.strategies:
            pop1.update_fitness(strategy['strategy_id'], 0.7)
        
        checkpoint_dir = os.path.join(temp_dir, 'checkpoints')
        os.makedirs(checkpoint_dir, exist_ok=True)
        
        pop1.save_checkpoint(checkpoint_dir)
        
        # Find the checkpoint file
        checkpoint_file = os.path.join(checkpoint_dir, f'population_gen_{pop1.generation:04d}.pkl')
        assert os.path.exists(checkpoint_file)
        
        # Load the checkpoint
        pop2 = Population.load_checkpoint(checkpoint_file, output_dir=temp_dir)
        
        assert pop2.generation == 3
        assert pop2.size == 5
        assert len(pop2.strategies) == 5
    
    def test_checkpoint_preserves_fitness(self, temp_dir):
        """Test that checkpointing preserves fitness scores."""
        pop1 = Population(size=3, generation=0, output_dir=temp_dir)
        pop1.initialize_random()
        
        # Set specific fitness scores
        fitness_map = {}
        for i, strategy in enumerate(pop1.strategies):
            fitness = 0.5 + i * 0.1
            pop1.update_fitness(strategy['strategy_id'], fitness)
            fitness_map[strategy['strategy_id']] = fitness
        
        checkpoint_dir = os.path.join(temp_dir, 'checkpoints')
        os.makedirs(checkpoint_dir, exist_ok=True)
        
        pop1.save_checkpoint(checkpoint_dir)
        
        # Find and load checkpoint
        checkpoint_file = os.path.join(checkpoint_dir, f'population_gen_{pop1.generation:04d}.pkl')
        pop2 = Population.load_checkpoint(checkpoint_file, output_dir=temp_dir)
        
        # Check fitness scores are preserved
        for strategy_id, fitness in fitness_map.items():
            assert pop2.fitness_scores.get(strategy_id) == fitness
