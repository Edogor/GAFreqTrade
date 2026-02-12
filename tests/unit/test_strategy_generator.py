"""
Unit tests for ga_core.strategy_generator module.
"""
import os
import pytest
from ga_core.strategy_generator import (
    IndicatorLibrary,
    ConditionGenerator,
    StrategyGenerator,
    generate_initial_population
)


class TestIndicatorLibrary:
    """Tests for IndicatorLibrary class."""
    
    def test_get_random_indicators_returns_list(self):
        """Test that get_random_indicators returns a list."""
        indicators = IndicatorLibrary.get_random_indicators(3, 5)
        assert isinstance(indicators, list)
        assert 3 <= len(indicators) <= 5
    
    def test_get_random_indicators_min_max_count(self):
        """Test that indicator count respects min and max."""
        indicators = IndicatorLibrary.get_random_indicators(2, 2)
        assert len(indicators) == 2
        
        indicators = IndicatorLibrary.get_random_indicators(5, 8)
        assert 5 <= len(indicators) <= 8
    
    def test_indicators_have_required_fields(self):
        """Test that each indicator has name and params."""
        indicators = IndicatorLibrary.get_random_indicators(3, 5)
        for indicator in indicators:
            assert 'name' in indicator
            assert 'params' in indicator
            assert isinstance(indicator['name'], str)
            assert isinstance(indicator['params'], dict)
    
    def test_no_duplicate_indicators(self):
        """Test that returned indicators are unique."""
        indicators = IndicatorLibrary.get_random_indicators(5, 10)
        indicator_names = [ind['name'] for ind in indicators]
        assert len(indicator_names) == len(set(indicator_names))


class TestConditionGenerator:
    """Tests for ConditionGenerator class."""
    
    def test_generate_conditions_returns_tuple(self):
        """Test that generate_conditions returns proper tuple."""
        indicators = [
            {'key': 'rsi', 'name': 'RSI', 'params': {'timeperiod': 14}, 'selected_params': {'timeperiod': 14}},
            {'key': 'macd', 'name': 'MACD', 'params': {}, 'selected_params': {}}
        ]
        result = ConditionGenerator.generate_conditions(indicators, 1, 2)
        
        assert isinstance(result, tuple)
        assert len(result) == 3  # buy_conditions, sell_conditions, hyperopt_params
    
    def test_generate_conditions_count(self):
        """Test that correct number of conditions are generated."""
        indicators = [
            {'key': 'rsi', 'name': 'RSI', 'params': {}, 'selected_params': {}},
            {'key': 'macd', 'name': 'MACD', 'params': {}, 'selected_params': {}},
        ]
        buy_conds, sell_conds, params = ConditionGenerator.generate_conditions(
            indicators, 1, 1
        )
        
        assert len(buy_conds) >= 1
        assert len(sell_conds) >= 1
        assert isinstance(params, dict)
    
    def test_conditions_are_strings(self):
        """Test that conditions are valid strings."""
        indicators = [
            {'key': 'rsi', 'name': 'RSI', 'params': {'timeperiod': 14}, 'selected_params': {'timeperiod': 14}}
        ]
        buy_conds, sell_conds, _ = ConditionGenerator.generate_conditions(
            indicators, 1, 1
        )
        
        assert all(isinstance(cond, str) for cond in buy_conds)
        assert all(isinstance(cond, str) for cond in sell_conds)
        assert all(len(cond) > 0 for cond in buy_conds)


