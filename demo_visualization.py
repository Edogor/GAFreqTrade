#!/usr/bin/env python3
"""
Demo: Visualization Example

This script creates a sample database with mock data and generates
all visualization plots to demonstrate the visualization capabilities.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tempfile
import random
from pathlib import Path
from storage.strategy_db import StrategyDB
from utils.visualization import EvolutionVisualizer


def create_sample_data(db_path: str, generations: int = 20, strategies_per_gen: int = 5):
    """
    Create sample evolution data for demonstration.
    
    Args:
        db_path: Path to database file
        generations: Number of generations to simulate
        strategies_per_gen: Number of strategies per generation
    """
    print(f"Creating sample database with {generations} generations...")
    
    db = StrategyDB(db_path)
    
    # Simulate evolution over generations
    base_fitness = 0.3
    base_profit = 5.0
    diversity = 0.8
    
    for gen in range(generations):
        # Evolution improves over time (with some noise)
        gen_improvement = gen * 0.03
        noise = random.uniform(-0.05, 0.05)
        
        best_fitness = base_fitness + gen_improvement + noise
        avg_fitness = best_fitness * 0.7
        best_profit = base_profit + gen * 2 + random.uniform(-2, 5)
        diversity_score = max(0.2, diversity - gen * 0.02)
        
        # Save generation stats
        db.save_generation(gen, {
            'best_fitness': best_fitness,
            'avg_fitness': avg_fitness,
            'best_profit': best_profit,
            'population_size': strategies_per_gen,
            'diversity': diversity_score
        })
        
        # Create strategies for this generation
        for i in range(strategies_per_gen):
            strategy_name = f"strategy_gen{gen:03d}_{i:02d}"
            
            # Fitness varies within generation
            fitness = avg_fitness + random.uniform(0, best_fitness - avg_fitness)
            
            # Calculate correlated metrics
            profit = best_profit * (fitness / best_fitness) + random.uniform(-3, 3)
            sharpe = max(0, fitness * 2 + random.uniform(-0.5, 0.5))
            drawdown = -5 - (1 - fitness) * 15 + random.uniform(-2, 2)
            win_rate = 45 + fitness * 30 + random.uniform(-5, 5)
            trades = random.randint(50, 200)
            
            # Save strategy result
            db.save_result(
                strategy_name=strategy_name,
                generation=gen,
                fitness=fitness,
                metrics={
                    'total_profit_pct': profit,
                    'sharpe_ratio': sharpe,
                    'max_drawdown': drawdown,
                    'win_rate': win_rate,
                    'trades_count': trades,
                    'avg_trade': profit / trades if trades > 0 else 0
                }
            )
        
        if (gen + 1) % 5 == 0:
            print(f"  Generated {gen + 1}/{generations} generations...")
    
    print("✓ Sample data created successfully!")
    return db


def main():
    """Main demo function."""
    print("=" * 80)
    print("GAFreqTrade Visualization Demo")
    print("=" * 80)
    print()
    
    # Create temporary database
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "demo.db")
        output_dir = "plots/demo"
        
        # Create sample data
        db = create_sample_data(db_path, generations=25, strategies_per_gen=10)
        
        # Create visualizer
        print("\nInitializing visualizer...")
        visualizer = EvolutionVisualizer(db, output_dir)
        
        # Generate all plots
        print("\nGenerating visualization plots...")
        print("-" * 80)
        
        plots = {}
        
        print("\n1. Fitness Evolution Plot...")
        plots['fitness'] = visualizer.plot_fitness_over_generations(show_diversity=True)
        print(f"   ✓ Saved to: {plots['fitness']}")
        
        print("\n2. Performance Comparison...")
        plots['performance'] = visualizer.plot_performance_comparison(top_n=15)
        print(f"   ✓ Saved to: {plots['performance']}")
        
        print("\n3. Population Diversity...")
        plots['diversity'] = visualizer.plot_population_diversity()
        print(f"   ✓ Saved to: {plots['diversity']}")
        
        print("\n4. Top Strategies Dashboard...")
        plots['dashboard'] = visualizer.create_top_strategies_dashboard(top_n=15)
        print(f"   ✓ Saved to: {plots['dashboard']}")
        
        print("\n" + "=" * 80)
        print("DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print(f"\nAll demo plots have been saved to: {output_dir}")
        print("\nGenerated files:")
        for plot_type, plot_path in plots.items():
            print(f"  • {plot_type.title()}: {plot_path}")
        
        print("\n" + "-" * 80)
        print("You can view these plots using any image viewer.")
        print("Try the visualization with your own evolution data:")
        print("  python visualize_evolution.py --db storage/strategies.db")
        print("=" * 80)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
