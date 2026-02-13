"""
Unit tests for visualization module.
"""

import sys
import os
import pytest
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.visualization import EvolutionVisualizer
from storage.strategy_db import StrategyDB


class TestEvolutionVisualizer:
    """Test suite for EvolutionVisualizer"""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database with sample data"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.db') as f:
            db_path = f.name
        
        db = StrategyDB(db_path)
        
        # Add sample generation data
        for gen in range(10):
            db.save_generation(gen, {
                'best_fitness': 0.5 + gen * 0.05,
                'avg_fitness': 0.3 + gen * 0.03,
                'best_profit': 10 + gen * 2,
                'population_size': 20,
                'diversity': 0.7 - gen * 0.02
            })
        
        # Add sample strategy results
        for i in range(20):
            gen = i // 2
            db.save_result(
                strategy_name=f"strategy_{i}",
                generation=gen,
                fitness=0.5 + i * 0.01,
                metrics={
                    'total_profit_pct': 10 + i * 2,
                    'sharpe_ratio': 1.0 + i * 0.1,
                    'max_drawdown': -5 - i * 0.5,
                    'win_rate': 50 + i * 2,
                    'trades_count': 100 + i * 5
                }
            )
        
        yield db
        
        # Cleanup
        os.unlink(db_path)
    
    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary output directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    def test_visualizer_init(self, temp_db, temp_output_dir):
        """Test visualizer initialization"""
        visualizer = EvolutionVisualizer(temp_db, temp_output_dir)
        
        assert visualizer.db == temp_db
        assert visualizer.output_dir == Path(temp_output_dir)
        assert visualizer.output_dir.exists()
    
    def test_plot_fitness_over_generations(self, temp_db, temp_output_dir):
        """Test fitness evolution plot"""
        visualizer = EvolutionVisualizer(temp_db, temp_output_dir)
        
        plot_path = visualizer.plot_fitness_over_generations()
        
        assert plot_path is not None
        assert os.path.exists(plot_path)
        assert plot_path.endswith('.png')
    
    def test_plot_performance_comparison(self, temp_db, temp_output_dir):
        """Test performance comparison plot"""
        visualizer = EvolutionVisualizer(temp_db, temp_output_dir)
        
        plot_path = visualizer.plot_performance_comparison(top_n=10)
        
        assert plot_path is not None
        assert os.path.exists(plot_path)
    
    def test_plot_population_diversity(self, temp_db, temp_output_dir):
        """Test population diversity plot"""
        visualizer = EvolutionVisualizer(temp_db, temp_output_dir)
        
        plot_path = visualizer.plot_population_diversity()
        
        assert plot_path is not None
        assert os.path.exists(plot_path)
    
    def test_create_top_strategies_dashboard(self, temp_db, temp_output_dir):
        """Test dashboard creation"""
        visualizer = EvolutionVisualizer(temp_db, temp_output_dir)
        
        plot_path = visualizer.create_top_strategies_dashboard(top_n=10)
        
        assert plot_path is not None
        assert os.path.exists(plot_path)
    
    def test_generate_all_plots(self, temp_db, temp_output_dir):
        """Test generating all plots at once"""
        visualizer = EvolutionVisualizer(temp_db, temp_output_dir)
        
        plots = visualizer.generate_all_plots()
        
        assert isinstance(plots, dict)
        assert 'fitness_evolution' in plots
        assert 'performance_comparison' in plots
        assert 'population_diversity' in plots
        assert 'dashboard' in plots
        
        # Check all plots were created
        for plot_type, plot_path in plots.items():
            if plot_path:
                assert os.path.exists(plot_path), f"Plot {plot_type} not created"
    
    def test_visualizer_without_db(self, temp_output_dir):
        """Test visualizer handles missing database gracefully"""
        visualizer = EvolutionVisualizer(None, temp_output_dir)
        
        # Should return None but not crash
        plot_path = visualizer.plot_fitness_over_generations()
        assert plot_path is None
    
    def test_custom_save_path(self, temp_db, temp_output_dir):
        """Test custom save path"""
        visualizer = EvolutionVisualizer(temp_db, temp_output_dir)
        
        custom_path = os.path.join(temp_output_dir, "custom_plot.png")
        plot_path = visualizer.plot_fitness_over_generations(save_path=custom_path)
        
        assert plot_path == custom_path
        assert os.path.exists(custom_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
