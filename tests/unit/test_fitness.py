"""
Unit tests for evaluation.fitness module.
"""
import pytest
from evaluation.fitness import FitnessCalculator, calculate_fitness


class TestFitnessCalculator:
    """Tests for FitnessCalculator class."""
    
    def test_initialization_default_weights(self):
        """Test FitnessCalculator with default weights."""
        calc = FitnessCalculator()
        
        assert calc.weights['profit'] > 0
        assert calc.weights['sharpe'] > 0
        assert calc.weights['drawdown'] > 0
        # Weights should sum to approximately 1.0
        assert 0.99 <= sum(calc.weights.values()) <= 1.01
    
    def test_initialization_custom_weights(self):
        """Test FitnessCalculator with custom weights."""
        custom_weights = {
            'profit': 0.5,
            'sharpe': 0.2,
            'drawdown': 0.3
        }
        calc = FitnessCalculator(weights=custom_weights)
        
        assert calc.weights['profit'] == 0.5
        assert calc.weights['sharpe'] == 0.2
    
    def test_calculate_fitness_returns_float(self, mock_backtest_metrics):
        """Test that calculate_fitness returns a float."""
        calc = FitnessCalculator()
        fitness = calc.calculate_fitness(mock_backtest_metrics)
        
        assert isinstance(fitness, float)
        assert 0.0 <= fitness <= 1.0
    
    def test_calculate_fitness_positive_metrics(self):
        """Test fitness calculation with positive metrics."""
        calc = FitnessCalculator()
        metrics = {
            'total_profit_pct': 20.0,
            'trades_count': 100,
            'win_rate': 65.0,
            'sharpe_ratio': 2.0,
            'sortino_ratio': 2.5,
            'calmar_ratio': 1.8,
            'max_drawdown_pct': -8.0,
            'profit_factor': 2.0,
            'expectancy': 0.5
        }
        
        fitness = calc.calculate_fitness(metrics)
        assert fitness > 0.5  # Should be relatively high
    
    def test_calculate_fitness_negative_metrics(self):
        """Test fitness calculation with poor metrics."""
        calc = FitnessCalculator()
        metrics = {
            'total_profit_pct': -10.0,
            'trades_count': 50,
            'win_rate': 30.0,
            'sharpe_ratio': -0.5,
            'sortino_ratio': -0.3,
            'calmar_ratio': -0.2,
            'max_drawdown_pct': -25.0,
            'profit_factor': 0.5,
            'expectancy': -0.2
        }
        
        fitness = calc.calculate_fitness(metrics)
        assert fitness < 0.3  # Should be relatively low
    
    def test_fitness_profit_component(self, mock_backtest_metrics):
        """Test profit fitness component calculation."""
        calc = FitnessCalculator()
        profit_fitness = calc._fitness_profit(mock_backtest_metrics)
        
        assert isinstance(profit_fitness, float)
        assert 0.0 <= profit_fitness <= 1.0
    
    def test_fitness_sharpe_component(self, mock_backtest_metrics):
        """Test Sharpe ratio fitness component."""
        calc = FitnessCalculator()
        sharpe_fitness = calc._fitness_sharpe(mock_backtest_metrics)
        
        assert isinstance(sharpe_fitness, float)
        assert 0.0 <= sharpe_fitness <= 1.0
    
    def test_fitness_drawdown_component(self, mock_backtest_metrics):
        """Test drawdown fitness component."""
        calc = FitnessCalculator()
        drawdown_fitness = calc._fitness_drawdown(mock_backtest_metrics)
        
        assert isinstance(drawdown_fitness, float)
        assert 0.0 <= drawdown_fitness <= 1.0
        # Lower drawdown should give higher fitness
    
    def test_fitness_winrate_component(self, mock_backtest_metrics):
        """Test win rate fitness component."""
        calc = FitnessCalculator()
        winrate_fitness = calc._fitness_winrate(mock_backtest_metrics)
        
        assert isinstance(winrate_fitness, float)
        assert 0.0 <= winrate_fitness <= 1.0
    
    def test_fitness_stability_component(self, mock_backtest_metrics):
        """Test stability fitness component."""
        calc = FitnessCalculator()
        stability_fitness = calc._fitness_stability(mock_backtest_metrics)
        
        assert isinstance(stability_fitness, float)
        assert 0.0 <= stability_fitness <= 1.0
    
    def test_fitness_trade_count_component(self):
        """Test trade count fitness component."""
        calc = FitnessCalculator()
        
        # Optimal range (30-200 trades)
        metrics_optimal = {'trades_count': 100}
        fitness_optimal = calc._fitness_trade_count(metrics_optimal)
        assert fitness_optimal > 0.8
        
        # Too few trades
        metrics_few = {'trades_count': 5}
        fitness_few = calc._fitness_trade_count(metrics_few)
        assert fitness_few < 0.5
        
        # Too many trades
        metrics_many = {'trades_count': 500}
        fitness_many = calc._fitness_trade_count(metrics_many)
        assert fitness_many < fitness_optimal
    
    def test_apply_penalties_losing_strategy(self):
        """Test penalties for losing strategies."""
        calc = FitnessCalculator()
        metrics = {
            'total_profit_pct': -5.0,
            'max_drawdown_pct': -15.0,
            'win_rate': 40.0,
            'trades_count': 50
        }
        
        fitness_before = 0.5
        fitness_after = calc._apply_penalties(fitness_before, metrics)
        
        # Penalty should reduce fitness
        assert fitness_after < fitness_before
    
    def test_apply_penalties_high_drawdown(self):
        """Test penalties for high drawdown."""
        calc = FitnessCalculator()
        metrics = {
            'total_profit_pct': 10.0,
            'max_drawdown_pct': -30.0,  # High drawdown
            'win_rate': 50.0,
            'trades_count': 100
        }
        
        fitness_before = 0.7
        fitness_after = calc._apply_penalties(fitness_before, metrics)
        
        # Penalty may or may not reduce depending on threshold
        assert isinstance(fitness_after, float)
        assert 0.0 <= fitness_after <= 1.0
    
    def test_apply_penalties_low_trades(self):
        """Test penalties for too few trades."""
        calc = FitnessCalculator()
        metrics = {
            'total_profit_pct': 10.0,
            'max_drawdown_pct': -10.0,
            'win_rate': 60.0,
            'trades_count': 5  # Too few
        }
        
        fitness_before = 0.7
        fitness_after = calc._apply_penalties(fitness_before, metrics)
        
        assert fitness_after < fitness_before
    
    def test_normalize_function(self):
        """Test normalization function."""
        calc = FitnessCalculator()
        
        # Test profit normalization
        norm_value = calc._normalize(10.0, 'profit', invert=False)
        assert 0.0 <= norm_value <= 1.0
        
        # Test drawdown normalization (inverted)
        norm_value = calc._normalize(-10.0, 'drawdown', invert=True)
        assert 0.0 <= norm_value <= 1.0
    
    def test_multi_objective_fitness(self, mock_backtest_metrics):
        """Test multi-objective fitness calculation."""
        calc = FitnessCalculator()
        objectives = calc.calculate_multi_objective_fitness(mock_backtest_metrics)
        
        assert isinstance(objectives, dict)
        assert 'profit' in objectives
        assert 'sharpe' in objectives
        assert 'drawdown' in objectives
        assert all(0.0 <= v <= 1.0 for v in objectives.values())
    
    def test_compare_strategies_better(self):
        """Test strategy comparison when first is better."""
        calc = FitnessCalculator()
        
        metrics1 = {
            'total_profit_pct': 20.0,
            'sharpe_ratio': 2.0,
            'max_drawdown_pct': -10.0,
            'win_rate': 60.0,
            'trades_count': 100
        }
        
        metrics2 = {
            'total_profit_pct': 10.0,
            'sharpe_ratio': 1.0,
            'max_drawdown_pct': -15.0,
            'win_rate': 50.0,
            'trades_count': 80
        }
        
        result = calc.compare_strategies(metrics1, metrics2)
        assert result == 1  # metrics1 is better
    
    def test_compare_strategies_worse(self):
        """Test strategy comparison when first is worse."""
        calc = FitnessCalculator()
        
        metrics1 = {
            'total_profit_pct': 5.0,
            'sharpe_ratio': 0.5,
            'max_drawdown_pct': -20.0,
            'win_rate': 45.0,
            'trades_count': 50
        }
        
        metrics2 = {
            'total_profit_pct': 15.0,
            'sharpe_ratio': 1.8,
            'max_drawdown_pct': -10.0,
            'win_rate': 55.0,
            'trades_count': 100
        }
        
        result = calc.compare_strategies(metrics1, metrics2)
        assert result == -1  # metrics1 is worse


class TestCalculateFitnessFunction:
    """Tests for standalone calculate_fitness function."""
    
    def test_calculate_fitness_function(self, mock_backtest_metrics):
        """Test standalone calculate_fitness function."""
        fitness = calculate_fitness(mock_backtest_metrics)
        
        assert isinstance(fitness, float)
        assert 0.0 <= fitness <= 1.0
    
    def test_calculate_fitness_with_custom_weights(self, mock_backtest_metrics):
        """Test calculate_fitness with custom weights."""
        custom_weights = {
            'profit': 0.5,
            'sharpe': 0.3,
            'drawdown': 0.2
        }
        
        fitness = calculate_fitness(mock_backtest_metrics, weights=custom_weights)
        assert isinstance(fitness, float)
    
    def test_missing_metrics_handled(self):
        """Test that missing metrics are handled gracefully."""
        incomplete_metrics = {
            'total_profit_pct': 10.0,
            'trades_count': 50
            # Missing other metrics
        }
        
        calc = FitnessCalculator()
        fitness = calc.calculate_fitness(incomplete_metrics)
        
        # Should still return a valid fitness score
        assert isinstance(fitness, float)
        assert 0.0 <= fitness <= 1.0
