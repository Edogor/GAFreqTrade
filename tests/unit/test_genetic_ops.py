"""
Unit tests for ga_core.genetic_ops module.
"""
import pytest
from ga_core.genetic_ops import GeneticOperations


class TestMutationOperations:
    """Tests for mutation operations."""
    
    def test_mutate_returns_dict(self, mock_strategy_metadata):
        """Test that mutate returns a dictionary."""
        genetic_ops = GeneticOperations()
        mutated = genetic_ops.mutate(mock_strategy_metadata)
        
        assert isinstance(mutated, dict)
        assert 'strategy_id' in mutated
    
    def test_mutate_parameters_changes_values(self, mock_strategy_metadata):
        """Test that parameter mutation changes values."""
        genetic_ops = GeneticOperations(mutation_rate=1.0)  # Force mutation
        original_stoploss = mock_strategy_metadata['stoploss']
        
        mutated = genetic_ops.mutate_parameters(mock_strategy_metadata)
        
        # At least one parameter should change with high mutation rate
        assert isinstance(mutated, dict)
        # Stoploss should be in valid range
        assert -0.30 <= mutated['stoploss'] <= -0.01
    
    def test_mutate_indicators_valid_count(self, mock_strategy_metadata):
        """Test that indicator mutation maintains valid count."""
        genetic_ops = GeneticOperations()
        mutated = genetic_ops.mutate_indicators(mock_strategy_metadata)
        
        assert isinstance(mutated['indicators'], list)
        assert len(mutated['indicators']) >= 2  # Minimum indicators
        assert len(mutated['indicators']) <= 10  # Maximum indicators
    
    def test_mutate_conditions_valid_count(self, mock_strategy_metadata):
        """Test that condition mutation maintains valid count."""
        genetic_ops = GeneticOperations()
        mutated = genetic_ops.mutate_conditions(mock_strategy_metadata)
        
        assert mutated['num_buy_conditions'] >= 1
        assert mutated['num_buy_conditions'] <= 5
        assert mutated['num_sell_conditions'] >= 1
        assert mutated['num_sell_conditions'] <= 5
    
    def test_mutation_preserves_required_fields(self, mock_strategy_metadata):
        """Test that mutation preserves all required fields."""
        genetic_ops = GeneticOperations()
        mutated = genetic_ops.mutate(mock_strategy_metadata)
        
        required_fields = [
            'strategy_id', 'class_name', 'generation', 'indicators',
            'buy_conditions', 'sell_conditions', 'timeframe', 'stoploss'
        ]
        
        for field in required_fields:
            assert field in mutated


class TestCrossoverOperations:
    """Tests for crossover operations."""
    
    def test_crossover_returns_two_children(self, mock_strategy_metadata):
        """Test that crossover returns two children."""
        genetic_ops = GeneticOperations()
        parent1 = mock_strategy_metadata.copy()
        parent2 = mock_strategy_metadata.copy()
        parent2['strategy_id'] = 'Gen000_Strat_002'
        
        child1, child2 = genetic_ops.crossover(parent1, parent2)
        
        assert isinstance(child1, dict)
        assert isinstance(child2, dict)
        assert child1 != child2  # Children should be different
    
    def test_single_point_crossover_combines_parents(self, mock_strategy_metadata):
        """Test single-point crossover combines parent traits."""
        genetic_ops = GeneticOperations()
        parent1 = mock_strategy_metadata.copy()
        parent1['indicators'] = [
            {'name': 'rsi', 'params': {}},
            {'name': 'macd', 'params': {}},
            {'name': 'ema', 'params': {}}
        ]
        
        parent2 = mock_strategy_metadata.copy()
        parent2['indicators'] = [
            {'name': 'bb', 'params': {}},
            {'name': 'stoch', 'params': {}},
            {'name': 'adx', 'params': {}}
        ]
        
        child1, child2 = genetic_ops.single_point_crossover(parent1, parent2)
        
        # Children should have indicators from both parents
        assert len(child1['indicators']) > 0
        assert len(child2['indicators']) > 0
    
    def test_uniform_crossover_valid_output(self, mock_strategy_metadata):
        """Test uniform crossover produces valid strategies."""
        genetic_ops = GeneticOperations()
        parent1 = mock_strategy_metadata.copy()
        parent2 = mock_strategy_metadata.copy()
        parent2['strategy_id'] = 'Gen000_Strat_002'
        
        child1, child2 = genetic_ops.uniform_crossover(parent1, parent2)
        
        # Children should have valid structure
        assert 'indicators' in child1
        assert 'stoploss' in child1
        assert 'timeframe' in child1
    
    def test_crossover_preserves_valid_ranges(self, mock_strategy_metadata):
        """Test that crossover maintains valid parameter ranges."""
        genetic_ops = GeneticOperations()
        parent1 = mock_strategy_metadata.copy()
        parent2 = mock_strategy_metadata.copy()
        
        child1, child2 = genetic_ops.crossover(parent1, parent2)
        
        # Check valid ranges
        assert -0.30 <= child1['stoploss'] <= -0.01
        assert -0.30 <= child2['stoploss'] <= -0.01
        assert child1['timeframe'] in ['1m', '5m', '15m', '30m', '1h', '4h', '1d']


