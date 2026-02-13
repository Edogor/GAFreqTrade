#!/usr/bin/env python3
"""
Visualize Evolution - Generate visualization plots for evolution progress.

This script provides an easy way to generate all visualization plots
from the evolution database.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import argparse
from pathlib import Path
from datetime import datetime
from storage.strategy_db import StrategyDB
from utils.visualization import EvolutionVisualizer, create_quick_report


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='GAFreqTrade Visualization Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate all plots
  python visualize_evolution.py
  
  # Specify custom database and output directory
  python visualize_evolution.py --db my_db.db --output my_plots
  
  # Generate specific plots only
  python visualize_evolution.py --fitness --dashboard
  
  # Custom plot settings
  python visualize_evolution.py --top-n 20 --diversity
        """
    )
    
    parser.add_argument(
        '--db',
        type=str,
        default='storage/strategies.db',
        help='Path to database file (default: storage/strategies.db)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='plots',
        help='Output directory for plots (default: plots)'
    )
    
    # Specific plot options
    parser.add_argument(
        '--fitness',
        action='store_true',
        help='Generate fitness evolution plot only'
    )
    
    parser.add_argument(
        '--performance',
        action='store_true',
        help='Generate performance comparison plot only'
    )
    
    parser.add_argument(
        '--diversity',
        action='store_true',
        help='Generate population diversity plot only'
    )
    
    parser.add_argument(
        '--dashboard',
        action='store_true',
        help='Generate top strategies dashboard only'
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Generate all plots (default if no specific plot is selected)'
    )
    
    # Plot customization
    parser.add_argument(
        '--top-n',
        type=int,
        default=10,
        help='Number of top strategies to include (default: 10)'
    )
    
    parser.add_argument(
        '--show-diversity',
        action='store_true',
        help='Show diversity on fitness plot'
    )
    
    args = parser.parse_args()
    
    # Check if database exists
    if not Path(args.db).exists():
        print(f"Error: Database not found at {args.db}")
        print("Run evolution first to create strategies.")
        return 1
    
    # Load database
    print(f"Loading database from {args.db}...")
    db = StrategyDB(args.db)
    
    # Create visualizer
    visualizer = EvolutionVisualizer(db, args.output)
    
    # Determine what to generate
    generate_all = args.all or not any([args.fitness, args.performance, args.diversity, args.dashboard])
    
    print(f"\nGenerating visualization plots in '{args.output}'...")
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_subdir = f"viz_{timestamp}"
    
    plots_generated = []
    
    try:
        if generate_all or args.fitness:
            print("  → Generating fitness evolution plot...")
            plot_path = visualizer.plot_fitness_over_generations(
                show_diversity=args.show_diversity
            )
            if plot_path:
                plots_generated.append(("Fitness Evolution", plot_path))
        
        if generate_all or args.performance:
            print("  → Generating performance comparison...")
            plot_path = visualizer.plot_performance_comparison(top_n=args.top_n)
            if plot_path:
                plots_generated.append(("Performance Comparison", plot_path))
        
        if generate_all or args.diversity:
            print("  → Generating population diversity plot...")
            plot_path = visualizer.plot_population_diversity()
            if plot_path:
                plots_generated.append(("Population Diversity", plot_path))
        
        if generate_all or args.dashboard:
            print("  → Generating top strategies dashboard...")
            plot_path = visualizer.create_top_strategies_dashboard(top_n=args.top_n)
            if plot_path:
                plots_generated.append(("Dashboard", plot_path))
        
        # Summary
        print("\n" + "=" * 80)
        print("VISUALIZATION SUMMARY")
        print("=" * 80)
        print(f"\nGenerated {len(plots_generated)} plot(s):\n")
        
        for plot_name, plot_path in plots_generated:
            print(f"  ✓ {plot_name}")
            print(f"    → {plot_path}")
            print()
        
        print("=" * 80)
        print(f"All plots saved in: {args.output}")
        print("=" * 80)
        
        return 0
        
    except Exception as e:
        print(f"\nError generating plots: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
