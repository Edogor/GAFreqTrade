#!/usr/bin/env python3
"""
Monitor - Display evolution progress and statistics.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import argparse
import time
from pathlib import Path
from storage.strategy_db import StrategyDB
from utils.visualization import EvolutionVisualizer


def display_stats(db: StrategyDB, clear_screen: bool = False):
    """Display evolution statistics."""
    if clear_screen:
        os.system('clear' if os.name == 'posix' else 'cls')
    
    generations = db.get_all_generations()
    
    if not generations:
        print("No generations found. Run evolution first.")
        return
    
    print("\n" + "=" * 80)
    print("GAFreqTrade Evolution Monitor")
    print("=" * 80)
    
    print(f"\nTotal Generations: {len(generations)}")
    
    # Latest generation
    latest = generations[-1]
    print(f"\nLatest Generation: {latest['generation']}")
    print(f"  Best Fitness: {latest['best_fitness']:.4f}")
    print(f"  Avg Fitness: {latest['avg_fitness']:.4f}")
    print(f"  Best Profit: {latest['best_profit']:.2f}%")
    
    # Overall best
    best_gen = max(generations, key=lambda x: x['best_fitness'])
    print(f"\nOverall Best:")
    print(f"  Generation: {best_gen['generation']}")
    print(f"  Fitness: {best_gen['best_fitness']:.4f}")
    print(f"  Profit: {best_gen['best_profit']:.2f}%")
    
    # Progress over last 10 generations
    if len(generations) >= 10:
        recent = generations[-10:]
        print(f"\nLast 10 Generations:")
        for gen in recent:
            print(f"  Gen {gen['generation']:3d}: "
                  f"Best={gen['best_fitness']:.4f}, "
                  f"Avg={gen['avg_fitness']:.4f}, "
                  f"Profit={gen['best_profit']:.2f}%")
    
    # Top strategies
    print(f"\nTop 5 Strategies:")
    top_strategies = db.get_top_strategies(5)
    for i, strategy in enumerate(top_strategies, 1):
        profit = strategy.get('profit') or 0
        print(f"  {i}. {strategy['name']}: "
              f"Fitness={strategy['fitness']:.4f}, "
              f"Profit={profit:.2f}%")
    
    print("\n" + "=" * 80)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='GAFreqTrade Monitor - Display evolution progress',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--db',
        type=str,
        default='storage/strategies.db',
        help='Path to database file (default: storage/strategies.db)'
    )
    
    parser.add_argument(
        '--live',
        action='store_true',
        help='Live monitoring mode (refresh every 10 seconds)'
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        default=10,
        help='Refresh interval for live mode in seconds (default: 10)'
    )
    
    parser.add_argument(
        '--plot',
        action='store_true',
        help='Generate visualization plots'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='plots',
        help='Output directory for plots (default: plots)'
    )
    
    args = parser.parse_args()
    
    # Check if database exists
    if not Path(args.db).exists():
        print(f"Error: Database not found at {args.db}")
        print("Run evolution first to create strategies.")
        return 1
    
    # Load database
    db = StrategyDB(args.db)
    
    # Generate plots if requested
    if args.plot:
        print(f"\nGenerating visualization plots in '{args.output_dir}'...")
        visualizer = EvolutionVisualizer(db, args.output_dir)
        plots = visualizer.generate_all_plots()
        
        print("\nGenerated plots:")
        for plot_type, plot_path in plots.items():
            if plot_path:
                print(f"  ✓ {plot_type}: {plot_path}")
        print()
    
    if args.live:
        print("Starting live monitoring (press Ctrl+C to exit)...")
        try:
            while True:
                display_stats(db, clear_screen=True)
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\n\nMonitoring stopped.")
    else:
        display_stats(db)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