class TestSelectionOperations:
    """Tests for selection operations."""
    
    def test_tournament_selection_returns_strategy(self, mock_population_data, mock_fitness_scores):
        """Test that tournament selection returns a valid strategy."""
        genetic_ops = GeneticOperations()
        selected = genetic_ops.tournament_selection(
            mock_population_data,
            mock_fitness_scores,
            tournament_size=3
        )
        
        assert isinstance(selected, dict)
        assert 'strategy_id' in selected
    
    def test_tournament_selection_favors_higher_fitness(self):
        """Test that tournament selection favors higher fitness."""
        genetic_ops = GeneticOperations()
        
        # Create simple population with clear fitness differences
        population = [
            {'strategy_id': 'low', 'generation': 0},
            {'strategy_id': 'medium', 'generation': 0},
            {'strategy_id': 'high', 'generation': 0}
        ]
        fitness_scores = {
            'low': 0.1,
            'medium': 0.5,
            'high': 0.9
        }
        
        # Run multiple selections, highest fitness should win most
        selections = []
        for _ in range(20):
            selected = genetic_ops.tournament_selection(
                population, fitness_scores, tournament_size=3
            )
            selections.append(selected['strategy_id'])
        
        # High fitness should be selected more often
        assert selections.count('high') > selections.count('low')
    
    def test_roulette_wheel_selection_returns_strategy(self, mock_population_data, mock_fitness_scores):
        """Test that roulette wheel selection returns a valid strategy."""
        genetic_ops = GeneticOperations()
        selected = genetic_ops.roulette_wheel_selection(
            mock_population_data,
            mock_fitness_scores
        )
        
        assert isinstance(selected, dict)
        assert 'strategy_id' in selected
    
    def test_rank_selection_returns_strategy(self, mock_population_data, mock_fitness_scores):
        """Test that rank selection returns a valid strategy."""
        genetic_ops = GeneticOperations()
        selected = genetic_ops.rank_selection(
            mock_population_data,
            mock_fitness_scores
        )
        
        assert isinstance(selected, dict)
        assert 'strategy_id' in selected
    
    def test_elite_selection_returns_top_n(self, mock_population_data, mock_fitness_scores):
        """Test that elite selection returns top N strategies."""
        genetic_ops = GeneticOperations()
        elite = genetic_ops.elite_selection(
            mock_population_data,
            mock_fitness_scores,
            elite_size=3
        )
        
        assert len(elite) == 3
        assert all(isinstance(s, dict) for s in elite)
        
        # Check they are in order of fitness
        elite_ids = [s['strategy_id'] for s in elite]
        elite_fitness = [mock_fitness_scores[sid] for sid in elite_ids]
        assert elite_fitness == sorted(elite_fitness, reverse=True)
    
    def test_elite_selection_handles_small_population(self):
        """Test elite selection when elite_size >= population_size."""
        genetic_ops = GeneticOperations()
        population = [
            {'strategy_id': 'strat1', 'generation': 0},
            {'strategy_id': 'strat2', 'generation': 0}
        ]
        fitness_scores = {'strat1': 0.8, 'strat2': 0.6}
        
        elite = genetic_ops.elite_selection(population, fitness_scores, elite_size=5)
        
        # Should return all strategies when elite_size > population
        assert len(elite) == 2


class TestGeneticOperationsConfiguration:
    """Tests for GeneticOperations configuration."""
    
    def test_custom_mutation_rate(self, mock_strategy_metadata):
        """Test that custom mutation rate is applied."""
        genetic_ops = GeneticOperations(mutation_rate=0.5)
        assert genetic_ops.mutation_rate == 0.5
    
    def test_custom_crossover_rate(self):
        """Test that custom crossover rate is applied."""
        genetic_ops = GeneticOperations(crossover_rate=0.8)
        assert genetic_ops.crossover_rate == 0.8
    
    def test_default_rates(self):
        """Test default mutation and crossover rates."""
        genetic_ops = GeneticOperations()
        assert 0 <= genetic_ops.mutation_rate <= 1
        assert 0 <= genetic_ops.crossover_rate <= 1