class TestStrategyGenerator:
    """Tests for StrategyGenerator class."""
    
    def test_initialization(self, temp_dir):
        """Test StrategyGenerator initialization."""
        generator = StrategyGenerator(output_dir=temp_dir)
        assert generator.output_dir == temp_dir
        assert os.path.exists(temp_dir)
    
    def test_generate_random_strategy_returns_dict(self, temp_dir):
        """Test that generate_random_strategy returns proper dict."""
        generator = StrategyGenerator(output_dir=temp_dir)
        strategy = generator.generate_random_strategy(
            generation=0,
            strategy_num=1,
            min_indicators=3,
            max_indicators=5,
            min_conditions=1,
            max_conditions=3
        )
        
        assert isinstance(strategy, dict)
        assert 'strategy_id' in strategy
        assert 'class_name' in strategy
        assert 'generation' in strategy
        assert 'indicators' in strategy
        assert 'file_path' in strategy
    
    def test_generate_random_strategy_creates_file(self, temp_dir):
        """Test that strategy file is created."""
        generator = StrategyGenerator(output_dir=temp_dir)
        strategy = generator.generate_random_strategy(0, 1)
        
        assert os.path.exists(strategy['file_path'])
        assert strategy['file_path'].endswith('.py')
    
    def test_strategy_file_is_valid_python(self, temp_dir):
        """Test that generated strategy is valid Python code."""
        generator = StrategyGenerator(output_dir=temp_dir)
        strategy = generator.generate_random_strategy(0, 1)
        
        # Try to compile the generated code
        with open(strategy['file_path'], 'r') as f:
            code = f.read()
        
        # Should not raise SyntaxError
        compile(code, strategy['file_path'], 'exec')
    
    def test_strategy_contains_required_methods(self, temp_dir):
        """Test that generated strategy has required Freqtrade methods."""
        generator = StrategyGenerator(output_dir=temp_dir)
        strategy = generator.generate_random_strategy(0, 1)
        
        with open(strategy['file_path'], 'r') as f:
            code = f.read()
        
        # Check for required methods
        assert 'def populate_indicators' in code
        assert 'def populate_entry_trend' in code
        assert 'def populate_exit_trend' in code
        assert 'IStrategy' in code
    
    def test_strategy_id_format(self, temp_dir):
        """Test strategy ID format."""
        generator = StrategyGenerator(output_dir=temp_dir)
        strategy = generator.generate_random_strategy(5, 42)
        
        assert strategy['strategy_id'] == 'Gen005_Strat_042'
        assert strategy['generation'] == 5
        assert strategy['strategy_num'] == 42
    
    def test_generate_minimal_roi_returns_dict(self, temp_dir):
        """Test that minimal ROI is generated correctly."""
        generator = StrategyGenerator(output_dir=temp_dir)
        strategy = generator.generate_random_strategy(0, 1)
        
        # ROI is generated but might not be in the metadata dict
        # The actual implementation writes it to the file
        assert 'strategy_id' in strategy
        assert 'file_path' in strategy
        # Read the generated file to check for ROI
        with open(strategy['file_path'], 'r') as f:
            code = f.read()
            assert 'minimal_roi' in code
    
    def test_multiple_strategies_unique(self, temp_dir):
        """Test that multiple generated strategies are unique."""
        generator = StrategyGenerator(output_dir=temp_dir)
        strategy1 = generator.generate_random_strategy(0, 1)
        strategy2 = generator.generate_random_strategy(0, 2)
        
        assert strategy1['strategy_id'] != strategy2['strategy_id']
        assert strategy1['file_path'] != strategy2['file_path']


class TestGenerateInitialPopulation:
    """Tests for generate_initial_population function."""
    
    def test_generate_initial_population_count(self, temp_dir):
        """Test that correct number of strategies are generated."""
        population = generate_initial_population(
            population_size=10,
            output_dir=temp_dir
        )
        
        assert len(population) == 10
    
    def test_generate_initial_population_all_valid(self, temp_dir):
        """Test that all generated strategies are valid."""
        population = generate_initial_population(5, temp_dir)
        
        for strategy in population:
            assert 'strategy_id' in strategy
            assert 'file_path' in strategy
            assert os.path.exists(strategy['file_path'])
    
    def test_generate_initial_population_unique_ids(self, temp_dir):
        """Test that all strategies have unique IDs."""
        population = generate_initial_population(10, temp_dir)
        strategy_ids = [s['strategy_id'] for s in population]
        
        assert len(strategy_ids) == len(set(strategy_ids))
